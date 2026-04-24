#!/usr/bin/env bash
set -u

status=0

run_required() {
  printf '\n==> %s\n' "$*"
  "$@"
  code=$?
  if [ "$code" -ne 0 ]; then
    printf 'required check failed: %s\n' "$*" >&2
    status=1
  fi
}

run_warning() {
  printf '\n==> %s\n' "$*"
  "$@"
  code=$?
  if [ "$code" -ne 0 ]; then
    printf 'warning check failed: %s\n' "$*" >&2
  fi
}

run_required pytest -q
run_required python3 -m pip check
run_required python3 scripts/security_audit.py
run_warning python3 scripts/security_audit.py --strict
run_required python3 scripts/build_compact_index.py --check
run_required python3 -c "import citation_auditor; import scripts.audit_document; import scripts.docx_citation_appendix; import scripts.lib.mcp_budget; print('imports ok')"

printf '\n==> stale text scan\n'
if rg -n "550 searchable|550개 검색|\\[주소\\]|\\[수신인 이름\\]|# \\.\\.\\." README.md README.ko.md docs/en/HOW-TO-USE.md docs/ko/HOW-TO-USE.md .claude/skills/legal-opinion-formatter; then
  printf 'required check failed: stale text remains\n' >&2
  status=1
fi

exit "$status"
