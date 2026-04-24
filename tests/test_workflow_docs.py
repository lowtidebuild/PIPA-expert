from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pipa_agent_freshness_policy_matches_decision_table() -> None:
    text = (ROOT / ".claude/agents/pipa-agent.md").read_text(encoding="utf-8")

    assert '| "의견서", "메모", "검토보고서" | opinion/memo | md unless DOCX requested | yes | yes | up to 5 laws |' in text
    assert '| "DOCX", "워드" | document | docx + md copy | yes | yes | up to 5 laws |' in text
    assert "`comparison`, `opinion/memo`, `document`: 최대 5개 법령" in text
    assert "질문당 총 MCP 예산 15회가 하드캡" in text
    assert "최대 2개 법령, 2 API 호출/질문" not in text
