# PIPA Agent-Native RAG System — Progress Log

## Project Overview

PIPA(개인정보보호법) 전문 Agent를 위한 구조화된 RAG 시스템.
ChatGPT Custom GPT / Gemini Gem의 flat document 방식을 넘어서, 법령의 계층 구조·교차참조·소스 등급을 반영하는 structured knowledge base 구축.

- **설계 방식:** Hybrid File + Vector RAG (Approach B)
- **핵심 원칙:** "데이터 구조가 곧 지능이다" — 더 똑똑한 검색이 아니라 더 똑똑한 데이터
- **확장성:** 범용 법령 RAG 아키텍처. PIPA로 시작, 어떤 법령이든 같은 구조로 추가 가능

## 2026-03-24: Initial Setup + Guideline Preprocessing

### 완료된 작업

#### 1. 디자인 문서 작성 및 승인
- `/office-hours` 브레인스토밍 → 디자인 문서 작성
- 2라운드 adversarial review (18개 이슈 발견 → 전부 수정)
- **Status: APPROVED**
- 파일: [DESIGN.md](DESIGN.md)

#### 2. 프로젝트 구조 생성
```
pipa-rag/
├── config/           # RAG 설정, 소스 등급 정의
├── sources/
│   ├── grade-a/      # 1차 공식 소스
│   │   ├── pipa/                    # (대기: API 검증 후)
│   │   ├── pipa-enforcement-decree/ # (대기: API 검증 후)
│   │   └── pipc-guidelines/         # ✅ 46개 가이드라인 전처리 완료
│   ├── grade-b/      # 2차 소스 (처분례, 판례 — 추후)
│   └── grade-c/      # 3차 소스 (학술 — 추후)
├── index/            # 검색 인덱스
├── embeddings/       # Phase 2: 벡터 임베딩
├── archive/          # 법령 개정 이력
└── scripts/          # 전처리 스크립트
```

#### 3. PIPC 가이드라인 전처리 (핵심 작업)

**입력:** 46개 PIPC 공식 가이드라인 PDF (~210MB)
**출력:** 46개 구조화된 Markdown 파일 (~11MB)

**전처리 파이프라인:**
1. `markitdown` CLI로 PDF → Markdown 변환
2. YAML frontmatter 자동 생성 (guideline_id, slug, title, source_grade, keywords, topics)
3. `_meta.json` — 컬렉션 메타데이터
4. `guideline-index.json` — 전체 가이드라인 검색 인덱스 (46 entries)
5. `source-registry.json` — 소스 수집 현황 대시보드

**가이드라인 목록 (46개):**

