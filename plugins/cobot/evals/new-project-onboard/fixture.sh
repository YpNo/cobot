#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A new repository of the owner's: one commit
# holding a README, no remote. Author, committer and dates are fixed, so the root commit and the
# line onboard leaves in ~/.claude/cobot/trusted are the same on every run.
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
printf '# notes2site\n' > README.md
git add README.md
GIT_AUTHOR_DATE="2026-01-01T00:00:00Z" GIT_COMMITTER_DATE="2026-01-01T00:00:00Z" \
  git commit -q -m "chore: initial commit"
