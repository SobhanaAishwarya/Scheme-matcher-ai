"""Government Scheme-Matching Assistant - Streamlit UI.

Run:  streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

try:  # optional: load API keys from a local .env file
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

from scheme_matcher.constants import FIELD_LABELS, format_value, inr
from scheme_matcher.llm import build_llm
from scheme_matcher.orchestrator import PIPELINE_DOT, build_pipeline, run_pipeline
from scheme_matcher.personas import PERSONAS, build_history
from scheme_matcher.questions import QUESTIONS, next_question, progress
from scheme_matcher.rules_engine import load_schemes

st.set_page_config(
    page_title="Scheme Matcher AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
.hero{background:linear-gradient(135deg,#1F3A5F 0%,#2E6FBF 62%,#F59E0B 135%);
      padding:1.4rem 1.7rem;border-radius:16px;color:#fff;margin-bottom:1.1rem}
.hero h1{color:#fff;margin:0;font-size:1.85rem;line-height:1.25}
.hero p{margin:.35rem 0 0;opacity:.93;font-size:1rem}
.pill{display:inline-block;background:#EEF2F7;color:#1F3A5F;border-radius:999px;
      padding:2px 11px;font-size:.74rem;margin:0 6px 6px 0;font-weight:500}
.rankbadge{display:inline-block;background:#F59E0B;color:#1a1a1a;border-radius:8px;
      padding:1px 9px;font-weight:700;margin-right:8px}
div[data-testid="stMetric"]{background:rgba(46,111,191,.08);padding:.7rem 1rem;border-radius:12px}
</style>
"""

PROVIDER_CHOICES = {
    "Auto (use key from .env if present)": "auto",
    "Anthropic Claude": "anthropic",
    "OpenAI": "openai",
    "Off (template mode)": "off",
}


# --------------------------------------------------------------------------- #
# State helpers
# --------------------------------------------------------------------------- #
def init_state() -> None:
    ss = st.session_state
    ss.setdefault("profile", {})
    ss.setdefault("history", [])
    ss.setdefault("results", None)


def clear_doc_checks() -> None:
    for key in [k for k in st.session_state if str(k).startswith("doc_")]:
        del st.session_state[key]


def record_answer(q: dict, value) -> None:
    ss = st.session_state
    ss.profile[q["id"]] = value
    ss.history.append(
        {"qid": q["id"], "question": q["text"], "answer": format_value(q["id"], value)}
    )
    ss.results = None


def choice_changed(q: dict) -> None:
    """on_change callback for radio questions: auto-advance on selection."""
    value = st.session_state.get(f"w_{q['id']}")
    if value is not None:
        record_answer(q, value)


def undo_last() -> None:
    ss = st.session_state
    if ss.history:
        entry = ss.history.pop()
        ss.profile.pop(entry["qid"], None)
        ss.results = None


def start_over() -> None:
    ss = st.session_state
    ss.profile, ss.history, ss.results = {}, [], None
    clear_doc_checks()


def load_persona(persona: dict) -> None:
    ss = st.session_state
    clear_doc_checks()
    ss.profile = dict(persona["profile"])
    ss.history = build_history(ss.profile)
    ss.results = None


def regenerate() -> None:
    st.session_state.results = None


def get_llm():
    ss = st.session_state
    provider = PROVIDER_CHOICES.get(ss.get("llm_provider", ""), "auto")
    return build_llm(provider, (ss.get("api_key") or "").strip(), (ss.get("model_name") or "").strip())


@st.cache_data(show_spinner=False)
def scheme_count() -> int:
    return len(load_schemes())


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## Scheme Matcher AI")
        st.caption(f"Multi-agent eligibility assistant · {scheme_count()} curated schemes")

        st.markdown("### Agent pipeline")
        for agent in build_pipeline():
            st.markdown(f"**{agent.name}**  \n<small>{agent.role}</small>", unsafe_allow_html=True)

        with st.expander("LLM settings (optional)"):
            st.selectbox("Provider", list(PROVIDER_CHOICES), key="llm_provider")
            st.text_input(
                "API key (optional)", type="password", key="api_key",
                help="Stored only in this browser session. Leave empty to use a .env file or template mode.",
            )
            st.text_input("Model (optional)", key="model_name", placeholder="default model")
            llm = get_llm()
            if llm:
                st.success(f"LLM active: {llm.label}")
            else:
                st.info("Template mode - works fully offline, no API key needed.")
            if st.session_state.results is not None:
                st.button("Regenerate explanations", on_click=regenerate)

        st.markdown("### Demo personas")
        st.caption("Load a ready-made profile and jump straight to results.")
        for i, p in enumerate(PERSONAS):
            st.button(
                p['name'], key=f"persona_{i}", on_click=load_persona,
                args=(p,), help=p["blurb"],
            )

        st.divider()
        c1, c2 = st.columns(2)
        c1.button("↩ Undo", on_click=undo_last, disabled=not st.session_state.history)
        c2.button("Start over", on_click=start_over)


