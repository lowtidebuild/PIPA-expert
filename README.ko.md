<div align="center">

**[English](README.md)** · **[한국어](#pipa-expert-agent)**

# PIPA Expert Agent

### KP Legal Orchestrator의 AI 개인정보보호 워크플로우 시스템

**929개 검색 가능한 법조문 파일** · **46건 공식 가이드라인** · **30건 landmark 판례·해석례** · **전문 형식 DOCX 분석 메모**

[Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) 전용 · 구조화된 RAG 기반 · **[사용 가이드](docs/ko/HOW-TO-USE.md)**

[![Statute Files](https://img.shields.io/badge/조문파일-929개-blue)](#-knowledge-base-법령-라이브러리)
[![Guidelines](https://img.shields.io/badge/PIPC_가이드라인-46건-green)](#-knowledge-base-법령-라이브러리)
[![Grade B Sources](https://img.shields.io/badge/Grade_B_소스-30건-yellow)](#-knowledge-base-법령-라이브러리)
[![Cross-ref Edges](https://img.shields.io/badge/교차참조_엣지-2%2C369개-orange)](#-knowledge-base-법령-라이브러리)

<br/>

> *"데이터 구조가 곧 지능이다."*
> — 더 똑똑한 검색이 아니라, 더 똑똑한 데이터를 추구합니다.

</div>

> [!CAUTION]
> **본 도구는 법률 리서치 보조 도구이며, 법률 자문을 제공하지 않습니다.** 출력물은 AI가 생성한 것으로, 검증 시스템이 내장되어 있으나 오류가 포함될 수 있습니다. 모든 법령 인용은 실제 활용 전 독립적으로 확인하시기 바랍니다. 구체적 법률 사안에 대해서는 반드시 전문 법률가와 상담하십시오. **[Disclaimer](docs/en/DISCLAIMER.md)** · **[면책사항](docs/ko/DISCLAIMER.md)**

---

## 문제 인식

기존 AI 법률 어시스턴트(ChatGPT Custom GPT, Gemini Gem 등)는 법령을 단순 텍스트 문서로 취급합니다. PDF를 업로드하고, 의미 검색을 돌리고, 결과를 기대합니다. 이 방식은 법률 업무에 **근본적으로 부적합**합니다:

- **계층 구조 무시** — 법률은 조·항·호·목의 계층을 가짐
- **교차참조 단절** — 제15조가 시행령 제17조에 위임하는 관계를 모름
- **소스 권위 미구분** — PIPC 가이드라인과 뉴스 기사를 동일하게 취급
- **검증 불가** — 인용된 조문 번호가 실제로 존재하는지 확인할 수 없음

결과? 환각된 조문 번호, 조작된 규정, 그대로 의사결정에 쓰기 어려운 분석 메모.

---

## 해결 방안

PIPA Expert는 다른 접근을 취합니다: **더 똑똑한 검색 대신, 더 똑똑한 데이터를 구축합니다.**

```mermaid
graph TB
    subgraph agent["<b>PIPA Expert Agent</b><br/>개인정보 스페셜리스트 · KP Legal Orchestrator"]
        direction TB

        subgraph core["핵심 기능"]
            direction LR
            KB["<b>구조화된 Knowledge Base</b><br/>929개 법조문 · 46건 가이드라인<br/>30건 판례·해석례"]
            WS["<b>Multi-Layer 웹서치</b><br/>주요 로펌 해설 · 학술 · 해외 DPA<br/>교차검증"]
            DX["<b>DOCX 분석 메모 생성</b><br/>전문 형식 문서<br/>검증된 인용 체계"]
        end

        subgraph pipeline["리서치 파이프라인"]
            direction LR
            S1["1️⃣ KB 검색<br/><i>조문·가이드라인 인덱스</i>"]
            S2["2️⃣ 교차참조 추적<br/><i>위임 조문 체인 탐색</i>"]
            S3["3️⃣ 웹서치<br/><i>4단계 신뢰도 기반</i>"]
            S4["4️⃣ Adversarial 검증<br/><i>Pass A vs Pass B</i>"]
            S1 --> S2 --> S3 --> S4
        end

        subgraph grades["Source Grade 체계"]
            direction LR
            GA["<b>Grade A</b> ✅<br/>법령 원문 · 가이드라인<br/><i>단독 근거 가능</i>"]
            GB["<b>Grade B</b> 🔍<br/>판례 · 처분례<br/><i>A 교차검증 권장</i>"]
            GC["<b>Grade C</b> 📝<br/>로펌 해설 · 학술 논문<br/><i>단독 근거 불가</i>"]
            GD["<b>Grade D</b> 🚫<br/>뉴스 · AI 요약<br/><i>RAG 미포함</i>"]
        end
    end

    Q["❓ 사용자 질문"] --> S1
    S4 --> O["📄 검증된 법률 분석 메모"]

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

## Knowledge Base (법령 라이브러리)

### 공식 법령 — Open Law API 수집

대한민국 [국가법령정보센터](https://law.go.kr) Open API에서 현행 법령을 수집하여, **검색 가능한 조문 단위 Markdown 파일**로 파싱 및 구조화합니다. 각 파일에 YAML frontmatter(키워드, 교차참조, 시행일 등)가 포함됩니다.

| 법령 | 검색 가능 파일 수 | 계층 조문 엔트리 | 추출 교차참조 엣지 | 디렉토리 |
|------|------------------|------------------|-------------------|---------|
| **개인정보 보호법** | 126 | 126 | 301 | `library/grade-a/pipa/` |
| 개인정보 보호법 시행령 | 140 | 140 | 406 | `library/grade-a/pipa-enforcement-decree/` |
| 정보통신망법 | 142 | 142 | 188 | `library/grade-a/network-act/` |
| 정보통신망법 시행령 | 131 | 131 | 266 | `library/grade-a/network-act-enforcement-decree/` |
| 정보통신망법 시행규칙 | 11 | 11 | 20 | `library/grade-a/network-act-enforcement-rule/` |
| 신용정보법 | 91 | 91 | 326 | `library/grade-a/credit-info-act/` |
| 신용정보법 시행령 | 81 | 81 | 435 | `library/grade-a/credit-info-act-enforcement-decree/` |
| 위치정보법 | 53 | 53 | 159 | `library/grade-a/location-info-act/` |
| 위치정보법 시행령 | 55 | 55 | 164 | `library/grade-a/location-info-act-enforcement-decree/` |
| 전자정부법 | 99 | 99 | 104 | `library/grade-a/e-government-act/` |
| **합계** | **929** | **929** | **2,369** | |

> [!IMPORTANT]
> 2026년 3월 27일 재수집 기준으로 기본 활성 corpus는 개인정보에 직접 관련된 법령 세트만 남기도록 다시 슬림화되었고, `article-index.json`의 검색 가능 법조문 파일 수는 929건입니다. `source-registry.json`의 활성 법령은 모두 `count == target` 상태이며, 같은 법 내부 교차참조의 미해결 타깃도 계속 0건입니다. `cross-reference-graph.json`에는 법령 간 교차참조 1,309건(로컬 corpus로 해소 가능한 869건)이 집계되고, `external-law-candidates.json`은 corpus 밖 외부 법령 154건을 선택적 확장 후보로 정리합니다(고우선 8건). 민법·상법 같은 대형 일반법은 명시적으로 요청할 때만 온디맨드로 수집하는 방향입니다. 폐지된 `pipa-enforcement-rule`은 의도적으로 수집 대상에서 제외하고 `retired`로 관리합니다.
> 상세 로그: [docs/2026-03-27-quality-audit-log.md](docs/2026-03-27-quality-audit-log.md)

> **제외 소스:** `library/grade-a/pipa-enforcement-rule/`은 폐지 법령 세트라서 의도적으로 수집하지 않습니다.

### PIPC 공식 가이드라인 — 46건

개인정보보호위원회가 발행한 공식 가이드라인 전수를 PDF에서 구조화된 Markdown으로 변환하여 보유하고 있습니다.

<details>
<summary><b>46건 가이드라인 전체 목록</b></summary>

| # | 제목 |
|---|------|
| 01 | 개인정보 보호법령 해설서 |
| 02 | 개인정보 처리 통합 안내서 |
| 03 | 공공/민간 분야별 안내서 |
| 04 | 재난/감염병 긴급 처리 |
| 05 | 아동·청소년 개인정보 보호 |
| 06 | 인터넷 게시물 접근배제 요청권 |
| 07 | 자동화된 의사결정 |
| 08 | 안전성 확보조치 기준 |
| 09 | 개발자를 위한 개인정보 보호 |
| 10 | 생체정보 보호 |
| 11 | 고정형 영상정보처리기기 |
| 12 | 이동형 영상정보처리기기 |
| 13 | 스마트시티 |
| 14 | 홈페이지 개인정보 노출방지 |
| 15 | 합성데이터 활용 |
| 16 | 가명정보 처리 가이드라인 |
| 17 | 가명정보 (공공분야) |
| 18 | 가명정보 (교육분야) |
| 19 | 보건의료 데이터 |
| 20 | 합성데이터 레퍼런스 모델 |
| 21 | 공공데이터 AI 개발 |
| 22 | AI 프라이버시 리스크 평가 |
| 23 | 생성형 AI 개인정보 처리 |
| 24 | 개인정보 처리방침 작성 |
| 25 | 개인정보 영향평가 |
| 26 | 영향평가 비용 산정 |
| 27 | ISMS-P 인증 |
| 28 | 개인정보 보호 교육 |
| 29 | 유출 대응 매뉴얼 |
| 30 | 외국 사업자 PIPA 적용 (한/영) |
| 31 | 손해배상 책임보험 |
| 32 | Q&A 모음 |
| 33 | 데이터 이동권 |
| 34-36 | 관리전문기관 지정 |
| 37 | 일반 데이터 수령자 등록 |
| 38 | 마이데이터 전송 절차 |
| 39a-c | 업종별 안내서 (부동산/숙박/학원) |
| 40 | 소상공인 핸드북 |
| 41a-c | 표준 개인정보 처리방침 템플릿 |

</details>

### Grade B — Landmark 판례·해석례 (30건)

Grade B 2차 소스는 법제처 Open API(`korean-law` MCP)에서 실시간으로 fetch되며, 사건번호·선고일·원문이 `VERIFIED` 상태로 수록됩니다. 6개 핵심 주제(동의·제3자 제공·안전조치/유출·가명정보·민감정보·고유식별)를 커버합니다.

| 카테고리 | 건수 | 발행기관 | 디렉토리 |
|---------|------|---------|---------|
| **대법원 판례** | 10 | 대법원 | `library/grade-b/court-precedents/` |
| **법령 해석례** | 20 | 법제처 | `library/grade-b/legal-interpretations/` |
| **합계** | **30** | | |

<details>
<summary><b>대법원 판례 10건 (landmark)</b></summary>

| 사건번호 | 선고일 | 주제 |
|---------|--------|------|
| 2014다235080 (로앤비) | 2016-08-17 | 공개된 개인정보의 동의 범위 |
| 2015다24904 (네이트/싸이월드) | 2018-01-25 | 유출 손해배상 — 기술적·관리적 보호조치 |
| 2017다219232 (구글) | 2023-04-13 | 제3자 제공 현황 공개 청구 |
| 2018다262103 (홈플러스) | 2024-05-17 | 경품 응모 개인정보를 보험사에 제공 |
| 2020도14713 (수능 감독관) | 2025-02-13 | "개인정보 제공받은 자"의 범위 |
| 2022두68923 | 2023-10-12 | 유출 과징금 처분 취소 |
| 2023다311184 | 2025-12-04 | 제39조의2 법정손해배상 |
| 2024다210554 | 2025-07-18 | 가명처리 정지 청구 |
| 2024도8121 | 2025-12-11 | CCTV 영상 제3자 제공 |
| 2013두2945 (주민등록번호 변경) | 2017-06-15 | 주민등록번호 변경 신청권 |

</details>

<details>
<summary><b>법령 해석례 20건 (법제처)</b></summary>

주요 주제: 제22조 동의 구조, 제18조제2항 "다른 법률 특별 규정" 범위(7건), 제35조 열람 요구 절차, 제31조 보호책임자 경과조치, 제2조 처리자 범위, 제28조의2 가명처리, 제23조 민감정보(2건), 제24조의2 주민등록번호(4건).

</details>

> [!NOTE]
> `library/grade-b/pipc-decisions/`는 법제처 Open API의 `get_pipc_decision_text` endpoint가 빈 응답을 반환하는 문제로 수집이 보류된 상태입니다. endpoint 복구 시 원 계획대로 PIPC 처분례 약 20건이 추가 수집될 예정입니다.

### 데이터 구조화 방식

모든 법조문은 개별 `.md` 파일로 저장되며, 풍부한 메타데이터가 포함됩니다:

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

이를 통해 AI 에이전트는:
- 인덱스 파일로 **키워드 검색** 가능
- 교차참조를 따라 **관련 조문 추적** 가능
- Grade 체계로 **소스 권위 검증** 가능
- 정확한 조문 원문을 **환각 없이 읽기** 가능

---

## 동작 방식

```mermaid
flowchart TD
    Q["❓ <b>사용자 질문</b>"]

    subgraph kb["Step 1–3: Knowledge Base 검색"]
        direction TB
        S1["📚 <b>조문 검색</b><br/><code>article-index.json</code> → 관련 법조문"]
        S2["📖 <b>가이드라인 검색</b><br/><code>guideline-index.json</code> → PIPC 해설"]
        S3["🔗 <b>교차참조 추적</b><br/><code>cross-reference-graph.json</code> → 위임 조문"]
        S1 --> S2 --> S3
    end

    subgraph web["Step 4: Multi-Layer 웹서치 <i>(KB 부족 시)</i>"]
        direction TB
        L1["🏛️ <b>Layer 1 · 법령 원문</b><br/>law.go.kr · pipc.go.kr"]
        L2["⚖️ <b>Layer 2 · 주요 로펌</b><br/>국내 주요 로펌<br/>뉴스레터 · 아티클"]
        L3["🎓 <b>Layer 3 · 학술</b><br/>KCI · RISS · SSRN"]
        L4["🌍 <b>Layer 4 · 해외 감독기관</b><br/>EDPB · ICO · IAPP"]
        L1 --> L2 --> L3 --> L4
    end

    subgraph verify["Adversarial 교차검증"]
        direction LR
        PA["✅ <b>Pass A</b><br/>긍정 근거"]
        PB["⚠️ <b>Pass B</b><br/>반례 탐색<br/>&amp; 예외 규정"]
        PA <--> PB
    end

    O["📄 <b>검증된 법률 분석 메모</b><br/>DOCX · 인용 체계 · 리스크 매트릭스"]

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

모든 인용에 검증 상태가 표시됩니다:

| 태그 | 의미 |
|------|------|
| `[VERIFIED]` | Grade A 소스에서 정확히 매칭 |
| `[UNVERIFIED]` | Grade B만 존재하거나 부분 일치 |
| `[INSUFFICIENT]` | 근거 부족 — 해당 부분 빈칸 |
| `[CONTRADICTED]` | 소스 간 모순 — 양쪽 모두 제시 |

---

## Fact-Check 레이어 (환각 방지)

최종 출력 전, **전용 fact-checker 서브에이전트**가 모든 법령 인용을 KB 원본과 대조합니다:

| 검증 항목 | 방법 | 실패 시 |
|----------|------|--------|
| 조문 존재 여부 | KB에서 `art{N}.md` Glob | `[UNVERIFIED]`로 다운그레이드 |
| 인용 원문 일치 | 파일 Read 후 대조 | 올바른 원문으로 교체 |
| 조문 번호 정확성 | frontmatter 대조 | 번호 정정 |
| 시행일 유효성 | `effective_date` 확인 | `[미시행]` 경고 추가 |
| 가이드라인 인용 | `guideline-index.json` 대조 | 다운그레이드 또는 삭제 |
| 교차참조 유효성 | 대상 파일 존재 확인 | 깨진 참조 표시 |
| 웹소스 신뢰도 | 신뢰 도메인 목록 대조 | Grade 다운그레이드 |

**신뢰도 점수:** 70% 미만이면 FAIL 항목을 수정하고 재검증 후 출력합니다. 핵심 결론에 영향을 주는 인용은 검증 없이 출력하지 않습니다.

---

## DOCX 법률 분석 메모 생성

에이전트는 **전문 형식의 Word 문서**를 생성합니다:

- KP Legal Orchestrator 레터헤드
- 구조화된 섹션: 쟁점 → 분석 → 결론 → 권고
- 색상 코딩된 리스크 매트릭스 테이블
- 검증 상태 표시된 전체 인용 체계
- Fact-check 리포트 첨부
- 서명란 및 면책 조항
- AI 생성 고지

---

## 소스 Ingest 시스템

### 나만의 소스 추가하기

1. `${PIPA_INBOX_DIR:-library/inbox/}`에 아무 파일(PDF, DOCX 등) 드롭
2. agent에게 알려주기: `/ingest` 또는 "파일 넣었어"
3. agent가 자동으로 처리:

```
${PIPA_INBOX_DIR:-library/inbox/}    ← 파일 드롭
     │
     ▼ /ingest 또는 "파일 넣었어"
     │
     ├─ Markdown 자동 변환 (MarkItDown)
     ├─ Grade 자동 판별 (A/B/C — 내용 분석 기반)
     ├─ Frontmatter 자동 생성 (키워드, 인용, 메타데이터)
     ├─ library/grade-{a,b,c}/ 에 배치
     └─ 검색 인덱스 업데이트
```

> **참고:** 파일을 넣는 것만으로는 자동 처리되지 않습니다. `/ingest`를 실행하거나 agent에게 알려줘야(예: "inbox에 파일 넣었어") 파싱 파이프라인이 시작됩니다.

---

## 시작하기

> **처음이신가요?** **[사용 가이드](docs/ko/HOW-TO-USE.md)** — 비개발자를 위한 단계별 안내서를 읽어보세요.

### 사전 요구사항

- [Claude Code](https://claude.ai/claude-code) CLI
- Python 3.10+
- `python-docx` (`pip install python-docx`)

### 설치

```bash
git clone <repository-url>
cd PIPA-expert
pip install python-docx
```

현재 저장소의 호스팅 페이지에서 실제 URL을 복사해 사용하면 됩니다.

### 법령 데이터 갱신 (월 1회)

```bash
python3 scripts/fetch-pipa-from-api.py --oc YOUR_EMAIL_ID
```

[Open Law API](https://open.law.go.kr) 무료 계정 필요. `--oc` 파라미터는 등록된 이메일 ID입니다.

### 에이전트 실행

```bash
cd PIPA-expert
claude   # Claude Code 실행
```

이후 `/agents/pipa-agent`로 개인정보 스페셜리스트 페르소나 활성화.

### 예시 질문

```
"개인정보보호법 제15조 보여줘"
"맞춤형 광고 동의 구조 재설계 방안 분석 메모 작성해줘"
"정보통신망법과 개인정보보호법의 동의 규정 차이점"
"제3자 제공 관련 법률 분석 메모 DOCX로 만들어줘"
```

---

## KP Legal Orchestrator

PIPA Expert는 **KP Legal Orchestrator** 소속 전문 법률 워크플로우 에이전트 시리즈 중 하나입니다:

| 에이전트 | 역할 | 전문 분야 |
|---------|------|----------|
| `game-legal-research` | 게임 산업 리서치 스페셜리스트 | 게임 산업법 |
| `legal-translation-agent` | 법률 번역 스페셜리스트 | 법률 번역 |
| `general-legal-research` | 일반 법률 리서치 스페셜리스트 | 법률 리서치 |
| **PIPA-expert** | **개인정보 스페셜리스트** | **개인정보보호법** |
| `GDPR-expert` | EU 데이터보호 스페셜리스트 | EU 데이터보호법 |
| `contract-review-agent` | 계약 검토 스페셜리스트 | 계약서 검토 |
| `legal-writing-agent` | 법률 드래프팅 스페셜리스트 | 법률 문서 작성 |
| `second-review-agent` | 시니어 리뷰 스페셜리스트 | 품질 리뷰 |

---

## 라이선스

[Apache License 2.0](LICENSE) 하에 배포됩니다.

---

<div align="center">
<sub>임베딩에 대한 맹신이 아니라, 구조화된 데이터 위에 세워졌습니다.</sub>
</div>
