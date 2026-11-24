from scoper.models import ScopePackage

STRIDE_LABELS = {
    "spoofing": "Spoofing",
    "tampering": "Tampering",
    "repudiation": "Repudiation",
    "information_disclosure": "Information disclosure",
    "denial_of_service": "Denial of service",
    "elevation_of_privilege": "Elevation of privilege",
}


def render_markdown(package: ScopePackage) -> str:
    sow = package.sow
    plan = package.pilot_plan
    lines: list[str] = [
        f"# {sow.title}",
        "",
        "## Customer problem",
        "",
        package.customer_problem.strip(),
        "",
        "## Four-week statement of work",
        "",
        sow.problem.strip(),
        "",
        "### Users",
        "",
    ]
    lines.extend(f"- {item}" for item in sow.users)
    lines.extend(["", "### Constraints", ""])
    lines.extend(f"- {item}" for item in sow.constraints)
    for week in sow.weeks:
        lines.extend(["", f"### Week {week.week}", "", "Goals:", ""])
        lines.extend(f"- {item}" for item in week.goals)
        lines.extend(["", "Deliverables:", ""])
        lines.extend(f"- {item}" for item in week.deliverables)
    lines.extend(["", "### Out of scope", ""])
    lines.extend(f"- {item}" for item in sow.out_of_scope)
    lines.extend(
        [
            "",
            "## Pilot plan",
            "",
            "### Baseline",
            "",
            plan.baseline.strip(),
            "",
            "### Success measures",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in plan.success_measures)
    lines.extend(
        [
            "",
            "### First shippable slice",
            "",
            plan.first_shippable_slice.strip(),
            "",
            "### First users",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in plan.first_users)
    lines.extend(
        [
            "",
            "## STRIDE threat model",
            "",
            package.threat_model.summary.strip(),
            "",
        ]
    )
    for item in package.threat_model.items:
        label = STRIDE_LABELS[item.category]
        lines.extend(
            [
                f"### {label}",
                "",
                f"- Threat: {item.threat}",
                f"- Mitigation: {item.mitigation}",
                "",
            ]
        )
    lines.extend(
        [
            "## Architecture",
            "",
            package.architecture.caption.strip(),
            "",
            "```mermaid",
            package.architecture.mermaid.strip(),
            "```",
            "",
            "## Success metrics",
            "",
            "| Metric | Baseline | Target | How measured |",
            "| --- | --- | --- | --- |",
        ]
    )
    for metric in package.success_metrics:
        lines.append(
            f"| {metric.name} | {metric.baseline} | {metric.target} | {metric.how_measured} |"
        )
    lines.append("")
    return "\n".join(lines)