| # | 제목 | 주요 주제 |
|---|------|----------|
| 01 | 개인정보 보호법령 해설서 | PIPA 총론, 법령해설 |
| 02 | 개인정보 처리 통합 안내서 | 수집, 이용, 제공, 파기 |
| 03 | 분야별 개인정보 보호 안내서 | 공공, 민간, 업종별 |
| 04 | 긴급상황 시 개인정보 처리 안내서 | 재난, 감염병, 생명보호 |
| 05 | 아동·청소년 개인정보 보호 안내서 | 아동, 법정대리인, 동의 |
| 06 | 인터넷 자기게시물 접근배제요청권 안내서 | 잊힐권리, 게시물삭제 |
| 07 | 자동화된 의사결정 정보주체 권리 안내서 | 프로파일링, AI |
| 08 | 개인정보 안전성 확보조치 안내서 | 암호화, 접근통제, 보안 |
| 09 | 개발자를 위한 프라이버시 보호조치 안내서 | Privacy by Design |
| 10 | 생체정보 보호 안내서 | 지문, 홍채, 얼굴인식 |
| 11 | 고정형 영상정보처리기기 안내서 | CCTV |
| 12 | 이동형 영상정보처리기기 개인정보 보호 안내서 | 드론, 바디캠 |
| 13 | 스마트시티 개인정보 보호 안내서 | IoT, 도시데이터 |
| 14 | 홈페이지 개인정보 노출방지 안내서 | 웹사이트 보안 |
| 15 | 합성데이터 활용 안내서 | 데이터활용, 비식별 |
| 16 | 가명정보 처리 가이드라인 | 가명처리, 결합, 재식별 |
| 17 | 공공부문 가명정보 처리 실무 안내서 | 공공부문 가명정보 |
| 18 | 교육분야 가명정보 처리 안내서 | 교육, 학생정보 |
| 19 | 보건의료 데이터 활용 안내서 | 건강정보, 의료데이터 |
| 20 | 합성데이터 생성 참조모델 | 기술표준 |
| 21 | AI 개발을 위한 공공 개인정보 처리 안내서 | AI, 공공데이터, 학습데이터 |
| 22 | AI 프라이버시 리스크 평가 모델 | AI 리스크평가 |
| 23 | 생성AI에 의한 개인정보 처리 안내서 | 생성AI, LLM |
| 24 | 개인정보 처리방침 작성 안내서 | Privacy Policy |
| 25 | 개인정보 영향평가 수행 안내서 | PIA |
| 26 | 개인정보 영향평가 비용 산정 안내서 | PIA 비용 |
| 27 | ISMS-P 인증기준 안내서 | ISMS-P, 인증 |
| 28 | 개인정보 보호 교육 안내서 | 교육 |
| 29 | 개인정보 유출사고 대응 매뉴얼 | 침해사고, 통지 |
| 30 | 외국 사업자 PIPA 적용 안내서 (한/영) | 역외적용 |
| 31 | 개인정보 손해배상 책임보험 안내서 | 보험, 배상 |
| 32 | 개인정보 보호 QA 모음집 | FAQ, 실무해석 |
| 33 | 개인정보 전송요구권 안내서 | 데이터이동권 |
| 34-36 | 개인정보 관리전문기관 지정 안내서 (일반/특례/중계) | MyData |
| 37 | 일반 데이터 수령인 등록 안내서 | MyData |
| 38 | 분야 간 본인정보 전송 절차·기술 안내서 | MyData 기술표준 |
| 39a-c | 업종별 개인정보 처리 안내서 (부동산/숙박/학원) | 업종별 |
| 40 | 소상공인 개인정보 보호 핸드북 | 소상공인 |
| 41a-c | 표준 개인정보처리방침 템플릿 (중개사/복지관/여행사) | 템플릿 |

#### 4. 인프라 파일
- `config/source-grades.json` — Grade A-D 소스 등급 정의
- `config/rag-config.json` — RAG 설정
- `index/guideline-index.json` — 검색 인덱스 (46 entries, keywords/topics 포함)
- `index/source-registry.json` — 전체 소스 수집 현황

### 사용한 도구
- **markitdown** (PDF → Markdown 변환)
- **Python 3** (전처리 스크립트)
- **Claude Code /office-hours** (디자인 문서 작성)

### 기술적 결정 사항
1. **Markdown + YAML frontmatter** 방식 선택 (JSON-only가 아닌 hybrid)
   - 이유: LLM이 markdown을 네이티브로 이해, frontmatter로 구조화된 메타데이터 제공
2. **Source Grade 체계** (A/B/C/D) 적용
   - PIPC 공식 가이드라인 = Grade A (단독 근거로 사용 가능)
3. **범용 구조** — `sources/grade-{a,b,c}/{법령or소스}/` 패턴
   - 새 법령 추가 시 동일 패턴으로 확장

---

## Next Steps

| 우선순위 | 작업 | 상태 |
|---------|------|------|
| **P0** | law.go.kr Open API 검증 (Phase 0 blocker) | 대기 |
| P1 | PIPA 본법 조문 수집 + 구조화 | 대기 (API 검증 후) |
| P1 | PIPA 시행령 수집 + 구조화 | 대기 (API 검증 후) |
| P2 | 교차참조 매핑 (본법 ↔ 시행령 ↔ 가이드라인) | 대기 |
| P2 | Agent 연동 테스트 | 대기 |
| P3 | 벡터 임베딩 (ChromaDB) | Phase 2 |

---

## 참고 링크
- law.go.kr Open API: https://open.law.go.kr/
- PIPC: https://www.pipc.go.kr
- 디자인 참고 논문: [Ontology-Driven Graph RAG for Legal Norms](https://arxiv.org/html/2505.00039v4)
