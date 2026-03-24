---
name: legal-opinion-formatter
description: >
  python-docx를 사용한 PIPA 법률의견서 DOCX 생성 상세 구현 가이드.
  SKILL.md의 문서 구조를 실제 .docx 파일로 변환하는 코드 레시피.
---

# PIPA Legal Opinion DOCX Implementation Guide

## Required Setup

```bash
pip install python-docx
```

## Core Imports

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement
import datetime
import os
```

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

# East Asian font (Korean)
rPr = style.element.get_or_add_rPr()
rFonts = rPr.get_or_add_rFonts()
rFonts.set(qn('w:eastAsia'), '바탕체')  # Batang for body text

# A4 page with Korean law firm margins
for section in doc.sections:
    section.page_width = Cm(21.0)    # A4 width
    section.page_height = Cm(29.7)   # A4 height
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)    # Wider left for binding
    section.right_margin = Cm(2.5)
```

---

## Custom Styles

```python
def setup_styles(doc):
    """PIPA 의견서 전용 스타일 정의."""
    styles = doc.styles

    # --- Section Heading (예: "I. 서론") ---
    s1 = styles.add_style('PIPAHeading1', 1)
    s1.font.name = 'Arial'
    s1.font.size = Pt(14)
    s1.font.bold = True
    s1.font.color.rgb = RGBColor(0x1B, 0x2A, 0x4A)  # Navy
    rPr1 = s1.element.get_or_add_rPr()
    rFonts1 = rPr1.get_or_add_rFonts()
    rFonts1.set(qn('w:eastAsia'), '맑은 고딕')
    s1.paragraph_format.space_before = Pt(20)
    s1.paragraph_format.space_after = Pt(10)
    s1.paragraph_format.keep_with_next = True

    # --- Sub Heading (예: "가. 쟁점 분석") ---
    s2 = styles.add_style('PIPAHeading2', 1)
    s2.font.name = 'Arial'
    s2.font.size = Pt(12)
    s2.font.bold = True
    s2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    rPr2 = s2.element.get_or_add_rPr()
    rFonts2 = rPr2.get_or_add_rFonts()
    rFonts2.set(qn('w:eastAsia'), '맑은 고딕')
    s2.paragraph_format.space_before = Pt(14)
    s2.paragraph_format.space_after = Pt(6)
    s2.paragraph_format.keep_with_next = True

    # --- Sub-sub Heading (예: "(1) 세부 쟁점") ---
    s2b = styles.add_style('PIPAHeading3', 1)
    s2b.font.name = 'Arial'
    s2b.font.size = Pt(11)
    s2b.font.bold = True
    s2b.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    rPr2b = s2b.element.get_or_add_rPr()
    rFonts2b = rPr2b.get_or_add_rFonts()
    rFonts2b.set(qn('w:eastAsia'), '맑은 고딕')
    s2b.paragraph_format.space_before = Pt(10)
    s2b.paragraph_format.space_after = Pt(4)
    s2b.paragraph_format.keep_with_next = True

    # --- Body Text ---
    s3 = styles.add_style('PIPABody', 1)
    s3.font.name = 'Times New Roman'
    s3.font.size = Pt(11)
    s3.font.color.rgb = RGBColor(0, 0, 0)
    rPr3 = s3.element.get_or_add_rPr()
    rFonts3 = rPr3.get_or_add_rFonts()
    rFonts3.set(qn('w:eastAsia'), '바탕체')
    s3.paragraph_format.space_after = Pt(6)
    s3.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    s3.paragraph_format.line_spacing = 1.15

    # --- Block Quote (조문 인용) ---
    s4 = styles.add_style('PIPABlockQuote', 1)
    s4.font.name = 'Times New Roman'
    s4.font.size = Pt(10)
    s4.font.italic = True
    s4.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    rPr4 = s4.element.get_or_add_rPr()
    rFonts4 = rPr4.get_or_add_rFonts()
    rFonts4.set(qn('w:eastAsia'), '바탕체')
    s4.paragraph_format.left_indent = Cm(1.5)
    s4.paragraph_format.right_indent = Cm(1.0)
    s4.paragraph_format.space_before = Pt(6)
    s4.paragraph_format.space_after = Pt(6)
    s4.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    s4.paragraph_format.line_spacing = 1.0

    # --- Verification Tag (인용 출처 태그) ---
    s4b = styles.add_style('PIPACitation', 1)
    s4b.font.name = 'Arial'
    s4b.font.size = Pt(9)
    s4b.font.color.rgb = RGBColor(0x1B, 0x2A, 0x4A)  # Navy
    rPr4b = s4b.element.get_or_add_rPr()
    rFonts4b = rPr4b.get_or_add_rFonts()
    rFonts4b.set(qn('w:eastAsia'), '맑은 고딕')
    s4b.paragraph_format.left_indent = Cm(1.5)
    s4b.paragraph_format.space_before = Pt(2)
    s4b.paragraph_format.space_after = Pt(8)

    # --- Confidential Marking ---
    s5 = styles.add_style('PIPAConfidential', 1)
    s5.font.name = 'Arial'
    s5.font.size = Pt(9)
    s5.font.bold = True
    s5.font.all_caps = True
    s5.font.color.rgb = RGBColor(0x80, 0x00, 0x00)  # Dark red
    rPr5 = s5.element.get_or_add_rPr()
    rFonts5 = rPr5.get_or_add_rFonts()
    rFonts5.set(qn('w:eastAsia'), '맑은 고딕')
    s5.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s5.paragraph_format.space_before = Pt(0)
    s5.paragraph_format.space_after = Pt(6)

    # --- Signature Block ---
    s6 = styles.add_style('PIPASignature', 1)
    s6.font.name = 'Times New Roman'
    s6.font.size = Pt(11)
    s6.font.color.rgb = RGBColor(0, 0, 0)
    rPr6 = s6.element.get_or_add_rPr()
    rFonts6 = rPr6.get_or_add_rFonts()
    rFonts6.set(qn('w:eastAsia'), '바탕체')
    s6.paragraph_format.space_after = Pt(2)
    s6.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # --- Disclaimer (면책 조항) ---
    s7 = styles.add_style('PIPADisclaimer', 1)
    s7.font.name = 'Arial'
    s7.font.size = Pt(8)
    s7.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    rPr7 = s7.element.get_or_add_rPr()
    rFonts7 = rPr7.get_or_add_rFonts()
    rFonts7.set(qn('w:eastAsia'), '맑은 고딕')
    s7.paragraph_format.space_before = Pt(12)
    s7.paragraph_format.space_after = Pt(2)
    s7.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # --- Risk Matrix Table Header ---
    s8 = styles.add_style('PIPATableHeader', 1)
    s8.font.name = 'Arial'
    s8.font.size = Pt(9)
    s8.font.bold = True
    s8.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)  # White
    rPr8 = s8.element.get_or_add_rPr()
    rFonts8 = rPr8.get_or_add_rFonts()
    rFonts8.set(qn('w:eastAsia'), '맑은 고딕')

    # --- Source List ---
    s9 = styles.add_style('PIPASourceList', 1)
    s9.font.name = 'Times New Roman'
    s9.font.size = Pt(9)
    s9.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    rPr9 = s9.element.get_or_add_rPr()
    rFonts9 = rPr9.get_or_add_rFonts()
    rFonts9.set(qn('w:eastAsia'), '바탕체')
    s9.paragraph_format.left_indent = Cm(0.5)
    s9.paragraph_format.space_after = Pt(2)

    return styles
```

