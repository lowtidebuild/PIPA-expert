from __future__ import annotations

from scripts.security_audit import audit_findings


def test_security_audit_default_treats_repo_default_paths_as_warnings(monkeypatch) -> None:
    monkeypatch.delenv("PIPA_OUTPUT_DIR", raising=False)
    monkeypatch.delenv("PIPA_INBOX_DIR", raising=False)
    monkeypatch.delenv("PIPA_PRIVATE_DIR", raising=False)

    findings = audit_findings(strict=False)

    assert any(finding.level == "WARN" for finding in findings)
    assert not any("points inside repo" in finding.message and finding.level == "FAIL" for finding in findings)


def test_security_audit_strict_treats_repo_default_paths_as_failures(monkeypatch) -> None:
    monkeypatch.delenv("PIPA_OUTPUT_DIR", raising=False)
    monkeypatch.delenv("PIPA_INBOX_DIR", raising=False)
    monkeypatch.delenv("PIPA_PRIVATE_DIR", raising=False)

    findings = audit_findings(strict=True)

    assert any("points inside repo" in finding.message and finding.level == "FAIL" for finding in findings)
