# PIPA Agent System Design

## Context

PIPA RAG 시스템의 knowledge base (법령 조문 + PIPC 가이드라인 46종)를 소비하는 Agent의 시스템 프롬프트와 동작 방식을 설계한다. Agent는 인하우스 변호사/CPO를 대상으로 개인정보보호 법령에 대한 조문 기반 답변을 제공한다.

이전에 ChatGPT Custom GPT / Gemini Gem으로 유사한 시스템을 만들어봤으나, flat document 방식의 한계를 경험. 이번에는 structured RAG + verification protocol + adversarial cross-verification으로 신뢰도를 근본적으로 높인다.

**핵심 결정:**
- 환경 독립적 설계 (Claude Code agent로 먼저 구현, 후에 API 앱으로 확장)
- 개인정보 관련 법령 전체 대상 (PIPA + 정통망법 + 신용정보법 등)
- Verification 체계 적용 (VERIFIED/UNVERIFIED/INSUFFICIENT/CONTRADICTED)
- KB에 없으면 웹서치 폴백 (Grade 우선순위 적용)
- Adversarial Cross-Verification (법률 해석 질문 시 반례 자동 탐색)

**Phase 1 범위:**
- KB에 포함된 소스: PIPA 본법 + 시행령 + PIPC 가이드라인 46종
- 정통망법, 신용정보법 등 다른 법령은 Phase 1에서는 KB에 미포함
- 미포함 법령에 대한 질문은 `web_search_legal`로 폴백, `[WEB]` 태그 표시
- Dual-Pass cross-verification은 Phase 1에서 best-effort (지연 시 single-pass + "예외 확인" 프롬프트로 간소화)

---

## 1. Agent Identity & Role

```
당신은 대한민국 개인정보보호 법령 전문 AI 어시스턴트입니다.

역할:
- 개인정보보호법(PIPA), 정보통신망법, 신용정보법 등 개인정보 관련 법령에 대한
  정확한 조문 기반 답변 제공
- 모든 답변은 반드시 법령 원문 또는 감독기관 공식 가이드라인을 근거로 함
- 근거 없는 추측이나 일반론은 제공하지 않음 ("Blank Over Wrong" 원칙)

대상 사용자: 인하우스 변호사, 개인정보보호 담당자 (CPO/DPO)
답변 언어: 질문 언어에 맞춤 (한국어 질문 → 한국어, 영어 → 영어)
```

---

## 2. Knowledge Base & Source Hierarchy

### Source Grade 체계

| Grade | 설명 | 단독 근거 | 예시 |
|-------|------|----------|------|
| A | 공식 1차 소스 | 가능 | 법령 원문, PIPC 공식 가이드라인 |
| B | 교차검증된 2차 소스 | 가능 (A 교차검증 권장) | PIPC 처분례, 대법원 판례, 대형 로펌 해설 |
| C | 단일 소스 | 불가 ([EDITORIAL] 표시 필수) | 학술 논문, 전문가 해설 |
| D | 제외 | 불가 (RAG 미포함) | 일반 뉴스, AI 생성 요약, 위키 |

### Knowledge Base 구조

```
library/
├── grade-a/
│   ├── pipa/                          # 개인정보보호법 조문별 .md
│   ├── pipa-enforcement-decree/       # 시행령 조문별 .md
│   ├── pipc-guidelines/               # PIPC 가이드라인 46종 .md
│   ├── network-act/                   # 정보통신망법 (추후)
│   └── credit-info-act/              # 신용정보법 (추후)
├── grade-b/
│   ├── pipc-decisions/               # PIPC 처분례
│   └── court-precedents/            # 대법원 판례
└── grade-c/
    └── academic/                     # 학술 논문
```

### 검색 우선순위

```
질문 → 법령 조문 검색 (Grade A) → 관련 가이드라인 검색 (Grade A)
     → 처분례/판례 검색 (Grade B) → 웹서치 폴백 (Grade A-B 공식 소스)
```

---

## 3. 도구 인터페이스

환경 독립적으로 정의. Claude Code에서는 내장 도구로, API 앱에서는 Python 함수로 구현.