---

## Letterhead Header

```python
def create_letterhead(doc, firm_info=None):
    """한국 로펌 스타일 레터헤드 생성."""
    if firm_info is None:
        firm_info = {
            'name_ko': '법무법인 진주',
            'name_en': 'Law Firm Pearl',
            'address': '[주소]',
            'phone': '[전화번호]',
            'email': '[이메일]',
            'website': '[웹사이트]',
        }

    section = doc.sections[0]
    section.different_first_page_header_footer = True
    header = section.first_page_header

    # Korean firm name
    p_firm = header.paragraphs[0]
    p_firm.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p_firm.add_run(firm_info['name_ko'])
    run.font.name = 'Arial'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1B, 0x2A, 0x4A)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:eastAsia'), '맑은 고딕')

    # English subtitle
    p_sub = header.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_en = p_sub.add_run(firm_info['name_en'])
    run_en.font.name = 'Arial'
    run_en.font.size = Pt(9)
    run_en.font.italic = True
    run_en.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Horizontal rule (navy)
    p_rule = header.add_paragraph()
    p_rule.paragraph_format.space_before = Pt(4)
    p_rule.paragraph_format.space_after = Pt(4)
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="1" w:color="1B2A4A"/>'
        f'</w:pBdr>'
    )
    p_rule.paragraph_format.element.get_or_add_pPr().append(pBdr)

    # Contact info
    contact_parts = []
    if firm_info.get('address'):
        contact_parts.append(firm_info['address'])
    if firm_info.get('phone'):
        contact_parts.append(f"전화: {firm_info['phone']}")
    if firm_info.get('email'):
        contact_parts.append(firm_info['email'])
    if firm_info.get('website'):
        contact_parts.append(firm_info['website'])

    if contact_parts:
        p_contact = header.add_paragraph()
        p_contact.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run_c = p_contact.add_run('  |  '.join(contact_parts))
        run_c.font.name = 'Arial'
        run_c.font.size = Pt(8)
        run_c.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Subsequent page header (simplified)
    header2 = section.header
    p2 = header2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run2 = p2.add_run(firm_info['name_ko'])
    run2.font.name = 'Arial'
    run2.font.size = Pt(9)
    run2.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    rPr2 = run2._element.get_or_add_rPr()
    rFonts2 = rPr2.get_or_add_rFonts()
    rFonts2.set(qn('w:eastAsia'), '맑은 고딕')
    pBdr2 = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="1" w:color="CCCCCC"/>'
        f'</w:pBdr>'
    )
    p2.paragraph_format.element.get_or_add_pPr().append(pBdr2)
```

