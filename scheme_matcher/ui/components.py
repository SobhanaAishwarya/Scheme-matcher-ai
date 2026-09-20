"""HTML building blocks for the dashboard. Every dynamic value is escaped."""
from __future__ import annotations

from html import escape as esc
from typing import Iterable, Sequence


def _h(s: str) -> str:
    """Collapse indented HTML to one line so Markdown never treats it as a code block."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


_ICONS = {
    "ok": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "near": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "no": '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    "all": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
}


def _svg(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICONS[name]}</svg>'


# ------------------------------------------------------------------ layout
def hero(eyebrow: str, title: str, subtitle: str, chips: Iterable[str] = ()) -> str:
    chip_html = "".join(f'<span class="chip">{esc(c)}</span>' for c in chips)
    chips_block = f'<div class="chips">{chip_html}</div>' if chip_html else ""
    return _h(
        f"""<div class="hero"><span class="eyebrow">{esc(eyebrow)}</span>
        <h1>{esc(title)}</h1><p>{esc(subtitle)}</p>{chips_block}</div>"""
    )


def brand(name: str, tagline: str, initial: str = "S") -> str:
    return _h(
        f"""<div class="sb-brand"><div class="sb-logo">{esc(initial)}</div>
        <div><div class="sb-name">{esc(name)}</div><div class="sb-tag">{esc(tagline)}</div></div></div>"""
    )


def user_chip(name: str, email: str) -> str:
    initial = (name.strip()[:1] or "?").upper()
    return _h(
        f"""<div class="sb-user"><div class="sb-avatar">{esc(initial)}</div>
        <div><div class="sb-uname">{esc(name)}</div><div class="sb-mail">{esc(email)}</div></div></div>"""
    )


def sidebar_heading(text: str) -> str:
    return f'<div class="sb-h">{esc(text)}</div>'


def stepper(steps: Sequence[tuple[str, str]], done: bool) -> str:
    cls = "step done" if done else "step"
    rows = "".join(
        f'<div class="{cls}"><div class="dot">{i}</div>'
        f'<div><div class="t">{esc(title)}</div><div class="r">{esc(role)}</div></div></div>'
        for i, (title, role) in enumerate(steps, 1)
    )
    return _h(f"<div>{rows}</div>")


# ------------------------------------------------------------------ dashboard
def kpi_row(n_e: int, n_n: int, n_x: int, total: int) -> str:
    def card(kind: str, num: int, label: str) -> str:
        return (
            f'<div class="kpi {kind}"><div class="ico">{_svg(kind)}</div>'
            f'<div><div class="num">{num}</div><div class="lbl">{esc(label)}</div></div></div>'
        )

    return _h(
        '<div class="kpis">'
        + card("ok", n_e, "Eligible schemes")
        + card("near", n_n, "One step away")
        + card("no", n_x, "Not applicable")
        + card("all", total, "Schemes checked")
        + "</div>"
    )


def donut_panel(n_e: int, n_n: int, n_x: int) -> str:
    total = max(n_e + n_n + n_x, 1)
    a = n_e / total * 100
    b = a + n_n / total * 100
    gradient = f"conic-gradient(#10B981 0 {a:.2f}%, #F97316 {a:.2f}% {b:.2f}%, #CBD5E1 {b:.2f}% 100%)"
    return _h(
        f"""<div class="panel"><h4>Eligibility breakdown</h4>
        <div class="donut-wrap"><div class="donut" style="background:{gradient}">
        <div class="c"><b>{n_e}</b><span>of {n_e + n_n + n_x} match</span></div></div>
        <div class="legend">
        <div><i style="background:#10B981"></i>Eligible<b>{n_e}</b></div>
        <div><i style="background:#F97316"></i>One step away<b>{n_n}</b></div>
        <div><i style="background:#CBD5E1"></i>Not applicable<b>{n_x}</b></div>
        </div></div></div>"""
    )


def matches_panel(eligible: Sequence[dict], limit: int = 5) -> str:
    top = list(eligible)[:limit]
    if not top:
        body = '<div class="empty">No fully matching scheme yet. Check the near-miss tab for what to change.</div>'
    else:
        peak = max(ev["rank_score"] for ev in top) or 1
        rows = "".join(
            f'<div class="bar-row"><span class="n" title="{esc(ev["scheme"]["short_name"])}">'
            f'{esc(ev["scheme"]["short_name"])}</span>'
            f'<div class="bar"><i style="width:{ev["rank_score"] / peak * 100:.0f}%"></i></div>'
            f'<span class="v">{ev["rank_score"]}</span></div>'
            for ev in top
        )
        body = rows
    return _h(
        f"""<div class="panel"><h4>Top matches</h4>
        <div class="sub">Ranked by benefit size and how closely each scheme targets you</div>{body}</div>"""
    )


def profile_panel(items: Sequence[tuple[str, str]]) -> str:
    if not items:
        body = '<div class="empty">Your answers will appear here as you go.</div>'
    else:
        body = '<div class="kv">' + "".join(
            f'<div><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>' for k, v in items
        ) + "</div>"
    return _h(f'<div class="panel"><h4>Your profile</h4>{body}</div>')


def how_it_works_panel() -> str:
    steps = [
        ("Answer a few questions", "Five to eight, adapted to your situation."),
        ("Agents check the rules", "Every scheme is checked by a deterministic rules engine."),
        ("Get a ranked report", "Reasons, near-misses and the documents to keep ready."),
    ]
    rows = "".join(
        f'<div class="s"><div class="n">{i}</div><div><b>{esc(t)}</b><span>{esc(d)}</span></div></div>'
        for i, (t, d) in enumerate(steps, 1)
    )
    return _h(f'<div class="panel"><h4>How it works</h4><div class="steps3">{rows}</div></div>')


# ------------------------------------------------------------------ scheme cards
_STATUS = {"eligible": ("ok", "Eligible"), "near_miss": ("near", "One step away"), "not_eligible": ("no", "Not applicable")}


def scheme_card_top(ev: dict, kind: str) -> str:
    s = ev["scheme"]
    cls, label = _STATUS[kind]
    rank = f'<div class="rank">#{ev["rank"]}</div>' if kind == "eligible" else ""
    return _h(
        f"""<div class="sc-head"><div class="sc-title">{rank}<div>
        <div class="sc-name">{esc(s["name"])}</div><div class="sc-min">{esc(s["ministry"])}</div></div></div>
        <span class="status {cls}">{label}</span></div>
        <span class="pill">{esc(s["category"])}</span>
        <div class="benefit"><b>Benefit</b> &middot; {esc(s["benefit"])}</div>"""
    )


def scheme_card_insight(ev: dict, kind: str, peak_score: int = 1) -> str:
    if kind == "eligible":
        width = ev["rank_score"] / (peak_score or 1) * 100
        return _h(
            f"""<div class="callout ok"><div class="ct">Why you qualify</div>{esc(ev["explanation"])}</div>
            <div class="meter"><span>Relative fit</span><div class="bar"><i style="width:{width:.0f}%"></i></div>
            <span>{ev["rank_score"]}</span></div>
            <div class="src">{esc(ev["priority_reason"])}</div>"""
        )
    hint = esc(ev["failed"][0]["hint"]) if ev.get("failed") else ""
    return _h(
        f"""<div class="callout near"><div class="ct">One condition missing</div>{esc(ev["explanation"])}</div>
        <div class="callout tip"><div class="ct">What would make you eligible</div>{hint}</div>"""
    )


def scheme_card_footer(ev: dict) -> str:
    s = ev["scheme"]
    source = "LLM" if ev["explanation_source"] == "llm" else "template"
    return _h(
        f"""<div class="apply"><b>How to apply</b> &middot; {esc(s["how_to_apply"])}
        &nbsp;<a href="{esc(s["apply_url"], quote=True)}" target="_blank" rel="noopener">Official portal &#8599;</a></div>
        <div class="src">Explained by: {source} &middot; eligibility decided by the rules engine</div>"""
    )


def rule_rows(ev: dict) -> str:
    rows = []
    for r in ev["rules"]:
        cls, text = ("ok", "Pass") if r["passed"] else (("near", "Near") if r["near"] else ("no", "Fail"))
        rows.append(
            f'<div class="rule"><span class="b {cls}">{text}</span>'
            f'<div>{esc(r["label"])}<small>Your answer: {esc(str(r["actual_display"]))}</small></div></div>'
        )
    return _h("".join(rows))
