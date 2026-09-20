"""Explanation Agent - writes the 'why you qualify' text.

* With an LLM: one batched call turns the rule results into friendly language.
  The LLM only receives facts produced by the rules engine and may not invent any.
* Without an LLM (or if the call fails): deterministic template explanations.
"""
from __future__ import annotations

import json
import time
from typing import Any

from ..constants import FIELD_LABELS, format_value
from .base import Agent, State

SYSTEM_PROMPT = (
    "You are a helpful assistant that explains Indian government scheme eligibility "
    "to ordinary citizens in simple, warm, plain English. You are given verified "
    "eligibility results produced by a rules engine. Use ONLY the facts provided. "
    "Never invent eligibility rules, amounts, deadlines or documents. "
    "Write in second person ('you'). Keep each explanation to 2-3 short sentences. "
    "For 'eligible' schemes: explain which of the user's details make them qualify and "
    "mention the main benefit in a few words. For 'near_miss' schemes: say clearly which "
    "single condition is not met and what would fix it, using the hint. "
    "Reply with ONLY valid JSON, no markdown fences."
)


# --------------------------------------------------------------------------- #
# Template (deterministic) explanations
# --------------------------------------------------------------------------- #
def template_explanation(ev: dict[str, Any]) -> str:
    s = ev["scheme"]
    if ev["status"] == "eligible":
        bits = [f"{r['label']} (you: {r['actual_display']})" for r in ev["passed"]]
        return (
            f"You qualify for {s['short_name']} because you meet all {len(ev['rules'])} "
            f"conditions: " + "; ".join(bits) + "."
        )
    if ev["status"] == "near_miss":
        f = ev["failed"][0]
        return (
            f"You are one condition away from {s['short_name']}. Everything matches except "
            f"'{f['label']}' (you: {f['actual_display']}). To qualify: {f['hint']}"
        )
    b = ev["blocking"]
    extra = len(ev["failed"]) - 1
    more = f" (+{extra} more condition{'s' if extra != 1 else ''} not met)" if extra else ""
    return f"Not eligible right now: '{b['label']}' not met (you: {b['actual_display']}){more}. {b['hint']}"


def template_summary(state: State) -> str:
    evs = state["evaluations"]
    elig = [e for e in evs if e["status"] == "eligible"]
    near = [e for e in evs if e["status"] == "near_miss"]
    if not elig and not near:
        return (
            "Based on your answers, none of the schemes in our current dataset match right now. "
            "You can start over with different details or explore more schemes on MyScheme.gov.in."
        )
    parts = [f"Good news - you are eligible for {len(elig)} scheme{'s' if len(elig) != 1 else ''}."]
    if near:
        parts.append(
            f"{len(near)} more {'is' if len(near) == 1 else 'are'} only one condition away."
        )
    parts.append("The schemes below are ranked by size of benefit and how closely they target your profile.")
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# LLM explanations
# --------------------------------------------------------------------------- #
def _facts_for_llm(state: State) -> list[dict[str, Any]]:
    facts = []
    for ev in state["evaluations"]:
        if ev["status"] not in ("eligible", "near_miss"):
            continue
        s = ev["scheme"]
        facts.append(
            {
                "id": s["id"],
                "scheme": s["name"],
                "status": ev["status"],
                "benefit": s["benefit"],
                "conditions_met": [
                    {"condition": r["label"], "user_value": r["actual_display"]}
                    for r in ev["passed"]
                ],
                "conditions_not_met": [
                    {"condition": r["label"], "user_value": r["actual_display"], "hint": r["hint"]}
                    for r in ev["failed"]
                ],
            }
        )
    return facts


def _profile_for_llm(profile: dict[str, Any]) -> dict[str, str]:
    return {FIELD_LABELS.get(k, k): format_value(k, v) for k, v in profile.items()}


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM reply did not contain JSON")
    return json.loads(text[start : end + 1])


class ExplanationAgent(Agent):
    name = "Explanation Agent"
    icon = "💬"
    role = "Turns rule results into plain-language 'why you qualify' reasoning"

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, state: State) -> State:
        t0 = time.perf_counter()
        mode, error = "template", None
        llm_texts: dict[str, str] = {}
        summary = None

        facts = _facts_for_llm(state)
        if self.llm is not None and facts:
            try:
                user_msg = json.dumps(
                    {
                        "user_profile": _profile_for_llm(state["profile"]),
                        "schemes": facts,
                        "output_format": {
                            "summary": "2-3 sentence friendly overview naming the best 1-2 schemes and one next step",
                            "explanations": {"<scheme id>": "explanation text for that scheme"},
                        },
                    },
                    ensure_ascii=False,
                )
                data = _parse_json(self.llm.complete(SYSTEM_PROMPT, user_msg))
                llm_texts = {
                    k: v.strip()
                    for k, v in (data.get("explanations") or {}).items()
                    if isinstance(v, str) and v.strip()
                }
                summary = data.get("summary") if isinstance(data.get("summary"), str) else None
                mode = f"LLM ({self.llm.label})"
            except Exception as exc:  # noqa: BLE001 - never let the LLM break the app
                error = f"{type(exc).__name__}: {exc}"
                llm_texts, summary, mode = {}, None, "template (LLM failed)"

        from_llm = 0
        for ev in state["evaluations"]:
            text = llm_texts.get(ev["scheme_id"])
            if text and ev["status"] in ("eligible", "near_miss"):
                ev["explanation"] = text
                ev["explanation_source"] = "llm"
                from_llm += 1
            else:
                ev["explanation"] = template_explanation(ev)
                ev["explanation_source"] = "template"

        state["summary"] = summary.strip() if summary else template_summary(state)
        state["llm_mode"] = mode
        state["llm_error"] = error

        detail = f"Mode: {mode}. {from_llm} LLM explanations, "
        detail += f"{len(state['evaluations']) - from_llm} template explanations."
        if error:
            detail += f" LLM error (fell back safely): {error}"
        self.log(
            state,
            "Generated explanations",
            detail,
            t0,
            status="warn" if error else "ok",
        )
        return state
