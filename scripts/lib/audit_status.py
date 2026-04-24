"""Citation audit status helpers for PIPA workflow sidecars."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_audit_status(
    aggregated: dict[str, Any],
    *,
    input_path: str | None = None,
    claim_count_expected: int | None = None,
    inserted_count: int = 0,
    invalid_span_count: int = 0,
    invalid_claim_ids: list[str] | None = None,
    invalid_span_reasons: list[dict[str, str]] | None = None,
    skipped_claim_ids: list[str] | None = None,
    failed_verifiers: list[str] | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Build a normalized audit_status.json payload from aggregated verdicts."""
    items = _verdict_items(aggregated)
    label_counts = _label_counts(items)
    expected = len(items) if claim_count_expected is None else claim_count_expected
    skipped = skipped_claim_ids or []
    failed = failed_verifiers or []
    invalid_ids = invalid_claim_ids or []
    invalid_reasons = invalid_span_reasons or []

    status = {
        "status": "complete",
        "input_path": input_path,
        "claim_count_expected": expected,
        "claim_count_extracted": len(items),
        "verified_count": label_counts["verified"],
        "unknown_count": label_counts["unknown"],
        "contradicted_count": label_counts["contradicted"],
        "inserted_count": inserted_count,
        "invalid_span_count": invalid_span_count,
        "invalid_claim_ids": invalid_ids,
        "invalid_span_reasons": invalid_reasons,
        "failed_verifiers": failed,
        "skipped_chunks": [],
        "skipped_claim_ids": skipped,
        "reason": reason,
    }
    status["status"] = derive_status(status)
    return status


def derive_status(status: dict[str, Any]) -> str:
    expected = int(status.get("claim_count_expected") or 0)
    extracted = int(status.get("claim_count_extracted") or 0)
    invalid = int(status.get("invalid_span_count") or 0)
    skipped_claims = status.get("skipped_claim_ids") or []
    skipped_chunks = status.get("skipped_chunks") or []
    failed_verifiers = status.get("failed_verifiers") or []
    reason = status.get("reason")

    if expected == 0 and extracted == 0:
        return "skipped"
    if expected > 0 and extracted == 0:
        return "failed"
    if reason and extracted == 0:
        return "failed"
    if invalid or skipped_claims or skipped_chunks or failed_verifiers or extracted < expected:
        return "partial"
    return "complete"


def _verdict_items(aggregated: dict[str, Any]) -> list[dict[str, Any]]:
    items = aggregated.get("aggregated")
    return items if isinstance(items, list) else []


def _label_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"verified": 0, "unknown": 0, "contradicted": 0}
    for item in items:
        verdict = item.get("verdict") if isinstance(item, dict) else None
        label = str((verdict or {}).get("label", "unknown"))
        if label == "verified":
            counts["verified"] += 1
        elif label == "contradicted":
            counts["contradicted"] += 1
        else:
            counts["unknown"] += 1
    return counts
