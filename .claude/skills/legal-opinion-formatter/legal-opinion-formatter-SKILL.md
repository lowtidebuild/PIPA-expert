---
name: legal-opinion-formatter
description: >
  python-docx를 사용한 PIPA 법률 분석 메모 DOCX 생성 상세 구현 가이드.
  SKILL.md의 문서 구조를 실제 `.docx` 파일로 변환하는 코드 레시피.
  호환성을 위해 built-in 스타일만 사용하고, 레터헤드는 본문에 배치한다.
---

# PIPA Legal Analysis Memo DOCX Implementation Guide

## Required Setup

```bash
pip install python-docx
```

## Core Imports

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import datetime
import os
```

---

## Compatibility Rules

**반드시 준수:**
1. **커스텀 스타일 사용 금지** — `doc.styles.add_style()` 사용하지 않음
2. **built-in 스타일만 사용** — `Heading 1`, `Heading 2`, `Heading 3`, `Normal`
3. **레터헤드는 본문에 배치** — `section.header` 사용하지 않음 (일부 뷰어 호환성 문제)
4. **footer 사용 자제** — 페이지 번호가 필요하면 본문 하단에 배치
5. **서식은 run 단위로 직접 적용** — 스타일 의존 최소화

---

## Page Setup (A4, Korean Standard)

```python
doc = Document()

# Default font
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(11)
font.color.rgb = RGBColor(0, 0, 0)
pf = style.paragraph_format
pf.space_after = Pt(6)
pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
pf.line_spacing = 1.15

# East Asian font (Korean)
rPr = style.element.get_or_add_rPr()
rFonts = rPr.get_or_add_rFonts()
rFonts.set(qn('w:eastAsia'), '바탕체')

# Heading styles — customize built-in only
for level, size, color in [(1, 14, (0x1B,0x2A,0x4A)), (2, 12, (0x33,0x33,0x33)), (3, 11, (0x33,0x33,0x33))]:
    hs = doc.styles[f'Heading {level}']
    hs.font.name = 'Arial'
    hs.font.size = Pt(size)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(*color)
    rp = hs.element.get_or_add_rPr()
    rf = rp.get_or_add_rFonts()
    rf.set(qn('w:eastAsia'), '맑은 고딕')
    hs.paragraph_format.space_before = Pt(18 if level == 1 else 12)
    hs.paragraph_format.space_after = Pt(8 if level == 1 else 6)

# A4 page with Korean memorandum margins
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)    # Wider left for binding
    section.right_margin = Cm(2.5)
```

---

## Color Constants

```python
NAVY = RGBColor(0x1B, 0x2A, 0x4A)
GRAY = RGBColor(0x66, 0x66, 0x66)
DARK = RGBColor(0x33, 0x33, 0x33)
RED = RGBColor(0x80, 0x00, 0x00)
```

---

## Letterhead (본문 배치)

```python
def create_letterhead(doc, firm_info=None):
    """레터헤드를 본문 최상단에 배치 (헤더 사용 안 함)."""
    if firm_info is None:
        firm_info = {
            'name_ko': 'KP Legal Orchestrator',
            'name_en': 'AI legal workflow system',
        }

    # Firm name (Korean)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(firm_info['name_ko'])
    r.font.name = 'Arial'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    rp = r._element.get_or_add_rPr()
    rf = rp.get_or_add_rFonts()
    rf.set(qn('w:eastAsia'), '맑은 고딕')

    # English subtitle
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r2 = p2.add_run(firm_info['name_en'])
    r2.font.name = 'Arial'
    r2.font.size = Pt(9)
    r2.font.italic = True
    r2.font.color.rgb = GRAY

    # Separator
    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_before = Pt(2)
    p_sep.paragraph_format.space_after = Pt(12)
    r_sep = p_sep.add_run('━' * 50)
    r_sep.font.size = Pt(8)
    r_sep.font.color.rgb = NAVY
```

---

## Content Helper Functions

```python
def add_confidential_marking(doc):
    """비밀유지 마킹."""
    for text in ['비밀유지 / 내부 검토 자료', 'CONFIDENTIAL & INTERNAL REVIEW']:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RED


def add_date_and_addressee(doc, date_str, recipient_lines):
    """날짜 및 수신인 블록."""
    doc.add_paragraph()
    doc.add_paragraph(date_str)
    doc.add_paragraph()
    for line in recipient_lines:
        p = doc.add_paragraph(line)
        if line == recipient_lines[0]:
            p.runs[0].bold = True


def add_reference_line(doc, subject):
    """건명 라인."""
    doc.add_paragraph()
    p = doc.add_paragraph()
    r1 = p.add_run('건명:  ')
    r1.bold = True
    r2 = p.add_run(subject)
    r2.bold = True


def add_salutation(doc, recipient_name):
    """수신인 인사."""
    doc.add_paragraph()
    doc.add_paragraph(f'{recipient_name} 귀하')


def add_section_heading(doc, text):
    """섹션 제목 (built-in Heading 1)."""
    doc.add_heading(text, level=1)


def add_sub_heading(doc, text):
    """서브 제목 (built-in Heading 2)."""
    doc.add_heading(text, level=2)


def add_body(doc, text):
    """본문 단락."""
    return doc.add_paragraph(text)


def add_body_bold(doc, prefix, text):
    """볼드 접두어 + 본문."""
    p = doc.add_paragraph()
    r = p.add_run(prefix)
    r.bold = True
    p.add_run(text)
    return p


def add_block_quote(doc, text):
    """조문 인용 블록 — 들여쓰기 + 이탤릭."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.right_indent = Cm(1.0)
    r = p.add_run(text)
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = DARK
    return p


def add_citation_tag(doc, tag_text):
    """출처 태그 — 들여쓰기 + Navy."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(tag_text)
    r.font.name = 'Arial'
    r.font.size = Pt(9)
    r.font.color.rgb = NAVY
    return p


