from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.lib.opinion_model import (
    CitationSource,
    OpinionArtifact,
    SourceGrade,
    VerificationStatus,
    load_opinion_artifact,
)
from scripts.validate_opinion_artifact import validate_artifact


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_load_opinion_artifact_fixture_and_render_markdown(tmp_path: Path) -> None:
    artifact = load_opinion_artifact(FIXTURES / "opinion_minimal.json")

    assert artifact.title == "개인정보 처리 위탁 검토 메모"
    assert "counter_analysis" in artifact.section_types()
    assert artifact.citations[0].markdown_label() == "[VERIFIED] [Grade A] 개인정보 보호법 제15조 제1항 제1호"

    rendered = artifact.to_markdown()
    out = tmp_path / "opinion.md"
    out.write_text(rendered, encoding="utf-8")

    result = validate_artifact(out, require_audit=True)
    assert result.ok is True


def test_opinion_artifact_rejects_missing_required_section() -> None:
    artifact = load_opinion_artifact(FIXTURES / "opinion_minimal.json").model_dump(mode="json")
    artifact["sections"] = [
        section for section in artifact["sections"] if section["section_type"] != "counter_analysis"
    ]

    with pytest.raises(ValidationError, match="missing required sections"):
        OpinionArtifact.model_validate(artifact)


def test_citation_source_requires_access_path_or_url() -> None:
    with pytest.raises(ValidationError, match="source_path or url"):
        CitationSource(
            id="missing-access",
            title="개인정보 보호법 제15조",
            citation="개인정보 보호법 제15조",
            grade=SourceGrade.A,
            verification_status=VerificationStatus.VERIFIED,
        )


def test_citation_source_rejects_grade_d() -> None:
    with pytest.raises(ValidationError, match="Grade D"):
        CitationSource(
            id="wiki",
            title="Untrusted wiki",
            citation="wiki",
            grade=SourceGrade.D,
            verification_status=VerificationStatus.UNVERIFIED,
            url="https://example.test/wiki",
        )


def test_non_complete_verification_run_requires_reason() -> None:
    artifact = load_opinion_artifact(FIXTURES / "opinion_minimal.json").model_dump(mode="json")
    artifact["fact_check"] = {"status": "partial"}

    with pytest.raises(ValidationError, match="require reason"):
        OpinionArtifact.model_validate(artifact)
