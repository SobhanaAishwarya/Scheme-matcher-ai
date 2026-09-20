"""Adaptive intake questions.

Every question may carry an ``ask_if`` condition, e.g. {"occupation": ["farmer"]}.
The question is only asked when the earlier answers satisfy the condition, so a
farmer is never asked about business turnover and a student is never asked
about land holding. A typical user answers 5-8 questions.
"""
from __future__ import annotations

from typing import Any

from .constants import (
    BUSINESS_STAGES,
    CATEGORIES,
    EDUCATION,
    GENDERS,
    OCCUPATIONS,
)

QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "age",
        "text": "First, how old are you?",
        "type": "number",
        "kind": "int",
        "min": 10,
        "max": 100,
        "default": 25,
        "step": 1,
    },
    {
        "id": "gender",
        "text": "What is your gender?",
        "type": "choice",
        "options": GENDERS,
        "help": "Some schemes are reserved for women entrepreneurs.",
    },
    {
        "id": "category",
        "text": "Which social category do you belong to?",
        "type": "choice",
        "options": CATEGORIES,
        "help": "Several scholarships and loan schemes depend on this.",
    },
    {
        "id": "occupation",
        "text": "What best describes what you do at present?",
        "type": "choice",
        "options": OCCUPATIONS,
    },
    {
        "id": "income",
        "text": "What is your total annual family income (in Rs)?",
        "type": "number",
        "kind": "int",
        "min": 0,
        "max": 100_000_000,
        "default": 200_000,
        "step": 10_000,
        "help": "Add up the yearly income of everyone in your household.",
    },
    # ---- adaptive follow-ups ------------------------------------------------
    {
        "id": "education",
        "text": "What is your current education level?",
        "type": "choice",
        "options": EDUCATION,
        "ask_if": {"occupation": ["student"]},
    },
    {
        "id": "marks",
        "text": "What percentage did you score in Class 12 (board exams)?",
        "type": "number",
        "kind": "float",
        "min": 0.0,
        "max": 100.0,
        "default": 60.0,
        "step": 1.0,
        "ask_if": {"occupation": ["student"], "education": ["undergraduate", "postgraduate"]},
    },
    {
        "id": "land_ha",
        "text": "How much cultivable land is registered in your name (in hectares)?",
        "type": "number",
        "kind": "float",
        "min": 0.0,
        "max": 1000.0,
        "default": 1.0,
        "step": 0.5,
        "help": "Enter 0 if you have no land in your name. 1 hectare is about 2.47 acres.",
        "ask_if": {"occupation": ["farmer"]},
    },
    {
        "id": "business_stage",
        "text": "Is your business idea new, or is it already running?",
        "type": "choice",
        "options": BUSINESS_STAGES,
        "ask_if": {"occupation": ["entrepreneur"]},
    },
    {
        "id": "project_cost",
        "text": "Roughly how much funding / project cost do you need (in Rs)?",
        "type": "number",
        "kind": "int",
        "min": 0,
        "max": 1_000_000_000,
        "default": 500_000,
        "step": 50_000,
        "ask_if": {"occupation": ["entrepreneur"]},
    },
]

QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}
BASE_IDS = ["age", "gender", "category", "occupation", "income"]


def is_applicable(question: dict[str, Any], profile: dict[str, Any]) -> bool:
    cond = question.get("ask_if")
    if not cond:
        return True
    return all(profile.get(field) in allowed for field, allowed in cond.items())


def next_question(profile: dict[str, Any]) -> dict[str, Any] | None:
    """Return the next unanswered, applicable question (or None when done)."""
    for q in QUESTIONS:
        if q["id"] not in profile and is_applicable(q, profile):
            return q
    return None


def applicable_questions(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """All questions that apply to this (possibly complete) profile, in order."""
    return [q for q in QUESTIONS if is_applicable(q, profile)]


def progress(profile: dict[str, Any]) -> tuple[int, int]:
    """(answered, estimated_total) for a progress bar."""
    answered = sum(1 for q in QUESTIONS if q["id"] in profile)
    remaining = sum(
        1 for q in QUESTIONS if q["id"] not in profile and is_applicable(q, profile)
    )
    total = answered + remaining
    if "occupation" not in profile:
        total += 1  # at least one adaptive follow-up is likely
    return answered, max(total, 1)
