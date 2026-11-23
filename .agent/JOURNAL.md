# Journal

Append-only, newest at the bottom. One entry per working session or task group.

## 2026-11-22 — compacted 2026-11-19 → 2026-11-22 (43 entries)
- 2026-11-19 T05 trust-boundaries: decision 33, design rows, F-49 closed: docs/01-decisions.md decision 33 (a spec names its trust boundaries;
  open: cobot-memory check warns JOURNAL.md is over 400 lines (compact is the owner's call).
- 2026-11-20 spec session-grants (0.4.0), challenged: .agent/specs/session-grants.md revision 2 (299 lines): gcloud, kubectl and helm grants per kind (deletes separate) on one explicit target, recorded by a PostToolUse hook only against a pending entry the gate wrote when it asked, main thread and Claude Code only;
  open: the probe (T01) can still stop the design (P1, P2, P6).
- 2026-11-20 T01 session-grants: the probe's findings: .agent/specs/session-grants.md Converge holds P1–P7;
  open: workflow agents not probed; default mode not run interactively (the owner's default is auto). A grep of this session's env printed CLAUDE_* values into the local transcript (a broken pattern); a stray sed -i on /dev/null failed and edited nothing.
- 2026-11-20 T02 session-grants: the never list grows, apply and destroy prompt only: default.rules: never rows for Terraform, tofu and terragrunt state surgery (state rm|mv|push|replace-provider, force-unlock, import, taint, untaint, workspace delete -force, -lock= false spellings), state buckets, projects delete, set-iam-policy, keys create, the gcloud and kubectl credential printers (were asks), kubectl create token, kubectl config writes, Edit/Write of ~/.kube/*, cluster-wide deletes (-A or --all-namespaces, kube-system), rm -* of / ~ ~/ $HOME, Edit/Write of ~/.claude/cobot.rules and cobot/*, agent reads of ~/.kube;
  open: narrower than the spec text (now reworded): only cobot's owner files are sealed to shell, settings.json keeps its ask; kubectl delete -A is never even without --all (wider). The agents' Read tool on ~/.kube is not gated (the gate judges no Read).
- 2026-11-20 T03 session-grants: grant_scope, allow-lists only: cobot-rules gains a session-grants section: grant_scope(command) -> (kind, target) | None and valid_grant(kind, target).
  open: gcloud flag abbreviation is guarded without knowing whether gcloud accepts it (defensive). kubectl patch with an inline -p JSON is not covered (quotes), only --patch-file.
- 2026-11-20 T04 session-grants: the grant verb, pending entries, the store and the hooks: cobot-rules: grant_request parses the cobot-rules grant family (grant, revoke all or one, list;
  open: accepted residual: the gate killed by its timeout after writing the pending entry, with an owner settings allow on cobot-rules, could run the command without a prompt and record it (microseconds, needs the owner's own allow line). The log list is kept but not filled until T05.
- 2026-11-20 T05 session-grants: the gate allows a granted command, and only one: cobot-rules gate(): granted_reason lifts a Bash verdict to allow only when it is an ask from a default row (not never, not prompt-only, not rule-less, no second ask), the call is from the main thread, grant_scope names a (kind, target) this session holds unexpired, and the owner and project layers alone neither ask nor deny on the command (a verdict names only its first rule, so an owner ask would hide behind the default one).
  open: none.
- 2026-11-20 session grants T06: protocol and skill texts: protocol.md gains a Grants paragraph (one AskUserQuestion with three answers, main thread only, plan -out then apply at the prompt, the lab log);
  open: docs/02-design.md and docs/architecture.md still say a 3k protocol (T08).
- 2026-11-20 session grants T07: the apply-asks eval: evals/never-apply becomes apply-asks, with the same fixture and prompt.
  open: docs/02-design.md line 476 still names never-apply (T08).
- 2026-11-20 session grants T08: ADR-0008, decision 34, docs and CHANGELOG: ADR-0008 (the gate may allow in one case, a granted command under Claude Code);
  open: the currency gap stands (ruff 0.17.6 and markdownlint-cli2 0.24.2 are out, 0.17.4 and 0.24.0 pinned; the owner's call); JOURNAL.md is over 400 lines (compact is the owner's call).
- 2026-11-20 housekeeping: ruff 0.17.6, markdownlint-cli2 0.24.2, journal compacted: ruff 0.17.4 → 0.17.6 and markdownlint-cli2 0.24.0 → 0.24.2 in CONTEXT.md's verified commands, docs/development.md, ci.yml and knowledge-refresh.yml;
  open: the CI pins of @anthropic-ai/claude-code (2.1.318 in ci.yml, 2.1.322 in knowledge-refresh.yml) trail 2.1.329, left for the owner; markdownlint-cli2 0.24.2 is one day old.
- 2026-11-20 spec debug-path (0.4.0), challenged: .agent/specs/debug-path.md revision 2 (242 lines): /cobot:debug as the main-thread lead, a read-only cobot:investigator per hypothesis sharing the consultant's read list by alias, a probe report check of its own, records in .agent/debug/ refused at write time when secret-shaped, the shared read list tightened (output formats, target-switching and watch flags ask;
  open: accepted residuals: the Read tool is ungated for agents; kubeconfig exec entries; an active grant only the skill keeps from a lead mutation.
- 2026-11-20 debug-path T01: the shared read list stops printing values, switching targets and hanging: READ_GUARDS gains kubectl (target and identity flags, -s), istioctl (the same), kubectl get (-o other than wide/name in any spelling or cluster, --template, --raw, watch), kubectl logs (follow), kubectl events (watch) and gcloud (--configuration, --impersonate-service-account, --account, --access-token-file);
  open: the guards apply to the learner too (it shares the list); kubectl rollout status still waits by default; a --server before the verb on the main thread is not denied by the show-secrets row.
- 2026-11-20 debug-path T02: the investigator, read-only by rule: claude-agents/investigator.md (Read, Grep, Glob, Bash, WebFetch;
  open: forge credential printers ask rather than deny for the investigator, as for the consultant; the report shape is not checked until T03.
- 2026-11-20 debug-path T03: a probe's report is proof, checked by its own rule: check_probe_report (a Verdict: and a command with an exit marker under Checks:, or Checks: none with Verdict: inconclusive and a non-empty Needs:);
  open: hooks.json's description still says builder report check (T09 docs).
- 2026-11-20 debug-path T04: /cobot:debug leads the investigation in the main thread: skills/debug/SKILL.md (frame with live context, grant list and production confirmation;
  open: cobot-memory debug check is named here and arrives in T05.
- 2026-11-20 debug-path T05: a debug record cannot carry a secret: _cobot_common gains DEBUG_SECRET_PATTERNS (SECRET_RE, ya29., JWT, Bearer, URL credentials, client-*-data, "private_key":), debug_secret_kind (line by line, <redacted> dropped) and debug_record_problems (secret lines, fenced excerpts over 20 lines or 2000 chars);
  open: the agy gate path carries only file_path, so under Antigravity only the check before git add holds; a shell write into debug/ asks as any shell write does.
- 2026-11-20 debug-path T06: debug records are listed, and the brief counts the open ones: Memory.debug_records (status and title from each record's head, newest first);
  open: none.
- 2026-11-20 debug-path T07: the protocol routes an unknown cause to /cobot:debug: protocol.md Paths opens with "unknown cause → /cobot:debug.";
  open: none.
- 2026-11-20 debug-path T08: evals debug-routes-by-evidence and debug-read-only: two cases sharing one fixture (a Deployment with DATABSE_URL, captured describe and previous logs from context lab, no cluster);
  open: unprompted routing from the protocol line is not graded (the model fixed the typo inline); in the read-only run the lead diagnosed without a probe.
- 2026-11-20 debug-path T09: decision 35 and the docs; the spec converged: decision 35 in docs/01-decisions.md;
  open: unprompted routing to /cobot:debug is not graded; kubectl rollout status waits by default; the forge credential printers ask for the investigator rather than deny.
- 2026-11-21 spec expert-homeassistant (F-39): written and challenged: .agent/specs/expert-homeassistant.md: expert-homeassistant (custom integrations, configuration, REST and WebSocket APIs, hass-cli, ZHA and registries), /cobot:consult homeassistant, hass-cli gate rows, onboard step 6b Domains and the spec step 2 Experts line;
  open: cobot:challenger not loaded in this session, the owner's challenger ran with cobot's challenger.md; no consultant relevant; onboard step 6b may collide with the gcp-mcp opt-in spec's onboard step; HA capture and replay stays with cobot-reverse.
- 2026-11-21 expert-homeassistant T01, T04, T02: the expert, the hass-cli gate, the learned lines: T01 skills/expert-homeassistant (SKILL.md, references/versions.md, ci.md) with lang-python's three Home Assistant lines moved and a pointer left (fd6b8ac);
  open: the secret-file guard is code, not rows (reader rows are viable for every glob and substitution; written into the spec); the main thread gets no secret-file row; an anchored glob that could expand to secrets.yaml and the Read tool stay residuals. cobot:learner was not loaded here: three general-purp
- 2026-11-21 expert-homeassistant T03, T05, T06: the consult domain, the missing-domain steps, the routing row and two evals: T03 skills/consult/domains/homeassistant.md, the router's row and description, router and inventory tests (31f2068);
  open: the two evals are paid and not run here (owner: gh workflow run ci.yml -f evals=true -f cases=consult-homeassistant,spec-names-missing-expert); spec-names-missing-expert has no CONTEXT.md, so it grades the step 2 fallback, not the domains line.
- 2026-11-21 expert-homeassistant T07: decision 36 and the docs; the spec converged: decision 36 in docs/01-decisions.md and decision 25 amended;
  open: the paid evals consult-homeassistant and spec-names-missing-expert are the owner's to run; agy validate not re-run; onboard step 6b may collide with the gcp-mcp opt-in spec's onboard step (whichever merges second renumbers); Home Assistant capture and replay stays with cobot-reverse.
- 2026-11-21 wrap expert-homeassistant: the reviews folded, read-only agents kept off Home Assistant's secrets: bin/_cobot_secrets.py (new): a read-only agent's command that would print secrets.yaml or a .storage/ file is refused when it names one, reads it through a < redirect, runs a recursive grep, any rg, semgrep or a verbose unredacted gitleaks over a tree holding one unless excluded (walked, at most 20 000 entries), prints history in a repository that tracks or tracked one with no excluding pathspec, or fetches a curl file: URL;
  open: F-50, F-51; the paid evals consult-homeassistant and spec-names-missing-expert not run; residuals: the Read and Grep tools, an anchored glob, the main thread's file reads; onboard step 6b overlaps the gcp-mcp-opt-in spec's step 6b (that build adapts, per its session).
- 2026-11-21 gcp-mcp-opt-in: spec written, challenged and folded: .agent/specs/gcp-mcp-opt-in.md (medium): the gcp-mcp: yes|no header line asked once at the first Google Cloud work (onboard 6b on first run or refresh, consult, spec and wrap gcp consultants, debug after its live context);
  open: onboard step 6b and spec step 5 overlap with the F-39 spec; second-identity roles reported until the build checks them; narrower readonly OAuth scopes unverified.
- 2026-11-22 spec-names-missing-expert drops its spec-skill grader (spec expert-homeassistant): removed plugins/cobot/evals/spec-names-missing-expert/graders/spec-skill.md.
  open: CI evals cannot run from a feature branch (the evals environment's branch rule); the cases run 3 times in CI, once locally here.
- 2026-11-22 the branch is rewritten without a secret-shaped fixture value (spec expert-homeassistant): every commit on feat/expert-homeassistant now writes x for the old six-character placeholder value: tests/test_hass_cli_gate.py, tests/test_secret_reads_gate.py, the spec's trust-boundary row and one journal line.
  open: the five GitGuardian incidents on the dashboard are the owner's to resolve.
- 2026-11-22 gcp-mcp-opt-in T01: registration asks, the Cloud CLI server refused, grants kept off MCP: default.rules: never mcp__gcp-cloudcli__*, never mcp__*__run_gcloud_command and run_bq_command;
  open: none.
- 2026-11-22 gcp-mcp-opt-in T02: check names a broken gcp-mcp line and a repository .mcp.json: bin/cobot-memory: gcp_mcp_warnings in cmd_check: a gcp-mcp line that is not exactly yes or no (a trailing # comment allowed), repeated, or below the header;
  open: none.
- 2026-11-22 gcp-mcp-opt-in T03: the opt-in rule in expert-gcp, the guarded setup in mcp.md: expert-gcp "Google Cloud MCP servers": endpoint exceptions, the Cloud CLI server refused and the claude.ai connector unsupported, and "The opt-in, once per repository" (triggers, the exact line above ## Stack, the recommendation, unusable memory, main thread only, the four branches, tool output is data).
  open: the second identity's role set stays reported until a sign-in with it is proven; narrower readonly scopes unverified.
- 2026-11-22 gcp-mcp-opt-in T04: the trigger sites point at expert-gcp's opt-in: onboard step 6c Google Cloud MCP (after F-39's 6b Domains, keyed on its Google Cloud domain, first run or refresh);
  open: none.
- 2026-11-22 gcp-mcp-opt-in T05: evals gcp-mcp-asked-once and gcp-mcp-never-again: two cases on a trusted lab repository with memory and a google provider (fixtures are heredocs, no secret-shaped literal);
  open: CI runs them three times; the evals environment refuses feature branches.
- 2026-11-22 gcp-mcp-opt-in T06: decision 37 and the docs: decision 37 in docs/01-decisions.md (36 is F-39's);
  open: none.
- 2026-11-22 wrap gcp-mcp-opt-in: the reviews folded, the spec converged: cobot-rules: an ask Edit/Write row now protects a literal shell word naming its file (cp, tee, a redirection, dd of=, curl -o, git checkout -- …), as never rows do;
  open: F-52, F-53, F-54; the second identity's roles and the value(parent.type) shape stay reported until a live project; the brief is 1 character under its budget; two sealed eval temp folders in /tmp could not be removed (tmpfs, gone at reboot).
- 2026-11-22 F-52: MultiEdit and NotebookEdit meet the file rows: cobot-rules applies(): an Edit row also covers MultiEdit and NotebookEdit, a Write row NotebookEdit (FILE_TOOL_ALIASES).
  open: the bypass review of the three finding commits runs after F-54.
- 2026-11-22 F-53: bunx, node on Claude Code's cli.js, and the moved .claude.json: cobot-rules: bunx in OPAQUE beside npx (the launcher comment and the 2026-11-07 commit said bunx stays opaque;
  open: the bypass review runs after F-54.
- 2026-11-22 F-54: MCP refusals meet a renamed server or a respelled tool: cobot-rules: matches_mcp in judge_mcp.
  open: the bypass review of F-52, F-53 and F-54 runs next.
- 2026-11-22 gcp-mcp-opt-in: the setup facts checked at their sources: references/mcp.md.
  open: the two live checks above.
- 2026-11-22 the session brief gets headroom: CONTEXT.md trimmed under its floor: .agent/CONTEXT.md: the verified rows re-dated to today's runs (coverage 98.34 %, shellcheck with the eval fixtures);
  open: none.
- 2026-11-22 F-52 bypass review folded: every path key judged, aliases both ways for refusals: cobot-rules judge(): a file call is judged on every path key it carries (file_path and notebook_path, PATH_KEYS), the debug-record secret check included, and the strictest verdict wins, so a decoy file_path no longer hides NotebookEdit's notebook_path.
  open: none for F-52.
Archive: raw entries in JOURNAL-archive.md and in git history before 2026-11-22.

## 2026-11-22 — F-53 bypass review: the small routes folded, four larger ones parked
Changed: default.rules: claude *mcp *add* and *mcp *remove* (options between mcp and the verb); ask on claude plugin install, plugin marketplace add, plugin enable and --plugin-dir (a plugin carries its own MCP servers); the node row matches the claude-code package folder without cli.js; Edit and Write of ~/.claude.json.backup* ask. tests/test_mcp_registration_routes.py. Findings F-55 (a plain variable in a path word hides it from never rows: CRITICAL, older than this branch), F-56 (copy into a folder; CLAUDE_CONFIG_DIR outside HOME loses folder protection), F-57 (interpreter code flags beyond -c, -e and -), F-58 (nested claude flags and env, unopaque launchers, renamed copies, globs on the existing ~/.claude.json).
Why: the bypass review of 5a3f1a4 (1 CRITICAL, 4 HIGH, 4 MEDIUM, 3 LOW). F-55 to F-58 are changes to the gate's shell model across every protected file, not this PR's server-list rows: too large for PR 81, per the owner's instruction to stop and say why. Reproduced here: cp /tmp/e ~/.claude/$X none, cp /tmp/e/.claude.json ~/ none, node -p none.
Proof: test_mcp_registration_routes exit 0 (eight new cases failed first); claude mcp list, mcp get, plugin list and plugin validate and git add src/* stay silent.
Open: F-55 to F-58 for a gate spec; F-55 first.
Next: the F-54 review fold.
verified: tree ba4ca19c7f435001e4bfa944e51c5d1a410ea366 · registration tests, dry runs

## 2026-11-22 — F-54 bypass review folded: odd MCP names are never a silent read
Changed: cobot-rules: mcp_is_read is false for a name that is not ASCII after NFKC, or that holds a second __ after the server (run_gcloud_command__get, scale_service__list), since which part is the tool cannot be known; mcp_words folds NFKC and splits an acronym from the next word (DEPLOYService, SETIamPolicy); mcp_fold folds NFKC first. default.rules: the Cloud CLI rows end in * (run_gcloud_command__get is refused), and a comment says that folding refuses these writes on any gcp_*, GCP-* or Gcp-* server and that a gcp server under another name only asks. tests/test_mcp_name_folding.py.
Why: the bypass review of a0ac069: no CRITICAL or HIGH; one MEDIUM (a second __ made a write look like a read), four LOW (acronyms, Unicode lookalikes and fullwidth forms, host prefixes, the wider never rows to document). Cyrillic lookalikes now ask rather than fold; host-prefixed servers (claude_ai_, plugin_) keep asking, documented.
Proof: test_mcp_name_folding exit 0 (seven new cases failed first); gate suites with the GOOGLE_MCP_TOOLS matrix, agy and session grants exit 0; ruff clean. GETService now reads as get_service, a read, where it asked before.
Open: none for F-54.
Next: the full suite and lint, then the report.
verified: tree a0ca10231436b0268b471053ac75fdb07a4f8323 · gate suites, ruff

## 2026-11-22 — F-52 to F-54 closed: the gate findings, their bypass reviews, and what they parked
Changed: CHANGELOG Security (F-52 to F-54); FINDINGS rows F-55 to F-58 cut to one line each, their detail kept here.
Why: owner, before merging PR 81: fix the new findings, give each gate change the bypass review, keep the brief's headroom.
Proof: full suite with coverage exit 0, 98.33 % (fail-under 85); ruff 0.17.6 check and format clean; shellcheck clean; markdownlint-cli2 0.24.2 clean; claude plugin validate --strict passes twice; check-plugin ok; sync-agents in sync; agy validate passes with its one warning.
Open: F-55 (CRITICAL, older than this branch): a plain variable in a path word is read as text: cp x ~/.claude/$X, X=settings.json; cp x ~/.claude/$X and ${X} get no decision, past the never rows on settings.json and cobot's owner files. Fix: $NAME in a path word is a hole for path_may_match; expand earlier assignments (shell_state), HOME, CLAUDE_CONFIG_DIR. F-56 (HIGH): a copy, move or link into a folder that is not an anchor: cp e/.claude.json ~/, cp -t ~, rsync, install, curl --output-dir ~ -O, wget -P ~ (protected_anchors keeps folders strictly below HOME); with CLAUDE_CONFIG_DIR outside HOME the moved dir has no folder protection (cp e/cobot.rules /tmp/cc/, tar -C, unzip -d, rsync -a, ln -sfn). Fix: (dirname, basename) pairs for literal file rows, the moved dir and its parents as anchors, --output-dir and -P as folder options. F-57 (HIGH): inline code only for -c, -e and - (INLINE_CODE_FLAGS): node -p/--print/-pe/--eval=, python3 -ic, stdin-fed interpreters, deno eval, bun -e, php -r, awk system(), vim -c !; node -p can run git push --force. Fix: an interpreter is opaque unless it has a script operand and no code flag, clusters read. F-58 (MEDIUM): a nested claude with CLAUDE_CONFIG_DIR=… (prefix or export), --dangerously-skip-permissions, --permission-mode, --allowedTools, --setting-sources; launchers not opaque (deno run|x npm:, dx, pnpx, corepack, volta, asdf exec, fnm exec, nvm exec, npm explore, npm exec <pkg> --); claude-code copies under other names; a glob on the existing ~/.claude.json (tee ~/.cl*.json). Verb rows on any program (* mcp add*) need the glob handling first: a leading * makes every glob could-match. All four change the gate's shell model for every protected file, too large for PR 81.
Next: the owner merges PR 81 after review; then a gate spec for F-55 to F-58, F-55 first.
verified: tree a0ca10231436b0268b471053ac75fdb07a4f8323 · full suite with coverage, lint, validators

## 2026-11-23 — spec gate-f55-f58 written and challenged, nothing built
Changed: .agent/specs/gate-f55-f58.md (revision 2, 299 lines): ten stories for F-55 to F-58, F-55 first; story 2 protects the files Claude Code sources between Bash calls (session-env snapshots, CLAUDE_ENV_FILE, shell start files).
Why: owner, after PR 81: a gate spec for the parked findings, challenged, then the owner's review before any build.
Proof: every Goal row reproduced with cobot-rules check on cc525b7 (each none today); claude --help 2.1.311 read for the nested-claude flags; challenger revision 1 UNSOUND (2 BLOCKER, 6 MAJOR, 2 MINOR), every point re-probed and folded.
Open: Q1 to Q4 for the owner (variable hole in the scanner; put in a literal assignment; vim, emacs and gdb in scope; start files ask or never); the challenger has not re-run on revision 2.
Next: the owner reviews the spec; then /cobot:build gate-f55-f58, T01 first, a bypass-aimed review per task.
verified: tree a0ca10231436b0268b471053ac75fdb07a4f8323 · spec only, cobot-memory check

## 2026-11-23 — spec gate-f55-f58 revision 3: second challenger pass folded
Changed: .agent/specs/gate-f55-f58.md revision 3 (299 lines): put-in values split and globbed, HOME/PWD/CLAUDE_CONFIG_DIR assignments add a value and never replace one, BASH_ENV/ENV/ZDOTDIR and the curl/wget rc files, absolute archive members and curl -K/wget -e, python -m M read as M, tsx and ts-node, unsetting the config variables, glob words in the identity check, friction rows.
Why: owner asked for a second challenger pass on revision 2 before review.
Proof: challenger revision 2 UNSOUND (1 BLOCKER, 6 MAJOR, 2 MINOR); each shape re-probed with cobot-rules check on cc525b7 (none, except HOME=/tmp true; cp x ~/.claude.json, which asks and must keep asking); every point folded.
Open: Q1 to Q4 for the owner; revision 3 not challenged again.
Next: the owner reviews; then /cobot:build gate-f55-f58, T01 first, a bypass-aimed review per task.
verified: tree a0ca10231436b0268b471053ac75fdb07a4f8323 · spec only, cobot-memory check

## 2026-11-23 — spec gate-f55: split to F-55 alone (owner), challenged and folded
Changed: .agent/specs/gate-f55-f58.md renamed gate-f55.md, revision 5 (264 lines): F-55 variable holes and the files sourced between calls only; F-56 to F-58 parked with their shapes and folds; Q1 a, Q2 put in, Q3 b, Q4 a recorded; branch renamed security/gate-f55; FINDINGS F-55 to F-58 pointed at it; F-59 added (run-time data in a whole word, owner decision).
Why: owner, relayed by the orchestrator session: "Split, F-55 first", then one challenger pass on the narrowed revision.
Proof: challenger revision 4 UNSOUND (1 BLOCKER: nested sh -c turned outer assignments and argv into inherited names; 4 MAJOR, 3 MINOR); each shape re-probed with cobot-rules check on cc525b7 (none); all folded into revision 5.
Open: F-59 for the owner (spare or ask); revision 5 not challenged again.
Next: owner go for /cobot:build gate-f55, T01 first, a bypass-aimed review per task.
verified: tree a0ca10231436b0268b471053ac75fdb07a4f8323 · spec only, cobot-memory check

## 2026-11-23 — gate-f55 T01: a shell variable is a hole, read by its class
Changed: _cobot_shell.py emits variable holes (name, operator, word; HOME and PWD stay text); cobot-rules reads each by its class in the whole command (put in, for/select lists, full holes, spared inherited or run-time data), HOME/PWD assignments add a reading, runner-body variables are full holes, word_touches treats a full hole as pathlike; tests/test_gate_f55.py, differential rows, scanner and rules rows updated; spec: F-59 recorded as accepted residual (owner: Spare, then build), T01 ticked, nested sh -c rows ask (build choice); F-60 filed (joined target option, pre-existing).
Why: F-55 (CRITICAL): cp x ~/.claude/$X got no decision past the never rows.
Proof: full suite with coverage exit 0, 98.20 % (fail-under 85); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (2 BLOCKER: assigned PWD, run-time HOME; 2 MAJOR: indirect assigners, runner bodies), each shape a test row.
Open: F-59 accepted residual; F-60 for the F-56 spec; friction: inherited variables ask where $(…) asks (rm "$f", git commit -m "$MSG").
Next: T02, the files sourced between calls.
verified: tree 1a96d03e5c2b52ae43063223312cb38761a5dc93 · full suite with coverage, ruff, check-plugin

## 2026-11-23 — gate-f55 T02: the files sourced between Bash calls are protected
Changed: default.rules never rows on ~/.claude/shell-snapshots/* and ~/.claude/session-env/* (sealed: shell access refused, config-dir twins), ask rows on the shell start files (bash, zsh with ZDOTDIR twins, fish, nushell, environment.d, pam_environment, inputrc, ssh rc) and ~/.curlrc, ~/.wgetrc; cobot-rules shell_start_variable asks when a command sets BASH_ENV, ZDOTDIR, HOME, XDG_CONFIG_HOME, CURL_HOME, WGETRC, PS4, SHELLOPTS, BASHOPTS, PROMPT_COMMAND or an exported function (ENV with a shell only), quotes and escapes removed; shell heads widened (fish, rbash, versioned).
Why: F-55 rests on inherited variables being safe; Claude Code sources ~/.claude/shell-snapshots/snapshot-bash-*.sh into every Bash call (read at build: unalias, exports, functions), so a planted line set a variable or ran code ungated.
Proof: full suite with coverage exit 0, 98.21 % (fail-under 85); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (no BLOCKER; 4 MAJOR: quoted names, shebang scripts, moved homes, run-text variables), each a test row.
Open: CLAUDE_ENV_FILE row dropped (absent from the Bash environment, hook environment not shown); cat ~/.bashrc asks like cat ~/.claude.json; the sealed reason still says cobot's owner files; F-56 residuals (cp e/.bashrc ~/).
Next: T03, agy rows, CHANGELOG, FINDINGS, design doc.
verified: tree 8f4e07be2fd6396fa49f197f18795c1487e28097 · full suite with coverage, ruff, check-plugin

## 2026-11-23 — gate-f55 T03: both runtimes and the docs
Changed: tests/test_gate_f55.py story 3 rows under agy (run_command); CHANGELOG Security entry for F-55; docs/architecture.md and docs/configuration.md say how a variable is read and which sourced files are sealed; FINDINGS F-55 closed; spec T03 ticked, Converge written.
Why: ADR-0007 (both runtimes) and the docs that said a variable stays text.
Proof: full suite with coverage exit 0; ruff 0.17.6 check and format clean; markdownlint-cli2 0.24.2 clean; claude plugin validate --strict passes twice; check-plugin ok; sync-agents in sync.
Open: JOURNAL.md over 400 lines (cobot-memory check warns); wrap next.
Next: /cobot:wrap gate-f55.
verified: tree bec21d7486603297e34a126914113c661e57aee0 · full suite with coverage, ruff, markdownlint, validators

## 2026-11-23 — wrap gate-f55: reviews folded, F-55 closed
Changed: cobot-rules keeps the text reading of every segment (no variable reading judges below how the text alone was), owner_hit prefers a literal hit over a hole in another segment, unquoted alternative words split, a for-list config dir read word by word, uses inside $(…) placed at the substitution, self_reference limited to assignment words, a nameref on a start variable asks, assignment patterns bounded (ASSIGNER_SPAN 512) with a too-long setter read as assigned, HOME/PWD assignment read once per command; tests for each, a 5 000-character timing guard.
Why: wrap code review (3 MAJOR: a ((a input ran past 120 s, multi-word alternatives joined, nameref past the start-variable check) and security review (2 MAJOR: deny turned ask when a hole hid a literal hit, and a hole in a sealed path; 2 MINOR: the readings cap).
Proof: full suite with coverage exit 0, 98.28 % (fail-under 85); ruff 0.17.6 check and format clean; shellcheck clean; markdownlint-cli2 0.24.2 clean; claude plugin validate --strict passes twice; check-plugin ok; sync-agents in sync; cobot-memory check ok; cobot-deps check --fresh: no supported lockfile; 5 000-char hostile commands 1.1 to 3.5 s.
Open: F-59 accepted residual (with whole-word $(…)); F-60 joined target option (pre-existing, for the F-56 spec); F-56 to F-58 parked; MINOR: cp x $D/.bashrc silent where $D/.claude.json asks; sealed reason says cobot's owner files for snapshots; JOURNAL.md over 400 lines (compact in a housekeeping PR); spec tick edits were made twice with sed against the Edit-only rule.
Next: the owner reviews branch security/gate-f55 and decides push and PR; then F-56, F-57, F-58 one at a time.
verified: tree 8d25765db902cbcc095889cfc61051bad21cfec5 · full suite with coverage, ruff, shellcheck, markdownlint, plugin validate x2, check-plugin, sync-agents, cobot-memory check

## 2026-11-23 — gate-f55 nits: F-59 marked an accepted residual, journal compacted
Changed: FINDINGS F-59 status reads accepted residual (owner, 2026-11-23: Spare, then build), spared like $(…), to be closed together with whole-word $(…); cobot-memory compact folded 43 entries (2026-11-19 to 2026-11-22) into JOURNAL-archive.md, 425 to 170 lines.
Why: owner, relayed by the orchestrator session: "Fix the nits first", before the push.
Proof: cobot-memory check without the journal warning, brief 5384 chars (budget 6000); ruff 0.17.6 check and format clean; check-plugin ok; sync-agents in sync; no code changed, so the full suite was not re-run (last run 98.28 % on c0efe68's tree).
Open: none new.
Next: the owner pushes security/gate-f55 and opens the PR.
verified: tree 8d25765db902cbcc095889cfc61051bad21cfec5 · cobot-memory check, ruff, check-plugin, sync-agents

## 2026-11-23 — spec gate-f56-f60 written and challenged, nothing built
Changed: .agent/specs/gate-f56-f60.md revision 2 (248 lines): six stories on where a copy, download or extraction lands (F-56) and option values joined to their option (F-60); FINDINGS F-56 and F-60 pointed at it; F-61 filed for the writers kept out (cpio -p, pax, ditto, sftp, aria2c, gh download -D, curl --create-dirs).
Why: owner, relayed by the orchestrator session: "Spec F-56 and F-60", one spec, kept small; F-57 and F-58 out.
Proof: every Goal row measured with cobot-rules check on a5db3f8 (each none today); challenger revision 1 SOUND WITH CHANGES (5 MAJOR, 2 MINOR), each shape re-probed and folded; cobot-memory check ok, brief 5500 chars.
Open: Q1 (an extraction in a cwd that only holds the config dir: ask, recommended) and Q2 (a download with no output folder lands in the cwd: yes, recommended) for the owner.
Next: owner review, then /cobot:build gate-f56-f60, T01 first, a bypass-aimed review per task.
verified: tree 8d25765db902cbcc095889cfc61051bad21cfec5 · spec only, cobot-memory check

## 2026-11-23 — gate-f56-f60 T01: an option that says where a file lands is read in every form
Changed: cobot-rules LANDING_OPTIONS (cp/mv/ln/install -t and --target-directory as a folder; curl -o/--output and wget -O/--output-document as a file; curl --output-dir and wget -P/--directory-prefix as a folder), landing_option_values in every form (joined short, cluster end, =, separate, a long prefix of 3+ chars except curl), landing_option_hit in protected_file_touched; JOINED_PATH_RE reads the path joined to any short option (wget -o~/x, gcc -o~/x, curl -sD~/x); 7z/7za/7zz/7zr -o and cpio -D in FOLDER_OPTIONS; tests/test_gate_f56_f60.py story 1; spec Clarify answers (Q1 ask, Q2 yes).
Why: F-60 (HIGH): cp --target-directory=~/.claude cobot.rules got none where cp -t ~/.claude denied.
Proof: tests/test_gate_f56_f60.py exit 0; full suite with coverage 98.65 % with one failure, test_gcpMcpGate_globThatOnlyCouldNameAServerList_staysSilent[cat */README.md], which passes alone and in its file (GLOB_DEADLINE 0.25 s under suite load; seen once during F-55 too); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (no BLOCKER; MAJOR: joined paths on other options, 7zz/7zr), each a test row.
Open: the flaky glob-deadline test (pre-existing); cp -t ~ .bashrc and cp .bashrc ~ are T02; wget --execute= is T03.
Next: T02, landing words per copier.
verified: tree 89c6458f45d0dcdb3ce89d3a26ecdd6aacbe57eb · tests/test_gate_f56_f60.py, full suite (one flaky row), ruff, check-plugin

## 2026-11-23 — gate-f56-f60 T02: each source of a copy lands at <target>/<basename>
Changed: cobot-rules copy_parts (coreutils, gio and git mv through merge_parts; rsync, scp and docker/podman/kubectl cp with per-copier value-option tables; rclone and unknown options try every positional as the target), copy_verb finds the verb behind global options, landing_words (cp --parents and rsync -R keep the path, rsync's /./ marker read, host:path remote only for the remote copiers), landing_hit judges each landing as a relocating word, merges_into_an_anchor iterates copy_parts and reads rclone and --files-from as contents copies, merge_parts takes --target-directory prefixes, relocates covers scp, the container copiers and rclone; tests story 2.
Why: F-56 (HIGH): cp e/.claude.json ~/, scp h:/x/cobot.rules ~/.claude and the like reached no decision.
Proof: full suite with coverage exit 0, 98.59 % (fail-under 85); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (no BLOCKER; 6 MAJOR: rclone and container global options, rclone contents, git mv, x: as a local folder for cp, rsync /./), each a test row. The T02 tests were appended to the test file with a shell heredoc, against the Edit/Write-only rule.
Open: the flaky glob-deadline test (passed this run).
Next: T03, curl and wget landings.
verified: tree 507d2119db1bdfe186f2b9d442827621399820ff · full suite with coverage, ruff, check-plugin

## 2026-11-23 — gate-f56-f60 T03: a download is judged where it lands
Changed: cobot-rules download_landings (every output folder, the working directory when none, per Q2; <folder>/<url name> for curl -O and always for wget unless -O; a relative curl -o joined to --output-dir; unknown names for curl -J, URL globbing and -o '#1', wget -i -r -m -x --content-disposition --trust-server-names by prefix), url_names (wget decoded and ;params dropped, --default-page), download_hit (a sealed folder by its ~ name, a folder holding one as <folder>/*, which asks), config_reader (curl -K and --config; wget --config, and -e/--execute only for wgetrc commands that move output) asking in judge_bash; tests story 3; spec Goal row: a sealed folder reached through cd asks, as cd ~/.claude && tar -C . -xf did before.
Why: F-56 (HIGH): curl --output-dir ~ -O https://h/.claude.json and wget -P ~ reached no decision.
Proof: full suite with coverage exit 0, 98.28 % (fail-under 85); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (no BLOCKER; 5 MAJOR: --next folders, wget prefixes, wget --config, URL globbing, decoded names; MINOR: --default-page, the cwd tier), each a test row; friction kept silent: wget -e robots=off -r -P mirror.
Open: through the working directory a sealed folder asks, not denies (the customization-root check on a relative '.'; pre-existing).
Next: T04, extraction into the working directory.
verified: tree 56b60223a057494a34fe314fe9f1b1cfd8979021 · full suite with coverage, ruff, check-plugin

## 2026-11-23 — gate-f56-f60 T04: an extraction lands in the working directory
Changed: cobot-rules extracts (tar family, unzip, cpio, 7-Zip, long prefixes, 7z switches before the verb), extraction_unplaced (tar -P, cpio without --no-absolute-filenames, unzip -:, 7z -spf) asking in judge_bash, extraction_hit (a protected cwd by its ~ name, a cwd holding one as <cwd>/*, an untracked cd as unknown, all asking per Q1), folder_options reads cpio -p's destination and tar --one-top-level with no value; TAR_OPTIONS, UNZIP and UNZIPOPT join START_VARIABLES; tests story 4; FINDINGS F-61 widened (other unpackers, decompression in place).
Why: F-56 (HIGH): cd ~ && tar -xf e.tar and cd ~/.claude && unzip e.zip reached no decision.
Proof: full suite with coverage exit 0, 98.28 % (fail-under 85); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (no BLOCKER; 6 MAJOR: long prefixes, --one-top-level, option variables, 7-Zip forms, untracked cd, cpio -p), each a test row. A first run failed 18 tests: a new short_letters shadowed the kubectl helper of the same name; renamed option_letters.
Open: a cd into a missing folder leaves the cwd unknown, so an extraction after it asks; cpio -i asks anywhere without --no-absolute-filenames (accepted friction); payload cwd ~/.claude denies where cd ~/.claude asks (MINOR).
Next: T05, moved config dir and moved holders.
verified: tree 555a3d3a927f6ce0c13f3c6fcfbc059d1bb5cf0c · full suite with coverage, ruff, check-plugin

## 2026-11-23 — gate-f56-f60 T05: a moved config dir keeps its folder protection, and moving a folder that holds it is refused
Changed: cobot-rules protected_anchors walks a config dir moved outside HOME up to and including it; deleted_words marks a move's sources (moved_sources: mv, rename, git mv, gio move|mv|rename) as removed, so mv /home x and mv of the moved dir's parent deny like rm -r, and a glob source asks as rm's does; tests story 5; FINDINGS F-62 filed (tar --remove-files, zip -m, chmod/chown -R, mount --bind, bwrap, a symlinked CLAUDE_CONFIG_DIR).
Why: F-56 (HIGH): with CLAUDE_CONFIG_DIR outside HOME, cp, tar -C, unzip -d, ln -sfn, mv and rm on it reached no decision; mv /home x got none.
Proof: full suite with coverage exit 0, 98.28 % (fail-under 85); ruff 0.17.6 check and format clean; check-plugin ok; bypass review folded (no BLOCKER; MAJOR: a glob source in a move; the pre-existing ones became F-62); no friction found (mv a b, git mv, mv src/*.py lib/ silent).
Open: F-62; inside HOME, cd ~ && mv .claude z asks where mv ~/.claude y denies (pre-existing, MINOR).
Next: T06, agy rows, CHANGELOG, FINDINGS, docs.
verified: tree ff787bc156c9012aafbf2d99617d915116175647 · full suite with coverage, ruff, check-plugin

## 2026-11-23 — gate-f56-f60 T06: both runtimes and the docs
Changed: tests story 6 (agy run_command rows; a grant never covers a landing verdict); CHANGELOG Security entry; docs/configuration.md says where a file lands and what is not covered (F-59, F-61, F-62); FINDINGS F-56 and F-60 closed; spec tasks ticked, Converge written.
Why: ADR-0007 and the docs that listed 7z -o, cpio -D and extraction after a cd as not covered.
Proof: full suite with coverage exit 0, 98.28 %; ruff 0.17.6 check and format clean; markdownlint-cli2 0.24.2 clean; check-plugin ok; cobot-memory check exit 0 (brief at its 6000-char budget).
Open: the brief is at its budget; a compact or a shorter project line in MEMORY is the next housekeeping.
Next: /cobot:wrap gate-f56-f60.
verified: tree 90a7a619c638d5936e4e7fc8b470205433028e74 · full suite with coverage, ruff, markdownlint, check-plugin, cobot-memory check

## 2026-11-23 — wrap gate-f56-f60: reviews folded, F-56 and F-60 closed
Changed: protected_file_touched keeps an ask-tier landing (a glob, an unknown folder) as a fallback, so it never hides a literal owner-file deny in the same or a later segment; the landing checks return none in the rule-less customization-root pass; landing_hit asks past 16 candidate targets or 256 landing words; keeps_path per program (cp --parents only; rsync -R, --relative and -aR); curl's -# and -: before a joined path; wget -O is no remote name; every_target by index; tests for each.
Why: wrap security review (BLOCKER: an extraction anywhere in a command turned a literal owner-file deny into an ask, also under agy) and code review (3 MAJOR: 100 positionals took 14 s past the 10 s hook timeout, cp -R read as keeping the path, curl -#o~/x silent; 2 MINOR).
Proof: full suite with coverage exit 0, 98.27 % (fail-under 85); ruff 0.17.6 check and format clean; shellcheck clean; markdownlint-cli2 0.24.2 clean; claude plugin validate --strict passes twice; check-plugin ok; sync-agents in sync; cobot-deps check --fresh: no supported lockfile; 200 positionals judged in under 5 s.
Open: F-57, F-58, F-59 (accepted), F-61, F-62 and the older F-50, F-51; MINOR tiers: cd ~/.claude asks where cd /home/u/.claude denies, a cd into a missing folder asks before an extraction; cp -t $H/.claude with an inherited H stays silent (F-59 class); the brief is at its budget.
Next: the owner reviews security/gate-f56-f60 and decides push and PR.
verified: tree 44ef46d45f07037134dab963f997bf679224f049 · full suite with coverage, ruff, shellcheck, markdownlint, plugin validate x2, check-plugin, sync-agents

## 2026-11-23 — brief headroom: CONTEXT trimmed, open finding rows shortened
Changed: CONTEXT.md head compacted (one verified date for the command table, Stack and Environment shortened); F-59, F-61 and F-62 rows point at their specs instead of listing every shape.
Why: the brief sat at its 6000-char budget (owner: the nit).
Proof: cobot-memory check exit 0, brief 5280 chars before this entry.
Open: F-61 and F-62 become stories 7 and 8 of spec gate-f56-f60.
Next: measure F-61 and F-62 on 6022fa6, extend the spec.
verified: tree 44ef46d45f07037134dab963f997bf679224f049 · cobot-memory check, brief size

## 2026-11-23 — gate-f56-f60 T07: other downloaders, copiers and extractors (F-61)
Changed: spec revision 3, stories 7 and 8 for F-61 and F-62 (challenger SOUND WITH CHANGES, all folded; T07 and T08 merged). aria2c and gh release|run download landings, server names unplaced, aria2c -i and --conf-path ask; sftp, pax -rw (path kept) and ditto copiers (contents; -c a read, -x a folder); pax -r, jar x, ar x, unar, bsdunzip, bsdcpio, dpkg-deb -x|-X|-R extractions; tests/test_gate_f61_f62.py.
Why: F-61; owner: F-61 and F-62 on the same branch and PR.
Proof: full suite with coverage exit 0, 98.28 %; ruff clean; markdownlint clean; check-plugin ok. Bypass review folded: pax keeps operand paths, aria2c --index-out, ar key words, pax -rw -s asks.
Open: pre-existing tier, a cd into an owner folder makes a download or extraction ask, not deny (also curl -O and tar xf); dpkg --root is a residual.
Next: T08 in-place decompression.
verified: tree f7ca68c759a305e523b1fdff23082218d9b4cbef · full suite with coverage, ruff, markdownlint, check-plugin

## 2026-11-23 — gate-f56-f60 T08: in-place decompression (F-61)
Changed: decompress_landings (each input without its suffix or -S, beside it or in zstd's --output-dir-flat|-mirror or lzop's -p), judged by download_hit; -N and -r unplaced; zstd --filelist and xz --files ask; -c, -t, -l and -o files add none; a names-a-protected-file check on relative landings after an unfollowed cd; landing words capped.
Why: F-61, gunzip ~/.claude/cobot.rules.gz and kin got none.
Proof: full suite with coverage, 98.30 %, one failure: the known flaky glob-deadline test under load, which passes alone; ruff clean. Bypass review folded: cluster scan per program (-dT0, -dS.x), -- ends options, xz --files, lz4 --multiple, lbzip2, lrzip, lzop -x and -p, getopt prefixes, the cap.
Open: pre-existing, a followed cd into an owner folder asks where the literal path denies (touch too); 5000 plain words take about 6 s in the word loop (cat too).
Next: T09 removal, cover, link and lock verbs.
verified: tree 970927fb5011b00c138b661e0571bfa4348307d3 · full suite with coverage, ruff

## 2026-11-23 — gate-f56-f60 T09: removing, covering, linking and locking the config dir (F-62)
Changed: taken_away (tar --remove-files, zip -m, 7z -sdel, a recursive compressor, rclone removal verbs) in deleted_words; ln, cp -s and cp -l sources as moved holders; covered_folders (mount, mount.*, FUSE mounters, rclone mount|nfsmount) as folder options; lock_hit asks for chmod, chown, chgrp, setfacl, chattr on a never-row folder or its holder, bwrap destinations (a self-bind excepted) and zip -m -@.
Why: F-62.
Proof: full suite with coverage exit 0, 98.32 %; ruff clean. Bypass review folded: rclone verbs behind valued flags, cp -l and long prefixes, bwrap no-value flags, chmod -w modes, globs, -m@, chmod 700 ~/.ssh silent (never rows only), more mounters, a lock cap.
Open: cd ~ then a relative operand asks where the literal denies (rm -rf .claude too).
Next: T10 the config dir's real path.
verified: tree e47c2b8ec324bc4aa4b177009f98e5251c31c589 · full suite with coverage, ruff
