from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pipa_agent_freshness_policy_matches_decision_table() -> None:
    text = (ROOT / ".claude/agents/pipa-agent.md").read_text(encoding="utf-8")
    protocol = (ROOT / "docs/agent-protocol.md").read_text(encoding="utf-8")

    assert '| "의견서", "메모", "검토보고서" | opinion/memo | md unless DOCX requested | yes | yes | up to 5 laws |' in protocol
    assert '| "DOCX", "워드" | document | docx + md copy | yes | yes | up to 5 laws |' in protocol
    assert "docs/agent-protocol.md`의 Request Decision Table" in text
    assert "`comparison`, `opinion/memo`, `document`: 최대 5개 법령" in text
    assert "질문당 총 MCP 예산 15회가 하드캡" in text
    assert "최대 2개 법령, 2 API 호출/질문" not in text


def test_shared_agent_protocol_is_referenced_by_execution_docs() -> None:
    protocol = (ROOT / "docs/agent-protocol.md").read_text(encoding="utf-8")
    assert "## Request Decision Table" in protocol
    assert "## Source Grade" in protocol
    assert "## Verification Status" in protocol
    assert "## Fact-Checker Responsibilities" in protocol
    assert "## Citation-Auditor Responsibilities" in protocol

    paths = [
        "CLAUDE.md",
        ".claude/agents/pipa-agent.md",
        ".claude/agents/fact-checker/AGENT.md",
        ".claude/skills/legal-opinion-formatter/SKILL.md",
        ".claude/skills/pipa-citation-audit/SKILL.md",
    ]
    for path in paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "docs/agent-protocol.md" in text, path
        assert "AGENTS.md" in text, path

    assert "## Source Grade 체계" not in (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "### Source Grade 체계" not in (ROOT / ".claude/agents/pipa-agent.md").read_text(encoding="utf-8")
    assert "| Signal | request_type | Output |" not in (ROOT / ".claude/agents/pipa-agent.md").read_text(encoding="utf-8")
