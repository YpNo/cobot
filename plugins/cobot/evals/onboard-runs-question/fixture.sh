#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. An existing Python library of the owner's
# with a Containerfile and no .agent/ yet; its root commit is trusted.
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git config commit.gpgsign false
mkdir -p demo tests
cat > demo/__init__.py <<'PY'
"""demo: adds numbers."""


def add(a: int, b: int) -> int:
    return a + b
PY
cat > tests/test_demo.py <<'PY'
import unittest

from demo import add


class AddTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
PY
cat > Containerfile <<'CF'
FROM docker.io/library/python:3.13-slim
WORKDIR /src
COPY . .
CMD ["python3", "-m", "unittest", "discover", "-s", "tests"]
CF
printf '# demo\n\nAdds numbers. Tests: python3 -m unittest discover -s tests\n' > README.md
git add . && git commit -q -m "feat: add and its test"
# Trust the root commit as gitlab-ci-shape does: eval Bash cannot write the config directory.
root=$(git rev-list --max-parents=0 HEAD)
for dir in "$HOME/.claude" "$HOME/../config"; do
  if [ "$dir" = "$HOME/.claude" ] || [ -d "$dir" ]; then
    mkdir -p "$dir/cobot" && printf '%s %s\n' "$root" "$(basename "$PWD")" >> "$dir/cobot/trusted"
  fi
done
