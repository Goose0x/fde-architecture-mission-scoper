from pathlib import Path

import pytest

from scoper.providers.template import TemplateProvider, _classify
from scoper.render import render_markdown
from scoper.rubric import check_markdown, check_package

REPO = Path(__file__).resolve().parents[1]


def test_classifies_ops_and_erp_intakes():
    ops = (REPO / "examples/northbridge-ops-request.md").read_text(encoding="utf-8")
    erp = (REPO / "examples/harborline-erp-request.md").read_text(encoding="utf-8")
    assert _classify(ops) == "ops"
    assert _classify(erp) == "erp"
    assert _classify("Please add AI somewhere, thanks") == "generic"


def test_ops_package_passes_rubric():
    request = (REPO / "examples/northbridge-ops-request.md").read_text(encoding="utf-8")
    package = TemplateProvider().generate(request)
    assert package.sow.title.startswith("Role-restricted")
    assert check_package(package) == []
    assert check_markdown(render_markdown(package)) == []


def test_erp_package_passes_rubric():
    request = (REPO / "examples/harborline-erp-request.md").read_text(encoding="utf-8")
    package = TemplateProvider().generate(request)
    assert "Legacy" in package.sow.title
    assert check_package(package) == []
    assert check_markdown(render_markdown(package)) == []


def test_template_is_deterministic():
    request = (REPO / "examples/northbridge-ops-request.md").read_text(encoding="utf-8")
    first = TemplateProvider().generate(request)
    second = TemplateProvider().generate(request)
    assert first == second


def test_empty_request_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        TemplateProvider().generate("   ")
