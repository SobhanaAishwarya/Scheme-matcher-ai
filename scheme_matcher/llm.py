"""Tiny provider-agnostic LLM wrapper.

The project works WITHOUT any API key (template explanations). If a key is
available the Explanation Agent uses an LLM to write friendlier explanations.
Eligibility itself is always decided by the rules engine, never by the LLM.
"""
from __future__ import annotations

import os

DEFAULT_MODELS = {
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
}
TIMEOUT_SECONDS = 45.0


class LLM:
    def __init__(self, provider: str, api_key: str, model: str | None = None):
        self.provider = provider
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS[provider]

    @property
    def label(self) -> str:
        return f"{self.provider} / {self.model}"

    def complete(self, system: str, user: str, max_tokens: int = 2500) -> str:
        if self.provider == "anthropic":
            import anthropic  # imported lazily so the app runs without it

            client = anthropic.Anthropic(
                api_key=self.api_key, timeout=TIMEOUT_SECONDS, max_retries=1
            )
            resp = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return "".join(
                b.text for b in resp.content if getattr(b, "type", "") == "text"
            )

        if self.provider == "openai":
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key, timeout=TIMEOUT_SECONDS, max_retries=1
            )
            resp = client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""

        raise ValueError(f"Unsupported provider: {self.provider}")


def build_llm(provider: str = "auto", api_key: str = "", model: str = "") -> LLM | None:
    """Return an LLM or None (=> template mode).

    provider: 'auto' | 'anthropic' | 'openai' | 'off'
    """
    provider = (provider or "auto").lower()
    if provider in ("off", "none", "template"):
        return None

    if provider == "auto":
        if api_key:
            provider = "anthropic" if api_key.startswith("sk-ant-") else "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            return None

    env_name = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
    key = api_key or os.getenv(env_name, "")
    if not key:
        return None
    return LLM(provider, key, model or None)
