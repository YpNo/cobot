# Harnesses

One row per runtime and version cobot was run on. A cell is `ok`, `fails` or `not run`, from a
run named in the last column, never from a design argument. A reviewer or check that did not run
is `not run`, never clean. Daily use is not a run: a cell turns `ok` from a run named here.

| Runtime | Version | Validate | Install | Gate | Gate in a subagent | Brief | Agents | Run |
|---|---|---|---|---|---|---|---|---|
| Claude Code | 2.1.322 | not run | not run | not run | not run | not run | ok | eval run 43584857035 (2026-11-13): consultant fan-out, 16 of 17 passed |
| Claude Code | 2.1.311 | ok | not run | not run | not run | not run | not run | `claude plugin validate --strict`, plugin and marketplace, on 0.3.0 (2026-11-15) |
| Claude Code | as of 2026-11-06 | not run | not run | ok | not run | not run | ok | `spike-coexistence.sh` A (agent listing), B and C (push asks, force push denied); `spike-r1.sh` |
| Antigravity CLI | 1.5.9 | ok | not run | not run | not run | not run | not run | `agy plugin validate` with a throwaway HOME (2026-11-15): skills 30, agents 9, hooks 1, one warning |

The Antigravity row's live cells come from `scripts/spikes/smoke-agy.sh` (T08), run by the owner
signed in. Its check lines map onto the columns:

- Gate: `g1`, `h1` and `h2`;
- Gate in a subagent: `g2`, `w1` and `b1`;
- Brief: `s1` and `o1`;
- MCP name form: `m1`, recorded in `docs/reference/antigravity-mechanics.md`.

S4 (`agy plugin import claude`) writes the real `~/.gemini`: `not run` unless the owner asks.
