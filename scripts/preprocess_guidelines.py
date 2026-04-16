#!/usr/bin/env python3
"""
PIPA RAG Preprocessor: Convert PIPC guideline PDFs to structured markdown with frontmatter.
"""

from datetime import datetime
import json
from pathlib import Path
import subprocess

from scripts.lib.sanitize import (
    sanitize_ingested_markdown,
    sanitize_yaml_string,
    write_audit_sidecar,
)

PROJECT_ROOT = Path(__file__).parent.parent
PDF_DIR = PROJECT_ROOT / "PIPC Official Guidelines"
OUTPUT_DIR = PROJECT_ROOT / "sources" / "grade-a" / "pipc-guidelines"

# Guideline metadata mapping (id, slug, title_kr, topics)
GUIDELINES = [
    (1, "commentary-on-pipa", "개인정보 보호법령 해설서", ["법령해설", "PIPA", "총론"]),
    (2, "integrated-processing-guide", "개인정보 처리 통합 안내서", ["개인정보처리", "수집", "이용", "제공", "파기"]),
    (3, "sector-specific-guide", "분야별 개인정보 보호 안내서", ["분야별", "공공", "민간", "업종"]),
    (4, "emergency-processing", "긴급상황 시 개인정보 처리 안내서", ["긴급상황", "재난", "감염병", "생명보호"]),
    (5, "children-adolescents", "아동·청소년 개인정보 보호 안내서", ["아동", "청소년", "법정대리인", "동의"]),
    (6, "access-exclusion-right", "인터넷 자기게시물 접근배제요청권 안내서", ["접근배제", "잊힐권리", "게시물삭제"]),
    (7, "automated-decision-making", "자동화된 의사결정에 대한 정보주체 권리 안내서", ["자동화의사결정", "프로파일링", "정보주체권리"]),
    (8, "safety-standards", "개인정보의 안전성 확보조치 안내서", ["안전조치", "암호화", "접근통제", "보안"]),
    (9, "developer-privacy", "개발자를 위한 프라이버시 보호조치 안내서", ["개발자", "Privacy by Design", "보호조치"]),
    (10, "biometric-info", "생체정보 보호 안내서", ["생체정보", "지문", "홍채", "얼굴인식"]),
    (11, "fixed-video-surveillance", "고정형 영상정보처리기기 안내서", ["CCTV", "영상정보", "고정형"]),
    (12, "mobile-surveillance", "이동형 영상정보처리기기 개인정보 보호 안내서", ["이동형", "드론", "바디캠", "영상정보"]),
    (13, "smart-city", "스마트시티 개인정보 보호 안내서", ["스마트시티", "IoT", "도시데이터"]),
    (14, "website-exposure-prevention", "홈페이지 개인정보 노출방지 안내서", ["웹사이트", "노출방지", "개인정보유출"]),
    (15, "synthetic-data", "합성데이터 활용 안내서", ["합성데이터", "데이터활용", "비식별"]),
    (16, "pseudonymization", "가명정보 처리 가이드라인", ["가명정보", "가명처리", "결합", "재식별"]),
    (17, "pseudonymization-public", "공공부문 가명정보 처리 실무 안내서", ["가명정보", "공공부문", "실무"]),
    (18, "pseudonymization-education", "교육분야 가명정보 처리 안내서", ["가명정보", "교육", "학생정보"]),
    (19, "health-medical-data", "보건의료 데이터 활용 안내서", ["보건의료", "건강정보", "의료데이터"]),
    (20, "synthetic-data-reference-model", "합성데이터 생성 참조모델", ["합성데이터", "생성모델", "기술표준"]),
    (21, "public-ai-development", "AI 개발을 위한 공공 개인정보 처리 안내서", ["AI", "공공데이터", "학습데이터"]),
    (22, "ai-privacy-risk-assessment", "AI 프라이버시 리스크 평가 모델", ["AI", "리스크평가", "프라이버시"]),
    (23, "generative-ai", "생성AI에 의한 개인정보 처리 안내서", ["생성AI", "ChatGPT", "LLM", "개인정보"]),
    (24, "privacy-policy-drafting", "개인정보 처리방침 작성 안내서", ["처리방침", "Privacy Policy", "고지"]),
    (25, "privacy-impact-assessment", "개인정보 영향평가 수행 안내서", ["영향평가", "PIA", "위험분석"]),
    (26, "pia-cost-estimation", "개인정보 영향평가 비용 산정 안내서", ["영향평가", "비용산정", "PIA"]),
    (27, "isms-p-certification", "ISMS-P 인증기준 안내서", ["ISMS-P", "인증", "정보보호"]),
    (28, "privacy-education", "개인정보 보호 교육 안내서", ["교육", "인식제고", "담당자교육"]),
    (29, "breach-response", "개인정보 유출사고 대응 매뉴얼", ["유출사고", "침해사고", "대응", "통지"]),
    ("30-en", "foreign-business-en", "Guide on Application of PIPA to Foreign Businesses (EN)", ["외국사업자", "역외적용", "English"]),
    ("30-kr", "foreign-business-kr", "외국의 사업자에 대한 개인정보 보호법 적용 안내서", ["외국사업자", "역외적용"]),
    (31, "liability-insurance", "개인정보 손해배상 책임보험 안내서", ["손해배상", "보험", "배상책임"]),
    (32, "qa-compilation", "개인정보 보호 QA 모음집", ["FAQ", "질의응답", "실무해석"]),
    (33, "data-portability", "개인정보 전송요구권 안내서", ["전송요구권", "데이터이동권", "포터빌리티"]),
    (34, "management-agency-general", "개인정보 관리전문기관 지정 안내서 (일반)", ["관리전문기관", "지정", "일반"]),
    (35, "management-agency-special", "개인정보 관리전문기관 지정 안내서 (특례)", ["관리전문기관", "지정", "특례"]),
    (36, "management-agency-relay", "개인정보 관리전문기관 지정 안내서 (중계)", ["관리전문기관", "지정", "중계"]),
    (37, "general-data-recipient", "일반 데이터 수령인 등록 안내서", ["데이터수령인", "등록", "MyData"]),
    (38, "mydata-transfer-procedures", "분야 간 본인정보 전송 절차·기술 안내서", ["MyData", "본인정보전송", "기술표준"]),
    ("39a", "industry-real-estate", "업종별 개인정보 처리 안내서 - 부동산", ["부동산", "업종별", "중개"]),
    ("39b", "industry-hotels", "업종별 개인정보 처리 안내서 - 숙박업", ["숙박업", "업종별", "호텔"]),
    ("39c", "industry-academies", "업종별 개인정보 처리 안내서 - 학원", ["학원", "업종별", "교육"]),
    (40, "small-business-handbook", "소상공인 개인정보 보호 핸드북", ["소상공인", "소규모", "핸드북"]),
    ("41a", "template-real-estate", "표준 개인정보처리방침 - 공인중개사", ["템플릿", "처리방침", "공인중개사"]),
    ("41b", "template-senior-welfare", "표준 개인정보처리방침 - 노인복지관", ["템플릿", "처리방침", "노인복지관"]),
    ("41c", "template-travel-agency", "표준 개인정보처리방침 - 여행사", ["템플릿", "처리방침", "여행사"]),
]