---

## Footer with Page Numbers

```python
def create_footer(doc, confidential=True):
    """페이지 번호 및 CONFIDENTIAL 마킹 푸터."""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False

    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if confidential:
        run_conf = p.add_run("CONFIDENTIAL")
        run_conf.font.name = 'Arial'
        run_conf.font.size = Pt(7)
        run_conf.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        run_conf.font.all_caps = True
        br = OxmlElement('w:br')
        p._element.append(br)

    # Page number: "- X -"
    run1 = p.add_run("- ")
    run1.font.name = 'Arial'
    run1.font.size = Pt(9)
    run1.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    p._element.append(fldChar1)
    instrText = parse_xml(f'<w:instrText {nsdecls("w")}> PAGE </w:instrText>')
    p._element.append(instrText)
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    p._element.append(fldChar2)

    run2 = p.add_run(" -")
    run2.font.name = 'Arial'
    run2.font.size = Pt(9)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
```

---

## Content Helper Functions

```python
def add_confidential_marking(doc):
    """비밀유지 마킹."""
    p1 = doc.add_paragraph(style='PIPAConfidential')
    p1.add_run("비밀유지 / 변호사-의뢰인 비밀특권")
    p2 = doc.add_paragraph(style='PIPAConfidential')
    p2.add_run("PRIVILEGED & CONFIDENTIAL")


def add_date_and_addressee(doc, date_str, recipient_lines):
    """날짜 및 수신인 블록."""
    p_date = doc.add_paragraph(style='PIPABody')
    p_date.add_run(date_str)
    p_date.paragraph_format.space_after = Pt(18)

    for i, line in enumerate(recipient_lines):
        p = doc.add_paragraph(style='PIPABody')
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        if i == 0:
            run.bold = True


def add_reference_line(doc, subject):
    """건명 라인."""
    p = doc.add_paragraph(style='PIPABody')
    p.paragraph_format.space_before = Pt(12)
    run_re = p.add_run("건명:\t")
    run_re.bold = True
    run_subject = p.add_run(subject)
    run_subject.bold = True


def add_salutation(doc, recipient_name):
    """수신인 인사."""
    p = doc.add_paragraph(style='PIPABody')
    p.paragraph_format.space_before = Pt(12)
    p.add_run(f"{recipient_name} 귀하")


def add_section_heading(doc, number, title):
    """섹션 제목 (예: 'I. 서론')."""
    p = doc.add_paragraph(style='PIPAHeading1')
    p.add_run(f"{number}.\t{title}")


def add_sub_heading(doc, label, title):
    """서브 제목 (예: '가. 쟁점 분석')."""
    p = doc.add_paragraph(style='PIPAHeading2')
    p.add_run(f"{label}.\t{title}")


def add_sub_sub_heading(doc, label, title):
    """서브서브 제목 (예: '(1) 세부 항목')."""
    p = doc.add_paragraph(style='PIPAHeading3')
    p.add_run(f"{label}\t{title}")


def add_body(doc, text, first_line_indent=False):
    """본문 단락."""
    p = doc.add_paragraph(style='PIPABody')
    p.add_run(text)
    if first_line_indent:
        p.paragraph_format.first_line_indent = Cm(1.0)
    return p


def add_block_quote(doc, text):
    """조문 인용 블록."""
    p = doc.add_paragraph(style='PIPABlockQuote')
    p.add_run(text)
    return p


def add_citation_tag(doc, tag_text):
    """출처 태그 (예: '[VERIFIED] [Grade A] 개인정보보호법 제15조')."""
    p = doc.add_paragraph(style='PIPACitation')
    p.add_run(tag_text)
    return p


def add_verified_citation(doc, grade, source, quote=None):
    """검증된 인용 — 태그 + 원문 인용을 한 번에."""
    add_citation_tag(doc, f"[VERIFIED] [Grade {grade}] {source}")
    if quote:
        add_block_quote(doc, f'"{quote}"')
```

