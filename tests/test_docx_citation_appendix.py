from __future__ import annotations

from zipfile import ZipFile

from docx import Document

from scripts.docx_citation_appendix import (
    append_citation_audit_log,
    inject_unverified_tags,
)


def _aggregated(text: str, start: int, end: int, label: str = "contradicted") -> dict:
    return {
        "aggregated": [
            {
                "claim": {
                    "text": text,
                    "sentence_span": {"start": start, "end": end},
                    "claim_type": "citation",
                },
                "verdict": {
                    "claim": {
                        "text": text,
                        "sentence_span": {"start": start, "end": end},
                        "claim_type": "citation",
                    },
                    "label": label,
                    "verifier_name": "korean-law",
                    "authority": 1.0,
                    "rationale": "fixture",
                    "evidence": [{"title": "source", "url": "https://example.test/source"}],
                },
            }
        ]
    }


def test_inject_unverified_tags_returns_backward_compatible_string() -> None:
    sentence = "개인정보 보호법 제15조는 동의 요건을 규정한다."
    start = 0
    end = len(sentence)

    rendered = inject_unverified_tags(sentence, _aggregated(sentence, start, end))

    assert rendered == f"{sentence} [Unverified]"


def test_inject_unverified_tags_can_report_invalid_spans() -> None:
    body = "본문입니다."

    result = inject_unverified_tags(body, _aggregated("없는 문장", 100, 120), return_result=True)

    assert result.body_md == body
    assert result.inserted_count == 0
    assert result.invalid_span_count == 1
    assert result.invalid_claim_ids == ["claim-1"]


def test_append_citation_audit_log_writes_status_summary(tmp_path) -> None:
    sentence = "개인정보 보호법 제15조는 동의 요건을 규정한다."
    result = inject_unverified_tags(sentence, _aggregated(sentence, 0, len(sentence)), return_result=True)
    doc = Document()
    doc.add_paragraph(sentence)

    append_citation_audit_log(doc, _aggregated(sentence, 0, len(sentence)), audit_status=result)

    out = tmp_path / "audit.docx"
    doc.save(out)
    xml = ZipFile(out).read("word/document.xml").decode("utf-8")
    assert "Citation Audit Log" in xml
    assert "Citation audit status: complete" in xml
    assert "맑은 고딕" in xml
