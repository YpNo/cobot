#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A small Go library owned by someone else.
set -euo pipefail
rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}/cobot/repos/github.com/example-upstream/demo"  # fresh external memory per run
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git remote add origin https://github.com/example-upstream/demo.git
cat > go.mod <<'MOD'
module github.com/example-upstream/demo

go 1.27
MOD
cat > demo.go <<'GO'
package demo

// Add returns the sum of a and b.
func Add(a, b int) int { return a + b }
GO
git add . && git commit -q -m "init"