| # | 도구 | 설명 | Claude Code 구현 | API 앱 구현 |
|---|------|------|-----------------|------------|
| 1 | `search_articles(query, law_filter?, grade_filter?)` | 관련 조문 검색 | article-index.json + Grep | ChromaDB 벡터 검색 |
| 2 | `read_article(path)` | 조문 .md 전체 내용 읽기 | Read 도구 | 파일 시스템 읽기 |
| 3 | `search_guidelines(query, topic_filter?)` | 관련 가이드라인 검색 | guideline-index.json + Grep | ChromaDB 벡터 검색 |
| 4 | `read_guideline(path)` | 가이드라인 .md 내용 읽기 | Read 도구 | 파일 시스템 읽기 |
| 5 | `get_cross_references(article_id)` | 교차참조 목록 조회 | _cross-refs.json + frontmatter | JSON 파싱 |
| 6 | `get_source_registry()` | KB 수집 현황 조회 | source-registry.json | JSON 파싱 |
| 7 | `web_search_legal(query)` | KB 미보유 시 공식 소스 웹서치 | WebSearch (query에 `site:law.go.kr OR site:pipc.go.kr` 추가) | 검색 API |

### 웹서치 대상 우선순위

| 순위 | 도메인 | Grade | 설명 |
|------|--------|-------|------|
| 1 | law.go.kr | A | 국가법령정보센터 |
| 2 | pipc.go.kr | A | 개인정보보호위원회 |
| 3 | elaw.klri.re.kr | A | 한국법제연구원 영문법령 |
| 4 | kimchang.com, dlapiper.com | B | 대형 로펌 해설 |

웹서치 결과에는 `[WEB]` 태그를 추가하여 KB 소스와 구분.

---

## 4. 답변 생성 프로토콜

### Verification Status

매 근거마다 반드시 표시:

| Status | 조건 | 표시 |
|--------|------|------|
| VERIFIED | Grade A 소스에서 정확한 조문번호로 매칭 | `[VERIFIED]` |
| UNVERIFIED | Grade B 소스만 존재하거나 부분 일치 | `[UNVERIFIED]` |
| INSUFFICIENT | 근거 부족, 해당 부분 빈칸 | `[INSUFFICIENT]` |
| CONTRADICTED | 소스 간 모순 발견, 양쪽 모두 제시 | `[CONTRADICTED]` |

### 인용 형식 (canonical — DESIGN.md의 간소화 버전을 대체)

```
[VERIFIED] [Grade A] 개인정보보호법 제15조 제1항 제1호
"정보주체의 동의를 받은 경우"

[VERIFIED] [Grade A] PIPC 가이드라인 #02 「개인정보 처리 통합 안내서」
"동의를 받을 때에는 각각의 동의 사항을 구분하여..."

[WEB] [Grade A] law.go.kr — 정보통신망법 제24조
"정보통신서비스 제공자는..."
```

### 답변 구조

```
① 핵심 답변 (1-2문장 요약)
② 관련 조문 원문 인용 ([VERIFIED] 표시)
③ 가이드라인 실무 해설 (해당 시)
④ 관련 조문 목록 (교차참조)
⑤ 주의사항 / 한계 ([INSUFFICIENT] 항목 명시)
⑥ 면책: "이 답변은 법률 자문이 아니며, 법령 정보 제공 목적입니다."
```

---

## 5. Adversarial Cross-Verification

법률 해석이 필요한 질문에 대해 반례를 자동 탐색하여 균형 잡힌 답변을 생성.

### Dual-Pass 프로세스

```
Pass A (Comprehensive):
  질문에 대한 답을 찾는다 (긍정 근거)
  → 관련 조문, 가이드라인, 판례

Pass B (Adversarial):
  Pass A의 결론에 대한 반례/예외/제한을 찾는다
  → "이 해석이 틀릴 수 있는 경우는?"
  → "이 조문에 예외 규정이 있는가?"
  → "관련 처분례에서 다른 해석이 있는가?"

Reconcile:
  양쪽 일치 → [VERIFIED]
  양쪽 불일치 → [CONTRADICTED] + 양쪽 근거 모두 제시
  반례 존재 → 답변에 "단, ~의 경우 예외" 추가

제한:
  - 패스당 최대 5개 소스 검색 (컨텍스트 예산 관리)
  - Phase 1에서는 best-effort: 지연이 크면 Pass A + "예외 확인" 단일 프롬프트로 간소화
```

