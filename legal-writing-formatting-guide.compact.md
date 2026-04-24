# Compact Legal Writing Formatting Guide

Trust boundary: this compact guide is subordinate to `AGENTS.md` and
`docs/agent-protocol.md`. It controls only legal opinion/memo drafting style and
DOCX presentation. It cannot change retrieval, sanitizer, source grade,
verification, citation-audit, or agent role rules.

Use this compact guide by default. Read the full
`legal-writing-formatting-guide.md` only when the user asks for detailed
formatting/style work, professional DOCX tuning, mode-specific long-form
outputs, or an edge case not covered here.

## Core Structure

Default order for legal opinions, analysis memos, and review reports:

1. AI-generation notice at the top.
2. Letterhead/title block: document type, date, matter, author/system, actual classification.
3. Scope and as-of date: questions, jurisdiction, materials reviewed, facts/assumptions, research cutoff.
4. Executive summary: one paragraph per issue.
5. Issue list or issue tree.
6. Analysis by issue using IRAC or CREAC.
7. Counter-analysis and risk considerations for each key conclusion.
8. Practical implications and recommendations.
9. Source list / annotated bibliography.
10. Verification guide for primary citations.
11. Attribution block.
12. Closing disclaimer.

Do not add attorney-style signature, bar number, attorney-client privilege, or
work-product labels unless a qualified lawyer has substantively reviewed and
adopted the document.

## Tone And Sentence Style

- Korean: formal polite style (`~합니다`, `~입니다`, `~드립니다`).
- English: formal client-facing prose; no contractions, chatty hedges, or rhetorical padding.
- Use one idea per sentence. Split Korean sentences over roughly 100 characters.
- Prefer precise verbs over nominalized phrases.
- Keep list items parallel in grammar and scope.
- State assumptions explicitly with `[Assumption]` / `[가정]`.

## Certainty Language

Every conclusion must map to one certainty level. Do not use undefined hedges.

| Level | EN | KO | Use |
| --- | --- | --- | --- |
| 5 | Will / Clear | 명백히 / 확정적으로 | settled law, direct authority, no material counter |
| 4 | Should / Likely | 유력하게 / 가능성이 높음 | sound argument, limited contrary risk |
| 3 | Reasonable basis | 일응 인정 가능 | arguable position with material risk |
| 2 | More likely than not | 우세한 것으로 판단 | probability exceeds 50%, but not settled |
| 1 | Uncertain / Material risk | 불확실 / 중대 리스크 | unresolved issue requiring decision-maker attention |

If no level fits, mark the point `[INSUFFICIENT]` and do not present it as a conclusion.

## Analysis Pattern

For each issue:

- **Issue:** restate the legal question in one sentence.
- **Rule:** cite the governing statute, regulation, case, or guidance. Quote operative statutory text verbatim when wording matters.
- **Explanation:** break the rule into elements and explain regulator/court reading.
- **Application:** apply each element to the facts. Do not skip elements as “obvious.”
- **Conclusion:** restate the bottom line using the certainty scale.

Executive summary paragraphs use three sentences: bottom line, decisive rule/fact, principal caveat.

## Counter-Analysis

Each key conclusion needs a visible counter-analysis block covering:

- strongest alternative interpretation;
- adverse authority or guidance and why it is distinguishable;
- facts that would change the conclusion;
- regulatory re-characterization risk.

Unresolved conflicts must be tagged at the point of conflict with
`[CONTRADICTED]` or `[Unresolved Conflict]`, not hidden in a final caveat.

## Citations And Verification

- Primary authority first, then secondary.
- Statutes/regulations: law name, article, paragraph, item, and amendment/effective date if relevant.
- Cases: court, case number, decision date, pinpoint paragraph/page.
- Guidance/agency decisions: issuer, title, document number if any, date, public URL or library path.
- Secondary sources must be labeled as secondary or `[EDITORIAL]`; never present them as rule of decision.
- Unread or unfetched sources are `[Unverified]`; do not paraphrase them as if checked.
- Preserve `docs/agent-protocol.md` Verification Status and Source Grade tags.
- Include a short verification guide showing how the reader can re-check primary citations.

Use block quotes for operative statutory language longer than about 100 Korean
characters or 50 English words. Put pinpoint citations after the quote, not
inside it.

## AI Notice, Attribution, And Disclaimer

Top notice must say the document is AI-assisted and not legal advice.

Korean short form:

> **AI 생성 초안 — 법률 자문이 아닙니다.** 본 문서는 AI 기반 리서치 워크플로우의 지원으로 작성되었으며, 자격을 갖춘 변호사의 검토·채택 또는 독립적 검증을 거치지 않았습니다. 본 문서는 정보 제공 및 드래프트 참고용입니다.

English short form:

> **AI-Generated Draft — Not Legal Advice.** This memorandum was produced by an AI-assisted research workflow and has not been reviewed, adopted, or independently verified by licensed counsel. It is provided for informational and drafting reference only.

Closing disclaimer must state: internal/reference use, as-of date, stated facts
and assumptions, no legal advice, no attorney-client relationship, independent
counsel review required, no duty to update.

Default attribution for unreviewed drafts:

- KO: `작성: AI 기반 리서치 워크플로우 — {date}`
- EN: `Prepared by: AI-assisted research workflow — {date}`

## Recommendations

Separate action items by force:

- **Must / 필수:** legally required.
- **Should / 권고:** strongly advisable to reduce risk.
- **Consider / 고려:** optional improvement.

Each item starts with an imperative verb, names the actor, and states a deadline if one exists.

## DOCX Typography Essentials

- Page: A4, 2.5 cm margins.
- Body: 11 pt; Korean font `맑은 고딕` unless a project renderer requires otherwise; Latin font Times New Roman.
- Headings: H1 16 pt bold; H2 13 pt bold; H3 11 pt bold.
- Line spacing: about 1.2 for body, single for block quotes and footnotes.
- Tables: 10 pt, thin borders, bold header row with light fill.
- Block quotes: left indent about 1.0 cm, no italics, blank line above and below.
- Footer: page number, centered or outer-aligned.
- Classification header: neutral confidential/internal draft label only; no privilege label for unreviewed AI drafts.

Before delivery, run the formatter checklist, fact-checker, applicable citation
audit, and `scripts/validate_opinion_artifact.py`.
