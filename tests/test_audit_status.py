from __future__ import annotations

import json
import subprocess
import sys

from scripts.lib.audit_status import build_audit_status


def _aggregated(label: str = "verified") -> dict:
    return {
        "aggregated": [
            {
                "claim": {"text": "claim", "sentence_span": {"start": 0, "end": 5}, "claim_type": "factual"},
                "verdict": {
                    "claim": {"text": "claim", "sentence_span": {"start": 0, "end": 5}, "claim_type": "factual"},
                    "label": label,
                    "verifier_name": "fixture",
                    "authority": 1.0,
                    "rationale": "fixture",
                    "evidence": [],
                },
            }
        ]
    }


def test_build_audit_status_complete() -> None:
    status = build_audit_status(_aggregated("verified"), inserted_count=0)

    assert status["status"] == "complete"
    assert status["claim_count_expected"] == 1
    assert status["verified_count"] == 1


def test_build_audit_status_partial_for_invalid_spans() -> None:
    status = build_audit_status(
        _aggregated("unknown"),
        inserted_count=0,
        invalid_span_count=1,
        invalid_claim_ids=["claim-1"],
    )

    assert status["status"] == "partial"
    assert status["unknown_count"] == 1
    assert status["invalid_claim_ids"] == ["claim-1"]


def test_build_audit_status_failed_when_expected_but_none_extracted() -> None:
    status = build_audit_status({"aggregated": []}, claim_count_expected=2, reason="extractor failed")

    assert status["status"] == "failed"
    assert status["reason"] == "extractor failed"


def test_build_audit_status_skipped_for_no_expected_claims() -> None:
    status = build_audit_status({"aggregated": []})

    assert status["status"] == "skipped"


def test_audit_status_cli_writes_sidecar(tmp_path) -> None:
    aggregated = tmp_path / "aggregated.json"
    out = tmp_path / "audit_status.json"
    aggregated.write_text(json.dumps(_aggregated("contradicted"), ensure_ascii=False), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_status.py",
            str(aggregated),
            "--output",
            str(out),
            "--invalid-span-count",
            "1",
            "--invalid-claim-id",
            "claim-1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "partial" in completed.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "partial"
    assert payload["contradicted_count"] == 1
