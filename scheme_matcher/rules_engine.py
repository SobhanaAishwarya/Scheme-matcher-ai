"""Deterministic eligibility rules engine.

Each scheme has a list of rules. A rule is either

  * a leaf:   {"field": "age", "op": "gte", "value": 18, "label": ..., "fixable": bool, "hint": ...}
  * an OR-group: {"any_of": [leaf, leaf, ...], "label": ..., "fixable": bool, "hint": ...}

A scheme evaluates to one of three statuses:

  eligible      every rule passes
  near_miss     exactly ONE rule fails, that rule is 'fixable' and the value is
                reasonably close to the limit (e.g. income within 50% of the cap)
  not_eligible  anything else

The engine never calls an LLM - eligibility is always reproducible and explainable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import format_value

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "schemes.json"

# A numeric limit is "close" if the user is within this factor of it.
NEAR_UP = 1.5    # e.g. income up to 1.5x the maximum allowed
NEAR_DOWN = 0.5  # e.g. marks / cost at least 0.5x the minimum required


def load_schemes(path: str | Path | None = None) -> list[dict[str, Any]]:
    with open(path or DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["schemes"]


# --------------------------------------------------------------------------- #
# Leaf checks
# --------------------------------------------------------------------------- #
def _check(op: str, actual: Any, expected: Any) -> bool:
    if actual is None:
        return False  # unanswered question => cannot qualify
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "in":
        return actual in expected
    if op == "not_in":
        return actual not in expected
    if op == "gte":
        return actual >= expected
    if op == "lte":
        return actual <= expected
    if op == "gt":
        return actual > expected
    if op == "lt":
        return actual < expected
    if op == "between":
        return expected[0] <= actual <= expected[1]
    raise ValueError(f"Unknown operator: {op}")


def _within_tolerance(rule: dict[str, Any], actual: Any) -> bool:
    """For numeric limits, is a failing value still 'close' to passing?"""
    if actual is None:
        return False
    op, val = rule["op"], rule["value"]
    if op == "lte":
        return actual <= val * NEAR_UP
    if op == "gte":
        return actual >= val * NEAR_DOWN
    if op == "between":
        return val[0] * NEAR_DOWN <= actual <= val[1] * NEAR_UP
    return True  # categorical / boolean-style rules: always 'closable'


def _eval_leaf(rule: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    field = rule["field"]
    actual = profile.get(field)
    passed = _check(rule["op"], actual, rule["value"])
    return {"field": field, "passed": passed, "actual": actual}


# --------------------------------------------------------------------------- #
# Rule / scheme evaluation
# --------------------------------------------------------------------------- #
def evaluate_rule(rule: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    fixable = bool(rule.get("fixable", False))

    if "any_of" in rule:  # OR-group
        subs = [_eval_leaf(r, profile) for r in rule["any_of"]]
        passed = any(s["passed"] for s in subs)
        shown: list[str] = []
        for s in subs:
            text = format_value(s["field"], s["actual"])
            if text not in shown:
                shown.append(text)
        return {
            "label": rule["label"],
            "passed": passed,
            "fixable": fixable,
            "near": False,
            "hint": rule.get("hint", ""),
            "actual": [s["actual"] for s in subs],
            "actual_display": " / ".join(shown),
        }

    leaf = _eval_leaf(rule, profile)
    near = (
        (not leaf["passed"])
        and fixable
        and _within_tolerance(rule, leaf["actual"])
    )
    return {
        "label": rule["label"],
        "passed": leaf["passed"],
        "fixable": fixable,
        "near": near,
        "hint": rule.get("hint", ""),
        "actual": leaf["actual"],
        "actual_display": format_value(rule["field"], leaf["actual"]),
    }


def evaluate_scheme(scheme: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    results = [evaluate_rule(r, profile) for r in scheme["rules"]]
    failed = [r for r in results if not r["passed"]]
    passed = [r for r in results if r["passed"]]

    if not failed:
        status = "eligible"
    elif len(failed) == 1 and failed[0]["near"]:
        status = "near_miss"
    else:
        status = "not_eligible"

    blocking = None
    if failed:
        blocking = next((f for f in failed if not f["fixable"]), failed[0])

    return {
        "scheme": scheme,
        "scheme_id": scheme["id"],
        "status": status,
        "rules": results,
        "passed": passed,
        "failed": failed,
        "blocking": blocking,
    }


def evaluate_all(schemes: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    return [evaluate_scheme(s, profile) for s in schemes]
