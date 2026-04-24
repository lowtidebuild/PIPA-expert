"""Raw-preserving Markdown renderer for PIPA citation audit append mode."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any


TAG_FOR_LABEL = {
    "contradicted": "[Unverified]",
    "unknown": "[Partially Unverified]",
}
LABEL_PRIORITY = {
    "unknown": 1,
    "contradicted": 2,
}
APPENDIX_HEADING = "## 부록: 검증 로그 (Citation Audit Log)"


def load_aggregated(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_audit_append(
    md_text: str,
    aggregated: dict[str, Any],
    *,
    base_status: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Append audit tags and a log without reparsing or re-rendering Markdown."""
    status = _initial_status(aggregated, base_status)
    skip_ranges = _skip_ranges(md_text)
    insertions: dict[int, str] = {}

    for item in _verdict_items(aggregated):
        verdict = _verdict(item)
        label = str(verdict.get("label", "unknown"))
        claim = _claim(item)
        status["claim_count_extracted"] += 1
        _increment_label_count(status, label)

        tag = TAG_FOR_LABEL.get(label)
        if tag is None:
            continue

        span = claim.get("sentence_span") or {}
        valid, reason = _valid_span(md_text, span, claim)
        claim_id = _claim_id(status["claim_count_extracted"], claim)
        if not valid:
            status["invalid_span_count"] += 1
            status["invalid_claim_ids"].append(claim_id)
            status["invalid_span_reasons"].append({"claim_id": claim_id, "reason": reason})
            continue

        start = int(span["start"])
        end = int(span["end"])
        if _span_overlaps_skip_range(start, end, skip_ranges):
            status["skipped_claim_ids"].append(claim_id)
            continue

        current = insertions.get(end)
        if current is None or LABEL_PRIORITY.get(label, 0) > LABEL_PRIORITY.get(_label_for_tag(current), 0):
            insertions[end] = tag

    rendered = md_text
    for offset, tag in sorted(insertions.items(), reverse=True):
        rendered = rendered[:offset] + f" {tag}" + rendered[offset:]

    status["inserted_count"] = len(insertions)
    status["status"] = _derive_status(status)
    rendered = rendered.rstrip() + "\n\n" + _audit_log_table(aggregated, status)
    return rendered, status


def _initial_status(aggregated: dict[str, Any], base_status: dict[str, Any] | None) -> dict[str, Any]:
    status = dict(base_status or {})
    status.setdefault("status", "complete")
    status.setdefault("claim_count_expected", len(_verdict_items(aggregated)))
    status["claim_count_extracted"] = 0
    status["verified_count"] = 0
    status["unknown_count"] = 0
    status["contradicted_count"] = 0
    status["invalid_span_count"] = 0
    status["invalid_claim_ids"] = []
    status["invalid_span_reasons"] = []
    status["skipped_claim_ids"] = []
    status["inserted_count"] = 0
    return status


def _derive_status(status: dict[str, Any]) -> str:
    if status["claim_count_expected"] == 0:
        return "skipped"
    if status["claim_count_extracted"] == 0:
        return "failed"
    if (
        status["invalid_span_count"] > 0
        or status["skipped_claim_ids"]
        or status["claim_count_extracted"] < status["claim_count_expected"]
    ):
        return "partial"
    return "complete"


def _increment_label_count(status: dict[str, Any], label: str) -> None:
    if label == "verified":
        status["verified_count"] += 1
    elif label == "contradicted":
        status["contradicted_count"] += 1
    else:
        status["unknown_count"] += 1


def _verdict_items(aggregated: dict[str, Any]) -> list[dict[str, Any]]:
    items = aggregated.get("aggregated")
    return items if isinstance(items, list) else []


def _verdict(item: dict[str, Any]) -> dict[str, Any]:
    verdict = item.get("verdict")
    return verdict if isinstance(verdict, dict) else {}


def _claim(item: dict[str, Any]) -> dict[str, Any]:
    verdict_claim = _verdict(item).get("claim")
    if isinstance(verdict_claim, dict):
        return verdict_claim
    claim = item.get("claim")
    return claim if isinstance(claim, dict) else {}


def _claim_id(index: int, claim: dict[str, Any]) -> str:
    raw = claim.get("id")
    if raw:
        return str(raw)
    return f"claim-{index}"


