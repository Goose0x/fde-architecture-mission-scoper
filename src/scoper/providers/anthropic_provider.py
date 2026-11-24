from __future__ import annotations

import os

from scoper.models import ScopePackage
from scoper.prompt import SYSTEM_PROMPT, user_prompt
from scoper.providers.base import Provider, package_from_model_text


class AnthropicProvider(Provider):
    """Claude via the Anthropic API. Key comes from ANTHROPIC_API_KEY."""

    name = "anthropic"

    def __init__(self, complete_json=None) -> None:
        self._complete_json = complete_json

    def generate(self, request: str) -> ScopePackage:
        text = request.strip()
        if not text:
            raise ValueError("request is empty")
        schema = ScopePackage.model_json_schema()
        raw = (self._complete_json or self._call_api)(text, schema)
        return package_from_model_text(raw)

    def _call_api(self, request: str, schema: dict) -> str:
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError(
                "The anthropic package is not installed. Run: pip install -e '.[anthropic]'"
            ) from exc
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env or export the variable."
            )
        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt(request, schema)}],
        )
        parts: list[str] = []
        for block in message.content:
            block_text = getattr(block, "text", None)
            if block_text:
                parts.append(block_text)
        if not parts:
            raise RuntimeError("Anthropic response did not include text content")
        return "\n".join(parts)
