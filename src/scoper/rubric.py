import re
from pathlib import Path

from scoper.models import STRIDE_CATEGORIES, ScopePackage

# Banners that would make a demo sample look like a real classified artifact.
BANNED_MARKING = re.compile(
    r"\b(TOP SECRET|SECRET//|SECRET\b|TS/SCI|CUI//|NOFORN|ORCON|PROPIN|FOUO)\b",
    re.IGNORECASE,
)
SSN_LIKE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_LIKE = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")

REQUIRED_MARKDOWN_HEADINGS = (
    "## Customer problem",
    "## Four-week statement of work",
    "## Pilot plan",
    "### Baseline",
    "### Success measures",
    "### First shippable slice",
    "### First users",
    "## STRIDE threat model",
    "## Architecture",
    "## Success metrics",
)


class RubricIssue:
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def scan_text(text: str) -> list[RubricIssue]:
    issues: list[RubricIssue] = []
    if BANNED_MARKING.search(text):
        issues.append(
            RubricIssue("banned_marking", "text looks like a classification or CUI banner")
        )
    if SSN_LIKE.search(text):
        issues.append(RubricIssue("ssn_like", "text contains an SSN-like pattern"))
    if CARD_LIKE.search(text):
        issues.append(RubricIssue("card_like", "text contains a payment-card-like pattern"))
    return issues


def check_package(package: ScopePackage) -> list[RubricIssue]:
    issues = scan_text(package.model_dump_json())
    present = {item.category for item in package.threat_model.items}
    for category in STRIDE_CATEGORIES:
        if category not in present:
            issues.append(RubricIssue("stride", f"missing STRIDE category {category}"))
    plan = package.pilot_plan
    if not plan.baseline.strip():
        issues.append(RubricIssue("pilot_plan", "baseline is empty"))
    if not plan.success_measures:
        issues.append(RubricIssue("pilot_plan", "success_measures is empty"))
    if not plan.first_shippable_slice.strip():
        issues.append(RubricIssue("pilot_plan", "first_shippable_slice is empty"))
    if not plan.first_users:
        issues.append(RubricIssue("pilot_plan", "first_users is empty"))
    return issues


def check_markdown(text: str) -> list[RubricIssue]:
    issues = scan_text(text)
    for heading in REQUIRED_MARKDOWN_HEADINGS:
        if heading not in text:
            issues.append(RubricIssue("heading", f"missing heading {heading}"))
    if "```mermaid" not in text:
        issues.append(RubricIssue("mermaid", "missing mermaid code fence"))
    return issues


def check_file(path: Path) -> list[RubricIssue]:
    return check_markdown(path.read_text(encoding="utf-8"))
