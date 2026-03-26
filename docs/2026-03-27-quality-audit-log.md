# 2026-03-27 Quality Audit Log

`PIPA-expert` 저장소에 대해 `GDPR-expert/docs/quality-audit-playbook.md`를 기준으로 수행한 품질 감사 및 수정 로그.

## 1. 목적

- `PIPA-expert`의 실제 KB 상태가 README, 인덱스, 운영 문서와 일치하는지 확인
- frontmatter / cross-reference / index-library sync 문제를 점검
- 즉시 수정 가능한 항목은 같은 세션에서 remediation까지 반영

## 2. 감사 기준

기준 문서:
- `GDPR-expert/docs/quality-audit-playbook.md`

적용한 점검 축:
- Frontmatter schema consistency
- Cross-reference validity
- Index-library sync
- 문서 수치 동기화
- 샘플 콘텐츠 spot-check

## 3. 감사 범위

검토 대상:
- `library/grade-a/**`
- `index/article-index.json`
- `index/guideline-index.json`
- `index/source-registry.json`
- `README.md`
- `README.ko.md`
- `CLAUDE.md`
- `.claude/agents/pipa-agent.md`
- `docs/en/HOW-TO-USE.md`
- `docs/ko/HOW-TO-USE.md`
- `scripts/fetch-pipa-from-api.py`
- `scripts/build-guideline-index.py`

## 4. 핵심 발견 사항

### 4.1 Index / Library Sync 불일치

감사 시점 기준:
- `article-index.json`: 550 searchable statute files
- `guideline-index.json`: 46 guidelines
- `_hierarchy.json` 기준 계층 조문 엔트리 합계: 929

즉, 문서에 적혀 있던 `929 statute articles`는 "현재 검색 가능한 로컬 파일 수"가 아니라 "계층상 조문 엔트리 수"에 가까웠다.

### 4.2 가지조문 평탄화 버그

가장 중요한 구조적 이슈:
- `제7조의2`, `제7조의3` 같은 가지조문이 개별 파일로 보존되지 않음
- 같은 기본 조문 번호(`art7.md` 등)로 덮어써지면서 마지막 가지조문만 남는 패턴 확인

실제 관찰 예:
- `library/grade-a/pipa/art7.md` 는 제7조 본문이 아니라 `제7조의14(운영 등)` 본문을 담고 있었음
- `library/grade-a/pipa-enforcement-decree/art4.md` 에서도 유사 패턴 확인
- `library/grade-a/network-act/art23.md` 는 `제23조의6` 계열이 기본 조문 번호에 흡수되는 구조가 보였음

원인:
- 수집 스크립트가 API의 `조문가지번호`를 읽지 않고 `조문번호`만으로 파일명을 생성

### 4.3 source-registry.json stale / 과장 문제

기존 `source-registry.json`은:
- 실제 디스크 파일 수가 아니라 `_meta.json`의 오래된 `article_count`를 사실상 신뢰
- `count < target` 상태를 반영하지 못함
- 결과적으로 "complete"처럼 보이지만 실제 searchable coverage는 부족한 상태였음

### 4.4 Guideline registry sync 문제

`build-guideline-index.py`는:
- 예전 경로인 `sources/grade-a/pipc-guidelines`를 참조하고 있었음
- registry 갱신 방식도 현재 레포 구조와 맞지 않았음

### 4.5 Cross-reference 품질 문제

감사 초기에 확인된 문제:
- self-reference 400건
- 동일 법령 내 미해결 target 23건

예:
- `network-act/art53.md` → `제170조`
- `credit-info-act/art24.md` → `제64조`
- `pipa/art69.md` → `제129조`, `제132조`

해석:
- self-reference는 정리 가능한 노이즈
- same-law 미해결 target 23건은 파서 오검출 또는 평탄화/누락의 후유증일 가능성이 높음

## 5. 수행한 수정

### 5.1 문서 동기화

다음 문서를 현재 상태에 맞게 수정:
- `README.md`
- `README.ko.md`
- `CLAUDE.md`
- `.claude/agents/pipa-agent.md`
- `docs/en/HOW-TO-USE.md`
- `docs/ko/HOW-TO-USE.md`

반영 내용:
- `929 articles` 대신 `550 searchable statute files / 929 hierarchy entries`로 이원화
- `source-registry.json`의 `count/target/status` 해석을 명시
- 가지조문 질의 시 `law.go.kr` 재검증 필요성을 문서화
- `pipa-enforcement-rule` 미수집 상태 명시