# --------------------------------------------------------------------------- #
# Intake (chat)
# --------------------------------------------------------------------------- #
def render_intake() -> None:
    ss = st.session_state
    answered, total = progress(ss.profile)
    st.progress(min(answered / total, 1.0), text=f"Question {min(answered + 1, total)} of about {total}")

    with st.chat_message("assistant"):
        st.markdown(
            "Namaste! I'll ask a few quick questions (about 5-8) and then check "
            "**which government schemes you are eligible for** - with reasons."
        )
    for h in ss.history:
        with st.chat_message("assistant"):
            st.markdown(h["question"])
        with st.chat_message("user"):
            st.markdown(f"**{h['answer']}**")

    q = next_question(ss.profile)
    if q is None:
        return
    with st.chat_message("assistant"):
        st.markdown(f"**{q['text']}**")
        if q.get("help"):
            st.caption(q["help"])
        key = f"w_{q['id']}"
        if q["type"] == "choice":
            st.radio(
                "Your answer", list(q["options"]), index=None, key=key,
                format_func=lambda k, opts=q["options"]: opts[k],
                label_visibility="collapsed", on_change=choice_changed, args=(q,),
            )
            st.caption("Tap an option to continue")
        else:
            if q["kind"] == "int":
                value = st.number_input(
                    "Your answer", min_value=int(q["min"]), max_value=int(q["max"]),
                    value=int(q["default"]), step=int(q["step"]), key=key,
                    label_visibility="collapsed",
                )
            else:
                value = st.number_input(
                    "Your answer", min_value=float(q["min"]), max_value=float(q["max"]),
                    value=float(q["default"]), step=float(q["step"]), key=key,
                    label_visibility="collapsed",
                )
            if q["id"] in ("income", "project_cost"):
                st.caption(f"= {inr(value)}")
            if st.button("Next →", type="primary", key=f"next_{q['id']}"):
                record_answer(q, value)
                st.rerun()


# --------------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------------- #
def rule_lines(ev: dict) -> None:
    for r in ev["rules"]:
        status = "Pass" if r["passed"] else ("Near miss" if r["near"] else "Fail")
        st.markdown(f"**{status} - {r['label']}**  \n&nbsp;&nbsp;&nbsp;&nbsp;Your answer: `{r['actual_display']}`")


def scheme_card(ev: dict, kind: str) -> None:
    s = ev["scheme"]
    with st.container(border=True):
        if kind == "eligible":
            st.markdown(f"#### <span class='rankbadge'>#{ev['rank']}</span>{s['name']}", unsafe_allow_html=True)
        else:
            st.markdown(f"#### {s['name']}")
        st.markdown(
            f"<span class='pill'>{s['category']}</span><span class='pill'>{s['ministry']}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Benefit:** {s['benefit']}")

        if kind == "eligible":
            st.success(f"**Why you qualify**\n\n{ev['explanation']}")
            st.caption(f"{ev['priority_reason']} · rank score {ev['rank_score']}")
        else:
            f = ev["failed"][0]
            st.warning(f"**So close - one condition missing**\n\n{ev['explanation']}")
            st.info(f"**What would make you eligible:** {f['hint']}")

        c1, c2 = st.columns(2)
        with c1:
            with st.expander("Rule-by-rule check"):
                rule_lines(ev)
        with c2:
            with st.expander("Documents to keep ready"):
                for i, doc in enumerate(s["documents"]):
                    st.checkbox(doc, key=f"doc_{s['id']}_{i}")
        st.markdown(f"**How to apply:** {s['how_to_apply']}  \n[Open official portal ↗]({s['apply_url']})")
        st.caption("Explained by: " + ("LLM" if ev["explanation_source"] == "llm" else "template") + " · eligibility decided by the rules engine")


