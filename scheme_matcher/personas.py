"""Ready-made demo personas (synthetic people, no real data)."""
from __future__ import annotations

from typing import Any

from .constants import format_value
from .questions import applicable_questions

PERSONAS: list[dict[str, Any]] = [
    {
        "name": "Lakshmi - woman entrepreneur",
        "blurb": "28, SC, planning a Rs 12 lakh venture",
        "profile": {
            "age": 28, "gender": "female", "category": "sc", "occupation": "entrepreneur",
            "income": 240000, "business_stage": "new", "project_cost": 1200000,
        },
    },
    {
        "name": "Ramesh - farmer",
        "blurb": "45, OBC, 1.5 ha of land",
        "profile": {
            "age": 45, "gender": "male", "category": "obc", "occupation": "farmer",
            "income": 180000, "land_ha": 1.5,
        },
    },
    {
        "name": "Priya - college student",
        "blurb": "19, SC, BSc, 88% in Class 12, income Rs 3 lakh",
        "profile": {
            "age": 19, "gender": "female", "category": "sc", "occupation": "student",
            "income": 300000, "education": "undergraduate", "marks": 88.0,
        },
    },
    {
        "name": "Ravi - job seeker",
        "blurb": "24, unemployed, looking for skills",
        "profile": {
            "age": 24, "gender": "male", "category": "general", "occupation": "unemployed",
            "income": 120000,
        },
    },
    {
        "name": "Kamala - senior citizen",
        "blurb": "71, homemaker",
        "profile": {
            "age": 71, "gender": "female", "category": "general", "occupation": "homemaker",
            "income": 90000,
        },
    },
]


def build_history(profile: dict[str, Any]) -> list[dict[str, str]]:
    """Recreate the chat transcript for a pre-filled profile."""
    history = []
    for q in applicable_questions(profile):
        if q["id"] in profile:
            history.append(
                {
                    "qid": q["id"],
                    "question": q["text"],
                    "answer": format_value(q["id"], profile[q["id"]]),
                }
            )
    return history
