#!/usr/bin/env python3
"""Build compact index projections for agent context efficiency."""

from __future__ import annotations

import argparse
from collections import OrderedDict
import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_ROOT / "index" / "article-index.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "index" / "article-index.compact.json"


def build_compact_article_index(source_path: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    articles = source.get("articles", [])
    laws: OrderedDict[str, dict[str, Any]] = OrderedDict()
    count = 0
    for item in articles:
        if not isinstance(item, dict):
            continue
        law = str(item.get("law", "")).strip()
        path = str(item.get("path", "")).strip()
        if not law or not path:
            continue
        directory, filename = path.rsplit("/", 1)
        law_entry = laws.setdefault(law, {"law": law, "prefix": f"{directory}/", "articles": []})
        law_entry["articles"].append(_compact_article(item, filename))
        count += 1
    return {
        "type": "compact_article_index",
        "generated_from": "index/article-index.json",
        "count": count,
        "laws": list(laws.values()),
    }


def _compact_article(item: dict[str, Any], filename: str) -> list[Any]:
    article = str(item.get("article", "")).strip()
    title = str(item.get("title", "")).strip()
    return [article, title, filename, _keywords(article, title)]


def _keywords(article: str, title: str) -> list[str]:
    raw = [article, f"제{article}조", title]
    raw.extend(re.findall(r"[가-힣A-Za-z0-9]{2,}", title))
    raw.extend(token[:-1] for token in list(raw) if token.endswith("의") and len(token) > 2)
    seen: set[str] = set()
    keywords: list[str] = []
    for value in raw:
        value = value.strip()
        if value and value not in seen:
            seen.add(value)
            keywords.append(value)
    return keywords


def write_compact_index(output_path: Path = DEFAULT_OUTPUT) -> None:
    compact = build_compact_article_index()
    output_path.write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def check_compact_index(output_path: Path = DEFAULT_OUTPUT) -> bool:
    expected = json.dumps(build_compact_article_index(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if not output_path.exists():
        print(f"missing compact index: {output_path}", file=sys.stderr)
        return False
    actual = output_path.read_text(encoding="utf-8")
    if actual != expected:
        print(f"compact index is stale: {output_path}", file=sys.stderr)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output compact index path.")
    parser.add_argument("--check", action="store_true", help="Check that the compact index is up to date.")
    args = parser.parse_args(argv)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    if args.check:
        return 0 if check_compact_index(output_path) else 1
    write_compact_index(output_path)
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
