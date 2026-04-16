# Private Workspace

- 권장 경로
  - `PIPA_OUTPUT_DIR=~/Private/pipa-output`
  - `PIPA_INBOX_DIR=~/Private/pipa-inbox`
  - `PIPA_PRIVATE_DIR=~/Private/pipa-private`
- 원칙
  - repo 안에는 placeholder 디렉터리만 남긴다: `_private/.gitkeep`, `library/inbox/.gitkeep`, `output/opinions/.gitkeep`
  - client DOCX, internal memo, generator scratch script는 repo 밖 private workspace에 둔다
  - env var가 repo 안 경로를 가리키면 hardening 효과가 크게 줄어든다

## Audit

- 전체 점검: `python3 scripts/security_audit.py`
- 성공 조건
  - 세 env var가 모두 repo 밖을 가리킴
  - repo root에 `.docx`가 없음
  - `_private/`는 `.gitkeep`만 남음
  - `library/inbox/`는 `.gitkeep`만 남음
  - `output/opinions/`는 `.gitkeep`만 남음
