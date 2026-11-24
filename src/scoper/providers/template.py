from __future__ import annotations

from scoper.models import (
    ArchitectureDiagram,
    FourWeekSow,
    PilotPlan,
    ScopePackage,
    SowWeek,
    StrideItem,
    SuccessMetric,
    ThreatModel,
)
from scoper.providers.base import Provider

_OPS_HINTS = (
    "operations center",
    "ops center",
    "ops floor",
    "warehouse",
    "wan link",
    "wan",
    "need-to-know",
    "need to know",
    "role-based",
    "carrier partner",
    "disconnected",
    "site brief",
    "northbridge",
)
_ERP_HINTS = (
    "erp",
    "sap",
    "oracle",
    "help desk",
    "helpdesk",
    "ticket",
    "invoice",
    "requisition",
    "legacy soap",
)


def _classify(request: str) -> str:
    lowered = request.lower()
    ops = sum(1 for hint in _OPS_HINTS if hint in lowered)
    erp = sum(1 for hint in _ERP_HINTS if hint in lowered)
    if ops > erp and ops > 0:
        return "ops"
    if erp > 0:
        return "erp"
    return "generic"


def _ops(_request: str) -> ScopePackage:
    return ScopePackage(
        customer_problem=(
            "Operators assemble site briefs by hand from shared drives and chat threads. "
            "The same question can surface material a given role should not see, and the "
            "assistant is simply unavailable when a site network link is down. The intake "
            "asks for a scoped four-week pilot, not a company-wide rollout. "
            "This package uses only fictional, unclassified assumptions about Northbridge Logistics."
        ),
        sow=FourWeekSow(
            title="Role-restricted operations assistant — four-week pilot",
            problem=(
                "Stand up a pilot assistant that drafts operations briefs for a fictional "
                "logistics company, respects role-based access, keeps sensitive fields out of "
                "the model context, and continues to run inside a private network when public "
                "egress is blocked."
            ),
            users=[
                "Site operations lead (drafts and reviews briefs)",
                "Finance analyst (different document set)",
                "Approver (human-in-the-loop for outbound partner shares)",
            ],
            constraints=[
                "Fictional, unclassified company data only",
                "Document-level access control at retrieval time",
                "No public internet egress from the pilot VPC",
                "High-stakes actions (share with a partner, or open a ticket) require a recorded human approval",
            ],
            weeks=[
                SowWeek(
                    week=1,
                    goals=[
                        "Lock the data model, roles, and fixture corpus",
                        "Stand up retrieval with document ACLs",
                    ],
                    deliverables=["Role matrix", "Unclassified fixture set", "ACL-filtered retrieval spike"],
                ),
                SowWeek(
                    week=2,
                    goals=[
                        "Add a deterministic sensitive-field proxy",
                        "Wire a first brief-drafting prompt",
                    ],
                    deliverables=["Tokenize-and-restore path with an audit log", "Draft-brief API"],
                ),
                SowWeek(
                    week=3,
                    goals=[
                        "Pause high-stakes tool calls for human approval",
                        "Prove the workflow survives a restart",
                    ],
                    deliverables=["Approval inbox for share/ticket actions", "Crash-recovery demo script"],
                ),
                SowWeek(
                    week=4,
                    goals=[
                        "Deploy into a private VPC with no public egress",
                        "Measure the pilot against the success metrics",
                    ],
                    deliverables=["Terraform/Helm private-VPC deploy", "Egress smoke test", "Pilot readout"],
                ),
            ],
            out_of_scope=[
                "Live production data or real customer records",
                "Company-wide rollout beyond the first operations-center cohort",
                "Production identity federation (stub identity is enough for the pilot)",
            ],
        ),
        pilot_plan=PilotPlan(
            baseline=(
                "Briefs are assembled manually from shared drives. Role-based access is informal. "
                "There is no assistant when a site link is down, and outbound partner shares have no recorded approval."
            ),
            success_measures=[
                "Zero unauthorized document hits on the fixture ACL tests",
                "All planted sensitive spans are tokenized before inference",
                "An in-flight approval still waits after a worker restart",
                "Egress smoke test shows no public internet path from the pilot VPC",
            ],
            first_shippable_slice=(
                "ACL-filtered retrieval, a sensitive-field proxy, one approval-gated action, "
                "and a private-VPC deploy on the fictional fixture set."
            ),
            first_users=[
                "Two fictional site operations leads",
                "One fictional finance analyst",
                "One fictional approver",
            ],
        ),
        threat_model=ThreatModel(
            summary=(
                "The pilot's main risks are identity confusion, prompt or corpus tampering, "
                "unlogged shares, leakage across role boundaries, a hard dependency on a single "
                "model endpoint, and an agent expanding its own privileges."
            ),
            items=[
                StrideItem(
                    category="spoofing",
                    threat="A user or agent presents itself as a more privileged role and retrieves the wrong corpus.",
                    mitigation="Authenticate at the edge, bind every request to a role, and enforce ACLs in the retriever, not the prompt.",
                ),
                StrideItem(
                    category="tampering",
                    threat="Fixture documents or prompts are modified to exfiltrate another role's context.",
                    mitigation="Version and hash the corpus, restrict who can edit prompts, and review retrieval traces.",
                ),
                StrideItem(
                    category="repudiation",
                    threat="A share or ticket is issued and later denied because there is no durable record.",
                    mitigation="Immutable audit log plus a workflow history for every high-stakes action.",
                ),
                StrideItem(
                    category="information_disclosure",
                    threat="Sensitive spans or unauthorized documents reach the model or another user.",
                    mitigation="Document-level access control, pre-inference tokenization, and no public egress from the VPC.",
                ),
                StrideItem(
                    category="denial_of_service",
                    threat="The assistant becomes unusable if a cloud endpoint is unreachable — the original customer complaint.",
                    mitigation="Keep inference and stores inside the private VPC; fail closed on egress; test a blocked-internet path.",
                ),
                StrideItem(
                    category="elevation_of_privilege",
                    threat="The agent calls a write or share tool it was not granted, or expands its own scopes.",
                    mitigation="Short-lived task-bound credentials, allowlisted tools, and a human approval gate on restricted actions.",
                ),
            ],
        ),
        architecture=ArchitectureDiagram(
            mermaid=(
                "flowchart LR\n"
                "  Officer[Site operations lead] --> UI[Ops UI]\n"
                "  UI --> API[Pilot API]\n"
                "  API --> ACL[Document ACL]\n"
                "  API --> Proxy[Sensitive-field proxy]\n"
                "  ACL --> RAG[Secure retriever]\n"
                "  Proxy --> RAG\n"
                "  RAG --> Store[Vector store]\n"
                "  Proxy --> LLM[Model in private VPC]\n"
                "  API --> Gate[Approval workflow]\n"
                "  Gate --> Approver[Human approver]\n"
                "  API --> Audit[Audit and traces]\n"
                "  VPC[Google Cloud private VPC, no public egress] -.-> API"
            ),
            caption=(
                "Pilot request path inside a Google Cloud private VPC: authorize, tokenize, "
                "retrieve only authorized chunks, infer with no public egress, and pause "
                "restricted actions for a human."
            ),
        ),
        success_metrics=[
            SuccessMetric(
                name="Unauthorized retrieval rate",
                baseline="Not measured; shared-drive access is informal",
                target="0 hits on the fixture ACL suite",
                how_measured="Automated retrieval tests per role",
            ),
            SuccessMetric(
                name="Sensitive-span handling",
                baseline="Raw fields can be pasted into a chat tool",
                target="100% of planted spans tokenized before infer",
                how_measured="Proxy audit log vs. planted fixture values",
            ),
            SuccessMetric(
                name="Approval durability",
                baseline="No recorded approval for outbound partner shares",
                target="In-flight approvals resume after a forced worker restart",
                how_measured="Chaos step in the demo script",
            ),
            SuccessMetric(
                name="Egress posture",
                baseline="Tools assume public internet",
                target="No public egress from the pilot VPC",
                how_measured="Automated egress smoke test",
            ),
        ],
    )


