#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold.
set -euo pipefail
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