def render_results(state: dict) -> None:
    ranked = state["ranked"]
    n_e, n_n, n_x = len(ranked["eligible"]), len(ranked["near_miss"]), len(ranked["not_eligible"])

    top = st.columns([4, 1, 1])
    top[0].markdown("### Your scheme matches")
    top[1].button("↩ Undo last answer", on_click=undo_last, key="undo_main")
    top[2].button("New profile", on_click=start_over, key="reset_main")

    st.info(state["summary"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eligible", n_e)
    m2.metric("Near-miss", n_n)
    m3.metric("Not eligible", n_x)
    m4.metric("Schemes checked", len(state["evaluations"]))

    with st.expander("Your profile"):
        cols = st.columns(3)
        for i, q in enumerate(QUESTIONS):
            if q["id"] in state["profile"]:
                cols[i % 3].markdown(
                    f"**{FIELD_LABELS.get(q['id'], q['id'])}**  \n{format_value(q['id'], state['profile'][q['id']])}"
                )

    tab_e, tab_n, tab_x, tab_t, tab_r = st.tabs(
        [f"Eligible ({n_e})", f"Near-miss ({n_n})", f"Not eligible ({n_x})", "Agent trace", "Report"]
    )

    with tab_e:
        if not ranked["eligible"]:
            st.warning("No fully matching schemes right now - check the Near-miss tab for what to change.")
        for ev in ranked["eligible"]:
            scheme_card(ev, "eligible")

    with tab_n:
        st.caption("Exactly one condition is missing. Here is what would make you eligible.")
        if not ranked["near_miss"]:
            st.success("No near-misses - every scheme is either a clear match or clearly not applicable.")
        for ev in ranked["near_miss"]:
            scheme_card(ev, "near_miss")

    with tab_x:
        st.caption("Schemes that do not apply to your profile, with the main reason.")
        for ev in ranked["not_eligible"]:
            b = ev["blocking"]
            with st.expander(f"{ev['scheme']['short_name']} - {b['label']}"):
                st.markdown(ev["explanation"])
                rule_lines(ev)

    with tab_t:
        st.markdown("#### How the agents handled your request")
        st.graphviz_chart(PIPELINE_DOT)
        df = pd.DataFrame(state["trace"])[["agent", "action", "detail", "ms"]]
        df.columns = ["Agent", "Action", "Result", "Time (ms)"]
        st.dataframe(df, hide_index=True)
        st.caption(
            f"Total pipeline time: {state['total_ms']} ms · Explanation mode: {state['llm_mode']}. "
            "Eligibility is always decided by deterministic rules - the LLM only phrases the explanation."
        )
        if state.get("llm_error"):
            st.warning(f"LLM call failed, template explanations were used instead: {state['llm_error']}")

    with tab_r:
        st.markdown("#### Download your report")
        d1, d2 = st.columns(2)
        if state.get("report_pdf"):
            d1.download_button(
                "Download PDF", data=state["report_pdf"], file_name="scheme_report.pdf",
                mime="application/pdf", key="dl_pdf",
            )
        d2.download_button(
            "Download Markdown", data=state["report_md"], file_name="scheme_report.md",
            mime="text/markdown", key="dl_md",
        )
        with st.expander("Preview report", expanded=True):
            st.markdown(state["report_md"])


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)
    render_sidebar()

    st.markdown(
        "<div class='hero'><h1>Government Scheme-Matching Assistant</h1>"
        "<p>Answer a few questions. Our agents check your profile against curated central-government "
        "schemes and explain <b>why</b> you qualify - or what is missing.</p></div>",
        unsafe_allow_html=True,
    )

    ss = st.session_state
    if ss.results is None and next_question(ss.profile) is None:
        try:
            with st.spinner("Agents are checking eligibility, writing explanations and ranking schemes..."):
                ss.results = run_pipeline(ss.profile, llm=get_llm())
        except ValueError as exc:
            st.error(f"Could not process the profile: {exc}")
            st.button("Start over", on_click=start_over, key="err_reset")
            return
        st.rerun()

    if ss.results is None:
        render_intake()
    else:
        render_results(ss.results)

    st.divider()
    st.caption(
        "Decision-support aid built on a simplified dataset. Scheme rules change - always confirm on the "
        "official portal before applying. Demo uses no real personal data."
    )


main()
