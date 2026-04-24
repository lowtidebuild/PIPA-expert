from __future__ import annotations

from scripts.render_audit_append import render_audit_append


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


def test_render_audit_append_preserves_markdown_and_adds_tag() -> None:
    sentence = "개인정보 보호법 제15조는 동의 요건을 규정한다."
    md_text = (
        "---\n"
        "title: sample\n"
        "---\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        f"{sentence}\n\n"
        "```python\n"
        "print('do not tag inside code')\n"
        "```\n"
    )
    start = md_text.index(sentence)
    end = start + len(sentence)

    rendered, status = render_audit_append(md_text, _aggregated(sentence, start, end))

    assert "---\ntitle: sample\n---" in rendered
    assert "| A | B |\n|---|---|\n| 1 | 2 |" in rendered
    assert "```python\nprint('do not tag inside code')\n```" in rendered
    assert f"{sentence} [Unverified]" in rendered
    assert "## 부록: 검증 로그 (Citation Audit Log)" in rendered
    assert status["status"] == "complete"
    assert status["inserted_count"] == 1


def test_render_audit_append_reports_invalid_span() -> None:
    md_text = "본문입니다."
    rendered, status = render_audit_append(
        md_text,
        _aggregated("없는 문장", 100, 120, label="unknown"),
    )

    assert "[Partially Unverified]" not in rendered
    assert "Audit status: partial" in rendered
    assert status["status"] == "partial"
    assert status["invalid_span_count"] == 1