def add_verified_citation(doc, grade, source, quote=None):
    """검증된 인용 — 태그 + 원문 인용을 한 번에."""
    add_citation_tag(doc, f'[VERIFIED] [Grade {grade}] {source}')
    if quote:
        add_block_quote(doc, f'{quote}')


def add_small_text(doc, text):
    """면책 등 소형 텍스트."""
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.color.rgb = GRAY
    return p
```

---

## Table

```python
def add_table(doc, headers, rows):
    """테이블 생성 (built-in 스타일 사용)."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    # Header
    for i, text in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = text
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.size = Pt(9)
    # Data
    for r_idx, row_data in enumerate(rows):
        for c_idx, text in enumerate(row_data):
            table.rows[r_idx + 1].cells[c_idx].text = text
    doc.add_paragraph()  # spacing after table
```

---

## Signature Block

```python
def add_signature_block(doc, firm_name='KP Legal Orchestrator',
                        author_name='개인정보 스페셜리스트',
                        title='Privacy Specialist',
                        registration=None):
    """서명 블록."""
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph('이상과 같이 분석 결과를 드립니다.')
    doc.add_paragraph()

    p_firm = doc.add_paragraph()
    r = p_firm.add_run(firm_name)
    r.bold = True

    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph('____________________________')
    doc.add_paragraph(author_name)
    doc.add_paragraph(title)
    if registration:
        doc.add_paragraph(registration)
```

---

## Disclaimer

```python
def add_disclaimer(doc):
    """면책 조항 (법률 자문 면책 + AI 생성 고지)."""
    doc.add_paragraph()
    p_line = doc.add_paragraph()
    r = p_line.add_run('━' * 50)
    r.font.size = Pt(8)
    r.font.color.rgb = GRAY

    add_small_text(doc,
        '본 분석 메모는 상기 특정된 사실관계와 법률 쟁점에 한정된 법률 정보 제공을 '
        '목적으로 작성되었으며, 일반적인 법률 자문을 구성하지 않습니다. 구체적 '
        '사안에 대해서는 전문 법률가와 상담하시기 바랍니다. 본 분석 메모의 분석은 '
        '작성일 기준 시행 중인 법령에 근거하며, 이후 법령 개정, 판례 변경, '
        '감독기관 유권해석 등에 의해 결론이 달라질 수 있습니다.')

    add_small_text(doc,
        '[AI 생성 고지] 본 분석 메모는 AI 시스템(PIPA Expert Agent)의 지원을 받아 '
        '작성되었습니다. AI가 제시한 법령 인용 및 분석은 Source Grade 체계에 따라 '
        '검증 상태가 표시되어 있으나, 최종 판단은 반드시 전문가 검토를 거쳐야 합니다.')
```

---

## Full Document Assembly

```python
def generate_pipa_opinion(
    subject,
    date_str=None,
    firm_info=None,
    recipient=None,
    sections=None,
    sources=None,
    author_info=None,
    confidential=True,
    output_dir=None,
):
    """PIPA 법률 분석 메모 DOCX 생성.

    Agent는 이 함수를 참고하여 인라인 Python 스크립트를 작성하고 실행한다.
    함수를 그대로 복사하지 말고, 분석 메모 내용에 맞게 필요한 부분만 조합하여 사용한다.
    """
    if date_str is None:
        today = datetime.date.today()
        date_str = f"{today.year}년 {today.month}월 {today.day}일"
    if output_dir is None:
        output_dir = os.environ.get('PIPA_OUTPUT_DIR', 'output/opinions')

    doc = Document()
    # ... (위 Page Setup, Heading styles 적용)

    create_letterhead(doc, firm_info)

    if confidential:
        add_confidential_marking(doc)

    if recipient is None:
        recipient = ['[수신인 이름]', '[직위]', '[회사/기관명]']
    add_date_and_addressee(doc, date_str, recipient)
    add_reference_line(doc, subject)
    add_salutation(doc, recipient[0])

    # 의뢰인 질문 사항 (맨 앞에 배치)
    add_section_heading(doc, 'I. 의뢰인 질문 사항')
    # ... (배경 + 질문 목록)

    # 핵심 요약
    add_section_heading(doc, 'II. 핵심 요약 (Executive Summary)')
    # ...

    # 이하 분석, 결론 등 sections dict 기반으로 동적 생성

    # 출처 목록
    # ... (Grade A, Grade B, Web 순)

    # 서명
    add_signature_block(doc)

    # 면책
    add_disclaimer(doc)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    today_str = datetime.date.today().strftime('%Y%m%d')
    safe_subject = subject.replace(' ', '_').replace('/', '_')[:30]
    filename = f"{today_str}_pipa_opinion_{safe_subject}_v1.docx"
    filepath = os.path.join(output_dir, filename)

    version = 1
    while os.path.exists(filepath):
        version += 1
        filename = f"{today_str}_pipa_opinion_{safe_subject}_v{version}.docx"
        filepath = os.path.join(output_dir, filename)

    doc.save(filepath)
    return filepath
```

---

## Usage Pattern (Agent가 따라야 할 흐름)

1. RAG 검색으로 근거 수집 (pipa-agent 프로토콜)
2. 수집 결과를 분석 메모 섹션별로 구조화
3. 위 헬퍼 함수들을 조합하여 인라인 Python 스크립트 작성
4. 스크립트 실행하여 DOCX 생성
5. 생성된 파일 경로를 사용자에게 안내

**주의:** 반드시 위 Compatibility Rules를 준수한다. 커스텀 스타일, 헤더/푸터 조작은 사용하지 않는다.
