"""Structured opinion artifact contract for PIPA memo/opinion workflows."""

from __future__ import annotations

import json
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    INSUFFICIENT = "INSUFFICIENT"
    CONTRADICTED = "CONTRADICTED"


class RunStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


SectionType = Literal[
    "ai_notice",
    "scope",
    "executive_summary",
    "issues",
    "analysis",
    "counter_analysis",
    "recommendations",
    "sources",
    "verification_guide",
    "disclaimer",
]


REQUIRED_SECTION_TYPES: frozenset[str] = frozenset(
    {
        "ai_notice",
        "scope",
        "executive_summary",
        "analysis",
        "counter_analysis",
        "recommendations",
        "sources",
        "verification_guide",
        "disclaimer",
    }
)


class CitationSource(BaseModel):
    """Typed source/citation item used by structured opinions."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    citation: str
    grade: SourceGrade
    verification_status: VerificationStatus
    source_path: str | None = None
    url: str | None = None
    law_name: str | None = None
    article: str | None = None
    paragraph: str | None = None
    item: str | None = None
    quote: str | None = None
    reliability_note: str | None = None

    @field_validator("id", "title", "citation")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def _requires_access_path(self) -> "CitationSource":
        if not self.source_path and not self.url:
            raise ValueError("citation source requires source_path or url")
        if self.grade == SourceGrade.D:
            raise ValueError("Grade D sources are not allowed in opinion artifacts")
        if self.verification_status == VerificationStatus.VERIFIED and self.grade in {SourceGrade.C}:
            raise ValueError("Grade C sources cannot be marked VERIFIED as primary authority")
        return self

    def markdown_label(self) -> str:
        return f"[{self.verification_status.value}] [Grade {self.grade.value}] {self.citation}"


class OpinionSection(BaseModel):
    """Ordered document section."""

    model_config = ConfigDict(extra="forbid")

    section_type: SectionType
    heading: str
    body: str

    @field_validator("heading", "body")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class VerificationRun(BaseModel):
    """Fact-check or citation-audit sidecar summary."""

    model_config = ConfigDict(extra="forbid")

    status: RunStatus
    sidecar_path: str | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def _partial_or_failed_requires_reason(self) -> "VerificationRun":
        if self.status in {RunStatus.PARTIAL, RunStatus.FAILED, RunStatus.SKIPPED} and not self.reason:
            raise ValueError("partial, failed, and skipped runs require reason")
        return self


class OpinionArtifact(BaseModel):
    """Minimum structured contract for PIPA legal opinion/memo artifacts."""

    model_config = ConfigDict(extra="forbid")

    title: str
    language: Literal["ko", "en", "bilingual"] = "ko"
    request_type: Literal["opinion", "memo", "review_report"] = "memo"
    as_of_date: date
    questions: list[str] = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    ai_notice: str
    disclaimer: str
    sections: list[OpinionSection] = Field(min_length=len(REQUIRED_SECTION_TYPES))
    citations: list[CitationSource] = Field(min_length=1)
    fact_check: VerificationRun
    citation_audit: VerificationRun | None = None

    @field_validator("title", "ai_notice", "disclaimer")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("questions", "assumptions")
    @classmethod
    def _strip_list_items(cls, values: list[str]) -> list[str]:
        stripped = [value.strip() for value in values if value.strip()]
        if not stripped and values:
            raise ValueError("list cannot contain only empty items")
        return stripped

    @model_validator(mode="after")
    def _validate_contract(self) -> "OpinionArtifact":
        missing = REQUIRED_SECTION_TYPES - {section.section_type for section in self.sections}
        if missing:
            raise ValueError(f"missing required sections: {', '.join(sorted(missing))}")
        if "AI" not in self.ai_notice and "인공지능" not in self.ai_notice:
            raise ValueError("ai_notice must disclose AI assistance")
        disclaimer_lower = self.disclaimer.lower()
        if "법률 자문" not in self.disclaimer and "legal advice" not in disclaimer_lower:
            raise ValueError("disclaimer must state that the artifact is not legal advice")
        if self.fact_check.status != RunStatus.COMPLETE and not self.fact_check.reason:
            raise ValueError("non-complete fact_check requires reason")
        return self

    def section_types(self) -> set[str]:
        return {section.section_type for section in self.sections}

    def to_markdown(self, *, include_audit_status: bool = True) -> str:
        """Render a simple Markdown copy for validation, review, and sidecars."""
        lines = [f"# {self.title}", "", self.ai_notice, ""]
        lines.append(f"작성 기준일: {self.as_of_date.isoformat()}")
        lines.append("")
        lines.append("## Questions")
        lines.extend(f"- {question}" for question in self.questions)
        if self.assumptions:
            lines.append("")
            lines.append("## Assumptions")
            lines.extend(f"- {assumption}" for assumption in self.assumptions)

        for section in self.sections:
            lines.append("")
            lines.append(f"## {section.heading}")
            lines.append("")
            lines.append(section.body)

        lines.append("")
        lines.append("## Structured Sources")
        lines.append("")
        for source in self.citations:
            lines.append(f"- {source.markdown_label()}")
            if source.quote:
                lines.append(f"  > {source.quote}")

        lines.append("")
        lines.append(f"Fact-check status: {self.fact_check.status.value}")
        if include_audit_status and self.citation_audit:
            lines.append(f"Citation audit status: {self.citation_audit.status.value}")
            if self.citation_audit.reason:
                lines.append(f"Citation audit reason: {self.citation_audit.reason}")

        lines.append("")
        lines.append(self.disclaimer)
        return "\n".join(lines).rstrip() + "\n"


def load_opinion_artifact(path: str | Path) -> OpinionArtifact:
    return OpinionArtifact.model_validate_json(Path(path).read_text(encoding="utf-8"))


def write_opinion_artifact_schema(path: str | Path) -> None:
    payload: dict[str, Any] = OpinionArtifact.model_json_schema()
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
