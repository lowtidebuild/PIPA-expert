# Publishing Policy

PIPA-expert release notes are published on GitHub Releases:

https://github.com/lowtidebuild/PIPA-expert/releases

Repository-local release note files are not committed. This includes:

- `docs/RELEASE-*.md`
- `docs/releases/**`

If a local draft is useful while preparing a release, keep it as an ignored working file and copy the final text into GitHub Releases. Do not link README banners or workflow docs to repo-local release note drafts.

Before publishing or externally sharing a release, run:

```bash
scripts/preflight.sh
python3 scripts/security_audit.py --strict
```

`scripts/preflight.sh` treats strict security audit failures as local
development warnings. For an actual release or external share, strict security
audit is release blocking. In other words, strict security audit is release
blocking and must pass after private/output paths are moved outside the
repository.

---

# 게시 정책

PIPA-expert의 릴리즈 노트는 GitHub Releases에 게시합니다:

https://github.com/lowtidebuild/PIPA-expert/releases

저장소 내부 릴리즈 노트 파일은 커밋하지 않습니다. 아래 경로가 이에 해당합니다:

- `docs/RELEASE-*.md`
- `docs/releases/**`

릴리즈 준비 중 로컬 초안이 필요하면 ignored working file로만 보관하고, 최종 본문은 GitHub Releases에 옮깁니다. README 배너나 workflow 문서가 repo-local 릴리즈 노트 초안을 가리키면 안 됩니다.

릴리즈 또는 외부 공유 전에는 다음을 실행합니다:

```bash
scripts/preflight.sh
python3 scripts/security_audit.py --strict
```

`scripts/preflight.sh`는 strict 보안 점검 실패를 로컬 개발 warning으로 처리합니다.
실제 릴리즈 또는 외부 공유 전에는 private/output 경로를 저장소 밖으로 옮긴 뒤
strict 보안 점검이 반드시 통과해야 합니다.
