# crissp, reviewed for ideas — 2026-11-06

Source: `github.com/richardedens/crissp` (Apache-2.0, Python 3.12+, first commits 2026-11-05, 21
stars, one author). Read: README, CRISSP.md, AGENTS.md, backlog/*, testsuite/README, template.

**Not adopted as a framework.** It is a product-SDLC system: a backlog with epics, features and
PBIs, a release certificate, a Helm + Terraform deploy template, a local dashboard and a panel of
virtual UX testers, all driven by a PyPI-installed engine and an MCP server. It assumes one
product per repository and a person who accepts every item on a board. Our target is a Claude
Code plugin used across many small repositories, with GitHub as the board. Its posture is close to
ours, though: AI builds, scripts prove, the owner decides, nothing outward without a yes.

## Ideas taken

| # | crissp | What we take | Where |
|---|---|---|---|
| 1 | "Guards are plain scripts, with no AI in them"; "never reports green what did not run" | **Proof, not promises**: any claim that a check passed carries the command, its exit code and the output tail; the orchestrator rejects a builder or consultant report without them | design §2, §4 report contract, `SubagentStop` check (R2) |
| 2 | FINDINGS: an observation is written the moment it is seen, with a "goes to" column, even when it is not the task at hand | `.agent/FINDINGS.md`, one row per parked observation; wrap triages rows into spec tasks, issues or `closed — reason`. Stops drive-by fixes and lost observations at once | §7 memory |
| 3 | A decision is a question with options **and a recommendation**; ask only for what is expensive to undo | Clarify questions in the spec always carry options and a recommended default; everything else is acted on and written down | §5 conceptor |
| 4 | Impact plan: a change runs only the steps its paths can affect; shared ground runs everything | Optional `paths → commands` table in CONTEXT.md; build runs the matching focused commands, wrap runs the full set | §7, build skill |
| 5 | Release certificate: a deploy needs a green full run on exactly this commit | A **verified stamp** in the wrap journal entry (`verified: <sha> · <commands>`); `contribute` and `ship` refuse to propose a push or PR when HEAD does not match the stamp | §7 journal, contribute/ship skills |
| 6 | The MCP `brief` answers with exactly the lines Claude needs instead of files | `partner-memory brief` is the SessionStart payload; skills ask for slices, never whole files | §10 token economy |
| 7 | `measure.py` turns Claude Code transcripts into per-session usage pages | `partner-usage` (R2): tokens per role and per skill from the local transcripts, the evidence behind any routing change | §10, §15 |
| 8 | Personas run outside the repository "so its agreement does not steer them" | The challenger gets `omitClaudeMd: true` and receives the spec as data, so the repo's own instructions cannot soften its objections | §4 challenger |
| 9 | `accepted-risks.json`: a finding is accepted for at most 90 days, with why and by whom | `.agent/accepted-risks.md` for `security-sweep`, same three fields, expiry enforced by the skill | R1.1 |
| 10 | `changes.json`: per change the problem, the fix and the tests that prove it | The journal entry keeps `Proof` as a first-class line, not an afterthought in `Tests` | §7 |

## Ideas left out

| crissp | Why not |
|---|---|
| Epic → feature → PBI backlog in Markdown, moved to `done/` by hand | GitHub issues plus the spec's task list already cover small projects; a second board is the two-planning-systems defect of the old scaffold |
| Coverage gate that only goes up, 100 % on the guard libraries | A repository concern; `ship` may offer a ratchet, the partner's own `bin/` is held at the 85 % floor |
| Dashboard, Sessions pages | A server to maintain; the measurement idea is kept, the UI is not |
| UX panel of five personas, designer, before/after approval | Only one of the owner's repos has a UI; parked as a possible plugin idea, not R1–R3 |
| Journeys as documentation, films | Same |
| Helm + Terraform deploy template | Out of scope for a partner plugin; `partner-gcp` and delivery plugins own this later |
| MCP server as the hands for writing the backlog | Our `bin/` scripts do it with zero MCP context cost and one deterministic surface for the gate |
| `F-42:` commit format | Conventional Commits stay, the owner's convention across repositories |

Watch item: the project is one day old with one author. Re-read it in a quarter for what the
release certificate and impact plan became in practice.
