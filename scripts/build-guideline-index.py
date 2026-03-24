#!/usr/bin/env python3
"""Build guideline-index.json from processed markdown files."""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
GUIDELINES_DIR = PROJECT_ROOT / "sources" / "grade-a" / "pipc-guidelines"
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
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "guidelines": guidelines,
    }

    out_path = INDEX_DIR / "guideline-index.json"
    out_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Index written: {out_path} ({len(guidelines)} entries)")

    # Also build source registry
    registry = {
        "type": "source_registry",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "sources": {
            "grade-a": {
                "pipa": {"status": "pending", "note": "법령 원문 — law.go.kr API로 수집 예정"},
                "pipa-enforcement-decree": {"status": "pending", "note": "시행령 — law.go.kr API로 수집 예정"},
                "pipc-guidelines": {
                    "status": "complete",
                    "count": len(guidelines),
                    "total_chars": sum(g["char_count"] for g in guidelines),
                },
            },
            "grade-b": {
                "pipc-decisions": {"status": "pending", "note": "PIPC 처분례 — 추후 수집"},
                "court-precedents": {"status": "pending", "note": "대법원 판례 — 추후 수집"},
            },
            "grade-c": {
                "academic": {"status": "pending", "note": "학술 논문 — 추후 수집"},
            },
        },
    }

    reg_path = INDEX_DIR / "source-registry.json"
    reg_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registry written: {reg_path}")


if __name__ == "__main__":
    build_index()
