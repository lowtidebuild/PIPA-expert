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
        ".claude/agents/fact-checker.md",
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


def test_fact_checker_has_convention_entrypoint_and_canonical_protocol() -> None:
    entrypoint = (ROOT / ".claude/agents/fact-checker.md").read_text(encoding="utf-8")
    canonical = (ROOT / ".claude/agents/fact-checker/AGENT.md").read_text(encoding="utf-8")
    pipa_agent = (ROOT / ".claude/agents/pipa-agent.md").read_text(encoding="utf-8")
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    assert ".claude/agents/<name>.md" in entrypoint
    assert ".claude/agents/fact-checker/AGENT.md" in entrypoint
    assert "Do not summarize from this wrapper alone" in entrypoint
    assert ".claude/agents/fact-checker.md" in pipa_agent
    assert ".claude/agents/fact-checker.md" in claude
    assert "## 검증 항목" in canonical


def test_release_notes_policy_uses_github_releases_only() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    policy = (ROOT / "docs/publishing-policy.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_ko = (ROOT / "README.ko.md").read_text(encoding="utf-8")

    assert "docs/releases/" in gitignore
    assert "docs/RELEASE-*.md" in gitignore
    assert "GitHub Releases" in policy
    assert "docs/releases/**" in policy
    assert "https://github.com/lowtidebuild/PIPA-expert/releases" in readme
    assert "https://github.com/lowtidebuild/PIPA-expert/releases" in readme_ko
    assert "docs/releases/v1.0.0.md" not in readme
    assert "docs/releases/v1.0.0.md" not in readme_ko


def test_compact_legal_writing_guide_is_default_reference() -> None:
    compact = ROOT / "legal-writing-formatting-guide.compact.md"
    full = ROOT / "legal-writing-formatting-guide.md"
    assert compact.exists()
    assert compact.stat().st_size < full.stat().st_size

    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    formatter = (ROOT / ".claude/skills/legal-opinion-formatter/SKILL.md").read_text(encoding="utf-8")
    assert "legal-writing-formatting-guide.compact.md" in claude
    assert "legal-writing-formatting-guide.compact.md" in formatter
    assert "professional DOCX tuning" in formatter


def test_preflight_docs_distinguish_dev_warning_from_release_gate() -> None:
    preflight = (ROOT / "scripts/preflight.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_ko = (ROOT / "README.ko.md").read_text(encoding="utf-8")
    policy = (ROOT / "docs/publishing-policy.md").read_text(encoding="utf-8")
    policy_flat = " ".join(policy.split())

    assert "python3 -m pip check" in preflight
    assert "release blocking" in preflight
    assert "strict security audit must pass" in preflight
    assert "Run the full preflight before pushing" in readme
    assert "push 전에는 전체 preflight를 실행" in readme_ko
    assert "strict security audit is release blocking" in policy_flat
