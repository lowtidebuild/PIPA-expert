from __future__ import annotations

from scripts.lib.citations import extract_citations, resolve_citation


def test_resolve_citation_keeps_law_context_for_pipa() -> None:
    ref = resolve_citation("개인정보 보호법 제15조 제1항 제2호에 따른 동의 요건")

    assert ref is not None
    assert ref.law_name == "개인정보 보호법"
    assert ref.law_id == "011357"
    assert ref.article == "제15조"
    assert ref.paragraph == "제1항"
    assert ref.item == "제2호"
    assert ref.source_path == "library/grade-a/pipa/art15.md"
    assert ref.confidence == "high"


def test_same_article_number_resolves_to_different_laws() -> None:
    pipa = resolve_citation("개인정보 보호법 제15조")
    credit = resolve_citation("신용정보법 제15조")

    assert pipa is not None
    assert credit is not None
    assert pipa.source_path == "library/grade-a/pipa/art15.md"
    assert credit.source_path == "library/grade-a/credit-info-act/art15.md"
    assert pipa.law_name != credit.law_name


def test_branch_article_resolution() -> None:
    ref = resolve_citation("개인정보보호법 제7조의2는 보호위원회의 구성을 정한다.")

    assert ref is not None
    assert ref.article == "제7조의2"
    assert ref.source_path == "library/grade-a/pipa/art7-2.md"


def test_extract_citations_carries_law_context_forward() -> None:
    refs = extract_citations("개인정보 보호법 제15조와 제17조를 함께 검토한다.")

    assert [ref.article for ref in refs] == ["제15조", "제17조"]
    assert [ref.law_name for ref in refs] == ["개인정보 보호법", "개인정보 보호법"]
    assert refs[0].confidence == "high"
    assert refs[1].confidence == "high"


def test_unqualified_article_is_low_confidence() -> None:
    ref = resolve_citation("제15조를 검토한다.")

    assert ref is not None
    assert ref.confidence == "low"
    assert ref.law_name is None
    assert ref.source_path is None
