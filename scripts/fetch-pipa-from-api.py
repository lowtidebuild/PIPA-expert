#!/usr/bin/env python3
"""
PIPA RAG: Fetch PIPA legislation from law.go.kr Open API.

Usage:
    python3 scripts/fetch-pipa-from-api.py --oc YOUR_EMAIL_ID

This script:
1. Searches for 개인정보보호법 (PIPA) and its enforcement decree
2. Fetches full law text (all articles)
3. Fetches each article individually via 조항호목 API
4. Creates structured markdown files with frontmatter
5. Builds hierarchy and cross-reference indexes

Requires: open.law.go.kr API registration (OC = email ID, IP registered)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_ROOT / "library" / "grade-a"

BASE_URL = "http://www.law.go.kr/DRF"

# Known law IDs (fallback if search fails)
KNOWN_LAWS = {
    # 개인정보 보호법 체계
    "개인정보보호법": {"search_query": "개인정보보호법", "target_dir": "pipa"},
    "개인정보보호법 시행령": {"search_query": "개인정보 보호법 시행령", "target_dir": "pipa-enforcement-decree"},
    "개인정보보호법 시행규칙": {"search_query": "개인정보 보호법 시행규칙", "target_dir": "pipa-enforcement-rule"},
    # 정보통신망법 체계
    "정보통신망법": {"search_query": "정보통신망 이용촉진 및 정보보호 등에 관한 법률", "target_dir": "network-act"},
    "정보통신망법 시행령": {"search_query": "정보통신망 이용촉진 및 정보보호 등에 관한 법률 시행령", "target_dir": "network-act-enforcement-decree"},
    "정보통신망법 시행규칙": {"search_query": "정보통신망 이용촉진 및 정보보호 등에 관한 법률 시행규칙", "target_dir": "network-act-enforcement-rule"},
    # 신용정보법 체계
    "신용정보법": {"search_query": "신용정보의 이용 및 보호에 관한 법률", "target_dir": "credit-info-act"},
    "신용정보법 시행령": {"search_query": "신용정보의 이용 및 보호에 관한 법률 시행령", "target_dir": "credit-info-act-enforcement-decree"},
    # 위치정보법 체계
    "위치정보법": {"search_query": "위치정보의 보호 및 이용 등에 관한 법률", "target_dir": "location-info-act"},
    "위치정보법 시행령": {"search_query": "위치정보의 보호 및 이용 등에 관한 법률 시행령", "target_dir": "location-info-act-enforcement-decree"},
    # 전자정부법 (개인정보 관련 조항 포함)
    "전자정부법": {"search_query": "전자정부법", "target_dir": "e-government-act"},
}
TARGET_DIR_TO_LAW_NAME = {config["target_dir"]: law_name for law_name, config in KNOWN_LAWS.items()}


def api_request(url: str, max_retries: int = 3) -> str:
    """Make API request with retry logic."""
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "PIPA-RAG-Builder/1.0")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries}: {e}")
                time.sleep(2)
            else:
                raise


def search_law(oc: str, query: str) -> dict | None:
    """Search for a law by name, return law info dict."""
    encoded_query = urllib.parse.quote(query)
    url = f"{BASE_URL}/lawSearch.do?OC={oc}&target=law&type=JSON&query={encoded_query}&display=5"

    print(f"  Searching: {query}")
    raw = api_request(url)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Sometimes returns XML error
        print(f"  ERROR: Non-JSON response: {raw[:200]}")
        return None

    # Handle different response structures
    laws = data.get("LawSearch", {}).get("law", [])
    if isinstance(laws, dict):
        laws = [laws]

    for law in laws:
        name = law.get("법령명한글", "")
        if query.replace(" ", "") in name.replace(" ", ""):
            print(f"  Found: {name} (ID: {law.get('법령ID')}, MST: {law.get('법령일련번호')})")
            return law

    print(f"  WARNING: '{query}' not found in search results")
    return None


def fetch_law_full_text(oc: str, mst: str) -> str:
    """Fetch full law XML text."""
    url = f"{BASE_URL}/lawService.do?OC={oc}&target=law&type=XML&MST={mst}"
    print(f"  Fetching full text (MST={mst})...")
    return api_request(url)


def fetch_article(oc: str, law_id: str, jo_num: str) -> str:
    """Fetch a specific article via 조항호목 API."""
    url = f"{BASE_URL}/lawService.do?OC={oc}&target=lawjosub&type=JSON&ID={law_id}&JO={jo_num}"
    return api_request(url)


def parse_full_law_xml(xml_text: str) -> dict:
    """Parse full law XML to extract metadata and article list."""
    root = ET.fromstring(xml_text)

    law_info = {
        "법령명한글": _find_text(root, ".//법령명_한글"),
        "법령ID": _find_text(root, ".//법령ID"),
        "법령키": _find_text(root, ".//법령키"),
        "공포일자": _find_text(root, ".//공포일자"),
        "공포번호": _find_text(root, ".//공포번호"),
        "시행일자": _find_text(root, ".//시행일자"),
        "소관부처": _find_text(root, ".//소관부처"),
        "법종구분": _find_text(root, ".//법종구분명"),
        "제개정구분": _find_text(root, ".//제개정구분명"),
    }

    # Extract articles (조문)
    articles = []
    for jo in root.findall(".//조문단위"):
        article = {
            "조문번호": _find_text(jo, "조문번호"),
            "조문가지번호": _find_text(jo, "조문가지번호"),
            "조문여부": _find_text(jo, "조문여부"),
            "조문제목": _find_text(jo, "조문제목"),
            "조문시행일자": _find_text(jo, "조문시행일자"),
            "조문내용": _find_text(jo, "조문내용"),
            "조문변경여부": _find_text(jo, "조문변경여부"),
        }

        # Extract 항 (paragraphs)
        paragraphs = []
        for hang in jo.findall(".//항"):
            p = {
                "항번호": _find_text(hang, "항번호"),
                "항내용": _find_text(hang, "항내용"),
            }
            # Extract 호 (subparagraphs)
            hos = []
            for ho in hang.findall(".//호"):
                h = {
                    "호번호": _find_text(ho, "호번호"),
                    "호내용": _find_text(ho, "호내용"),
                }
                # Extract 목 (items)
                moks = []
                for mok in ho.findall(".//목"):
                    moks.append({
                        "목번호": _find_text(mok, "목번호"),
                        "목내용": _find_text(mok, "목내용"),
                    })
                if moks:
                    h["목"] = moks
                hos.append(h)
            if hos:
                p["호"] = hos
            paragraphs.append(p)
        if paragraphs:
            article["항"] = paragraphs

        articles.append(article)

    # Extract 편장절관 (chapters/sections)
    chapters = []
    for ch in root.findall(".//편장절관단위"):
        chapters.append({
            "편장절관키": _find_text(ch, "편장절관키"),
            "편장절관명": _find_text(ch, "편장절관명"),
        })

    law_info["articles"] = articles
    law_info["chapters"] = chapters

    return law_info


def _find_text(element, path: str) -> str:
    """Safely find text in XML element."""
    el = element.find(path)
    return el.text.strip() if el is not None and el.text else ""


def extract_cross_references(text: str) -> list[str]:
    """Extract cross-references from article text (e.g., '제15조', '시행령 제17조')."""
    refs = []
    seen = set()
    # Pattern: 제N조, 제N조의N, 제N조제N항
    pattern = r"제(\d+)조(?:의(\d+))?(?:제(\d+)항)?"
    for match in re.finditer(pattern, text):
        ref = f"제{match.group(1)}조"
        if match.group(2):
            ref += f"의{match.group(2)}"
        if match.group(3):
            ref += f"제{match.group(3)}항"
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)
    return refs


def extract_keywords(title: str, content: str) -> list[str]:
    """Extract keywords from article title and content."""
    keywords = []
    if title:
        # Use title words as primary keywords
        keywords.extend(re.findall(r"[가-힣]{2,}", title))

    # Common PIPA topic keywords
    topic_map = {
        "수집": "수집", "이용": "이용", "제공": "제공", "파기": "파기",
        "동의": "동의", "정보주체": "정보주체", "영향평가": "영향평가",
        "안전조치": "안전조치", "유출": "유출", "통지": "통지",
        "가명": "가명정보", "익명": "익명정보", "민감정보": "민감정보",
        "고유식별": "고유식별정보", "영상정보": "영상정보",
        "국외이전": "국외이전", "손해배상": "손해배상", "과징금": "과징금",
        "처벌": "벌칙", "전송요구": "전송요구권",
    }
    for keyword, topic in topic_map.items():
        if keyword in content:
            keywords.append(topic)

    return list(set(keywords))[:10]


def _normalize_numeric_token(num_str: str) -> str:
    """Normalize a numeric token from the API into a plain integer string."""
    if not num_str:
        return ""

    # Handle circled numbers (①②③...)
    circled = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
    if num_str in circled:
        return str(circled.index(num_str) + 1)

    # Handle plain digits
    digits_only = re.sub(r"[^\d]", "", num_str)
    if not digits_only:
        return num_str

    return str(int(digits_only))


def format_article_number(num_str: str, branch_str: str = "") -> str:
    """Format article number: ('10', '2') -> '10의2', legacy '001002' -> '10의2'."""
    if branch_str:
        main = _normalize_numeric_token(num_str)
        branch = _normalize_numeric_token(branch_str)
        if main and branch and branch != "0":
            return f"{main}의{branch}"
        if main:
            return main

    digits_only = re.sub(r"[^\d]", "", num_str or "")
    if len(digits_only) >= 6:
        num = str(int(digits_only[:4]))
        sub = str(int(digits_only[4:6]))
        if sub != "0":
            return f"{num}의{sub}"
        return num

    return _normalize_numeric_token(num_str)


def format_article_citation(num_str: str, branch_str: str = "") -> str:
    """Format a legal article citation label: ('10', '2') -> '제10조의2'."""
    article_number = format_article_number(num_str, branch_str)
    if "의" in article_number:
        main, sub = article_number.split("의", 1)
        return f"제{main}조의{sub}"
    return f"제{article_number}조"


def format_article_slug(num_str: str, branch_str: str = "") -> str:
    """Format the filename slug for an article."""
    return f"art{format_article_number(num_str, branch_str).replace('의', '-')}"


def collect_article_text(article: dict) -> str:
    """Collect article text for keyword and cross-reference extraction."""
    parts = [article.get("조문제목", ""), article.get("조문내용", "")]
    for paragraph in article.get("항", []):
        parts.append(paragraph.get("항내용", ""))
        for ho in paragraph.get("호", []):
            parts.append(ho.get("호내용", ""))
            for mok in ho.get("목", []):
                parts.append(mok.get("목내용", ""))
    return " ".join(part for part in parts if part)


def build_chapter_map(chapters: list) -> dict:
    """Build a map from article number ranges to chapter names."""
    # This is a simplified version — the full law XML has 편장절관 structure
    # We'll use the chapter data from the API
    return {ch["편장절관키"]: ch["편장절관명"] for ch in chapters}


def create_article_md(law_info: dict, article: dict, law_slug: str) -> str:
    """Create markdown content for a single article."""
    art_num = format_article_number(article["조문번호"], article.get("조문가지번호", ""))
    art_label = format_article_citation(article["조문번호"], article.get("조문가지번호", ""))
    title = article.get("조문제목", "")
    content = article.get("조문내용", "")
    effective_date = article.get("조문시행일자", law_info.get("시행일자", ""))

    # Extract cross-references and keywords
    full_text = collect_article_text(article)
    cross_refs = [ref for ref in extract_cross_references(full_text) if ref != art_label]
    keywords = extract_keywords(title, full_text)

    # Build frontmatter
    fm = f"""---
