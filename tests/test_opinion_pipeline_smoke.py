from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

from docx import Document

from scripts.docx_citation_appendix import append_citation_audit_log, inject_unverified_tags
from scripts.lib.audit_status import write_json
from scripts.lib.mcp_budget import record_call
from scripts.lib.workflow_routing import classify_request
from scripts.render_audit_append import render_audit_append
from scripts.validate_opinion_artifact import validate_artifact


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_json(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_opinion_pipeline_smoke_markdown_docx_and_fallback(tmp_path) -> None:
    request = (FIXTURES / "opinion_request.txt").read_text(encoding="utf-8")
    decision = classify_request(request)

    assert decision.request_type == "opinion/memo"
    assert decision.requires_fact_check is True
    assert decision.requires_citation_audit is True
    assert decision.mcp_freshness_limit == 5

    budget_path = tmp_path / "mcp-budget.json"
    mcp_fixture = _load_json("mcp_freshness_unavailable.json")
    budget_result = record_call(
        budget_path,
        tool=mcp_fixture["tool"],
        purpose=mcp_fixture["purpose"],
        query=mcp_fixture["query"],
        limit=15,
        session_id="opinion-pipeline-smoke",
    )
    assert budget_result.allowed is True
    assert mcp_fixture["marker"] == "[MCP UNAVAILABLE]"
    assert mcp_fixture["fallback"] == "local_kb"

    compact = _load_json("compact_index_candidate.json")
    assert compact["laws"][0]["articles"][0][2] == "art15.md"

    factcheck = _load_json("factcheck_result_complete.json")
    assert factcheck["status"] == "complete"
    assert all(claim["result"] == "supported" for claim in factcheck["checked_claims"])

    draft = (FIXTURES / "opinion_minimal.md").read_text(encoding="utf-8")
    aggregated = _load_json("citation_audit_aggregated.json")
    claim = aggregated["aggregated"][0]["claim"]
    span = claim["sentence_span"]
    assert draft[span["start"] : span["end"]] == claim["text"]

    audited_md, audit_status = render_audit_append(draft, aggregated)
    audited_path = tmp_path / "opinion.audited.md"
    status_path = tmp_path / "audit_status.json"
    audited_path.write_text(audited_md, encoding="utf-8")
    write_json(status_path, audit_status)

    assert "## 부록: 검증 로그 (Citation Audit Log)" in audited_md
    assert audit_status["status"] == "complete"
    assert validate_artifact(audited_path, require_audit=True, audit_status_path=status_path).ok is True

    placeholder_path = tmp_path / "opinion.placeholder.md"
    placeholder_path.write_text(audited_md + "\n[수신인 이름]\n", encoding="utf-8")
    placeholder_result = validate_artifact(placeholder_path, require_audit=True, audit_status_path=status_path)
    assert placeholder_result.ok is False
    assert any(issue.code == "placeholder" for issue in placeholder_result.issues)

    injected = inject_unverified_tags(draft, aggregated, return_result=True)
    doc = Document()
    for block in injected.body_md.split("\n\n"):
        doc.add_paragraph(block.strip())
    append_citation_audit_log(doc, aggregated, audit_status=injected)

    docx_path = tmp_path / "opinion.docx"
    doc.save(docx_path)
    assert validate_artifact(docx_path, require_audit=True).ok is True
    xml = ZipFile(docx_path).read("word/document.xml").decode("utf-8")
    assert "Citation Audit Log" in xml
    assert "맑은 고딕" in xml
