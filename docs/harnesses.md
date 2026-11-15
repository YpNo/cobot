# Harnesses

One row per runtime and version cobot was run on. A cell is `ok`, `fails` or `not run`, from a
run named in the last column, never from a design argument. A reviewer or check that did not run
is `not run`, never clean. Daily use is not a run: a cell turns `ok` from a run named here.

| Runtime | Version | Validate | Install | Gate | Gate in a subagent | Brief | Agents | Run |
|---|---|---|---|---|---|---|---|---|
| Claude Code | 2.1.322 | not run | not run | not run | not run | not run | ok | eval run 43584857035 (2026-11-13): consultant fan-out, 16 of 17 passed |
| Claude Code | 2.1.311 | ok | not run | not run | not run | not run | not run | `claude plugin validate --strict`, plugin and marketplace, on 0.3.0 (2026-11-15) |
| Claude Code | as of 2026-11-06 | not run | not run | ok | not run | not run | ok | `spike-coexistence.sh` A (agent listing), B and C (push asks, force push denied); `spike-r1.sh` |
| Antigravity CLI | 1.5.9 | ok | ok | fails | ok | ok | not run | `smoke-agy.sh` (2026-11-15, signed in, real HOME): install 30 skills, 9 agents, 1 hook; g1, g2 denied; **h2 fails**: a workspace hook group named `cobot` with `enabled: false` disables the gate; s1, o1 brief; b1 asks; w1 and m1 not reached; no cobot agent was invoked |

The Antigravity row's live cells come from `scripts/spikes/smoke-agy.sh` (T08), run by the owner
signed in. Its check lines map onto the columns:

- Gate: `g1`, `h1` and `h2`;
- Gate in a subagent: `g2`, `w1` and `b1`;
- Brief: `s1` and `o1`;
- MCP name form: `m1`, recorded in `docs/reference/antigravity-mechanics.md`.

S4 (`agy plugin import claude`) writes the real `~/.gemini`: `not run` unless the owner asks.

The 2026-11-15 run, line by line:

- `g1` ok: the main thread's `git push --force` denied by the gate.
- `g2` ok: the same push inside an `invoke_subagent` child, denied (the child's call reached the
  gate).
- `h1`: a workspace hook printing deny and exiting 1 blocked the call, and cobot's hook never
  ran for it: agy 1.5.9 stops at a failing hook, workspace hooks first.
- `h2` **fails**: with `.agents/hooks.json` holding a group `cobot` with `enabled: false`, the
  forced push went through and the gate log has no entry: hook groups merge by name across
  sources, so a committed repository file can switch the plugin's gate off. Fixed after the run
  (a random group name per install); the next run's `h2` and `h3` decide the Gate cell.
- `w1` not reached: the gate asked on `run_workflow`, and print mode denies an ask it cannot
  prompt for, so the workflow's own calls never ran.
- `b1` ok: a `branch` child after an uncommitted `.agent/cobot.rules` line asked.
- `s1` ok: the model saw the agy section and reports it as a system message (its own account).
- `o1` ok: onboard ran `cobot-memory check` through the brief's absolute path; the gate asked
  on it then (the plugin lives under the protected `~/.gemini/config/`), fixed since.
- `m1` not reached: no MCP server configured.
