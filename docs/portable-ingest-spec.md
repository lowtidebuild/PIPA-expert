# Library Ingest Pattern — Portable Spec

다른 에이전트 프로젝트에 library ingest 구조를 도입할 때 이 문서를 참조한다.

## Origin

- **Source project:** `/Users/kpsfamily/코딩 프로젝트/PIPA-expert`
- **Created:** 2026-03-25
- **Commit:** `37de66f`

## What to Copy

### 1. Directory Structure

```
library/
├── inbox/              # 유저가 파일 드롭하는 곳 (.gitkeep 포함)
├── grade-a/            # 공식 1차 소스 (법령, 가이드라인)
├── grade-b/            # 2차 소스 (판례, 로펌 해설)
└── grade-c/            # 학술/참고 소스
```

기존에 `sources/`를 쓰고 있었다면 `library/`로 rename하고 모든 참조 업데이트.

### 2. Ingest Skill

**Copy from:** `.claude/skills/ingest/SKILL.md`

**핵심 워크플로우:**
1. `library/inbox/`의 모든 파일 스캔
2. markitdown MCP로 .md 변환 (PDF, DOCX, PPTX 등)
3. 내용 분석 → Grade 자동 판별 (A/B/C)
4. YAML frontmatter 자동 생성
5. `library/grade-x/` 적절한 폴더로 이동
6. 인덱스 업데이트
7. 원본은 `inbox/_processed/`로 보존

### 3. Grade 판별 규칙

| Grade | 시그널 |
|-------|--------|
| A | 법률 번호, 고시 번호, 정부기관 발행, law.go.kr 출처 |
| B | 판례 번호, 처분례, 로펌 레터헤드/도메인, 뉴스레터 형식 |
| C | 학술지, 초록/Abstract, 참고문헌, KCI/RISS/SSRN |
| D | 뉴스, AI 요약, 위키 → ingest 거부 |

판별 불가 시 유저에게 Grade 선택 질문.

### 4. Frontmatter Schema

```yaml
---
source_id: "{grade}-{category}-{slug}"
slug: "{auto}"
title_kr: "{extracted}"
title_en: "{extracted or empty}"
document_type: "{statute | guideline | decision | precedent | newsletter | article | paper}"
source_grade: "{A | B | C}"
publisher: "{extracted}"
author: "{extracted}"
published_date: "{extracted}"
source_url: "{extracted}"
original_format: "{pdf | docx | ...}"
ingested_at: "{ISO 8601}"
keywords: ["{5-10 keywords}"]
topics: ["{topic classification}"]
char_count: {number}
verification_status: "{VERIFIED | UNVERIFIED}"
grade_confidence: "{high | medium | low}"
---
```

### 5. Agent 연동

agent .md 파일에 아래 섹션 추가:

```markdown
## 소스 Ingest

사용자가 외부 소스 파일을 `library/inbox/`에 넣고 `/ingest`를 요청하면:

1. `.claude/skills/ingest/SKILL.md`를 읽어 워크플로우 확인
2. inbox 내 파일을 markitdown으로 .md 변환
3. 내용 분석하여 Grade 자동 판별 (A/B/C)
4. frontmatter 생성 + 적절한 `library/grade-x/` 폴더로 배치
5. 인덱스 업데이트

**트리거 키워드:** "ingest", "소스 추가", "자료 넣었어", "inbox"
```

### 6. CLAUDE.md 업데이트

프로젝트 구조에 inbox 추가, Skills에 ingest 추가.

### 7. Adaptation Checklist

각 프로젝트에 맞게 조정할 부분:

- [ ] Grade 판별 시그널 — 프로젝트 도메인에 맞게 조정 (예: 게임법 vs 개인정보법)
- [ ] frontmatter의 도메인 특화 필드 (예: `pipa_articles` → `game_law_articles`)
- [ ] `library/grade-x/` 하위 폴더 구조 — 프로젝트의 소스 분류에 맞게
- [ ] 인덱스 파일명/구조 — 기존 인덱스와 호환
- [ ] 기존 `sources/` → `library/` rename 필요 여부

## Files to Read

PIPA-expert에서 실제 구현을 확인하려면:

| 파일 | 용도 |
|------|------|
| `.claude/skills/ingest/SKILL.md` | 전체 워크플로우 + 에러 처리 |
| `.claude/agents/pipa-agent.md` | agent 연동 예시 |
| `CLAUDE.md` | 프로젝트 구조 기재 예시 |
| `library/grade-a/pipc-guidelines/_meta.json` | 컬렉션 메타 예시 |
| `library/grade-a/pipc-guidelines/23-generative-ai.md` | frontmatter 예시 |
| `index/guideline-index.json` | 인덱스 구조 예시 |
| `index/source-registry.json` | 소스 레지스트리 예시 |
| `config/source-grades.json` | Grade 정의 예시 |
