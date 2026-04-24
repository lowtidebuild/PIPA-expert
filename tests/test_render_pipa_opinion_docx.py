from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

from scripts.lib.opinion_model import load_opinion_artifact
from scripts.render_pipa_opinion_docx import render_opinion_artifact
from scripts.validate_opinion_artifact import validate_artifact


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _aggregated_for(text: str, label: str = "unknown") -> dict:
    claim = "개인정보 보호법 제15조상 정보주체 동의가 있는 경우 개인정보 수집·이용 근거가 인정됩니다."
    start = text.index(claim)
    end = start + len(claim)
    return {
        "aggregated": [
            {
                "claim": {
                    "id": "summary-claim",
                    "text": claim,
                    "sentence_span": {"start": start, "end": end},
                    "claim_type": "citation",
                },
                "verdict": {
                    "claim": {
                        "id": "summary-claim",
                        "text": claim,
                        "sentence_span": {"start": start, "end": end},
                        "claim_type": "citation",
                    },
                    "label": label,
                    "verifier_name": "fixture",
                    "authority": 1.0,
                    "rationale": "fixture",
                    "evidence": [{"title": "개인정보 보호법 제15조", "url": "library/grade-a/pipa/art15.md"}],
                },
            }
        ]
    }


def test_render_opinion_artifact_writes_docx_and_markdown(tmp_path) -> None:
    rendered = render_opinion_artifact(FIXTURES / "opinion_minimal.json", out=tmp_path)

    assert rendered.docx_path == tmp_path / "opinion_minimal.docx"
    assert rendered.markdown_path == tmp_path / "opinion_minimal.md"
    assert rendered.docx_path.exists()
    assert rendered.markdown_path.exists()
    assert "개인정보 처리 위탁 검토 메모" in rendered.markdown_path.read_text(encoding="utf-8")
    assert validate_artifact(rendered.docx_path, require_audit=True).ok is True

    xml = ZipFile(rendered.docx_path).read("word/document.xml").decode("utf-8")
    assert "개인정보 처리 위탁 검토 메모" in xml
    assert "맑은 고딕" in xml


def test_render_opinion_artifact_appends_citation_audit(tmp_path) -> None:
    artifact = load_opinion_artifact(FIXTURES / "opinion_minimal.json")
    source_md = artifact.to_markdown()
    aggregated_path = tmp_path / "aggregated.json"
    aggregated_path.write_text(json.dumps(_aggregated_for(source_md), ensure_ascii=False), encoding="utf-8")

    rendered = render_opinion_artifact(
        FIXTURES / "opinion_minimal.json",
        out=tmp_path,
        aggregated_path=aggregated_path,
    )

    markdown = rendered.markdown_path.read_text(encoding="utf-8")
    assert "[Partially Unverified]" in markdown
    assert "## 부록: 검증 로그 (Citation Audit Log)" in markdown
    assert rendered.audit_status_path is not None
    status = json.loads(rendered.audit_status_path.read_text(encoding="utf-8"))
    assert status["status"] == "complete"

    xml = ZipFile(rendered.docx_path).read("word/document.xml").decode("utf-8")
    assert "Citation Audit Log" in xml
    assert "Citation audit status: complete" in xml


def test_render_pipa_opinion_docx_cli_outputs_json(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/render_pipa_opinion_docx.py",
            "tests/fixtures/opinion_minimal.json",
            "--out",
            str(tmp_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["docx"].endswith("opinion_minimal.docx")
    assert payload["markdown"].endswith("opinion_minimal.md")