### 5.2 fetch 스크립트 보강

수정 파일:
- `scripts/fetch-pipa-from-api.py`

수정 내용:
- `조문가지번호` 파싱 추가
- article label / slug 생성 로직 보강
- self-reference가 frontmatter 및 `_cross-refs.json`에 남지 않도록 정리
- `article-index.json`에 `article_main`, `article_sub` 필드 추가
- `source-registry.json`을 실제 디스크 기준 `count`, `_hierarchy.json` 기준 `target`으로 재생성하도록 변경

주의:
- 이번 세션에서는 실제 Open Law API 재수집까지는 수행하지 않았음
- 따라서 "앞으로 다시 fetch할 때" 평탄화 버그를 막는 수정과, 현재 문서/인덱스/레지스트리를 현실에 맞게 정렬하는 수정이 중심

### 5.3 guideline 빌더 수정

수정 파일:
- `scripts/build-guideline-index.py`

수정 내용:
- 경로 `sources/...` → `library/...` 수정
- guideline registry entry를 현재 `source-registry.json` 구조에 맞게 병합
- `pipc-guidelines`를 `count=46`, `target=46`로 기록

### 5.4 self-reference cleanup

실행 결과:
- self-reference 포함 파일: 400개 수정
- 제거된 self-reference: 400건
- 현재 남은 self-reference: 0건

## 6. 수정 후 상태

### 6.1 source-registry.json 기준 현황

| Source | Status | Count | Target |
|--------|--------|------:|-------:|
| pipa | partial | 76 | 126 |
| pipa-enforcement-decree | partial | 63 | 140 |
| pipa-enforcement-rule | pending | 0 | 0 |
| network-act | partial | 76 | 142 |
| network-act-enforcement-decree | partial | 74 | 131 |
| network-act-enforcement-rule | partial | 10 | 11 |
| credit-info-act | partial | 52 | 91 |
| credit-info-act-enforcement-decree | partial | 38 | 81 |
| location-info-act | partial | 43 | 53 |
| location-info-act-enforcement-decree | partial | 40 | 55 |
| e-government-act | partial | 78 | 99 |
| pipc-guidelines | complete | 46 | 46 |

### 6.2 남은 미해결 이슈

- 동일 법령 내 미해결 cross-reference target: 23건
- searchable file 수와 hierarchy entry 수의 큰 차이
- 기존 corpus 자체가 이미 평탄화된 상태이므로, 스크립트 수정만으로는 자동 복구되지 않음

## 7. 검증

수행한 검증:
- `python3 -m py_compile scripts/fetch-pipa-from-api.py scripts/build-guideline-index.py`
- `python3 scripts/build-guideline-index.py`
- patched `update_indexes()` 실행으로 `article-index.json`, `source-registry.json` 재생성
- 샘플 파일 직접 확인:
  - `library/grade-a/pipa/art7.md`
  - `library/grade-a/pipa-enforcement-decree/art4.md`
  - `library/grade-a/network-act/art23.md`
- self-reference 재검산: `0`
- same-law 미해결 target 재검산: `23`

## 8. 권장 후속 작업

우선순위 순:
1. patched `scripts/fetch-pipa-from-api.py`로 법령 전체 재수집
2. 재수집 후 `art7-2.md`, `art7-3.md` 같은 branch-article 파일이 실제 생성되는지 확인
3. `article-index.json` / `source-registry.json` 재생성
4. 남은 23건 unresolved same-law reference 재감사
5. coverage가 target과 맞춰지면 README 수치를 다시 단순화할지 검토

## 9. 이번 세션에서 수정된 주요 파일

- `README.md`
- `README.ko.md`
- `CLAUDE.md`
- `.claude/agents/pipa-agent.md`
- `docs/en/HOW-TO-USE.md`
- `docs/ko/HOW-TO-USE.md`
- `docs/2026-03-27-quality-audit-log.md`
- `scripts/fetch-pipa-from-api.py`
- `scripts/build-guideline-index.py`
- `index/article-index.json`
- `index/guideline-index.json`
- `index/source-registry.json`

## 10. 결론

이번 감사로 확인된 핵심은 다음 두 가지다:
- 문서상 KB 규모와 실제 searchable corpus 사이에 차이가 있었고, 이를 문서와 인덱스에 반영했다.
- 법령 수집 파이프라인이 가지조문을 평탄화하고 있었으며, 이를 막기 위한 스크립트 수정은 반영했지만 corpus 자체를 정상화하려면 재수집이 필요하다.
