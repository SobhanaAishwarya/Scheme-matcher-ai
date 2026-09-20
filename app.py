"""Government Scheme-Matching Assistant - Streamlit UI.

Flow: emoji splash -> sign in / create account -> adaptive intake -> results dashboard.

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
from scheme_matcher.ui import components as ui
from scheme_matcher.ui.gate import render_login, show_splash, sign_out
from scheme_matcher.ui.styles import CSS

st.set_page_config(
    page_title="Scheme Matcher AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    ss.setdefault("user", None)
    ss.setdefault("splash_shown", False)


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


def profile_items(profile: dict) -> list[tuple[str, str]]:
    return [
        (FIELD_LABELS.get(q["id"], q["id"]), format_value(q["id"], profile[q["id"]]))
        for q in QUESTIONS
        if q["id"] in profile
    ]


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
def render_sidebar(user: dict) -> None:
    with st.sidebar:
        st.markdown(ui.brand("Scheme Matcher", f"{scheme_count()} curated schemes"), unsafe_allow_html=True)
        st.markdown(ui.user_chip(user["name"], user["email"]), unsafe_allow_html=True)
        st.button("Sign out", on_click=sign_out, use_container_width=True, key="sign_out")

        st.markdown(ui.sidebar_heading("Agent pipeline"), unsafe_allow_html=True)
        steps = [(a.name, a.role) for a in build_pipeline()]
        st.markdown(ui.stepper(steps, done=st.session_state.results is not None), unsafe_allow_html=True)

        st.markdown(ui.sidebar_heading("Demo profiles"), unsafe_allow_html=True)
        for i, p in enumerate(PERSONAS):
            st.button(
                p["name"], key=f"persona_{i}", on_click=load_persona, args=(p,),
                help=p["blurb"], use_container_width=True,
            )

        st.markdown(ui.sidebar_heading("Controls"), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.button("Undo", on_click=undo_last, disabled=not st.session_state.history, use_container_width=True, key="undo_side")
        c2.button("Start over", on_click=start_over, use_container_width=True, key="reset_side")

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


# --------------------------------------------------------------------------- #
# Intake (chat)
# --------------------------------------------------------------------------- #
def render_intake(user: dict) -> None:
    ss = st.session_state
    first = user["name"].split()[0]
    st.markdown(
        ui.hero(
            "Step 1 of 2 - Your profile",
            f"Welcome, {first}",
            "Answer a few quick questions. Our agents will check your profile against curated "
            "central-government schemes and explain why you qualify, or what is missing.",
            ["5 to 8 adaptive questions", f"{scheme_count()} curated schemes", "Works offline"],
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns([2.1, 1], gap="large")
    with right:
        st.markdown(ui.profile_panel(profile_items(ss.profile)), unsafe_allow_html=True)
        st.markdown(ui.how_it_works_panel(), unsafe_allow_html=True)

    with left:
        answered, total = progress(ss.profile)
        st.progress(min(answered / total, 1.0), text=f"Question {min(answered + 1, total)} of about {total}")

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.markdown(
                "Namaste! I'll ask a few quick questions (about 5-8) and then check "
                "**which government schemes you are eligible for** - with reasons."
            )
        for h in ss.history:
            with st.chat_message("assistant", avatar=":material/smart_toy:"):
                st.markdown(h["question"])
            with st.chat_message("user", avatar=":material/person:"):
                st.markdown(f"**{h['answer']}**")

        q = next_question(ss.profile)
        if q is None:
            return
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
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
                if st.button("Next", type="primary", key=f"next_{q['id']}"):
                    record_answer(q, value)
                    st.rerun()


# --------------------------------------------------------------------------- #
# Results dashboard
# --------------------------------------------------------------------------- #
def scheme_card(ev: dict, kind: str, peak: int = 1) -> None:
    s = ev["scheme"]
    with st.container(key=f"card-{kind}-{s['id']}"):
        st.markdown(ui.scheme_card_top(ev, kind), unsafe_allow_html=True)
        st.markdown(ui.scheme_card_insight(ev, kind, peak), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("Rule-by-rule check"):
                st.markdown(ui.rule_rows(ev), unsafe_allow_html=True)
        with c2:
            with st.expander("Documents to keep ready"):
                for i, doc in enumerate(s["documents"]):
                    st.checkbox(doc, key=f"doc_{s['id']}_{i}")
        st.markdown(ui.scheme_card_footer(ev), unsafe_allow_html=True)


def render_results(user: dict, state: dict) -> None:
    ranked = state["ranked"]
    n_e, n_n, n_x = len(ranked["eligible"]), len(ranked["near_miss"]), len(ranked["not_eligible"])
    first = user["name"].split()[0]

    st.markdown(
        ui.hero(
            "Step 2 of 2 - Your results",
            f"{first}, you match {n_e} scheme{'s' if n_e != 1 else ''}",
            state["summary"],
            [f"{n_e} eligible", f"{n_n} one step away", f"Pipeline {state['total_ms']} ms", f"Explanations: {state['llm_mode']}"],
        ),
        unsafe_allow_html=True,
    )
    st.markdown(ui.kpi_row(n_e, n_n, n_x, len(state["evaluations"])), unsafe_allow_html=True)

    p1, p2, p3 = st.columns([1.1, 1.25, 1.05], gap="medium")
    p1.markdown(ui.donut_panel(n_e, n_n, n_x), unsafe_allow_html=True)
    p2.markdown(ui.matches_panel(ranked["eligible"]), unsafe_allow_html=True)
    p3.markdown(ui.profile_panel(profile_items(state["profile"])), unsafe_allow_html=True)

    st.write("")
    a1, a2, _ = st.columns([1, 1, 4])
    a1.button("Undo last answer", on_click=undo_last, key="undo_main", use_container_width=True)
    a2.button("New profile", on_click=start_over, key="reset_main", type="primary", use_container_width=True)

    tab_e, tab_n, tab_x, tab_t, tab_r = st.tabs(
        [f"Eligible ({n_e})", f"One step away ({n_n})", f"Not applicable ({n_x})", "Agent trace", "Report"]
    )

    with tab_e:
        if not ranked["eligible"]:
            st.warning("No fully matching schemes right now - check the next tab for what to change.")
        peak = max((ev["rank_score"] for ev in ranked["eligible"]), default=1)
        for ev in ranked["eligible"]:
            scheme_card(ev, "eligible", peak)

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
                st.markdown(ui.rule_rows(ev), unsafe_allow_html=True)

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
                mime="application/pdf", key="dl_pdf", type="primary", use_container_width=True,
            )
        d2.download_button(
            "Download Markdown", data=state["report_md"], file_name="scheme_report.md",
            mime="text/markdown", key="dl_md", use_container_width=True,
        )
        with st.expander("Preview report", expanded=True):
            st.markdown(state["report_md"])


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)
    ss = st.session_state

    if not ss.splash_shown:  # one-time emoji splash at the start of each session
        show_splash()
        ss.splash_shown = True
        st.rerun()

    if ss.user is None:  # auth gate
        render_login()
        return

    user = ss.user
    render_sidebar(user)

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
        render_intake(user)
    else:
        render_results(user, ss.results)

    st.divider()
    st.caption(
        "Decision-support aid built on a simplified dataset. Scheme rules change - always confirm on the "
        "official portal before applying. Demo uses no real personal data."
    )


main()
