# Sanitizer

- 목적: ingest/MCP/WebSearch 텍스트에서 role-marker, jailbreak, forged firewall 토큰을 감지하고 `<escape>...</escape>`로 중립화합니다.
- 구현 위치: `scripts/lib/sanitize.py`
- 패턴 테이블: `scripts/lib/patterns.py`
- 출력: sanitized 본문 + `*.sanitize.json` sidecar

## What It Catches

- Role markers: `[SYSTEM]`, `[USER]`, `[시스템]`, `<|im_start|>`
- XML role tags: `<system>`, `</assistant>`
- Jailbreak phrases: `ignore previous instructions`, `이전 지시를 무시`
- Forged firewall markers: `[AUDIENCE FIREWALL]`

## How To Extend

1. `scripts/lib/patterns.py`에 `PatternSpec` 하나를 추가합니다.
2. `pattern_id`, `severity`, `regex`를 지정합니다.
3. `python3 -m pytest tests/test_sanitize.py -v`로 회귀 확인합니다.

## Audit Sidecar

- 파일명: `target.sanitize.json`
- 포함 정보: `generated_at`, `aborted`, `match_count`, `matches[]`
- 각 match는 `pattern_id`, `severity`, `start`, `end`, `snippet`을 가집니다.

## Manual Verification

- 파일 검사: `python3 scripts/sanitize-check.py path/to/file.md`
- stdin 검사: `cat some-text.txt | python3 scripts/sanitize-check.py -`
- 종료 코드: `0` clean, `1` matches found, `2` IO error, `3` sanitizer load failure