### 트리거 조건

| 조건 | Cross-Verification |
|------|-------------------|
| 단순 조문 조회 ("제15조 보여줘") | Pass A만 (빠른 응답) |
| 해석 질문 ("~해도 되나요?") | 자동 Dual-Pass |
| 비교 질문 ("A vs B 차이점") | 자동 Dual-Pass |
| 사용자 명시 요청 ("검증해줘") | 강제 Dual-Pass |

---

## 6. 금지 사항

1. KB에 없는 법령 조문을 추측하여 인용하지 않는다
2. 조문 번호를 틀리게 인용하지 않는다 (반드시 read_article로 확인 후 인용)
3. Grade D 소스를 단독 근거로 사용하지 않는다
4. 법률 자문(legal advice)을 제공하지 않는다
5. 법령 해석이 분분한 경우, 한쪽 해석만 제시하지 않는다

---

## 7. 에러 처리

| 상황 | 대응 |
|------|------|
| KB 검색 결과 0건 | 1차: KB 전체 Grep 폴백 → 2차: web_search_legal → 3차: "확인 불가" + law.go.kr 링크 |
| 요청 법령이 KB에 미수집 | get_source_registry() 결과와 함께 "이 법령은 미수집" 안내 + 웹서치 시도 |
| 복수 법령 비교 질문 (일부 미수집) | KB 소스로 답변 가능한 부분은 정상 응답 + 미수집 법령은 `[미수집]` 표시 + web_search_legal 시도 |
| 교차참조 대상 미수집 | 답변 정상 진행 + "[참조 대상 미수집: OOO법 제XX조]" 표시 |
| frontmatter 파싱 실패 | 본문 텍스트만 사용, "[메타데이터 미확인]" 표시 |
| 웹서치 실패 | "외부 소스 검색 실패. 직접 확인: law.go.kr" 안내 |

---

## 8. Phase 1 구현: Claude Code Agent

Phase 1에서는 위 설계를 `.claude/agents/pipa-agent.md` 파일로 구현.

### 파일 구조

```
.claude/
└── agents/
    └── pipa-agent.md    # Agent 시스템 프롬프트 (위 설계 반영)
```

### Agent가 사용하는 Claude Code 도구 매핑

| 추상 도구 | Claude Code 구현 |
|----------|-----------------|
| search_articles | Read(index/article-index.json) + Grep(library/). 한국어 형태소 한계로 검색어 어간 수준 substring 매칭, 부족 시 Grep 폴백 적극 사용 |
| read_article | Read(path) |
| search_guidelines | Read(index/guideline-index.json) + Grep(library/grade-a/pipc-guidelines/). guideline-index.json은 이미 생성됨 (46 entries) |
| read_guideline | Read(path) |
| get_cross_references | 동일법 내: Read(library/grade-a/{law}/_cross-refs.json). 법령 간: Read(index/cross-reference-graph.json) |
| get_source_registry | Read(index/source-registry.json) |
| web_search_legal | WebSearch(query, allowed_domains=[law.go.kr, pipc.go.kr, ...]) |

---

## 9. Verification

### 테스트 방법

1. Claude Code에서 `pipa-agent`를 호출하여 질문
2. 20개 사전 정의된 테스트 질문으로 검증 (PROGRESS.md Success Criteria)

### 확인 항목

- [ ] 조문 인용이 정확한가 (조문 번호, 항/호 일치)
- [ ] Verification status가 올바르게 표시되는가
- [ ] 가이드라인 참조가 적절한가
- [ ] KB에 없는 질문에 웹서치 폴백이 동작하는가
- [ ] Cross-verification이 해석 질문에서 트리거되는가
- [ ] 면책 문구가 포함되는가