# === 식별 정보 ===
law: "{law_info['법령명한글']}"
law_id: "{law_info.get('법령ID', '')}"
law_mst: "{law_info.get('법령키', '')}"
article: {art_num.split('의')[0] if '의' in art_num else art_num}
article_sub: {art_num.split('의')[1] if '의' in art_num else 0}
article_title: "{title}"
paragraph: null

# === 소스 정보 ===
source_grade: "A"
source_url: "https://law.go.kr/법령/{urllib.parse.quote(law_info['법령명한글'])}/{urllib.parse.quote(art_label)}"
effective_date: "{effective_date}"
last_amended: "{law_info.get('공포일자', '')}"
retrieved_at: "{datetime.now().strftime('%Y-%m-%d')}"

# === 관계 정보 ===
cross_references:
{chr(10).join(f'  - "{ref}"' for ref in cross_refs) if cross_refs else '  []'}

# === 검색 메타 ===
keywords:
{chr(10).join(f'  - "{kw}"' for kw in keywords) if keywords else '  []'}
---

"""

    # Build article body
    body = f"## {art_label}"
    if title:
        body += f"({title})"
    body += "\n\n"

    if content and not article.get("항"):
        body += f"{content}\n\n"

    # Add paragraphs
    for p in article.get("항", []):
        p_num = format_article_number(p.get("항번호", ""))
        p_content = p.get("항내용", "")
        if p_content:
            body += f"{p_content}\n"

        # Add subparagraphs (호)
        for h in p.get("호", []):
            h_num = format_article_number(h.get("호번호", ""))
            h_content = h.get("호내용", "")
            if h_content:
                body += f"  {h_content}\n"

            # Add items (목)
            for m in h.get("목", []):
                m_content = m.get("목내용", "")
                if m_content:
                    body += f"    {m_content}\n"

        body += "\n"

    return fm + body


def process_law(oc: str, law_name: str, config: dict):
    """Process a single law: search, fetch, parse, write files."""
    target_dir = SOURCES_DIR / config["target_dir"]
    target_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Search for the law
    print(f"\n{'='*60}")
    print(f"Processing: {law_name}")
    print(f"{'='*60}")

    law_search = search_law(oc, config["search_query"])
    if not law_search:
        print(f"  FAILED: Could not find '{law_name}' via API")
        return False

    mst = law_search.get("법령일련번호", "")
    law_id = law_search.get("법령ID", "")

    if not mst:
        print(f"  FAILED: No MST number for '{law_name}'")
        return False

    # Step 2: Fetch full law text
    time.sleep(1)  # Rate limiting
    xml_text = fetch_law_full_text(oc, mst)

    # Check for error response (actual API errors, not law content containing these words)
    if xml_text.strip().startswith("<OpenAPI_ServiceResponse") or "<errMsg>" in xml_text:
        print(f"  API ERROR: {xml_text[:300]}")
        return False

    # Step 3: Parse XML
    print("  Parsing law structure...")
    try:
        law_info = parse_full_law_xml(xml_text)
    except ET.ParseError as e:
        print(f"  XML PARSE ERROR: {e}")
        # Save raw XML for debugging
        debug_path = target_dir / "_raw_response.xml"
        debug_path.write_text(xml_text, encoding="utf-8")
        print(f"  Saved raw XML to {debug_path}")
        return False

    articles = law_info.get("articles", [])
    print(f"  Found {len(articles)} articles")

    if not articles:
        print("  WARNING: No articles found in response")
        debug_path = target_dir / "_raw_response.xml"
        debug_path.write_text(xml_text, encoding="utf-8")
        print(f"  Saved raw XML to {debug_path}")
        return False

    # Step 4: Write _hierarchy.json
    hierarchy_article_count = sum(1 for a in articles if a.get("조문여부", "") == "조문")
    hierarchy = {
        "law": law_info["법령명한글"],
        "chapters": law_info.get("chapters", []),
        "articles": [
            {
                "number": format_article_number(a["조문번호"], a.get("조문가지번호", "")),
                "title": a.get("조문제목", ""),
                "is_article": a.get("조문여부", "") == "조문",
            }
            for a in articles
        ],
    }
    hier_path = target_dir / "_hierarchy.json"
    hier_path.write_text(json.dumps(hierarchy, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote {hier_path.name}")

    # Step 5: Write individual article files
    cross_refs_all = []
    article_count = 0

    for article in articles:
        # Skip non-article entries (편, 장, 절 headings marked as "전문")
        if article.get("조문여부") != "조문":
            continue

        art_num = format_article_number(article["조문번호"], article.get("조문가지번호", ""))
        art_label = format_article_citation(article["조문번호"], article.get("조문가지번호", ""))
        slug = format_article_slug(article["조문번호"], article.get("조문가지번호", ""))

        md_content = create_article_md(law_info, article, config["target_dir"])

        filename = f"{slug}.md"
        filepath = target_dir / filename
        filepath.write_text(md_content, encoding="utf-8")
        article_count += 1

        # Collect cross-references
        full_text = collect_article_text(article)
        refs = extract_cross_references(full_text)
        for ref in refs:
            if ref != art_label:  # Skip self-references
                cross_refs_all.append({
                    "from": art_label,
                    "to": ref,
                    "type": "references",
                })

    print(f"  Wrote {article_count} article files")

    # Step 6: Write _meta.json
    meta = {
        "law_name": law_info["법령명한글"],
        "law_id": law_info.get("법령ID", ""),
        "law_mst": law_info.get("법령키", ""),
        "law_type": law_info.get("법종구분", ""),
        "effective_date": law_info.get("시행일자", ""),
        "promulgation_date": law_info.get("공포일자", ""),
        "promulgation_number": law_info.get("공포번호", ""),
        "governing_body": law_info.get("소관부처", ""),
        "amendment_type": law_info.get("제개정구분", ""),
        "article_count": article_count,
        "hierarchy_article_count": hierarchy_article_count,
        "source_grade": "A",
        "retrieved_at": datetime.now().isoformat(),
    }
    meta_path = target_dir / "_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote {meta_path.name}")

    # Step 7: Write _cross-refs.json
    cross_refs = {
        "law": law_info["법령명한글"],
        "cross_references": cross_refs_all,
    }
    xref_path = target_dir / "_cross-refs.json"
    xref_path.write_text(json.dumps(cross_refs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote {xref_path.name} ({len(cross_refs_all)} references)")

    print(f"\n  SUCCESS: {law_name} → {target_dir}")
    print(f"  {article_count} articles, {len(cross_refs_all)} cross-references")
    return True


def update_indexes(oc: str):
    """Update master indexes after processing all laws."""
    index_dir = PROJECT_ROOT / "index"
    index_dir.mkdir(parents=True, exist_ok=True)

    # Build article-index.json from all processed laws
    all_articles = []
    for law_dir in SOURCES_DIR.iterdir():
        if not law_dir.is_dir():
            continue
        for md_file in sorted(law_dir.glob("art*.md")):
            # Quick frontmatter parse
            text = md_file.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue

            meta = {}
            try:
                end = text.index("---", 3)
                fm = text[3:end]
                for line in fm.split("\n"):
                    match = re.match(r'(\w+):\s*"([^"]*)"', line)
                    if match:
                        meta[match.group(1)] = match.group(2)
                    match2 = re.match(r'(\w+):\s*(\d+)', line)
                    if match2 and match2.group(1) not in meta:
                        meta[match2.group(1)] = match2.group(2)
            except ValueError:
                continue

            rel_path = md_file.relative_to(PROJECT_ROOT)
            article_main = meta.get("article", "")
            article_sub = meta.get("article_sub", "0")
            article_label = article_main
            article_id = article_main
            if article_sub not in ("", "0", 0):
                article_label = f"{article_main}의{article_sub}"
                article_id = f"{article_main}-{article_sub}"
            all_articles.append({
                "id": f"{law_dir.name}-art{article_id or 'x'}",
                "law": meta.get("law", ""),
                "article": article_label,
                "article_main": article_main,
                "article_sub": article_sub,
                "title": meta.get("article_title", ""),
                "path": str(rel_path),
                "source_grade": "A",
                "effective_date": meta.get("effective_date", ""),
            })

    # Merge with existing guideline index
    existing_index_path = index_dir / "article-index.json"
    index = {
        "type": "article_index",
        "count": len(all_articles),
        "generated_at": datetime.now().isoformat(),
        "articles": all_articles,
    }
    existing_index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nUpdated article-index.json ({len(all_articles)} articles)")

    # Update source-registry.json
    registry_path = index_dir / "source-registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        registry = {"type": "source_registry", "sources": {"grade-a": {}, "grade-b": {}, "grade-c": {}}}

    for law_dir in SOURCES_DIR.iterdir():
        if not law_dir.is_dir():
            continue
        if law_dir.name == "pipc-guidelines":
            continue
        meta_path = law_dir / "_meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        count = len(list(law_dir.glob("art*.md")))

        hier_path = law_dir / "_hierarchy.json"
        target = count
        if hier_path.exists():
            hierarchy = json.loads(hier_path.read_text(encoding="utf-8"))
            target = sum(1 for article in hierarchy.get("articles", []) if article.get("is_article"))

        if count == 0:
            status = "pending"
        elif target == count:
            status = "complete"
        else:
            status = "partial"

        entry = {
            "status": status,
            "count": count,
            "target": target,
            "law_name": meta.get("law_name", TARGET_DIR_TO_LAW_NAME.get(law_dir.name, "")),
            "retrieved_at": meta.get("retrieved_at", ""),
        }
        if status == "partial":
            entry["note"] = "Branch articles are currently flattened into base article files; re-ingest required."
        elif status == "pending":
            entry["note"] = "Directory exists but no ingested statute files are available yet."

        registry["sources"]["grade-a"][law_dir.name] = entry

    registry["generated_at"] = datetime.now().isoformat()
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Updated source-registry.json")


def main():
    parser = argparse.ArgumentParser(description="Fetch PIPA legislation from law.go.kr API")
    parser.add_argument("--oc", required=True, help="API user code (email ID part)")
    parser.add_argument("--law", choices=list(KNOWN_LAWS.keys()) + ["all"], default="all",
                        help="Which law to fetch (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Only search, don't fetch full text")
    args = parser.parse_args()

    print(f"PIPA RAG — Law Fetcher")
    print(f"OC: {args.oc}")
    print(f"Target: {args.law}")
    print(f"Output: {SOURCES_DIR}")
    print()

    if args.law == "all":
        laws_to_process = KNOWN_LAWS
    else:
        laws_to_process = {args.law: KNOWN_LAWS[args.law]}

    results = {}
    for law_name, config in laws_to_process.items():
        if args.dry_run:
            search_law(args.oc, config["search_query"])
            continue
        success = process_law(args.oc, law_name, config)
        results[law_name] = success
        time.sleep(2)  # Rate limiting between laws

    if not args.dry_run:
        # Update indexes
        update_indexes(args.oc)

        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        for law, success in results.items():
            status = "OK" if success else "FAILED"
            print(f"  {law}: {status}")


if __name__ == "__main__":
    main()
