<div align="center">

**[English](#pipa-expert-agent)** · **[한국어](README.ko.md)**

# PIPA Expert Agent

### KP Legal Orchestrator's Korean Data Privacy Specialist

**929 searchable statute files** · **46 official guidelines** · **30 landmark case law & interpretations** · **Professional-format DOCX analysis memos**

Built for [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) · Powered by structured RAG · **[How to Use](docs/en/HOW-TO-USE.md)**

[![Statute Files](https://img.shields.io/badge/Statute_Files-929-blue)](#-knowledge-base)
[![Guidelines](https://img.shields.io/badge/PIPC_Guidelines-46-green)](#-knowledge-base)
[![Grade B Sources](https://img.shields.io/badge/Grade_B_Sources-30-yellow)](#-knowledge-base)
[![Cross-ref Edges](https://img.shields.io/badge/Cross--Ref_Edges-2%2C369-orange)](#-knowledge-base)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](#license)

<br/>

> *"Data structure is intelligence."*
> — The philosophy behind this project: smarter data beats smarter search.

</div>

> [!CAUTION]
> **This tool is for legal research assistance only — it does not provide legal advice.** Outputs are AI-generated and may contain errors despite built-in verification. All legal citations should be independently verified before reliance. Consult a qualified attorney for advice on specific legal matters. **[Full Disclaimer](docs/en/DISCLAIMER.md)** · **[면책사항](docs/ko/DISCLAIMER.md)**

---

## The Problem

Existing AI legal assistants (ChatGPT Custom GPTs, Gemini Gems, etc.) treat legislation as flat text documents. They upload PDFs, run semantic search, and hope for the best. This approach **fundamentally fails** for legal work because it ignores:

- **Hierarchical structure** — statutes have articles, paragraphs, subparagraphs, and items
- **Cross-references** — Article 15 delegates to Enforcement Decree Article 17
- **Source authority** — a PIPC guideline ≠ a news article ≠ an academic paper
- **Verification** — every citation must be traceable to the exact provision

The result? Hallucinated article numbers, fabricated provisions, and analysis memos teams cannot safely rely on.

---

## The Solution

PIPA Expert takes a different approach: **instead of smarter search, build smarter data.**

```mermaid
graph TB
    subgraph agent["<b>PIPA Expert Agent</b><br/>Privacy Specialist · KP Legal Orchestrator"]
        direction TB

        subgraph core["Core Capabilities"]
            direction LR
            KB["<b>Structured Knowledge Base</b><br/>929 Statute Files · 46 Guidelines<br/>30 Case Law &amp; Interpretations"]
            WS["<b>Multi-Layer Web Search</b><br/>Law firm analyses · Academic · DPAs<br/>Cross-Reference Verification"]
            DX["<b>DOCX Analysis Memo Generator</b><br/>Professional-format Documents<br/>Verified Citations"]
        end

        subgraph pipeline["Research Pipeline"]
            direction LR
            S1["1️⃣ KB Search<br/><i>Article & Guideline Index</i>"]
            S2["2️⃣ Cross-Reference<br/><i>Follow delegation chains</i>"]
            S3["3️⃣ Web Search<br/><i>4-layer trusted sources</i>"]
            S4["4️⃣ Adversarial Check<br/><i>Pass A vs Pass B</i>"]
            S1 --> S2 --> S3 --> S4
        end

        subgraph grades["Source Grade System"]
            direction LR
            GA["<b>Grade A</b> ✅<br/>Statutes · Guidelines<br/><i>Sole authority</i>"]
            GB["<b>Grade B</b> 🔍<br/>Case Law · Enforcement<br/><i>Cross-verify with A</i>"]
            GC["<b>Grade C</b> 📝<br/>Law firm analyses · Academic<br/><i>Editorial only</i>"]
            GD["<b>Grade D</b> 🚫<br/>News · AI Summaries<br/><i>Excluded from RAG</i>"]
        end
    end

    Q["❓ User Question"] --> S1
    S4 --> O["📄 Verified Legal Analysis Memo"]

    style agent fill:#f8fafc,stroke:#1B2A4A,stroke-width:2px,color:#1B2A4A
    style core fill:#eef2ff,stroke:#4f46e5,stroke-width:1px
    style pipeline fill:#f0fdf4,stroke:#16a34a,stroke-width:1px
    style grades fill:#fffbeb,stroke:#d97706,stroke-width:1px
    style KB fill:#dbeafe,stroke:#2563eb,color:#1e40af
    style WS fill:#dbeafe,stroke:#2563eb,color:#1e40af
    style DX fill:#dbeafe,stroke:#2563eb,color:#1e40af
    style GA fill:#d1fae5,stroke:#059669,color:#065f46
    style GB fill:#fef3c7,stroke:#d97706,color:#92400e
    style GC fill:#fee2e2,stroke:#dc2626,color:#991b1b
    style GD fill:#f3f4f6,stroke:#6b7280,color:#374151
    style Q fill:#ede9fe,stroke:#7c3aed,color:#5b21b6
    style O fill:#d1fae5,stroke:#059669,color:#065f46
    style S1 fill:#f0fdf4,stroke:#16a34a,color:#166534
    style S2 fill:#f0fdf4,stroke:#16a34a,color:#166534
    style S3 fill:#f0fdf4,stroke:#16a34a,color:#166534
    style S4 fill:#f0fdf4,stroke:#16a34a,color:#166534
```

---

## Knowledge Base

### Official Legislation — via Open Law API

Every statute is fetched from Korea's [National Law Information Center](https://law.go.kr) Open API, parsed into **searchable article-level Markdown files** with YAML frontmatter, and enriched with keyword extraction and cross-reference mapping.

| Law | Searchable Files | Hierarchy Entries | Extracted Cross-Ref Edges | Directory |
|-----|------------------|-------------------|---------------------------|-----------|
| **Personal Information Protection Act (PIPA)** | 126 | 126 | 301 | `library/grade-a/pipa/` |
| PIPA Enforcement Decree | 140 | 140 | 406 | `library/grade-a/pipa-enforcement-decree/` |
| Network Act (정보통신망법) | 142 | 142 | 188 | `library/grade-a/network-act/` |
| Network Act Enforcement Decree | 131 | 131 | 266 | `library/grade-a/network-act-enforcement-decree/` |
| Network Act Enforcement Rule | 11 | 11 | 20 | `library/grade-a/network-act-enforcement-rule/` |
| Credit Information Act (신용정보법) | 91 | 91 | 326 | `library/grade-a/credit-info-act/` |
| Credit Information Act Enforcement Decree | 81 | 81 | 435 | `library/grade-a/credit-info-act-enforcement-decree/` |
| Location Information Act (위치정보법) | 53 | 53 | 159 | `library/grade-a/location-info-act/` |
| Location Information Act Enforcement Decree | 55 | 55 | 164 | `library/grade-a/location-info-act-enforcement-decree/` |
| E-Government Act (전자정부법) | 99 | 99 | 104 | `library/grade-a/e-government-act/` |
| **Total** | **929** | **929** | **2,369** | |

> [!IMPORTANT]
> Re-ingest status as of March 27, 2026: the default active corpus has been slimmed back down to the directly privacy-related statute sets only, `article-index.json` now exposes 929 searchable statute files, the active law sets in `source-registry.json` all report `count == target`, same-law internal cross-reference misses remain at 0, `cross-reference-graph.json` aggregates 1,309 cross-law edges (869 resolved to local corpus), and `external-law-candidates.json` prioritizes 154 out-of-corpus statutes for optional expansion (8 high priority). Larger general-law corpora are intentionally kept out of the default KB unless explicitly requested. The repealed `pipa-enforcement-rule` source is intentionally excluded and tracked as `retired`.
> Detailed log: [docs/2026-03-27-quality-audit-log.md](docs/2026-03-27-quality-audit-log.md)

> **Retired source:** `library/grade-a/pipa-enforcement-rule/` is a repealed statute set and is intentionally excluded from ingest.

### PIPC Official Guidelines — 46 Documents

All publicly available guidelines from the Personal Information Protection Commission (PIPC), converted from PDF to structured Markdown with frontmatter metadata.

<details>
<summary><b>Full list of 46 guidelines</b></summary>

| # | Title |
|---|-------|
| 01 | Commentary on PIPA (법령해설서) |
| 02 | Integrated Processing Guide (처리 통합 안내서) |
| 03 | Sector-Specific Guide (공공/민간) |
| 04 | Emergency Processing (재난/감염병) |
| 05 | Children & Adolescents Protection |
| 06 | Internet Content Access Exclusion Right |
| 07 | Automated Decision-Making |
| 08 | Safety Standards |
| 09 | Developer Privacy |
| 10 | Biometric Information |
| 11 | Fixed Video Surveillance |
| 12 | Mobile Surveillance |
| 13 | Smart City |
| 14 | Website Exposure Prevention |
| 15 | Synthetic Data Utilization |
| 16 | Pseudonymization Guidelines |
| 17 | Pseudonymization (Public Sector) |
| 18 | Pseudonymization (Education) |
| 19 | Healthcare/Medical Data |
| 20 | Synthetic Data Reference Model |
| 21 | AI Development (Public Data) |
| 22 | AI Privacy Risk Assessment |
| 23 | Generative AI Processing |
| 24 | Privacy Policy Drafting |
| 25 | Privacy Impact Assessment |
| 26 | PIA Cost Estimation |
| 27 | ISMS-P Certification |
| 28 | Privacy Education |
| 29 | Breach Response Manual |
| 30 | Foreign Business PIPA Application (KR + EN) |
| 31 | Liability Insurance |
| 32 | Q&A Compilation |
| 33 | Data Portability |
| 34-36 | Management Agency Designation |
| 37 | General Data Recipient Registration |
| 38 | MyData Transfer Procedures |
| 39a-c | Industry-Specific Guides |
| 40 | Small Business Handbook |
| 41a-c | Standard Privacy Policy Templates |

</details>

### Grade B — Landmark Case Law & Interpretations (30 items)

Grade B secondary sources are fetched from Korea's Open Law API (`korean-law` MCP) with real citations, case numbers, and `VERIFIED` verbatim text. Initial landmark collection covers 6 core topics: consent, third-party provision, safety measures & breach, pseudonymized data, sensitive info, and unique identifiers.

| Category | Count | Publisher | Directory |
|----------|-------|-----------|-----------|
| **Supreme Court Precedents** | 10 | 대법원 | `library/grade-b/court-precedents/` |
| **Statutory Interpretations** | 20 | 법제처 (MOLEG) | `library/grade-b/legal-interpretations/` |
| **Total** | **30** | | |

<details>
<summary><b>Court precedents (10 landmark cases)</b></summary>

| Case No. | Date | Topic |
|----------|------|-------|
| 2014다235080 (LAW&B) | 2016-08-17 | Scope of consent for publicly available personal info |
| 2015다24904 (Nate/Cyworld) | 2018-01-25 | Data breach damages — technical/administrative safeguards |
| 2017다219232 (Google) | 2023-04-13 | Third-party provision disclosure request |
| 2018다262103 (Homeplus) | 2024-05-17 | Sweepstakes data sold to insurers |
| 2020도14713 (CSAT supervisor) | 2025-02-13 | "Recipient of personal info" definition |
| 2022두68923 | 2023-10-12 | Breach administrative fine revocation |
| 2023다311184 | 2025-12-04 | PIPA §39-2 statutory damages |
| 2024다210554 | 2025-07-18 | Pseudonym processing stop request |
| 2024도8121 | 2025-12-11 | CCTV footage third-party provision |
| 2013두2945 (RRN change) | 2017-06-15 | Right to change resident registration number |

</details>

<details>
<summary><b>Statutory interpretations (20 MOLEG rulings)</b></summary>

Core topics: §22 consent structure, §18(2) "other laws special provisions" scope (7 rulings), §35 access request, §31 DPO transition, §2 processor scope, §28-2 pseudonymization, §23 sensitive info (2), §24-2 resident registration number (4).

</details>

> [!NOTE]
> Grade B `pipc-decisions/` directory remains empty pending MCP endpoint recovery. The `get_pipc_decision_text` endpoint returns empty responses — once fixed, an additional ~20 PIPC disposition cases will be collected per the original plan.

### How the Data is Structured

Every article is stored as a standalone `.md` file with rich frontmatter:

```yaml
---
law: "개인정보 보호법"
article: 15
article_title: "개인정보의 수집ㆍ이용"
source_grade: "A"
effective_date: "20251002"
cross_references:
  - "제17조"
  - "제22조"
keywords:
  - "수집"
  - "동의"
  - "정당한 이익"
---

## 제15조(개인정보의 수집ㆍ이용)

① 개인정보처리자는 다음 각 호의 어느 하나에 해당하는 경우에는...
```

This means the AI agent can:
- **Search by keyword** using the index files
- **Follow cross-references** to related articles
- **Verify source authority** via the grade system
- **Read exact provisions** without hallucination

---

## How It Works

```mermaid
flowchart TD
    Q["❓ <b>User Question</b>"]

    subgraph kb["Step 1–3: Knowledge Base Search"]
        direction TB
        S1["📚 <b>Article Search</b><br/><code>article-index.json</code> → relevant statutes"]
        S2["📖 <b>Guideline Search</b><br/><code>guideline-index.json</code> → PIPC guidance"]
        S3["🔗 <b>Cross-Reference Tracking</b><br/><code>cross-reference-graph.json</code> → delegated provisions"]
        S1 --> S2 --> S3
    end

    subgraph web["Step 4: Multi-Layer Web Search <i>(if KB insufficient)</i>"]
        direction TB
        L1["🏛️ <b>Layer 1 · Statutes</b><br/>law.go.kr · pipc.go.kr"]
        L2["⚖️ <b>Layer 2 · Major Law Firm Analyses</b><br/>Top-tier Korean law firm<br/>newsletters &amp; articles"]
        L3["🎓 <b>Layer 3 · Academic</b><br/>KCI · RISS · SSRN"]
        L4["🌍 <b>Layer 4 · Foreign DPAs</b><br/>EDPB · ICO · IAPP"]
        L1 --> L2 --> L3 --> L4
    end

    subgraph verify["Adversarial Cross-Verification"]
        direction LR
        PA["✅ <b>Pass A</b><br/>Supporting evidence"]
        PB["⚠️ <b>Pass B</b><br/>Counterarguments<br/>&amp; exceptions"]
        PA <--> PB
    end

    O["📄 <b>Verified Legal Analysis Memo</b><br/>DOCX with citations &amp; risk matrix"]

    Q --> kb
    kb --> web
    web --> verify
    verify --> O

    style Q fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#5b21b6
    style kb fill:#eff6ff,stroke:#2563eb,stroke-width:1px
    style web fill:#fefce8,stroke:#ca8a04,stroke-width:1px
    style verify fill:#fef2f2,stroke:#dc2626,stroke-width:1px
    style O fill:#d1fae5,stroke:#059669,stroke-width:2px,color:#065f46
    style S1 fill:#dbeafe,stroke:#3b82f6,color:#1e40af
    style S2 fill:#dbeafe,stroke:#3b82f6,color:#1e40af
    style S3 fill:#dbeafe,stroke:#3b82f6,color:#1e40af
    style L1 fill:#fef9c3,stroke:#ca8a04,color:#713f12
    style L2 fill:#fef9c3,stroke:#ca8a04,color:#713f12
    style L3 fill:#fef9c3,stroke:#ca8a04,color:#713f12
    style L4 fill:#fef9c3,stroke:#ca8a04,color:#713f12
    style PA fill:#dcfce7,stroke:#16a34a,color:#166534
    style PB fill:#fee2e2,stroke:#ef4444,color:#991b1b
```

Every citation is tagged with its verification status:

| Tag | Meaning |
|-----|---------|
| `[VERIFIED]` | Exact match in Grade A source |
| `[UNVERIFIED]` | Grade B only, or partial match |
| `[INSUFFICIENT]` | Not enough evidence — left blank |
| `[CONTRADICTED]` | Sources conflict — both sides shown |

---

## Fact-Check Layer (Hallucination Prevention)

Before any output is finalized, a **dedicated fact-checker sub-agent** verifies every legal citation against the knowledge base:

| Check | Method | On Fail |
|-------|--------|---------|
| Article exists | Glob for `art{N}.md` in KB | Downgrade to `[UNVERIFIED]` |
| Quoted text matches source | Read file, substring match | Replace with correct text |
| Article number is precise | Frontmatter `article` + `article_title` match | Correct the number |
| Effective date is valid | Compare `effective_date` to today | Add `[미시행]` warning |
| Guideline citation exists | Check `guideline-index.json` | Downgrade or remove |
| Cross-reference is valid | Verify target file exists | Flag broken reference |
| Web source is trusted | Match against trusted domain list | Downgrade Grade |

**Confidence score:** If below 70%, FAIL items are corrected and re-verified before output. Citations affecting core conclusions are withdrawn rather than left unverified.

---

## DOCX Legal Analysis Memo Generator

The agent produces **professional-format Word documents** with:

- KP Legal Orchestrator letterhead
- Structured sections: Issues → Analysis → Conclusions → Recommendations
- Risk matrix tables with color coding
- Full citation trail with verification status
- Fact-check report appended
- Signature block and disclaimer
- AI disclosure notice

---

## Source Ingest System

### Adding Your Own Sources

1. Drop any file (PDF, DOCX, etc.) into `${PIPA_INBOX_DIR:-library/inbox/}`
2. Tell the agent: `/ingest` or "파일 넣었어"
3. The agent will automatically:

```
${PIPA_INBOX_DIR:-library/inbox/}    ← drop files here
     │
     ▼ /ingest or "파일 넣었어"
     │
     ├─ Auto-convert to Markdown (via MarkItDown)
     ├─ Auto-classify Grade (A/B/C based on content signals)
     ├─ Auto-generate frontmatter (keywords, citations, metadata)
     ├─ Place in library/grade-{a,b,c}/
     └─ Update search indexes
```

> **Note:** Dropping files alone does not trigger processing. You must run `/ingest` or tell the agent (e.g. "inbox에 파일 넣었어") to start the parsing pipeline.

---

## Project Structure

```
PIPA-expert/
├── library/
│   ├── inbox/                    # Drop zone for new sources
│   ├── grade-a/                  # Authoritative sources
│   │   ├── pipa/                 #   PIPA searchable files (126)
│   │   ├── pipa-enforcement-decree/  #   Enforcement Decree files (140)
│   │   ├── network-act/          #   Network Act files (142)
│   │   ├── pipc-guidelines/      #   Official guidelines (46)
│   │   └── ...                   #   + 7 more statute sets, 1 retired
│   ├── grade-b/                  # Case law & interpretations (30)
│   │   ├── court-precedents/     #   Supreme Court decisions (10)
│   │   ├── legal-interpretations/ #  MOLEG statutory interpretations (20)
│   │   └── pipc-decisions/       #   PIPC dispositions (pending)
│   └── grade-c/                  # Law firm analysis, academic papers
├── index/
│   ├── article-index.json        # Searchable statute index (929 entries)
│   ├── cross-reference-graph.json # Cross-law reference graph (1,309 edges)
│   ├── external-law-candidates.json # Out-of-corpus law expansion queue (154 candidates)
│   ├── guideline-index.json      # Guideline index (46 entries)
│   └── source-registry.json      # Collection status dashboard
├── config/
│   ├── source-grades.json        # A/B/C/D grade definitions
│   └── rag-config.json           # Search configuration
├── scripts/
│   ├── fetch-pipa-from-api.py    # Open Law API collector
│   ├── preprocess_guidelines.py  # PDF → Markdown pipeline
│   └── build-guideline-index.py  # Index generator
├── .claude/
│   ├── agents/pipa-agent.md      # Agent definition
│   └── skills/
│       ├── legal-opinion-formatter/  # DOCX generation skill
│       └── ingest/               # Source ingestion skill
├── ${PIPA_OUTPUT_DIR:-output/opinions/}  # Generated DOCX opinions
└── docs/                         # Design specs
```

---

## Getting Started

> **New here?** Read the **[How to Use Guide](docs/en/HOW-TO-USE.md)** — a step-by-step walkthrough for non-developers.

### Prerequisites

- [Claude Code](https://claude.ai/claude-code) CLI
- Python 3.10+
- `python-docx` (`pip install python-docx`)

### Setup

```bash
git clone <repository-url>
cd PIPA-expert
pip install python-docx
```

Use the current repository URL from your Git hosting page.

### Refresh Law Data (Monthly)

```bash
python3 scripts/fetch-pipa-from-api.py --oc YOUR_EMAIL_ID
```

Requires a free [Open Law API](https://open.law.go.kr) account. The `--oc` parameter is your registered email ID.

### Run the Agent

```bash
cd PIPA-expert
claude   # launches Claude Code in this directory
```

Then use `/agents/pipa-agent` to activate the privacy specialist persona.

### Example Queries

```
"개인정보보호법 제15조 보여줘"
"맞춤형 광고 동의 구조 재설계 방안 분석 메모 작성해줘"
"정보통신망법과 개인정보보호법의 동의 규정 차이점"
"제3자 제공 관련 법률 분석 메모 DOCX로 만들어줘"
```

---

## Part of KP Legal Orchestrator

PIPA Expert is one of several specialized legal workflow agents operating under **KP Legal Orchestrator**:

| Agent | Role | Focus |
|-------|------|-------|
| `game-legal-research` | Game Industry Research Specialist | Game industry law |
| `legal-translation-agent` | Legal Translation Specialist | Legal translation |
| `general-legal-research` | General Legal Research Specialist | Legal research |
| **PIPA-expert** | **Privacy Specialist** | **Data privacy law** |
| `GDPR-expert` | EU Data Protection Specialist | EU data protection law |
| `contract-review-agent` | Contract Review Specialist | Contract review |
| `legal-writing-agent` | Legal Drafting Specialist | Legal writing |
| `second-review-agent` | Senior Review Specialist | Quality review |

---

## License

Licensed under the [Apache License, Version 2.0](LICENSE).

---

<div align="center">
<sub>Built with structured data, not blind faith in embeddings.</sub>
</div>
