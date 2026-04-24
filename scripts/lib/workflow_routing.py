"""Request routing helper mirroring docs/agent-protocol.md."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowDecision:
    request_type: str
    output: str
    fact_check: str
    citation_audit: str
    mcp_freshness: str
    mcp_freshness_limit: int | None
    matched_signal: str
    weight: int

    @property
    def requires_fact_check(self) -> bool:
        return self.fact_check == "yes"

    @property
    def requires_citation_audit(self) -> bool:
        return self.citation_audit == "yes"


@dataclass(frozen=True)
class _WorkflowRule:
    request_type: str
    signals: tuple[str, ...]
    output: str
    fact_check: str
    citation_audit: str
    mcp_freshness: str
    mcp_freshness_limit: int | None
    weight: int


_RULES = [
    _WorkflowRule(
        request_type="document",
        signals=("docx", "워드"),
        output="docx + md copy",
        fact_check="yes",
        citation_audit="yes",
        mcp_freshness="up to 5 laws",
        mcp_freshness_limit=5,
        weight=50,
    ),
    _WorkflowRule(
        request_type="opinion/memo",
        signals=("의견서", "법률의견서", "메모", "검토보고서", "legal opinion"),
        output="md unless DOCX requested",
        fact_check="yes",
        citation_audit="yes",
        mcp_freshness="up to 5 laws",
        mcp_freshness_limit=5,
        weight=40,
    ),
    _WorkflowRule(
        request_type="comparison",
        signals=("비교", "차이점", " vs ", "vs."),
        output="chat/md",
        fact_check="yes",
        citation_audit="conditional",
        mcp_freshness="up to 5 laws",
        mcp_freshness_limit=5,
        weight=30,
    ),
    _WorkflowRule(
        request_type="audit",
        signals=("/audit", "citation audit", "인용 감사"),
        output="same as input/sidecar",
        fact_check="avoid duplicate",
        citation_audit="yes",
        mcp_freshness="no new freshness unless needed",
        mcp_freshness_limit=None,
        weight=20,
    ),
    _WorkflowRule(
        request_type="analysis",
        signals=("해도 되나요", "가능한가요", "가능한가", "해야 하나요"),
        output="chat/md",
        fact_check="yes if 3+ citations",
        citation_audit="conditional",
        mcp_freshness="up to 2 laws",
        mcp_freshness_limit=2,
        weight=10,
    ),
    _WorkflowRule(
        request_type="lookup",
        signals=("조문 보여줘", "원문", "보여줘"),
        output="chat",
        fact_check="optional",
        citation_audit="no",
        mcp_freshness="up to 2 laws",
        mcp_freshness_limit=2,
        weight=5,
    ),
]

_DEFAULT_RULE = _WorkflowRule(
    request_type="analysis",
    signals=("",),
    output="chat/md",
    fact_check="yes if 3+ citations",
    citation_audit="conditional",
    mcp_freshness="up to 2 laws",
    mcp_freshness_limit=2,
    weight=0,
)


def classify_request(text: str) -> WorkflowDecision:
    """Classify a user request using the protocol's heaviest matching signal."""
    normalized = f" {text.casefold()} "
    matches: list[tuple[_WorkflowRule, str]] = []
    for rule in _RULES:
        for signal in rule.signals:
            if signal.casefold() in normalized:
                matches.append((rule, signal))
                break

    rule, signal = max(matches, key=lambda item: item[0].weight) if matches else (_DEFAULT_RULE, "")
    return WorkflowDecision(
        request_type=rule.request_type,
        output=rule.output,
        fact_check=rule.fact_check,
        citation_audit=rule.citation_audit,
        mcp_freshness=rule.mcp_freshness,
        mcp_freshness_limit=rule.mcp_freshness_limit,
        matched_signal=signal,
        weight=rule.weight,
    )
