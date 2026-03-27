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
    "개인정보보호법 시행규칙": {
        "search_query": "개인정보 보호법 시행규칙",
        "target_dir": "pipa-enforcement-rule",
        "skip_fetch": True,
        "registry_status": "retired",
        "note": "Repealed statute; excluded from ingest.",
    },
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
    # 온디맨드 확장 후보 (기본 corpus 제외)
    "전기통신사업법": {
        "search_query": "전기통신사업법",
        "target_dir": "telecommunications-business-act",
        "default_enabled": False,
    },
    "자본시장과 금융투자업에 관한 법률": {
        "search_query": "자본시장과 금융투자업에 관한 법률",
        "target_dir": "capital-markets-act",
        "default_enabled": False,
    },
    "채권의 공정한 추심에 관한 법률": {
        "search_query": "채권의 공정한 추심에 관한 법률",
        "target_dir": "fair-debt-collection-act",
        "default_enabled": False,
    },
    "형법": {"search_query": "형법", "target_dir": "criminal-act", "default_enabled": False},
    "여신전문금융업법": {
        "search_query": "여신전문금융업법",
        "target_dir": "specialized-credit-finance-business-act",
        "default_enabled": False,
    },
    "상법": {
        "search_query": "상법",
        "target_dir": "commercial-act",
        "mst": "284143",
        "default_enabled": False,
    },
    "의료법": {"search_query": "의료법", "target_dir": "medical-act", "default_enabled": False},
    "민법": {"search_query": "민법", "target_dir": "civil-act", "default_enabled": False},
}
TARGET_DIR_TO_LAW_NAME = {config["target_dir"]: law_name for law_name, config in KNOWN_LAWS.items()}
TARGET_DIR_TO_CONFIG = {config["target_dir"]: config for config in KNOWN_LAWS.values()}
DEFAULT_ENABLED_TARGET_DIRS = {
    config["target_dir"]
    for config in KNOWN_LAWS.values()
    if config.get("default_enabled", True)
}
DEFAULT_ENABLED_LAWS = {
    law_name: config
    for law_name, config in KNOWN_LAWS.items()
    if config.get("default_enabled", True)
}


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
    url = f"{BASE_URL}/lawSearch.do?OC={oc}&target=law&type=JSON&query={encoded_query}&display=20"

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

    normalized_query = query.replace(" ", "")

    for law in laws:
        name = law.get("법령명한글", "")
        if normalized_query == name.replace(" ", ""):
            print(f"  Found: {name} (ID: {law.get('법령ID')}, MST: {law.get('법령일련번호')})")
            return law

    for law in laws:
        name = law.get("법령명한글", "")
        if len(normalized_query) >= 5 and normalized_query in name.replace(" ", ""):
            print(f"  Found: {name} (ID: {law.get('법령ID')}, MST: {law.get('법령일련번호')})")
            return law

    print(f"  WARNING: '{query}' not found in search results")
    if laws:
        print("  Search results:", ", ".join(law.get("법령명한글", "") for law in laws[:10]))
    return None


def clear_generated_outputs(target_dir: Path):
    """Remove previously generated statute outputs before rewriting a law set."""
    for md_file in target_dir.glob("art*.md"):
        md_file.unlink()

    for filename in ("_hierarchy.json", "_meta.json", "_cross-refs.json", "_raw_response.xml"):
        path = target_dir / filename
        if path.exists():
            path.unlink()


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


CROSS_REFERENCE_PATTERN = re.compile(
    r"(?:(?P<named_law>「[^」]+」)(?:\s*\(이하\s+\"[^\"]+\"\s*이라\s+한다\))?\s*|"
    r"(?P<prefix>(?:같은|이)\s*(?:법|영|규칙)|[법영규칙])\s*)?"
    r"제(?P<article>\d+)조(?:의(?P<article_sub>\d+))?(?:제(?P<paragraph>\d+)항)?"
)
ARTICLE_CITATION_PATTERN = re.compile(r"^제(?P<article>\d+)조(?:의(?P<article_sub>\d+))?(?:제(?P<paragraph>\d+)항)?$")


