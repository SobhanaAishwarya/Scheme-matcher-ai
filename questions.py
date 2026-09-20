"""Base class for all agents. Each agent reads/updates a shared state dict and
appends a step to ``state['trace']`` so the UI can show what happened."""
from __future__ import annotations

import time
from typing import Any

State = dict[str, Any]


class Agent:
    name = "Agent"
    icon = "🤖"
    role = ""

    def run(self, state: State) -> State:  # pragma: no cover - interface
        raise NotImplementedError

    def log(
        self,
        state: State,
        action: str,
        detail: str,
        started: float | None = None,
        status: str = "ok",
    ) -> None:
        duration = round((time.perf_counter() - started) * 1000) if started else 0
        state.setdefault("trace", []).append(
            {
                "agent": f"{self.icon} {self.name}",
                "action": action,
                "detail": detail,
                "status": status,
                "ms": duration,
            }
        )
