#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A Rust library whose rust-toolchain.toml
# floats on stable, with committed memory, a wrap stamp on HEAD, and an origin that is an empty
# bare repository inside .git (invisible to the stamp's readiness check; spec memory-and-ship,
# story 9). A local-path origin defeats forge detection, so CONTEXT.md says forge: github.
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git init -q --bare .git/remote.git
git remote add origin "$PWD/.git/remote.git"
mkdir -p src .agent
cat > Cargo.toml <<'TOML'
[package]
name = "demo"
version = "0.1.0"
edition = "2024"

[dependencies]
TOML
cat > src/lib.rs <<'RS'
//! demo: adds numbers.

/// The sum of a and b.
pub fn add(a: i64, b: i64) -> i64 {
    a + b
}

#[cfg(test)]
mod tests {
    #[test]
    fn adds() {
        assert_eq!(super::add(1, 2), 3);
    }
}
RS
printf '[toolchain]\nchannel = "stable"\ncomponents = ["clippy", "rustfmt"]\n' > rust-toolchain.toml
cat > .agent/CONTEXT.md <<'CTX'
# demo — context

profile: library          # spike | script | cli | library | service | infra
forge: github             # github | gitlab | gitea | other — where CI runs; ship reads it

## Goal

A small Rust library that adds numbers; to be hosted on github.com under example-org/demo.

## Stack

Rust (edition 2024), no dependency yet.

## Verified commands

| purpose | command | verified |
|---|---|---|
| unit tests | `cargo test` | 2026-11-18 |
| lint | `cargo clippy -- -D warnings` | 2026-11-18 |
| format | `cargo fmt --check` | 2026-11-18 |

## Constraints

- No third-party dependency without a decision.
CTX
printf '# Journal\n\nAppend-only, newest at the bottom.\n' > .agent/JOURNAL.md
printf '# Findings\n\n| id | seen | observation | goes to |\n|---|---|---|---|\n' > .agent/FINDINGS.md
git add . && git commit -q -m "feat: add and its test"
sha=$(git rev-parse --short HEAD)
cat >> .agent/JOURNAL.md <<EOF

## 2026-11-18 — wrap
Changed: add() and its test.
Why: first slice.
Proof: cargo test → exit 0 (1 test); cargo clippy -- -D warnings → exit 0; cargo fmt --check → exit 0.
Open: none.
Next: the delivery pipeline.
verified: $sha · cargo test · cargo clippy -- -D warnings · cargo fmt --check
EOF
git add .agent/JOURNAL.md && git commit -q -m "docs: journal with the wrap stamp"
# Trust the root commit as `cobot-memory init --trust-root` would (as gitlab-ci-shape does: eval
# Bash cannot write it, and the run's config directory sits beside its home).
root=$(git rev-list --max-parents=0 HEAD)
for dir in "$HOME/.claude" "$HOME/../config"; do
  if [ "$dir" = "$HOME/.claude" ] || [ -d "$dir" ]; then
    mkdir -p "$dir/cobot" && printf '%s %s\n' "$root" "$(basename "$PWD")" >> "$dir/cobot/trusted"
  fi
done
