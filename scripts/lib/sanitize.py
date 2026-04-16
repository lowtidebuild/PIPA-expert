from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
from typing import Literal


Severity = Literal["role-marker", "jailbreak", "forged-firewall", "role-tag"]


@dataclass(frozen=True)
class Match:
    pattern_id: str
    severity: Severity
    start: int
    end: int
    snippet: str


@dataclass
class SanitizeResult:
    text: str
    matches: list[Match] = field(default_factory=list)
    aborted: bool = False


def _load_patterns():
    try:
        module = importlib.import_module("scripts.lib.patterns")
    except Exception:
        return (), True
    return getattr(module, "PATTERNS", ()), False


def _truncate_snippet(text: str, limit: int = 80) -> str:
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _collect_matches(text: str, patterns) -> list[Match]:
    raw_matches: list[Match] = []
    for pattern in patterns:
        for regex_match in pattern.regex.finditer(text):
            raw_matches.append(
                Match(
                    pattern_id=pattern.pattern_id,
                    severity=pattern.severity,
                    start=regex_match.start(),
                    end=regex_match.end(),
                    snippet=_truncate_snippet(regex_match.group(0)),
                )
            )

    raw_matches.sort(key=lambda item: (item.start, item.end))

    deduped: list[Match] = []
    last_end = -1
    for match in raw_matches:
        if match.start < last_end:
            continue
        deduped.append(match)
        last_end = match.end
    return deduped


def _wrap_matches(text: str, matches: list[Match]) -> str:
    if not matches:
        return text

    parts: list[str] = []
    cursor = 0
    for match in matches:
        parts.append(text[cursor:match.start])
        parts.append(f"<escape>{text[match.start:match.end]}</escape>")
        cursor = match.end
    parts.append(text[cursor:])
    return "".join(parts)


def _sanitize_text(text: str) -> SanitizeResult:
    patterns, aborted = _load_patterns()
    if aborted:
        return SanitizeResult(text=text, aborted=True)

    matches = _collect_matches(text, patterns)
    return SanitizeResult(text=_wrap_matches(text, matches), matches=matches)


def sanitize_ingested_markdown(text: str) -> SanitizeResult:
    return _sanitize_text(text)


def sanitize_fetched_text(text: str, *, source: str) -> SanitizeResult:
    _ = source
    return _sanitize_text(text)


def sanitize_yaml_string(s: str) -> str:
    value = "" if s is None else str(s)
    return json.dumps(value, ensure_ascii=False)[1:-1]


def write_audit_sidecar(path, result: SanitizeResult) -> None:
    target = Path(path)
    sidecar_path = (
        target.with_suffix(".sanitize.json")
        if target.suffix
        else target.with_name(f"{target.name}.sanitize.json")
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aborted": result.aborted,
        "match_count": len(result.matches),
        "matches": [asdict(match) for match in result.matches],
    }
    sidecar_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