def infer_law_reference_kind(law_name: str) -> str | None:
    """Infer the shorthand kind used by Korean legal citations."""
    if not law_name:
        return None
    if law_name.endswith(" 시행규칙"):
        return "규칙"
    if law_name.endswith(" 시행령"):
        return "영"
    return "법"


def related_law_names(current_law_name: str) -> dict[str, str]:
    """Resolve shorthand 법/영/규칙 references relative to the current law."""
    if current_law_name.endswith(" 시행령"):
        base_law = current_law_name[: -len(" 시행령")]
        decree = current_law_name
        rule = f"{base_law} 시행규칙"
    elif current_law_name.endswith(" 시행규칙"):
        base_law = current_law_name[: -len(" 시행규칙")]
        decree = f"{base_law} 시행령"
        rule = current_law_name
    else:
        base_law = current_law_name
        decree = f"{current_law_name} 시행령"
        rule = f"{current_law_name} 시행규칙"

    return {
        "법": base_law,
        "영": decree,
        "규칙": rule,
    }


def normalize_reference_kind(token: str) -> str | None:
    """Normalize a 법/영/규칙 shorthand token."""
    if not token:
        return None
    compact = token.replace(" ", "")
    if compact.endswith("규칙"):
        return "규칙"
    if compact.endswith("영"):
        return "영"
    if compact.endswith("법"):
        return "법"
    return None


def should_inherit_previous_law(separator: str) -> bool:
    """Return True when a bare citation is part of the same citation chain."""
    cleaned = separator
    cleaned = re.sub(
        r"제\d+(?:항|호|목)(?:부터\s*제\d+(?:항|호|목)까지)?",
        "",
        cleaned,
    )
    cleaned = cleaned.replace("각 호", "").replace("각호", "").replace("각 목", "").replace("각목", "")
    for token in ("부터", "까지", "내지", "및", "또는", "와", "과"):
        cleaned = cleaned.replace(token, "")
    cleaned = re.sub(r"[\s,·ㆍ\-~()]+", "", cleaned)
    return cleaned == ""


def format_cross_reference_citation(article_num: str, branch_str: str = "", paragraph_str: str = "") -> str:
    """Format a citation string with optional paragraph suffix."""
    citation = format_article_citation(article_num, branch_str)
    paragraph = _normalize_numeric_token(paragraph_str)
    if paragraph:
        citation += f"제{paragraph}항"
    return citation


def parse_article_citation(citation: str) -> dict:
    """Parse a legal citation into article/sub/paragraph components."""
    match = ARTICLE_CITATION_PATTERN.match(citation or "")
    if not match:
        return {"article_main": "", "article_sub": "0", "paragraph": ""}
    return {
        "article_main": _normalize_numeric_token(match.group("article")),
        "article_sub": _normalize_numeric_token(match.group("article_sub")) if match.group("article_sub") else "0",
        "paragraph": _normalize_numeric_token(match.group("paragraph")) if match.group("paragraph") else "",
    }


def is_self_article_reference(ref: dict, current_law_name: str, article_num: str, branch_str: str = "") -> bool:
    """Check whether a reference points back to the current article."""
    return (
        ref.get("law") == current_law_name
        and ref.get("article_citation") == format_article_citation(article_num, branch_str)
    )


