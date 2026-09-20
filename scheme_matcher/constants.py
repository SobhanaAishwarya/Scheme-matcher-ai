"""Shared constants: option lists, field labels and display formatting."""
from __future__ import annotations

from typing import Any

OCCUPATIONS = {
    "student": "Student",
    "farmer": "Farmer",
    "entrepreneur": "Entrepreneur / Self-employed / Planning a business",
    "salaried": "Salaried employee",
    "unemployed": "Unemployed / Job seeker",
    "homemaker": "Homemaker",
}

GENDERS = {
    "female": "Female",
    "male": "Male",
    "other": "Other / Prefer not to say",
}

CATEGORIES = {
    "general": "General",
    "obc": "OBC",
    "sc": "SC (Scheduled Caste)",
    "st": "ST (Scheduled Tribe)",
    "ews": "EWS",
}

EDUCATION = {
    "class_9_10": "Class 9-10",
    "class_11_12": "Class 11-12",
    "diploma_iti": "Diploma / ITI",
    "undergraduate": "Undergraduate (Degree)",
    "postgraduate": "Postgraduate",
}

BUSINESS_STAGES = {
    "new": "New venture (not started yet)",
    "existing": "Existing business (already running)",
}

FIELD_OPTIONS = {
    "occupation": OCCUPATIONS,
    "gender": GENDERS,
    "category": CATEGORIES,
    "education": EDUCATION,
    "business_stage": BUSINESS_STAGES,
}

FIELD_LABELS = {
    "age": "Age",
    "gender": "Gender",
    "category": "Social category",
    "occupation": "Occupation",
    "income": "Annual family income",
    "education": "Education level",
    "marks": "Class 12 score",
    "land_ha": "Agricultural land",
    "business_stage": "Business stage",
    "project_cost": "Funding needed",
}

MONEY_FIELDS = {"income", "project_cost"}


def inr(amount: float) -> str:
    """Format a number the Indian way: 1234567 -> 'Rs 12,34,567'."""
    n = int(round(amount))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + "Rs " + s


def format_value(field: str, value: Any) -> str:
    """Human-readable version of a profile value."""
    if value is None:
        return "Not provided"
    if field in FIELD_OPTIONS:
        return FIELD_OPTIONS[field].get(value, str(value))
    if field in MONEY_FIELDS:
        return inr(value)
    if field == "age":
        return f"{int(value)} years"
    if field == "marks":
        return f"{value:g}%"
    if field == "land_ha":
        return f"{value:g} ha"
    return str(value)
