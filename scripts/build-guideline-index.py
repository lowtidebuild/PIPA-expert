#!/usr/bin/env python3
"""Build guideline-index.json from processed markdown files."""

import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
GUIDELINES_DIR = PROJECT_ROOT / "library" / "grade-a" / "pipc-guidelines"
INDEX_DIR = PROJECT_ROOT / "index"


def parse_frontmatter(md_path: Path) -> dict:
    """Extract YAML frontmatter as dict (simple parser, no PyYAML needed)."""
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    end = text.index("---", 3)
    fm_text = text[3:end]

    meta = {}
    current_key = None
    current_list = None

    for line in fm_text.strip().split("\n"):
        if line.startswith("#") or not line.strip():
            continue

        list_match = re.match(r'\s+-\s+"(.+)"', line)
        if list_match and current_key:
            if current_list is None:
                current_list = []
            current_list.append(list_match.group(1))
            meta[current_key] = current_list
            continue
        else:
            current_list = None

        kv_match = re.match(r'(\w+):\s*"?([^"]*)"?\s*$', line)
        if kv_match:
            current_key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val:
                meta[current_key] = val
            else:
                current_list = []
                meta[current_key] = current_list

    return meta


def build_index():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    guidelines = []
    for md_file in sorted(GUIDELINES_DIR.glob("*.md")):
        if md_file.name.startswith("_"):
            continue

        meta = parse_frontmatter(md_file)
        if not meta:
            continue

        rel_path = md_file.relative_to(PROJECT_ROOT)

        entry = {
            "id": f"pipc-guideline-{meta.get('guideline_id', 'unknown')}",
            "guideline_id": meta.get("guideline_id", ""),
            "slug": meta.get("slug", ""),
            "title_kr": meta.get("title_kr", ""),
            "title_en": meta.get("title_en", ""),
            "source_grade": meta.get("source_grade", "A"),
            "publisher": meta.get("publisher", ""),
            "path": str(rel_path),
            "keywords": meta.get("keywords", []),
            "topics": meta.get("topics", []),
            "char_count": int(meta.get("char_count", 0)),
            "retrieved_at": meta.get("retrieved_at", ""),
        }
        guidelines.append(entry)

    index = {
        "type": "guideline_index",
        "collection": "PIPC Official Guidelines",
        "source_grade": "A",
        "count": len(guidelines),
        "generated_at": datetime.now().isoformat(),
        "guidelines": guidelines,
    }

    out_path = INDEX_DIR / "guideline-index.json"
    out_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Index written: {out_path} ({len(guidelines)} entries)")

    reg_path = INDEX_DIR / "source-registry.json"
    if reg_path.exists():
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
    else:
        registry = {"type": "source_registry", "sources": {"grade-a": {}, "grade-b": {}, "grade-c": {}}}

    registry["generated_at"] = datetime.now().isoformat()
    registry["sources"].setdefault("grade-a", {})
    registry["sources"].setdefault("grade-b", {})
    registry["sources"].setdefault("grade-c", {})
    registry["sources"]["grade-a"]["pipc-guidelines"] = {
        "status": "complete",
        "count": len(guidelines),
        "target": len(guidelines),
        "collection": "PIPC Official Guidelines",
        "publisher": "개인정보보호위원회 (PIPC)",
        "retrieved_at": datetime.now().isoformat(),
        "total_chars": sum(g["char_count"] for g in guidelines),
    }
    registry["sources"]["grade-b"].setdefault("pipc-decisions", {"status": "pending", "note": "PIPC 처분례 — 추후 수집"})
    registry["sources"]["grade-b"].setdefault("court-precedents", {"status": "pending", "note": "대법원 판례 — 추후 수집"})
    registry["sources"]["grade-c"].setdefault("law-firm", {"status": "pending", "note": "로펌 해설/뉴스레터 — 추후 수집"})
    registry["sources"]["grade-c"].setdefault("academic", {"status": "pending", "note": "학술 논문 — 추후 수집"})

    reg_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registry written: {reg_path}")


if __name__ == "__main__":
    build_index()
