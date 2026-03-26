# PIPA Agent-Native RAG System

개인정보보호 법령 전문 Agent를 위한 구조화된 RAG 시스템.

## 프로젝트 구조

```
library/inbox/             # 외부 소스 드롭 → /ingest로 자동 처리
library/grade-a/           # Grade A 공식 1차 소스
  pipc-guidelines/          # PIPC 가이드라인 46종 (전처리 완료)
  pipa/                     # 개인정보보호법 searchable 파일 76건 (계층 126건)
  pipa-enforcement-decree/  # 시행령 searchable 파일 63건 (계층 140건)
  pipa-enforcement-rule/    # 시행규칙 폴더만 존재, 재수집 필요
library/grade-b/           # Grade B 2차 소스 (처분례, 판례)
library/grade-c/           # Grade C 3차 소스 (로펌 해설, 학술)
index/                     # 검색 인덱스 (article-index.json, guideline-index.json, source-registry.json)
config/                    # RAG 설정, 소스 등급 정의
scripts/                   # 전처리/수집 스크립트
docs/specs/                # 설계 문서
```

## Current Status

- 검색 가능한 Grade A 법령 파일: 550건 (`index/article-index.json`)
- PIPC 가이드라인: 46건 (`index/guideline-index.json`)
- 알려진 감사 이슈: 가지조문(예: `제7조의2`)이 기본 조문 파일로 평탄화되어 `count`와 `target`이 다를 수 있음. 법령별 실제 커버리지는 `index/source-registry.json`의 `count/target/status`를 확인할 것.
- 상세 감사/수정 로그: `docs/2026-03-27-quality-audit-log.md`

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
  - **한국어 의견서 작성 시 반드시 `docs/ko-legal-opinion-style-guide.md`를 읽고 따를 것**
- **ingest** — 외부 소스 자동 파싱/분류/인덱싱 (`.claude/skills/ingest/`)
  - `library/inbox/`에 파일 드롭 → `/ingest`로 자동 처리
  - Grade 자동 판별 → frontmatter 생성 → 폴더 배치 → 인덱스 업데이트

## Dependencies

- `python-docx` — DOCX 생성용 (`pip install python-docx`)

## 주요 문서

- `DESIGN.md` — RAG 시스템 전체 설계
- `PROGRESS.md` — 작업 기록 및 진행 상황
- `docs/specs/2026-03-24-pipa-agent-system-design.md` — Agent 시스템 스펙
