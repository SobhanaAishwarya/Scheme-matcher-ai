"""Ranking Agent - orders schemes by benefit size and how targeted they are."""
from __future__ import annotations

import time

from .base import Agent, State

SPECIFICITY_LABELS = {
    3: "Designed specifically for your profile",
    2: "Good fit for your profile",
    1: "Broad scheme open to many people",
}


def rank_score(scheme: dict) -> int:
    """benefit (1-10) weighted x10 + targeting (1-3) weighted x10 => 20..130."""
    return scheme["benefit_score"] * 10 + scheme["specificity"] * 10


def priority_reason(scheme: dict) -> str:
    bits = []
    if scheme["benefit_score"] >= 8:
        bits.append("High-value benefit")
    elif scheme["benefit_score"] >= 6:
        bits.append("Solid benefit")
    else:
        bits.append("Useful safety net")
    bits.append(SPECIFICITY_LABELS[scheme["specificity"]])
    return " · ".join(bits)


class RankingAgent(Agent):
    name = "Ranking Agent"
    icon = "🏆"
    role = "Ranks matches by benefit size and relevance to the user"

    def run(self, state: State) -> State:
        t0 = time.perf_counter()
        groups: dict[str, list] = {"eligible": [], "near_miss": [], "not_eligible": []}
        for ev in state["evaluations"]:
            ev["rank_score"] = rank_score(ev["scheme"])
            ev["priority_reason"] = priority_reason(ev["scheme"])
            groups[ev["status"]].append(ev)

        for key in ("eligible", "near_miss"):
            groups[key].sort(key=lambda e: (-e["rank_score"], e["scheme"]["name"]))
        groups["not_eligible"].sort(key=lambda e: e["scheme"]["name"])

        for i, ev in enumerate(groups["eligible"], start=1):
            ev["rank"] = i

        state["ranked"] = groups
        top = groups["eligible"][0]["scheme"]["short_name"] if groups["eligible"] else "n/a"
        self.log(
            state,
            "Ranked matches",
            f"Score = benefit x10 + targeting x10. Top match: {top}.",
            t0,
        )
        return state
