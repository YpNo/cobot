---
name: builder-routing
description: A small Rust change is delegated to the Rust builder agent (plugin-scoped name), not to the generic builder and not to the main thread.
tags: [protocol, builders]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent]
scaffold_script: |
  mkdir -p src
  cat > Cargo.toml <<'TOML'
  [package]
  name = "demo"
  version = "0.1.0"
  edition = "2024"
  TOML
  cat > src/lib.rs <<'RS'
  pub fn add(a: u32, b: u32) -> u32 { a + b }
  RS
---

This is a Rust crate. Add a `sub(a: u32, b: u32) -> u32` function with a unit test to
`src/lib.rs`. Treat it as small work and delegate the implementation to the matching builder
agent for isolation (do not edit the file yourself in this thread); accept the builder's report
only if it carries the commands it ran with exit codes. Do not ask me anything.
