"""Intake Agent - owns the adaptive question flow and validates the profile."""
from __future__ import annotations

import time

from ..questions import BASE_IDS, QUESTIONS, applicable_questions, next_question
from .base import Agent, State


class IntakeAgent(Agent):
    name = "Intake Agent"
    role = "Asks adaptive questions and builds a clean user profile"

    # Question flow is exposed as thin wrappers so the UI talks to the agent.
    @staticmethod
    def next_question(profile):
        return next_question(profile)

    def run(self, state: State) -> State:
        t0 = time.perf_counter()
        profile = dict(state["profile"])

        missing = [f for f in BASE_IDS if profile.get(f) is None]
        if missing:
            raise ValueError(f"Profile is incomplete, missing: {', '.join(missing)}")

        # Normalise types
        profile["age"] = int(profile["age"])
        profile["income"] = int(profile["income"])
        for key in ("marks", "land_ha"):
            if key in profile and profile[key] is not None:
                profile[key] = float(profile[key])
        if "project_cost" in profile and profile["project_cost"] is not None:
            profile["project_cost"] = int(profile["project_cost"])

        # Drop answers to questions that no longer apply (e.g. after editing)
        valid_ids = {q["id"] for q in applicable_questions(profile)}
        profile = {k: v for k, v in profile.items() if k in valid_ids}

        state["profile"] = profile
        asked = len(profile)
        skipped = len(QUESTIONS) - asked
        self.log(
            state,
            "Validated profile",
            f"{asked} answers collected ({skipped} irrelevant questions skipped adaptively): "
            + ", ".join(sorted(profile)),
            t0,
        )
        return state
