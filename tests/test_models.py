import pytest
from pydantic import ValidationError

from scoper.models import ArchitectureDiagram, ThreatModel
from scoper.providers.template import TemplateProvider


def _package():
    return TemplateProvider().generate(
        "We need AI in the operations center at Northbridge Logistics, with role-based access, when the WAN is down."
    )


def test_package_validates():
    package = _package()
    assert package.sow.weeks[0].week == 1
    assert len(package.success_metrics) >= 3


def test_weeks_must_be_one_through_four():
    package = _package()
    payload = package.sow.model_dump()
    payload["weeks"][0]["week"] = 2
    with pytest.raises(ValidationError):
        type(package.sow).model_validate(payload)


def test_threat_model_requires_all_stride_categories():
    item = {
        "category": "spoofing",
        "threat": "x",
        "mitigation": "y",
    }
    with pytest.raises(ValidationError, match="missing STRIDE"):
        ThreatModel(summary="incomplete", items=[item] * 6)


def test_mermaid_must_look_like_a_flowchart():
    with pytest.raises(ValidationError, match="mermaid"):
        ArchitectureDiagram(mermaid="this is not a diagram", caption="caption")
