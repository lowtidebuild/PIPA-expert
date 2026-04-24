from __future__ import annotations

from scripts.build_compact_index import build_compact_article_index


def test_build_compact_article_index_preserves_count_and_paths() -> None:
    compact = build_compact_article_index()

    assert compact["type"] == "compact_article_index"
    assert compact["count"] == 929
    assert sum(len(law["articles"]) for law in compact["laws"]) == 929
    first_law = compact["laws"][0]
    assert {"law", "prefix", "articles"} <= set(first_law)
    assert first_law["prefix"].startswith("library/grade-a/")
    assert len(first_law["articles"][0]) == 4


def test_compact_article_index_contains_search_keywords() -> None:
    compact = build_compact_article_index()
    pipa = next(law for law in compact["laws"] if law["law"] == "개인정보 보호법")
    pipa_15 = next(item for item in pipa["articles"] if item[2] == "art15.md")

    assert pipa["prefix"] == "library/grade-a/pipa/"
    assert pipa_15[0] == "15"
    assert "제15조" in pipa_15[3]
    assert "개인정보" in pipa_15[3]
