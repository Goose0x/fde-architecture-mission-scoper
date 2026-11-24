from __future__ import annotations

import os

from scoper.models import ScopePackage
from scoper.prompt import SYSTEM_PROMPT, user_prompt
from scoper.providers.base import Provider, package_from_model_text


class VertexProvider(Provider):
    """Gemini (or compatible) on Vertex AI. Uses Application Default Credentials."""

    name = "vertex"

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
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project:
            raise RuntimeError(
                "GOOGLE_CLOUD_PROJECT is not set. Use Application Default Credentials "
                "and export the project id (see .env.example)."
            )
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        model = os.environ.get("VERTEX_MODEL", "gemini-2.5-flash")
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "The google-genai package is not installed. Run: pip install -e '.[vertex]'"
            ) from exc
        client = genai.Client(vertexai=True, project=project, location=location)
        response = client.models.generate_content(
            model=model,
            contents=user_prompt(request, schema),
            config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.2},
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Vertex AI response did not include text content")
        return text