def extract_cross_references(text: str, current_law_name: str) -> list[dict]:
    """Extract cross-references with law context when it is explicit or inferable."""
    refs = []
    seen = set()
    law_aliases = related_law_names(current_law_name)
    last_context_by_kind = {}
    previous_match_end = 0
    previous_target_law = None

    for match in CROSS_REFERENCE_PATTERN.finditer(text):
        named_law = match.group("named_law")
        prefix = match.group("prefix")
        article_num = match.group("article")
        article_sub = match.group("article_sub") or ""
        paragraph = match.group("paragraph") or ""

        target_law = None

        if named_law:
            target_law = named_law.strip("「」")
            ref_kind = infer_law_reference_kind(target_law)
            if ref_kind:
                last_context_by_kind[ref_kind] = target_law
        elif prefix:
            ref_kind = normalize_reference_kind(prefix)
            compact_prefix = prefix.replace(" ", "")
            if compact_prefix.startswith("같은"):
                target_law = last_context_by_kind.get(ref_kind)
                if not target_law:
                    previous_match_end = match.end()
                    previous_target_law = None
                    continue
            else:
                target_law = law_aliases.get(ref_kind)
                if not target_law:
                    previous_match_end = match.end()
                    previous_target_law = None
                    continue
                last_context_by_kind[ref_kind] = target_law
        else:
            separator = text[previous_match_end:match.start()]
            if previous_target_law and should_inherit_previous_law(separator):
                target_law = previous_target_law
            else:
                target_law = current_law_name

        article_citation = format_article_citation(article_num, article_sub)
        citation = format_cross_reference_citation(article_num, article_sub, paragraph)
        scope = "internal" if target_law == current_law_name else "external"
        display = citation if scope == "internal" else f"{target_law} {citation}"

        if display not in seen:
            seen.add(display)
            refs.append({
                "citation": display,
                "law": target_law,
                "article_citation": article_citation,
                "article_main": _normalize_numeric_token(article_num),
                "article_sub": _normalize_numeric_token(article_sub) if article_sub else "0",
                "paragraph": _normalize_numeric_token(paragraph) if paragraph else "",
                "scope": scope,
            })

        previous_match_end = match.end()
        previous_target_law = target_law

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
    cross_ref_entries = extract_cross_references(full_text, law_info["법령명한글"])
    cross_refs = [
        ref["citation"]
        for ref in cross_ref_entries
        if not is_self_article_reference(
            ref,
            law_info["법령명한글"],
            article["조문번호"],
            article.get("조문가지번호", ""),
        )
    ]
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