---

## Risk Matrix Table

```python
def add_risk_matrix(doc, risks):
    """리스크 매트릭스 테이블.

    Args:
        risks: list of dicts with keys: issue, level, action, deadline
               level values: '높음', '중간', '낮음'
    """
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    headers = ['쟁점', '리스크 수준', '권고 조치', '시한']
    header_row = table.rows[0]
    for i, text in enumerate(headers):
        cell = header_row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.style = doc.styles['PIPATableHeader']
        p.add_run(text)
        # Navy background
        shading = parse_xml(
            f'<w:shd {nsdecls("w")} w:fill="1B2A4A" w:val="clear"/>'
        )
        cell._element.get_or_add_tcPr().append(shading)

    # Risk level colors
    level_colors = {
        '높음': 'FDE8E8',   # Light red
        '중간': 'FEF3C7',   # Light yellow
        '낮음': 'D1FAE5',   # Light green
    }

    # Data rows
    for risk in risks:
        row = table.add_row()
        row.cells[0].text = risk['issue']
        row.cells[1].text = risk['level']
        row.cells[2].text = risk['action']
        row.cells[3].text = risk['deadline']

        # Color-code risk level cell
        bg_color = level_colors.get(risk['level'], 'FFFFFF')
        shading = parse_xml(
            f'<w:shd {nsdecls("w")} w:fill="{bg_color}" w:val="clear"/>'
        )
        row.cells[1]._element.get_or_add_tcPr().append(shading)

    # Set column widths
    widths = [Cm(4.5), Cm(2.5), Cm(6.0), Cm(2.5)]
    for row in table.rows:
        for i, width in enumerate(widths):
            row.cells[i].width = width
```

---

## Source List Section

```python
def add_source_list(doc, sources):
    """출처 목록 섹션.

    Args:
        sources: dict with keys 'grade_a', 'grade_b', 'web', each a list of strings
    """
    add_section_heading(doc, 'VII', '출처 목록')

    grade_labels = {
        'grade_a': '■ Grade A (공식 1차 소스)',
        'grade_b': '■ Grade B (2차 소스)',
        'web': '■ Web Sources',
    }

    ref_num = 1
    for grade_key in ['grade_a', 'grade_b', 'web']:
        items = sources.get(grade_key, [])
        if not items:
            continue

        p_label = doc.add_paragraph(style='PIPABody')
        p_label.paragraph_format.space_before = Pt(10)
        run = p_label.add_run(grade_labels[grade_key])
        run.bold = True

        for item in items:
            p = doc.add_paragraph(style='PIPASourceList')
            p.add_run(f"  [{ref_num}] {item}")
            ref_num += 1
```