def _erp(_request: str) -> ScopePackage:
    return ScopePackage(
        customer_problem=(
            "Analysts swivel-chair between a chat assistant and a thick-client ERP or ticket "
            "system. Any automation today would mean a shared password and unlogged writes. "
            "The intake asks for a scoped four-week pilot that can read — and carefully write — "
            "a legacy system of record through a typed tool interface."
        ),
        sow=FourWeekSow(
            title="Legacy system-of-record assistant — four-week pilot",
            problem=(
                "Give an assistant a safe, allowlisted interface to a fictional legacy SOAP/RPC "
                "system so users can look up records and propose updates without a raw pipe to "
                "destructive methods."
            ),
            users=[
                "Operations analyst (lookups and proposed updates)",
                "Approver (commits to the system of record)",
                "IT administrator (allowlist and audit review)",
            ],
            constraints=[
                "Fictional records only; no production ERP connectivity",
                "Writes are dry-run by default",
                "Deny-by-default for methods not on the allowlist",
                "Every tool call is audited",
            ],
            weeks=[
                SowWeek(
                    week=1,
                    goals=["Stand up a mock SOAP service and a typed tool contract"],
                    deliverables=["Mock schema and fixture records", "Read-only lookup tools"],
                ),
                SowWeek(
                    week=2,
                    goals=["Add a two-phase write path (propose, then commit)"],
                    deliverables=["Dry-run diffs", "Explicit commit flag"],
                ),
                SowWeek(
                    week=3,
                    goals=["Enforce the allowlist and wire an optional human approval on commit"],
                    deliverables=["Deny-by-default policy tests", "Approval hook"],
                ),
                SowWeek(
                    week=4,
                    goals=["Package a client config, audit viewer, and pilot readout"],
                    deliverables=["Documented tool-client config", "Audit sample", "Pilot metrics"],
                ),
            ],
            out_of_scope=[
                "A real SAP, Oracle, or other vendor connection",
                "Bulk data migration",
                "Replacing the legacy client for all users",
            ],
        ),
        pilot_plan=PilotPlan(
            baseline=(
                "Lookups and updates happen in a thick client. Informal copy-paste into a chat "
                "tool is unlogged. There is no allowlist or dry-run for automated writes."
            ),
            success_measures=[
                "100% of non-allowlisted methods are denied in contract tests",
                "Every write produces a dry-run diff and an audit record before commit",
                "Commit cannot proceed without an explicit confirmation (and an approval id when enabled)",
            ],
            first_shippable_slice=(
                "Read tools plus a two-phase write against a mock SOAP service, with deny-by-default "
                "and a published client config."
            ),
            first_users=[
                "One fictional operations analyst",
                "One fictional approver",
                "One fictional IT administrator",
            ],
        ),
        threat_model=ThreatModel(
            summary=(
                "The pilot must not become an unauthenticated, unlogged back door into a system "
                "of record, even when that system is a mock."
            ),
            items=[
                StrideItem(
                    category="spoofing",
                    threat="A caller invokes tools without a user or task identity.",
                    mitigation="Require a user-bound credential on every tool call; reject anonymous traffic.",
                ),
                StrideItem(
                    category="tampering",
                    threat="A proposed update is altered between dry-run and commit.",
                    mitigation="Bind commit to the dry-run hash and expire stale proposals.",
                ),
                StrideItem(
                    category="repudiation",
                    threat="A record changes and no one can show which tool call did it.",
                    mitigation="Append-only audit with tool name, actor, payload, and result.",
                ),
                StrideItem(
                    category="information_disclosure",
                    threat="The model echoes fields a given user should not see.",
                    mitigation="Filter tool results by role and keep raw SOAP out of logs by default.",
                ),
                StrideItem(
                    category="denial_of_service",
                    threat="A looping agent floods the legacy mock or the real interface later.",
                    mitigation="Rate limits, timeouts, and idempotency keys on writes.",
                ),
                StrideItem(
                    category="elevation_of_privilege",
                    threat="The agent calls a delete or admin method that was never granted.",
                    mitigation="Deny-by-default allowlist and contract tests for disallowed methods.",
                ),
            ],
        ),
        architecture=ArchitectureDiagram(
            mermaid=(
                "flowchart LR\n"
                "  User[Analyst] --> Agent[Assistant]\n"
                "  Agent --> MCP[Typed tool server]\n"
                "  MCP --> Policy[Allowlist and schema]\n"
                "  Policy --> Adapter[Legacy SOAP adapter]\n"
                "  Adapter --> Mock[Mock system of record]\n"
                "  Policy --> Audit[Audit log]\n"
                "  Policy -.-> Approver[Optional human approval]"
            ),
            caption=(
                "The assistant never talks to the legacy API directly. A typed tool layer applies "
                "allowlist, schema, dry-run, and audit policy first."
            ),
        ),
        success_metrics=[
            SuccessMetric(
                name="Allowlist enforcement",
                baseline="No method-level policy",
                target="100% of disallowed methods denied",
                how_measured="Contract test suite against the mock service",
            ),
            SuccessMetric(
                name="Write safety",
                baseline="Unlogged direct edits in a thick client",
                target="Every write has a dry-run diff and an audit record",
                how_measured="Audit log review of the demo script",
            ),
            SuccessMetric(
                name="Time to look up a record",
                baseline="Swivel-chair between chat and thick client",
                target="Lookup completed in one assistant turn on fixture records",
                how_measured="Timed walkthrough on the sample data",
            ),
        ],
    )