def safe_int(value: str | int | None) -> int:
    """Convert numeric-like values to ints for stable sorting."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def build_cross_reference_graph(all_articles: list[dict], active_target_dirs: set[str]) -> dict:
    """Build a cross-law reference graph from per-law cross-reference files."""
    article_lookup = {}
    indexed_laws = set()
    for article in all_articles:
        article_main = _normalize_numeric_token(str(article.get("article_main", "")))
        article_sub = str(article.get("article_sub", "0") or "0")
        article_sub = _normalize_numeric_token(article_sub) if article_sub not in ("", "0") else "0"
        key = (article.get("law", ""), article_main, article_sub)
        article_lookup[key] = article
        indexed_laws.add(article.get("law", ""))

    edges = []
    pair_counts = {}

    for law_dir in SOURCES_DIR.iterdir():
        if not law_dir.is_dir():
            continue
        if law_dir.name not in active_target_dirs:
            continue
        xref_path = law_dir / "_cross-refs.json"
        if not xref_path.exists():
            continue

        xref_data = json.loads(xref_path.read_text(encoding="utf-8"))
        for ref in xref_data.get("cross_references", []):
            if ref.get("scope") != "external":
                continue

            from_parts = parse_article_citation(ref.get("from", ""))
            to_main = str(ref.get("to_article_main", "") or "")
            to_sub = str(ref.get("to_article_sub", "0") or "0")
            if not to_main:
                parsed_to = parse_article_citation(ref.get("to_article", ""))
                to_main = parsed_to["article_main"]
                to_sub = parsed_to["article_sub"]
            to_key = (
                ref.get("to_law", ""),
                _normalize_numeric_token(to_main),
                _normalize_numeric_token(to_sub) if to_sub not in ("", "0") else "0",
            )
            target_article = article_lookup.get(to_key)
            target_status = "resolved" if target_article else (
                "missing_article" if ref.get("to_law", "") in indexed_laws else "external_unindexed"
            )

            edge = {
                "from_law": ref.get("from_law", xref_data.get("law", "")),
                "from_article": ref.get("from", ""),
                "from_article_main": ref.get("from_article_main", from_parts["article_main"]),
                "from_article_sub": ref.get("from_article_sub", from_parts["article_sub"]),
                "from_path": ref.get("from_path", ""),
                "to_law": ref.get("to_law", ""),
                "to_article": ref.get("to_article", ""),
                "to_display": ref.get("to", ""),
                "to_article_main": to_key[1],
                "to_article_sub": to_key[2],
                "to_paragraph": ref.get("to_paragraph", ""),
                "to_path": target_article["path"] if target_article else "",
                "to_id": target_article["id"] if target_article else "",
                "target_status": target_status,
                "type": ref.get("type", "references"),
            }
            edges.append(edge)
            pair_key = (edge["from_law"], edge["to_law"])
            pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1

    edges.sort(
        key=lambda edge: (
            edge["from_law"],
            safe_int(edge["from_article_main"]),
            safe_int(edge["from_article_sub"]),
            edge["to_law"],
            safe_int(edge["to_article_main"]),
            safe_int(edge["to_article_sub"]),
            safe_int(edge["to_paragraph"]),
        )
    )
    pairs = [
        {"from_law": from_law, "to_law": to_law, "count": count}
        for (from_law, to_law), count in sorted(pair_counts.items())
    ]

    return {
        "type": "cross_reference_graph",
        "generated_at": datetime.now().isoformat(),
        "count": len(edges),
        "resolved_count": sum(1 for edge in edges if edge["target_status"] == "resolved"),
        "unresolved_count": sum(1 for edge in edges if edge["target_status"] != "resolved"),
        "pairs": pairs,
        "edges": edges,
    }


def build_external_law_candidates(cross_reference_graph: dict) -> dict:
    """Summarize unresolved external-law references into fetch candidates."""
    candidate_map = {}

    for edge in cross_reference_graph.get("edges", []):
        if edge.get("target_status") != "external_unindexed":
            continue

        law_name = edge.get("to_law", "")
        if not law_name:
            continue

        entry = candidate_map.setdefault(
            law_name,
            {
                "law": law_name,
                "reference_count": 0,
                "source_laws": set(),
                "sample_backlinks": [],
            },
        )
        entry["reference_count"] += 1
        entry["source_laws"].add(edge.get("from_law", ""))
        if len(entry["sample_backlinks"]) < 5:
            entry["sample_backlinks"].append({
                "from_law": edge.get("from_law", ""),
                "from_article": edge.get("from_article", ""),
                "from_path": edge.get("from_path", ""),
                "to_display": edge.get("to_display", ""),
            })

    candidates = []
    for entry in candidate_map.values():
        source_laws = sorted(law for law in entry["source_laws"] if law)
        reference_count = entry["reference_count"]
        if reference_count >= 10:
            priority_tier = "high"
        elif reference_count >= 5:
            priority_tier = "medium"
        else:
            priority_tier = "low"

        candidates.append({
            "law": entry["law"],
            "reference_count": reference_count,
            "source_law_count": len(source_laws),
            "source_laws": source_laws,
            "priority_tier": priority_tier,
            "sample_backlinks": entry["sample_backlinks"],
        })

    candidates.sort(
        key=lambda candidate: (
            -candidate["reference_count"],
            -candidate["source_law_count"],
            candidate["law"],
        )
    )
    for idx, candidate in enumerate(candidates, start=1):
        candidate["priority_rank"] = idx

    return {
        "type": "external_law_candidates",
        "generated_at": datetime.now().isoformat(),
        "count": len(candidates),
        "high_priority_count": sum(1 for candidate in candidates if candidate["priority_tier"] == "high"),
        "medium_priority_count": sum(1 for candidate in candidates if candidate["priority_tier"] == "medium"),
        "low_priority_count": sum(1 for candidate in candidates if candidate["priority_tier"] == "low"),
        "candidates": candidates,
    }


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
        mst = config.get("mst", "")
        law_id = ""
        if not mst:
            print(f"  FAILED: Could not find '{law_name}' via API")
            return False
        print(f"  Using configured MST fallback: {mst}")
    else:
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

    clear_generated_outputs(target_dir)

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
        refs = extract_cross_references(full_text, law_info["법령명한글"])
        for ref in refs:
            if is_self_article_reference(
                ref,
                law_info["법령명한글"],
                article["조문번호"],
                article.get("조문가지번호", ""),
            ):
                continue
            cross_refs_all.append({
                "from": art_label,
                "from_law": law_info["법령명한글"],
                "from_article_main": art_num.split("의")[0] if "의" in art_num else art_num,
                "from_article_sub": art_num.split("의")[1] if "의" in art_num else "0",
                "from_path": str(filepath.relative_to(PROJECT_ROOT)),
                "to": ref["citation"],
                "to_law": ref["law"],
                "to_article": ref["article_citation"],
                "to_article_main": ref["article_main"],
                "to_article_sub": ref["article_sub"],
                "to_paragraph": ref["paragraph"],
                "scope": ref["scope"],
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
    active_target_dirs = DEFAULT_ENABLED_TARGET_DIRS | {"pipc-guidelines"}

    # Build article-index.json from all processed laws
    all_articles = []
    for law_dir in SOURCES_DIR.iterdir():
        if not law_dir.is_dir():
            continue
        if law_dir.name not in active_target_dirs:
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

    cross_reference_graph = build_cross_reference_graph(all_articles, DEFAULT_ENABLED_TARGET_DIRS)
    cross_reference_graph_path = index_dir / "cross-reference-graph.json"
    cross_reference_graph_path.write_text(
        json.dumps(cross_reference_graph, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        "Updated cross-reference-graph.json "
        f"({cross_reference_graph['count']} edges, "
        f"{cross_reference_graph['resolved_count']} resolved)"
    )

    external_law_candidates = build_external_law_candidates(cross_reference_graph)
    external_law_candidates_path = index_dir / "external-law-candidates.json"
    external_law_candidates_path.write_text(
        json.dumps(external_law_candidates, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        "Updated external-law-candidates.json "
        f"({external_law_candidates['count']} candidates, "
        f"{external_law_candidates['high_priority_count']} high priority)"
    )

    # Update source-registry.json
    registry_path = index_dir / "source-registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        registry = {"type": "source_registry", "sources": {"grade-a": {}, "grade-b": {}, "grade-c": {}}}
    existing_guidelines_entry = registry.get("sources", {}).get("grade-a", {}).get("pipc-guidelines")
    registry["sources"]["grade-a"] = {}
    if existing_guidelines_entry:
        registry["sources"]["grade-a"]["pipc-guidelines"] = existing_guidelines_entry

    for law_name, law_config in DEFAULT_ENABLED_LAWS.items():
        law_dir = SOURCES_DIR / law_config["target_dir"]
        meta_path = law_dir / "_meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        count = len(list(law_dir.glob("art*.md"))) if law_dir.exists() else 0

        if law_config.get("skip_fetch"):
            registry["sources"]["grade-a"][law_config["target_dir"]] = {
                "status": law_config.get("registry_status", "retired"),
                "count": 0,
                "target": 0,
                "law_name": meta.get("law_name", law_name),
                "retrieved_at": meta.get("retrieved_at", ""),
                "note": law_config.get("note", "Excluded from ingest."),
            }
            continue

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
            "law_name": meta.get("law_name", law_name),
            "retrieved_at": meta.get("retrieved_at", ""),
        }
        if status == "partial":
            entry["note"] = "Branch articles are currently flattened into base article files; re-ingest required."
        elif status == "pending":
            entry["note"] = "Directory exists but no ingested statute files are available yet."

        registry["sources"]["grade-a"][law_config["target_dir"]] = entry

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
        laws_to_process = DEFAULT_ENABLED_LAWS
    else:
        laws_to_process = {args.law: KNOWN_LAWS[args.law]}

    results = {}
    for law_name, config in laws_to_process.items():
        if config.get("skip_fetch"):
            print(f"\n{'='*60}")
            print(f"Processing: {law_name}")
            print(f"{'='*60}")
            print(f"  SKIPPED: {config.get('note', 'Excluded from ingest.')}")
            results[law_name] = "SKIPPED"
            continue
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
            if isinstance(success, str):
                status = success
            else:
                status = "OK" if success else "FAILED"
            print(f"  {law}: {status}")


if __name__ == "__main__":
    main()
