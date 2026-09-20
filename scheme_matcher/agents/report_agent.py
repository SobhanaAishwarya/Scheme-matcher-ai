"""Report Agent - builds the final downloadable report (Markdown + PDF)."""
from __future__ import annotations

import io
import time
from datetime import date
from typing import Any
from xml.sax.saxutils import escape

from ..constants import FIELD_LABELS, format_value
from ..questions import QUESTIONS
from .base import Agent, State

DISCLAIMER = (
    "This report is a decision-support aid built from a simplified, curated scheme dataset. "
    "Eligibility rules change and some conditions (e.g. state-specific rules) are not modelled. "
    "Always confirm the latest criteria on the official scheme portal before applying."
)


# --------------------------------------------------------------------------- #
# Markdown
# --------------------------------------------------------------------------- #
def build_markdown(state: State) -> str:
    profile = state["profile"]
    ranked = state["ranked"]
    lines: list[str] = []
    lines.append("# Government Scheme Eligibility Report")
    lines.append(f"_Generated on {date.today().strftime('%d %b %Y')}_\n")

    lines.append("## Your profile")
    for q in QUESTIONS:
        if q["id"] in profile:
            lines.append(f"- **{FIELD_LABELS.get(q['id'], q['id'])}:** {format_value(q['id'], profile[q['id']])}")
    lines.append("")

    lines.append("## Summary")
    lines.append(state.get("summary", ""))
    lines.append("")

    lines.append(f"## Schemes you are eligible for ({len(ranked['eligible'])})")
    if not ranked["eligible"]:
        lines.append("_No fully matching schemes found._\n")
    for ev in ranked["eligible"]:
        s = ev["scheme"]
        lines.append(f"### {ev['rank']}. {s['name']}")
        lines.append(f"- **Benefit:** {s['benefit']}")
        lines.append(f"- **Why you qualify:** {ev['explanation']}")
        lines.append("- **Documents to keep ready:**")
        for d in s["documents"]:
            lines.append(f"  - [ ] {d}")
        lines.append(f"- **How to apply:** {s['how_to_apply']}")
        lines.append(f"- **Official link:** {s['apply_url']}\n")

    lines.append(f"## Near-miss schemes ({len(ranked['near_miss'])})")
    if not ranked["near_miss"]:
        lines.append("_None._\n")
    for ev in ranked["near_miss"]:
        s = ev["scheme"]
        f = ev["failed"][0]
        lines.append(f"### {s['name']}")
        lines.append(f"- **Benefit:** {s['benefit']}")
        lines.append(f"- **What is missing:** {f['label']} (you: {f['actual_display']})")
        lines.append(f"- **How to become eligible:** {f['hint']}")
        lines.append(f"- **Official link:** {s['apply_url']}\n")

    lines.append(f"## Not eligible ({len(ranked['not_eligible'])})")
    for ev in ranked["not_eligible"]:
        b = ev["blocking"]
        lines.append(f"- {ev['scheme']['short_name']}: {b['label']} (you: {b['actual_display']})")
    lines.append("")
    lines.append("---")
    lines.append(f"**Disclaimer:** {DISCLAIMER}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# PDF (reportlab, optional dependency)
# --------------------------------------------------------------------------- #
def _pdf_safe(text: Any) -> str:
    """Standard PDF fonts only cover Latin-1/cp1252; replace anything else."""
    t = str(text)
    for src, dst in {"≤": "<=", "≥": ">=", "≈": "~", "→": "->", "·": "-"}.items():
        t = t.replace(src, dst)
    return escape(t.encode("cp1252", "replace").decode("cp1252"))


def build_pdf(state: State) -> bytes | None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        return None

    profile, ranked = state["profile"], state["ranked"]
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1F3A5F"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#1F3A5F"), spaceBefore=10)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], spaceBefore=8, spaceAfter=2)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.HexColor("#555555"))

    def P(text, style=body):
        return Paragraph(_pdf_safe(text), style)

    story: list[Any] = [P("Government Scheme Eligibility Report", h1)]
    story.append(P(f"Generated on {date.today().strftime('%d %b %Y')}", small))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#1F3A5F")))

    def bold_line(label: str, value: str):
        # label is trusted, value is escaped by _pdf_safe
        return Paragraph(f"<b>{escape(label)}</b> {_pdf_safe(value)}", body)

    story.append(P("Your profile", h2))
    for q in QUESTIONS:
        if q["id"] in profile:
            story.append(
                bold_line(f"{FIELD_LABELS.get(q['id'], q['id'])}:", format_value(q["id"], profile[q["id"]]))
            )
    story.append(P("Summary", h2))
    story.append(P(state.get("summary", "")))

    story.append(P(f"Schemes you are eligible for ({len(ranked['eligible'])})", h2))
    for ev in ranked["eligible"]:
        s = ev["scheme"]
        story.append(P(f"{ev['rank']}. {s['name']}", h3))
        story.append(bold_line("Benefit:", s["benefit"]))
        story.append(bold_line("Why you qualify:", ev["explanation"]))
        story.append(bold_line("Documents to keep ready:", ""))
        story.append(ListFlowable([ListItem(P(d)) for d in s["documents"]], bulletType="bullet", leftIndent=14))
        story.append(bold_line("How to apply:", s["how_to_apply"]))
        story.append(bold_line("Official link:", s["apply_url"]))

    story.append(P(f"Near-miss schemes ({len(ranked['near_miss'])})", h2))
    for ev in ranked["near_miss"]:
        s, f = ev["scheme"], ev["failed"][0]
        story.append(P(s["name"], h3))
        story.append(bold_line("Benefit:", s["benefit"]))
        story.append(bold_line("What is missing:", f"{f['label']} (you: {f['actual_display']})"))
        story.append(bold_line("How to become eligible:", f["hint"]))

    story.append(P(f"Not eligible ({len(ranked['not_eligible'])})", h2))
    for ev in ranked["not_eligible"]:
        b = ev["blocking"]
        story.append(P(f"- {ev['scheme']['short_name']}: {b['label']} (you: {b['actual_display']})", small))

    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", color=colors.grey))
    story.append(P(f"Disclaimer: {DISCLAIMER}", small))

    buf = io.BytesIO()
    SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        title="Government Scheme Eligibility Report",
    ).build(story)
    return buf.getvalue()


class ReportAgent(Agent):
    name = "Report Agent"
    role = "Compiles the final report with reasoning and document checklists"

    def run(self, state: State) -> State:
        t0 = time.perf_counter()
        state["report_md"] = build_markdown(state)
        try:
            state["report_pdf"] = build_pdf(state)
        except Exception as exc:  # noqa: BLE001
            state["report_pdf"] = None
            self.log(state, "PDF skipped", f"{type(exc).__name__}: {exc}", t0, status="warn")
            return state
        fmt = "Markdown + PDF" if state["report_pdf"] else "Markdown (install reportlab for PDF)"
        self.log(state, "Built report", f"Formats: {fmt}", t0)
        return state
