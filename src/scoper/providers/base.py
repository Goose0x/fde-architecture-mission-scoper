from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any

from scoper.models import ScopePackage


class Provider(ABC):
    name: str

    @abstractmethod
    def generate(self, request: str) -> ScopePackage:
        raise NotImplementedError


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object, tolerating a markdown fence around it."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(stripped[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("model output is not a JSON object")
    return data


def package_from_model_text(text: str) -> ScopePackage:
    return ScopePackage.model_validate(extract_json_object(text))


def resolve_provider_name(explicit: str | None = None) -> str:
    name = (explicit or os.environ.get("SCOPER_PROVIDER") or "auto").strip().lower()
    if name == "auto":
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            return "vertex"
        return "template"
    return name


def get_provider(name: str | None = None) -> Provider:
    resolved = resolve_provider_name(name)
    if resolved == "template":
        from scoper.providers.template import TemplateProvider

        return TemplateProvider()
    if resolved == "anthropic":
        from scoper.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    if resolved == "vertex":
        from scoper.providers.vertex_provider import VertexProvider

        return VertexProvider()
    raise ValueError(f"unknown provider: {resolved}")