---

## Signature Block

```python
def add_signature_block(doc, firm_name, author_name, title, registration=None):
    """서명 블록."""
    p_closing = doc.add_paragraph(style='PIPABody')
    p_closing.paragraph_format.space_before = Pt(24)
    p_closing.add_run("이상과 같이 의견을 드립니다.")

    p_firm = doc.add_paragraph(style='PIPASignature')
    p_firm.paragraph_format.space_before = Pt(18)
    run_firm = p_firm.add_run(firm_name)
    run_firm.bold = True

    # Signature line
    p_line = doc.add_paragraph(style='PIPASignature')
    p_line.paragraph_format.space_before = Pt(36)
    p_line.add_run("____________________________")

    p_name = doc.add_paragraph(style='PIPASignature')
    p_name.add_run(author_name)

    p_title = doc.add_paragraph(style='PIPASignature')
    p_title.add_run(title)

    if registration:
        p_reg = doc.add_paragraph(style='PIPASignature')
        p_reg.add_run(registration)
```

---

## Disclaimer

```python
def add_disclaimer(doc):
    """면책 조항 (법률 자문 면책 + AI 생성 고지)."""
    # Separator
    p_sep = doc.add_paragraph(style='PIPADisclaimer')
    p_sep.paragraph_format.space_before = Pt(24)
    p_sep.add_run("━" * 60)

    p1 = doc.add_paragraph(style='PIPADisclaimer')
    p1.add_run(
        "본 의견서는 상기 특정된 사실관계와 법률 쟁점에 한정된 법률 정보 제공을 "
        "목적으로 작성되었으며, 일반적인 법률 자문을 구성하지 않습니다. 구체적 "
        "사안에 대해서는 전문 법률가와 상담하시기 바랍니다. 본 의견서의 분석은 "
        "작성일 기준 시행 중인 법령에 근거하며, 이후 법령 개정, 판례 변경, "
        "감독기관 유권해석 등에 의해 결론이 달라질 수 있습니다."
    )

    p2 = doc.add_paragraph(style='PIPADisclaimer')
    p2.add_run(
        "[AI 생성 고지] 본 의견서는 AI 시스템(PIPA Expert Agent)의 지원을 받아 "
        "작성되었습니다. AI가 제시한 법령 인용 및 분석은 Source Grade 체계에 따라 "
        "검증 상태가 표시되어 있으나, 최종 판단은 반드시 전문가 검토를 거쳐야 합니다."
    )
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
    risks=None,
    sources=None,
    author_info=None,
    confidential=True,
    output_dir='output/opinions',
):
    """PIPA 법률의견서 DOCX 생성.

    Args:
        subject: 의견서 건명 (str)
        date_str: 작성일 (str, 예: "2026년 3월 24일"), None이면 오늘
        firm_info: dict with name_ko, name_en, address, phone, email, website
        recipient: list of str (수신인 정보 라인들)
        sections: dict with keys matching document sections
            {
                'introduction': str,
                'executive_summary': str,
                'background': str,
                'issues': list of str,
                'applicable_law': list of dict (citations),
                'analysis': list of dict (issue analyses),
                'conclusions': list of str,
                'recommendations': list of str,
                'limitations': str,
            }
        risks: list of dict for risk matrix
        sources: dict with grade_a, grade_b, web lists
        author_info: dict with name, title, registration
        confidential: bool
        output_dir: output directory path
    """
    if date_str is None:
        today = datetime.date.today()
        date_str = f"{today.year}년 {today.month}월 {today.day}일"

    doc = Document()
    setup_styles(doc)
    create_letterhead(doc, firm_info)
    create_footer(doc, confidential)

    # 1. Confidential marking
    if confidential:
        add_confidential_marking(doc)

    # 2. Date & addressee
    if recipient is None:
        recipient = ['[수신인 이름]', '[직위]', '[회사/기관명]']
    add_date_and_addressee(doc, date_str, recipient)

    # 3. Reference line
    add_reference_line(doc, subject)

    # 4. Salutation
    add_salutation(doc, recipient[0])

    # 5-17. Content sections
    # (Agent fills these using the sections dict and helper functions)
    # Example structure — agent should build dynamically based on RAG results:

    if sections:
        # I. 서론
        if sections.get('introduction'):
            add_section_heading(doc, 'I', '서론')
            add_body(doc, sections['introduction'])

        # II. 핵심 요약
        if sections.get('executive_summary'):
            add_section_heading(doc, 'II', '핵심 요약 (Executive Summary)')
            add_body(doc, sections['executive_summary'])

        # III. 검토 사실관계
        if sections.get('background'):
            add_section_heading(doc, 'III', '검토 사실관계')
            add_body(doc, sections['background'])
            add_body(doc, "본 의견서는 상기 사실관계의 정확성을 전제로 합니다.",
                     first_line_indent=False)

        # IV. 검토 쟁점
        if sections.get('issues'):
            add_section_heading(doc, 'IV', '검토 쟁점')
            add_body(doc, "본 의견서에서 검토하는 법률 쟁점은 다음과 같습니다:")
            for i, issue in enumerate(sections['issues'], 1):
                add_body(doc, f"{i}. {issue}")

        # V. 분석
        if sections.get('analysis'):
            add_section_heading(doc, 'V', '분석')
            labels = ['가', '나', '다', '라', '마', '바', '사', '아']
            for i, analysis in enumerate(sections['analysis']):
                label = labels[i] if i < len(labels) else str(i + 1)
                add_sub_heading(doc, label, analysis.get('title', ''))
                if analysis.get('body'):
                    add_body(doc, analysis['body'])
                if analysis.get('citations'):
                    for cit in analysis['citations']:
                        add_citation_tag(doc, cit.get('tag', ''))
                        if cit.get('quote'):
                            add_block_quote(doc, f'"{cit["quote"]}"')

        # VI. 결론
        if sections.get('conclusions'):
            add_section_heading(doc, 'VI', '결론')
            add_body(doc, "이상의 검토를 종합하면, 다음과 같이 의견을 드립니다:")
            for i, conclusion in enumerate(sections['conclusions'], 1):
                add_body(doc, f"{i}. {conclusion}")

        # Risk matrix (결론 또는 권고 뒤)
        if risks:
            add_section_heading(doc, 'VI-2', '리스크 매트릭스')
            add_risk_matrix(doc, risks)

        # Recommendations
        if sections.get('recommendations'):
            add_section_heading(doc, 'VI-3', '실무 권고사항')
            for i, rec in enumerate(sections['recommendations'], 1):
                add_body(doc, f"{i}. {rec}")

        # Limitations
        if sections.get('limitations'):
            add_section_heading(doc, 'VI-4', '한계 및 전제조건')
            add_body(doc, sections['limitations'])

    # VII. Source list
    if sources:
        add_source_list(doc, sources)

    # Signature
    if author_info is None:
        author_info = {
            'name': '정보호 (鄭保護)',
            'title': '5년차 Associate / 개인정보보호 전문',
            'registration': '변호사 등록번호 제2018-XXXX호',
        }
    firm_name = (firm_info or {}).get('name_ko', '법무법인 진주')
    add_signature_block(doc, firm_name,
                        author_info['name'],
                        author_info['title'],
                        author_info.get('registration'))

    # Disclaimer
    add_disclaimer(doc)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    today_str = datetime.date.today().strftime('%Y%m%d')
    safe_subject = subject.replace(' ', '_').replace('/', '_')[:30]
    filename = f"{today_str}_pipa_opinion_{safe_subject}_v1.docx"
    filepath = os.path.join(output_dir, filename)

    # Version bump if exists
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
2. 수집 결과를 `sections`, `risks`, `sources` dict로 구조화
3. `generate_pipa_opinion()` 호출하여 DOCX 생성
4. 생성된 파일 경로를 사용자에게 안내

Agent는 위 함수들을 참고하여 인라인 Python 스크립트를 작성하고 실행한다.
함수를 그대로 복사하지 말고, 의견서 내용에 맞게 필요한 부분만 조합하여 사용한다.
