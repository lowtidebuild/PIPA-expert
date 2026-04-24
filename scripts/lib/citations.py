"""Project-local Korean legal citation resolver.

The vendored citation-auditor parser is useful, but PIPA workflow should not
depend on its internal API. This module resolves statute citations against the
local article index and keeps the law context attached to each article number.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from scripts.lib.paths import repo_root


KNOWN_LAW_IDS = {
    "개인정보 보호법": "011357",
    "개인정보보호법": "011357",
}

MANUAL_ALIASES = {
    "개보법": "개인정보 보호법",
    "개인정보보호법": "개인정보 보호법",
    "개인정보 보호법": "개인정보 보호법",
    "개인정보보호법 시행령": "개인정보 보호법 시행령",
    "개인정보 보호법 시행령": "개인정보 보호법 시행령",
    "정보통신망법": "정보통신망 이용촉진 및 정보보호 등에 관한 법률",
    "정보통신망법 시행령": "정보통신망 이용촉진 및 정보보호 등에 관한 법률 시행령",
    "신용정보법": "신용정보의 이용 및 보호에 관한 법률",
    "신용정보법 시행령": "신용정보의 이용 및 보호에 관한 법률 시행령",
    "위치정보법": "위치정보의 보호 및 이용 등에 관한 법률",
    "위치정보법 시행령": "위치정보의 보호 및 이용 등에 관한 법률 시행령",
    "전자정부법": "전자정부법",
}

ARTICLE_RE = re.compile(
    r"제\s*(?P<main>\d+)\s*조"
    r"(?:\s*의\s*(?P<sub>\d+))?"
    r"(?:\s*제\s*(?P<paragraph>\d+)\s*항)?"
    r"(?:\s*제\s*(?P<item>\d+)\s*호)?"
)


@dataclass(frozen=True)
class CitationRef:
    kind: str
    raw: str
    law_name: str | None
    law_id: str | None
    law_key: str | None
    article: str | None
    paragraph: str | None
    item: str | None
    source_path: str | None
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_citation(text: str) -> CitationRef | None:
    refs = extract_citations(text)
    return refs[0] if refs else None


def extract_citations(text: str) -> list[CitationRef]:
    registry = _registry()
    refs: list[CitationRef] = []
    current_law: str | None = None

    for match in ARTICLE_RE.finditer(text):
        prefix = text[: match.start()]
        resolved_law = _extract_law_name(prefix, registry.aliases)
        if resolved_law:
            current_law = resolved_law
            confidence = "high"
        elif current_law:
            resolved_law = current_law
            confidence = "medium"
        else:
            confidence = "low"

        article = _format_article_key(match.group("main"), match.group("sub"))
        entry = registry.find_article(resolved_law, article) if resolved_law else None
        law_name = resolved_law
        raw = _raw_with_law_context(text, match, resolved_law)
        refs.append(
            CitationRef(
                kind="statute",
                raw=raw,
                law_name=law_name,
                law_id=KNOWN_LAW_IDS.get(law_name or ""),
                law_key=_law_key(entry),
                article=_format_article_label(match.group("main"), match.group("sub")),
                paragraph=_format_unit("항", match.group("paragraph")),
                item=_format_unit("호", match.group("item")),
                source_path=(entry or {}).get("path"),
                confidence=confidence if entry else "low",
            )
        )
    return refs


@dataclass(frozen=True)
class _ArticleRegistry:
    articles: list[dict[str, Any]]
    aliases: dict[str, str]

    def find_article(self, law_name: str | None, article: str) -> dict[str, Any] | None:
        candidates = self.articles
        if law_name:
            candidates = [item for item in candidates if item.get("law") == law_name]
        for item in candidates:
            if str(item.get("article")) == article:
                return item
        return None


@lru_cache(maxsize=1)
def _registry() -> _ArticleRegistry:
    index_path = repo_root() / "index" / "article-index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    articles = data.get("articles", [])
    if not isinstance(articles, list):
        articles = []

    aliases = dict(MANUAL_ALIASES)
    for item in articles:
        law = str(item.get("law", "")).strip()
        if law:
            aliases.setdefault(law, law)
            aliases.setdefault(law.replace(" ", ""), law)
    return _ArticleRegistry(articles=articles, aliases=aliases)


def _extract_law_name(prefix_text: str, aliases: dict[str, str]) -> str | None:
    trimmed = prefix_text[-80:]
    best: tuple[int, int, str] | None = None
    for alias, canonical in aliases.items():
        for match in re.finditer(re.escape(alias), trimmed):
            candidate = (match.start(), len(alias), canonical)
            if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] > best[1]):
                best = candidate
    return best[2] if best else None


def _raw_with_law_context(text: str, match: re.Match[str], law_name: str | None) -> str:
    article_text = match.group(0)
    if law_name and law_name not in article_text:
        return f"{law_name} {article_text}"
    return article_text


def _format_article_key(main: str, sub: str | None) -> str:
    if sub:
        return f"{int(main)}의{int(sub)}"
    return str(int(main))


def _format_article_label(main: str, sub: str | None) -> str:
    if sub:
        return f"제{int(main)}조의{int(sub)}"
    return f"제{int(main)}조"


def _format_unit(suffix: str, value: str | None) -> str | None:
    if value is None:
        return None
    return f"제{int(value)}{suffix}"


def _law_key(entry: dict[str, Any] | None) -> str | None:
    if not entry:
        return None
    raw_id = str(entry.get("id", ""))
    marker = "-art"
    if marker in raw_id:
        return raw_id.split(marker, 1)[0]
    path = str(entry.get("path", ""))
    parts = Path(path).parts
    if len(parts) >= 3:
        return parts[2]
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve Korean statute citations against index/article-index.json.")
    parser.add_argument("text", nargs="+", help="Text containing Korean legal citations.")
    args = parser.parse_args(argv)
    refs = [ref.to_dict() for ref in extract_citations(" ".join(args.text))]
    print(json.dumps(refs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
