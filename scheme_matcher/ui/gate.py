"""Emoji splash screen and the Sign In / Create account gate."""
from __future__ import annotations

import math
import os
import time

import streamlit as st

from .. import auth
from .components import _h

SPLASH_SECONDS = float(os.environ.get("SCHEME_SPLASH_SECONDS", "3.5"))

_ORBIT = ["\U0001F33E", "\U0001F393", "\U0001F4BC", "\U0001FA7A", "\U0001F3E0", "\U0001F4DC", "\U0001F91D", "\U0001F4A1"]
_CORE = "\U0001F3DB️"


def show_splash(seconds: float = SPLASH_SECONDS) -> None:
    """One-time emoji splash at the start of a browser session."""
    orbit = []
    radius, centre, half = 132, 170, 28
    for i, emoji in enumerate(_ORBIT):
        angle = math.radians(i * 360 / len(_ORBIT) - 90)
        left = centre + radius * math.cos(angle) - half
        top = centre + radius * math.sin(angle) - half
        orbit.append(f'<span class="e" style="left:{left:.0f}px;top:{top:.0f}px;animation-delay:{i * 0.35:.2f}s">{emoji}</span>')
    st.markdown(
        _h(
            f"""<div class="splash" style="--dur:{seconds}s">
            <div class="orbit"><div class="core">{_CORE}</div>{"".join(orbit)}</div>
            <div class="s-name">Scheme Matcher AI</div>
            <div class="s-tag">Find every government scheme you qualify for</div>
            <div class="s-bar"><i></i></div></div>"""
        ),
        unsafe_allow_html=True,
    )
    time.sleep(seconds)


_BRAND_PANEL = _h(
    """<div class="brand-panel"><div>
    <div class="logo">S</div>
    <h2>Know which government schemes you qualify for.</h2>
    <p>Answer a few adaptive questions. Our agents check your profile against curated central-government
    schemes and explain exactly why you match, or what is missing.</p>
    <ul>
    <li><i>&#10003;</i>Adaptive 5 to 8 question intake</li>
    <li><i>&#10003;</i>Deterministic rules engine, no guesswork</li>
    <li><i>&#10003;</i>Near-miss detection with clear next steps</li>
    <li><i>&#10003;</i>Document checklist and downloadable report</li>
    </ul></div>
    <div class="foot">Decision-support aid. Always confirm on the official portal before applying.</div></div>"""
)


def render_login() -> None:
    left, right = st.columns([1.1, 1], gap="large", vertical_alignment="center")
    with left:
        st.markdown(_BRAND_PANEL, unsafe_allow_html=True)
    with right:
        with st.container(key="auth-card"):
            st.markdown(
                '<div class="auth-h">Welcome to Scheme Matcher</div>'
                '<div class="auth-s">Sign in or create a free account to continue.</div>',
                unsafe_allow_html=True,
            )
            tab_in, tab_up = st.tabs(["Sign in", "Create account"])

            with tab_in:
                with st.form("signin_form", border=False):
                    email = st.text_input("Email", key="signin_email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", key="signin_password", placeholder="Your password")
                    submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
                if submitted:
                    user, error = auth.sign_in(email, password)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.user = user
                        st.rerun()

            with tab_up:
                with st.form("signup_form", border=False):
                    name = st.text_input("Full name", key="signup_name", placeholder="Your name")
                    email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
                    password = st.text_input(
                        "Password", type="password", key="signup_password",
                        placeholder=f"At least {auth.MIN_PASSWORD_LENGTH} characters",
                    )
                    confirm = st.text_input("Confirm password", type="password", key="signup_confirm", placeholder="Re-enter your password")
                    submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
                if submitted:
                    user, error = auth.sign_up(name, email, password, confirm)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.user = user
                        st.rerun()


def sign_out() -> None:
    """Clear the signed-in user and any in-progress profile or results."""
    for key in [k for k in st.session_state if str(k).startswith(("doc_", "w_", "next_"))]:
        del st.session_state[key]
    st.session_state.user = None
    st.session_state.profile, st.session_state.history, st.session_state.results = {}, [], None