def _generic(request: str) -> ScopePackage:
    excerpt = " ".join(request.split())
    if len(excerpt) > 280:
        excerpt = excerpt[:277] + "..."
    if not excerpt:
        excerpt = "The intake was empty of detail, so this package states assumptions explicitly."
    return ScopePackage(
        customer_problem=(
            "The requester wants an AI capability but has not yet defined users, constraints, "
            "success measures, or a first slice. The four-week pilot below turns that ambiguity "
            "into a testable plan. Intake excerpt: "
            f'"{excerpt}"'
        ),
        sow=FourWeekSow(
            title="Enterprise AI pilot — four-week scope",
            problem=(
                "Deliver a narrow, measurable assistant for a single workflow, with clear data "
                "boundaries, a human approval on high-stakes actions, and a documented success bar."
            ),
            users=[
                "Primary operator of the workflow",
                "Approver for restricted actions",
                "IT sponsor",
            ],
            constraints=[
                "Fictional or sanitized data only in the pilot",
                "Least-privilege access to tools and records",
                "High-stakes actions require a recorded human decision",
                "Secrets stay in the environment, never in source control",
            ],
            weeks=[
                SowWeek(
                    week=1,
                    goals=["Clarify the workflow, users, and data sources", "Agree the success metrics"],
                    deliverables=["Written assumptions", "Metric definitions", "Fixture or sample set"],
                ),
                SowWeek(
                    week=2,
                    goals=["Build a thin retrieval or tool path for the first workflow"],
                    deliverables=["End-to-end happy path on fixture data"],
                ),
                SowWeek(
                    week=3,
                    goals=[
                        "Add guardrails: access control, logging, and an approval on restricted actions"
                    ],
                    deliverables=["Audit trail", "Approval demo", "Failure-case tests"],
                ),
                SowWeek(
                    week=4,
                    goals=["Deploy to the agreed environment and run the pilot readout"],
                    deliverables=[
                        "Deploy notes",
                        "Measured results vs. targets",
                        "Go / no-go recommendation",
                    ],
                ),
            ],
            out_of_scope=[
                "Organization-wide rollout",
                "Unscoped access to all enterprise systems",
                "Production authorization or compliance certification",
            ],
        ),
        pilot_plan=PilotPlan(
            baseline=(
                "The workflow is manual or informal. There is no agreed metric, no recorded "
                "approval path, and no documented data boundary for an assistant."
            ),
            success_measures=[
                "The first workflow completes on fixture data without leaving the agreed boundary",
                "Restricted actions cannot complete without a recorded human approval",
                "Pilot metrics are captured and compared to the targets in this package",
            ],
            first_shippable_slice=(
                "One workflow, fixture data, basic access control, logging, and a single "
                "approval-gated action."
            ),
            first_users=[
                "One fictional primary operator",
                "One fictional approver",
                "One fictional IT sponsor",
            ],
        ),
        threat_model=ThreatModel(
            summary=(
                "A vaguely scoped assistant is most dangerous when it is over-connected and under-logged."
            ),
            items=[
                StrideItem(
                    category="spoofing",
                    threat="Calls are accepted without binding them to a person or role.",
                    mitigation="Authenticate users and attach a role to every request and tool call.",
                ),
                StrideItem(
                    category="tampering",
                    threat="Prompts, tools, or fixtures are changed without review.",
                    mitigation="Version configuration and require review for tool or prompt changes.",
                ),
                StrideItem(
                    category="repudiation",
                    threat="Actions cannot be traced to a user or a model decision.",
                    mitigation="Audit logs for prompts, retrieval, tool calls, and approvals.",
                ),
                StrideItem(
                    category="information_disclosure",
                    threat="The assistant is pointed at data the first users should not see.",
                    mitigation="Start with a fixture set; expand data access only with an explicit decision.",
                ),
                StrideItem(
                    category="denial_of_service",
                    threat="The pilot depends on a single unbounded API and fails when that API is rate-limited or down.",
                    mitigation="Timeouts, budgets, and a documented degraded mode.",
                ),
                StrideItem(
                    category="elevation_of_privilege",
                    threat="A general-purpose agent is given broad tools 'just in case.'",
                    mitigation="Allowlist the minimum tools for the first slice; deny the rest.",
                ),
            ],
        ),
        architecture=ArchitectureDiagram(
            mermaid=(
                "flowchart LR\n"
                "  User[Operator] --> App[Pilot assistant]\n"
                "  App --> Policy[Access and approval policy]\n"
                "  Policy --> Tools[Allowlisted tools]\n"
                "  Policy --> Store[Approved data set]\n"
                "  App --> Log[Audit log]"
            ),
            caption=(
                "A minimal pilot: one user path, one approved data set, allowlisted tools, and an audit log."
            ),
        ),
        success_metrics=[
            SuccessMetric(
                name="Workflow completion on fixtures",
                baseline="Not measured",
                target="First workflow completes end-to-end on the fixture set",
                how_measured="Scripted walkthrough",
            ),
            SuccessMetric(
                name="Approval coverage",
                baseline="No recorded approvals",
                target="100% of restricted actions show a human decision",
                how_measured="Audit log review",
            ),
            SuccessMetric(
                name="Scope discipline",
                baseline="Request is unbounded",
                target="No tool or data source used outside the written allowlist",
                how_measured="Tool-call inventory vs. the week-1 list",
            ),
        ],
    )


class TemplateProvider(Provider):
    """Deterministic, offline packager. No network and no API key."""

    name = "template"

    def generate(self, request: str) -> ScopePackage:
        text = request.strip()
        if not text:
            raise ValueError("request is empty")
        kind = _classify(text)
        if kind == "ops":
            return _ops(text)
        if kind == "erp":
            return _erp(text)
        return _generic(text)
