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

- 개발 점검: `python3 scripts/security_audit.py`
  - repo 내부 기본 경로는 clone 직후 사용성을 위해 WARN으로 표시하고 exit 0
  - 실제 private artifact가 repo 안에 있으면 FAIL
- 릴리즈/외부 공유 전 점검: `python3 scripts/security_audit.py --strict`
  - 세 env var가 repo 내부를 가리키거나 누락되면 FAIL
- 전체 점검: `scripts/preflight.sh`
- strict 성공 조건
  - 세 env var가 모두 repo 밖을 가리킴
  - repo root에 `.docx`가 없음
  - `_private/`는 `.gitkeep`만 남음
  - `library/inbox/`는 `.gitkeep`만 남음
  - `output/opinions/`는 `.gitkeep`만 남음
