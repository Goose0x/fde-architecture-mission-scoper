from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

StrideCategory = Literal[
    "spoofing",
    "tampering",
    "repudiation",
    "information_disclosure",
    "denial_of_service",
    "elevation_of_privilege",
]

STRIDE_CATEGORIES: tuple[StrideCategory, ...] = (
    "spoofing",
    "tampering",
    "repudiation",
    "information_disclosure",
    "denial_of_service",
    "elevation_of_privilege",
)


class PilotPlan(BaseModel):
    baseline: str = Field(min_length=1)
    success_measures: list[str] = Field(min_length=1)
    first_shippable_slice: str = Field(min_length=1)
    first_users: list[str] = Field(min_length=1)


class SowWeek(BaseModel):
    week: int = Field(ge=1, le=4)
    goals: list[str] = Field(min_length=1)
    deliverables: list[str] = Field(min_length=1)


class FourWeekSow(BaseModel):
    title: str = Field(min_length=1)
    problem: str = Field(min_length=1)
    users: list[str] = Field(min_length=1)
    constraints: list[str] = Field(min_length=1)
    weeks: list[SowWeek] = Field(min_length=4, max_length=4)
    out_of_scope: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def weeks_are_one_through_four(self) -> "FourWeekSow":
        numbers = [week.week for week in self.weeks]
        if numbers != [1, 2, 3, 4]:
            raise ValueError("weeks must be numbered 1, 2, 3, and 4 in order")
        return self


class StrideItem(BaseModel):
    category: StrideCategory
    threat: str = Field(min_length=1)
    mitigation: str = Field(min_length=1)


class ThreatModel(BaseModel):
    summary: str = Field(min_length=1)
    items: list[StrideItem] = Field(min_length=6)

    @model_validator(mode="after")
    def all_stride_categories_present(self) -> "ThreatModel":
        present = {item.category for item in self.items}
        missing = [category for category in STRIDE_CATEGORIES if category not in present]
        if missing:
            raise ValueError(f"threat model missing STRIDE categories: {', '.join(missing)}")
        return self


class ArchitectureDiagram(BaseModel):
    mermaid: str = Field(min_length=1)
    caption: str = Field(min_length=1)

    @field_validator("mermaid")
    @classmethod
    def looks_like_mermaid_flowchart(cls, value: str) -> str:
        first = value.lstrip().splitlines()[0].lower() if value.strip() else ""
        if not (first.startswith("flowchart") or first.startswith("graph ")):
            raise ValueError("architecture mermaid must start with flowchart or graph")
        return value


class SuccessMetric(BaseModel):
    name: str = Field(min_length=1)
    baseline: str = Field(min_length=1)
    target: str = Field(min_length=1)
    how_measured: str = Field(min_length=1)


class ScopePackage(BaseModel):
    customer_problem: str = Field(min_length=1)
    sow: FourWeekSow
    pilot_plan: PilotPlan
    threat_model: ThreatModel
    architecture: ArchitectureDiagram
    success_metrics: list[SuccessMetric] = Field(min_length=3)
