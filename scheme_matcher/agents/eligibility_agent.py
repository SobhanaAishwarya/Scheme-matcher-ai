"""Eligibility Agent - checks the profile against every scheme (rules engine)."""
from __future__ import annotations

import time

from ..rules_engine import evaluate_all
from .base import Agent, State


class EligibilityAgent(Agent):
    name = "Eligibility Agent"
    role = "Runs deterministic rule checks: eligible / near-miss / not eligible"

    def run(self, state: State) -> State:
        t0 = time.perf_counter()
        evaluations = evaluate_all(state["schemes"], state["profile"])
        state["evaluations"] = evaluations

        counts = {"eligible": 0, "near_miss": 0, "not_eligible": 0}
        rules_checked = 0
        for ev in evaluations:
            counts[ev["status"]] += 1
            rules_checked += len(ev["rules"])

        self.log(
            state,
            f"Checked {len(evaluations)} schemes ({rules_checked} rules)",
            f"{counts['eligible']} eligible, {counts['near_miss']} near-miss, "
            f"{counts['not_eligible']} not eligible",
            t0,
        )
        return state