# Map PDF filenames to guideline index
PDF_FILES = sorted(PDF_DIR.glob("*.pdf"))


def convert_pdf_to_markdown(pdf_path: Path) -> str:
    """Convert PDF to markdown using markitdown CLI."""
    try:
        result = subprocess.run(
            ["markitdown", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"  WARNING: markitdown error for {pdf_path.name}: {result.stderr[:200]}")
            return f"[CONVERSION ERROR: {result.stderr[:200]}]"
    except subprocess.TimeoutExpired:
        print(f"  WARNING: markitdown timeout for {pdf_path.name}")
        return "[CONVERSION TIMEOUT]"
    except Exception as e:
        print(f"  WARNING: markitdown exception for {pdf_path.name}: {e}")
        return f"[CONVERSION EXCEPTION: {e}]"


def _wrap_untrusted_content(text: str, *, source: str) -> str:
    return (
        f'<untrusted_content source="{source}" sanitized="true">\n'
        f"{text}\n"
        "</untrusted_content>\n"
    )


def create_frontmatter(guideline_id, slug, title_kr, topics, pdf_name, char_count) -> str:
    """Create YAML frontmatter for a guideline."""
    title_en_raw = pdf_name.split(" ", 1)[1].rsplit(".pdf", 1)[0] if " " in pdf_name else pdf_name
    escaped_topics = [sanitize_yaml_string(topic) for topic in topics]
    return f"""---
# === 식별 정보 ===
guideline_id: "{guideline_id}"
slug: "{sanitize_yaml_string(slug)}"
title_kr: "{sanitize_yaml_string(title_kr)}"
title_en: "{sanitize_yaml_string(title_en_raw)}"
document_type: "guideline"

# === 소스 정보 ===
source_grade: "A"
publisher: "{sanitize_yaml_string('개인정보보호위원회 (PIPC)')}"
source_url: "{sanitize_yaml_string('https://www.pipc.go.kr')}"
retrieved_at: "{datetime.now().strftime('%Y-%m-%d')}"

# === 검색 메타 ===
keywords:
{chr(10).join(f'  - "{topic}"' for topic in escaped_topics)}
topics:
{chr(10).join(f'  - "{topic}"' for topic in escaped_topics)}
char_count: {char_count}
---

"""


def process_all():
    """Process all guideline PDFs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if len(PDF_FILES) != len(GUIDELINES):
        print(f"WARNING: {len(PDF_FILES)} PDFs but {len(GUIDELINES)} guideline entries")

    processed = 0
    errors = 0

    for i, (pdf_path, guideline) in enumerate(zip(PDF_FILES, GUIDELINES)):
        gid, slug, title_kr, topics = guideline
        print(f"[{i+1}/{len(PDF_FILES)}] Converting: {pdf_path.name}")

        # Convert PDF to markdown
        md_content = convert_pdf_to_markdown(pdf_path)
        char_count = len(md_content)

        if md_content.startswith("[CONVERSION"):
            errors += 1
            print(f"  SKIPPED (error)")
            continue

        sanitize_result = sanitize_ingested_markdown(md_content)
        if sanitize_result.aborted:
            errors += 1
            print("  SKIPPED ([SANITIZER UNAVAILABLE])")
            continue

        # Create frontmatter
        frontmatter = create_frontmatter(gid, slug, title_kr, topics, pdf_path.name, char_count)
        wrapped_body = _wrap_untrusted_content(sanitize_result.text, source="pipc-pdf")

        # Write output file
        output_file = OUTPUT_DIR / f"{str(gid).zfill(2)}-{slug}.md"
        output_file.write_text(frontmatter + wrapped_body, encoding="utf-8")
        write_audit_sidecar(output_file, sanitize_result)

        size_kb = output_file.stat().st_size / 1024
        print(f"  OK → {output_file.name} ({size_kb:.0f} KB)")
        processed += 1

    # Write _meta.json
    meta = {
        "collection": "PIPC Official Guidelines",
        "source_grade": "A",
        "publisher": "개인정보보호위원회 (PIPC)",
        "document_count": processed,
        "errors": errors,
        "generated_at": datetime.now().isoformat(),
        "guidelines": [
            {
                "id": str(g[0]),
                "slug": g[1],
                "title_kr": g[2],
                "file": f"{str(g[0]).zfill(2)}-{g[1]}.md",
            }
            for g in GUIDELINES
        ],
    }
    meta_path = OUTPUT_DIR / "_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nDone: {processed} converted, {errors} errors")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Meta: {meta_path}")


if __name__ == "__main__":
    process_all()
