import json

import pytest

from scoper.providers.anthropic_provider import AnthropicProvider
from scoper.providers.base import extract_json_object, get_provider, resolve_provider_name
from scoper.providers.template import TemplateProvider
from scoper.providers.vertex_provider import VertexProvider


def _seed_json() -> str:
    package = TemplateProvider().generate(
        "We need AI in the operations center at Northbridge Logistics, with role-based access, when the WAN is down."
    )
    return package.model_dump_json()


def test_extract_json_object_tolerates_fences():
    payload = {"ok": True}
    fenced = "```json\n" + json.dumps(payload) + "\n```"
    assert extract_json_object(fenced) == payload


def test_auto_without_keys_selects_template(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("SCOPER_PROVIDER", raising=False)
    assert resolve_provider_name("auto") == "template"
    assert get_provider("auto").name == "template"


def test_auto_prefers_anthropic_when_key_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    assert resolve_provider_name("auto") == "anthropic"


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="unknown provider"):
        get_provider("fax-machine")


def test_anthropic_provider_uses_injected_completer():
    seed = _seed_json()
    provider = AnthropicProvider(complete_json=lambda request, schema: seed)
    package = provider.generate("We need AI in the operations center at Northbridge Logistics, with role-based access.")
    assert package.sow.title.startswith("Role-restricted")


def test_vertex_provider_uses_injected_completer():
    seed = _seed_json()
    provider = VertexProvider(complete_json=lambda request, schema: seed)
    package = provider.generate("We need AI in the operations center at Northbridge Logistics, with role-based access.")
    assert "private VPC" in package.architecture.caption


def test_anthropic_provider_rejects_empty_request():
    with pytest.raises(ValueError, match="empty"):
        AnthropicProvider(complete_json=lambda request, schema: "{}").generate(" ")
