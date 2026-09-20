"""Orchestrator - runs the agent pipeline over a shared state dict.

    Intake  ->  Eligibility  ->  Explanation  ->  Ranking  ->  Report

Each agent reads the state, adds its output and appends a trace step, so the
UI can show exactly which agent did what (explainability).

The design mirrors a LangGraph state graph: nodes are agents, the state is a
plain dict, edges are a fixed sequence. It can be ported to LangGraph by
wrapping each agent's ``run`` as a node.
"""
from __future__ import annotations

import time
from typing import Any

from .agents.eligibility_agent import EligibilityAgent
from .agents.explanation_agent import ExplanationAgent
from .agents.intake_agent import IntakeAgent
from .agents.ranking_agent import RankingAgent
from .agents.report_agent import ReportAgent
from .rules_engine import load_schemes


def build_pipeline(llm=None):
    return [
        IntakeAgent(),
        EligibilityAgent(),
        ExplanationAgent(llm),
        RankingAgent(),
        ReportAgent(),
    ]


def run_pipeline(profile: dict[str, Any], llm=None, schemes=None) -> dict[str, Any]:
    state: dict[str, Any] = {
        "profile": dict(profile),
        "schemes": schemes if schemes is not None else load_schemes(),
        "trace": [],
    }
    t0 = time.perf_counter()
    for agent in build_pipeline(llm):
        state = agent.run(state)
    state["total_ms"] = round((time.perf_counter() - t0) * 1000)
    return state


PIPELINE_DOT = """
digraph G {
  rankdir=LR; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, color="#1F3A5F", fillcolor="#EAF1FB"];
  edge [color="#1F3A5F"];
  P [label="User profile\\n(adaptive Q&A)", fillcolor="#FFF4D6"];
  I [label="Intake Agent"];
  E [label="Eligibility Agent\\n(rules engine)"];
  X [label="Explanation Agent\\n(LLM / template)"];
  R [label="Ranking Agent"];
  D [label="Report Agent\\n(MD + PDF)", fillcolor="#E3F6E8"];
  P -> I -> E -> X -> R -> D;
}
"""
