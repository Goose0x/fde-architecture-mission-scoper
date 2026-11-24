from scoper.providers.template import TemplateProvider
from scoper.render import render_markdown
from scoper.rubric import check_markdown, scan_text


def test_render_includes_required_sections_and_mermaid():
    package = TemplateProvider().generate(
        "We need AI in the operations center, disconnected, with role-based access."
    )
    text = render_markdown(package)
    assert "## Pilot plan" in text
    assert "### Baseline" in text
    assert "### Success measures" in text
    assert "### First shippable slice" in text
    assert "### First users" in text
    assert "## STRIDE threat model" in text
    assert "```mermaid" in text
    assert "flowchart" in text
    assert check_markdown(text) == []


def test_rubric_flags_banned_markings_and_ssn_like_values():
    issues = scan_text("This is marked SECRET and the id is 123-45-6789.")
    codes = {issue.code for issue in issues}
    assert "banned_marking" in codes
    assert "ssn_like" in codes


def test_rubric_flags_missing_headings():
    issues = check_markdown("# Title\n\nNo sections here.\n")
    codes = {issue.code for issue in issues}
    assert "heading" in codes
    assert "mermaid" in codes