def _valid_span(md_text: str, span: dict[str, Any], claim: dict[str, Any]) -> tuple[bool, str | None]:
    start = span.get("start")
    end = span.get("end")
    if not isinstance(start, int) or not isinstance(end, int):
        return False, "missing start/end"
    if start < 0 or end < start or end > len(md_text):
        return False, "span out of bounds"

    claim_text = _normalize(str(claim.get("text", "")))
    span_text = _normalize(md_text[start:end])
    if claim_text and span_text and claim_text not in span_text and span_text not in claim_text:
        return False, "span text mismatch"
    return True, None


def _audit_log_table(aggregated: dict[str, Any], status: dict[str, Any]) -> str:
    lines = [
        "---",
        "",
        APPENDIX_HEADING,
        "",
        "본 산출물에 포함된 사실·인용 주장에 대한 자동 citation audit 결과입니다. "
        "자동 감사는 전문가 검토를 대체하지 않으며, Contradicted 또는 Unknown 항목은 "
        "최종 검토 시 독립 확인이 필요합니다.",
        "",
        f"Audit status: {status['status']}",
        f"Invalid spans: {status['invalid_span_count']}",
        "",
        "| # | 클레임 (Claim) | 판정 (Verdict) | Verifier | 근거 (Evidence) |",
        "|---|---|---|---|---|",
    ]
    for index, item in enumerate(_verdict_items(aggregated), start=1):
        verdict = _verdict(item)
        claim = _claim(item)
        label = str(verdict.get("label", "unknown"))
        claim_cell = _escape_table_cell(_truncate(str(claim.get("text", "")), 100))
        verdict_cell = _escape_table_cell(label)
        verifier_cell = _escape_table_cell(str(verdict.get("verifier_name", "-")))
        evidence_cell = _escape_table_cell(_format_evidence(verdict.get("evidence") or []))
        lines.append(f"| {index} | {claim_cell} | {verdict_cell} | {verifier_cell} | {evidence_cell} |")
    return "\n".join(lines).rstrip() + "\n"


def _format_evidence(evidence: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in evidence:
        url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        if title and url and title != url:
            parts.append(f"{title} ({url})")
        elif url:
            parts.append(url)
        elif title:
            parts.append(title)
    return "; ".join(parts) if parts else "-"


def _skip_ranges(md_text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    fence_start: int | None = None
    fence_token: str | None = None
    cursor = 0
    for line in md_text.splitlines(keepends=True):
        stripped = line.lstrip()
        if fence_start is None:
            match = re.match(r"([`~]{3,})", stripped)
            if match:
                fence_start = cursor
                fence_token = match.group(1)[0] * len(match.group(1))
        elif fence_token and stripped.startswith(fence_token):
            ranges.append((fence_start, cursor + len(line)))
            fence_start = None
            fence_token = None
        cursor += len(line)
    if fence_start is not None:
        ranges.append((fence_start, len(md_text)))

    in_quote = False
    quote_start = 0
    cursor = 0
    for line in md_text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(">"):
            if not in_quote:
                quote_start = cursor
                in_quote = True
        elif in_quote:
            ranges.append((quote_start, cursor))
            in_quote = False
        cursor += len(line)
    if in_quote:
        ranges.append((quote_start, len(md_text)))
    return ranges


def _span_overlaps_skip_range(start: int, end: int, skip_ranges: Iterable[tuple[int, int]]) -> bool:
    for skip_start, skip_end in skip_ranges:
        if start < skip_end and end > skip_start:
            return True
    return False


def _label_for_tag(tag: str) -> str:
    for label, known_tag in TAG_FOR_LABEL.items():
        if tag == known_tag:
            return label
    return ""


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _truncate(text: str, max_len: int) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= max_len:
        return collapsed
    return collapsed[: max_len - 1] + "..."


def _escape_table_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_md", help="Markdown file to annotate.")
    parser.add_argument("aggregated_json", help="citation-auditor aggregate JSON.")
    parser.add_argument("--status", help="Optional audit_status.json input/output path.")
    parser.add_argument("--output", help="Write annotated Markdown to this path instead of stdout.")
    args = parser.parse_args(argv)

    input_path = Path(args.input_md)
    aggregated_path = Path(args.aggregated_json)
    md_text = input_path.read_text(encoding="utf-8")
    aggregated = load_aggregated(aggregated_path)
    base_status = load_aggregated(args.status) if args.status and Path(args.status).exists() else None
    rendered, status = render_audit_append(md_text, aggregated, base_status=base_status)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    if args.status:
        Path(args.status).write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
