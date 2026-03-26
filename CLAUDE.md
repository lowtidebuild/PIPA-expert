# PIPA Agent-Native RAG System

개인정보보호 법령 전문 Agent를 위한 구조화된 RAG 시스템.

## 프로젝트 구조

```
library/inbox/             # 외부 소스 드롭 → /ingest로 자동 처리
library/grade-a/           # Grade A 공식 1차 소스
  pipc-guidelines/          # PIPC 가이드라인 46종 (전처리 완료)
  pipa/                     # 개인정보보호법 조문 (API 수집 예정)
  pipa-enforcement-decree/  # 시행령 (API 수집 예정)
library/grade-b/           # Grade B 2차 소스 (처분례, 판례)
library/grade-c/           # Grade C 3차 소스 (로펌 해설, 학술)
index/                     # 검색 인덱스 (guideline-index.json, source-registry.json)
config/                    # RAG 설정, 소스 등급 정의
scripts/                   # 전처리/수집 스크립트
docs/specs/                # 설계 문서
```

## Source Grade 체계

- **A**: 법령 원문, PIPC 가이드라인 — 단독 근거 가능
- **B**: 처분례, 판례 — A 교차검증 권장
- **C**: 로펌 해설, 학술 논문 — 단독 근거 불가, [EDITORIAL] 표시 필수
- **D**: 뉴스, AI 요약, 위키 — RAG 미포함

## Agents

- **pipa-agent** — PIPA 전문 메인 에이전트 (`.claude/agents/pipa-agent.md`). `/agents/pipa-agent`로 호출.
- **fact-checker** — 환각 검증 서브에이전트 (`.claude/agents/fact-checker/AGENT.md`). pipa-agent가 답변 생성 후 자동 호출. 모든 법령 인용을 KB 원본과 대조하여 PASS/WARN/FAIL 리포트 반환.

## Skills

- **legal-opinion-formatter** — 로펌 수준 DOCX 법률의견서 생성 (`.claude/skills/legal-opinion-formatter/`)
  - `SKILL.md` — 의견서 구조 및 워크플로우
  - `legal-opinion-formatter-SKILL.md` — python-docx 상세 구현 가이드
  - `references/format-checklist.md` — 생성 전 체크리스트
- **ingest** — 외부 소스 자동 파싱/분류/인덱싱 (`.claude/skills/ingest/`)
  - `library/inbox/`에 파일 드롭 → `/ingest`로 자동 처리
  - Grade 자동 판별 → frontmatter 생성 → 폴더 배치 → 인덱스 업데이트

## Dependencies

- `python-docx` — DOCX 생성용 (`pip install python-docx`)

## 주요 문서

- `DESIGN.md` — RAG 시스템 전체 설계
- `PROGRESS.md` — 작업 기록 및 진행 상황
- `docs/specs/2026-03-24-pipa-agent-system-design.md` — Agent 시스템 스펙
