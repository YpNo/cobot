#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A new repository of the owner's: one commit
# holding a README, no remote. The README carries a random token, so every run's root commit is
# unique: a fixed root would be public, and once trusted any repository merging it in would be
# trusted too. Each run leaves one such unforgeable line in ~/.claude/cobot/trusted.
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git config commit.gpgsign false
printf '# notes2site\n\n<!-- eval %s -->\n' "$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')" > README.md
git add README.md
git commit -q -m "chore: initial commit"
