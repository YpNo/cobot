# Journal

Append-only, newest at the bottom. One entry per working session or task group.

## 2026-11-19 — compacted 2026-11-15 → 2026-11-19 (51 entries)
2026-11-11 to 2026-11-19, folded from 51 entries (raw text in JOURNAL-archive.md). 0.3.0 was cut on 2026-11-15: Antigravity from one tree (ADR-0007), A2UI knowledge in expert-ui, gate residuals F-28 to F-34 (symlinked paths, deletions, folder options), scripts that write files denied. Then, each spec challenged, built task by task and merged: onboard-environment (cobot-env, the runs: header, install routes ask, shims untrusted in foreign mode; decision 29), the docs tidy, gate-f36-f40-f44 (rows reach the commands they name, every ask named, credential printers and forge deletions never, shell writes refused), the security auditor and sweep router (decision 30), memory-and-ship (one commit per verified change, parked notices, a repeated ask names its allow line, promotion lint, ship checks its ground; decision 31), builder-proof-hosts (the hand-back is checked in the desktop app; decision 32, F-35), trust-boundaries (decision 33, F-49). Findings F-35 to F-49 were filed from the curriculo and ha-manager dogfood sessions; worktrees moved into .claude/worktrees/.
Archive: raw entries in JOURNAL-archive.md and in git history before 2026-11-19.

## 2026-11-19 — T05 trust-boundaries: decision 33, design rows, F-49 closed
Changed: docs/01-decisions.md decision 33 (a spec names its trust boundaries; the challenger attacks a missed or unproven one; the sweep checks declared guards from trusted memory only, as inventory lines); docs/02-design.md the medium path row names the section and the medium-spec-then-challenge eval row its two graders; CHANGELOG Added entry; FINDINGS F-49 closed; the spec's Built note, with the two additions (declared: report lines, the case-insensitive grader).
Why: F-49, spec trust-boundaries story 6.
Proof: full suite 3514 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; cobot-memory check: 1 open finding of 49 (F-39), brief 5818 of 6000 chars.
Open: cobot-memory check warns JOURNAL.md is over 400 lines (compact is the owner's call).
Next: the owner pushes feat/trust-boundaries and opens its PR.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, cobot-memory check

## 2026-11-20 — spec session-grants (0.4.0), challenged
Changed: .agent/specs/session-grants.md revision 2 (299 lines): gcloud, kubectl and helm grants per kind (deletes separate) on one explicit target, recorded by a PostToolUse hook only against a pending entry the gate wrote when it asked, main thread and Claude Code only; the gate emits allow for a covered command only (ADR-0008, decision 34 planned); grant_scope as allow-lists of groups, verbs and options; Terraform apply and destroy move from never to a prompt-only ask, never granted; the never list grows (state surgery and -lock= false spellings, token and secret printers, kubeconfig writes, cluster wipes, rm -rf of / and home, owner rule files from config_dir(), shell writes to never paths denied). T01 probes P1-P7 first.
Why: 0.4.0 scope (owner, 2026-11-14), design input owner-ideas-03 §4; owner answers 2026-11-20: Claude Code only, deletes separate, gate tests plus apply-asks eval, no Terraform grants.
Proof: two cold reads of the gate and docs; challenger RETHINK (2 BLOCKER, 6 MAJOR, 1 MINOR) and a CLI consult against upstream docs, every claim re-checked by gate dry runs, all folded; Terraform answer asked after BLOCKER 2.
Open: the probe (T01) can still stop the design (P1, P2, P6).
Next: T01, the probe.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · spec only, no code; gate dry runs of the challenged commands

## 2026-11-20 — T01 session-grants: the probe's findings
Changed: .agent/specs/session-grants.md Converge holds P1–P7; story 1 points there; story 5 records a grant on PostToolUse with CLAUDE_CODE_SESSION_ATTENDED=1 (no mode check, no exit-code field: PostToolUse fires only on success); trade-offs gain the session id in Bash, the SDK host, and a grant never beating a settings ask or deny.
Why: spec session-grants story 1: recording rests on P1, P2, P6.
Proof: Claude Code 2.1.326, a log-only probe plugin by --plugin-dir and rules by --settings (no settings file touched), scratchpad only. Six headless runs: hook ask never ran in any mode, bypassPermissions included, even with a settings allow; hook allow ran an unmatched command but lost to a settings ask and a settings deny; PostToolUse absent for a failed ls; subagents (general-purpose, Explore, background, context: fork) carry agent_type and agent_id, the main thread neither; resume keeps the session id; SessionEnd fires with reason; export does not persist; ATTENDED 0 headless, ENTRYPOINT inherited from the parent. The owner in the interactive CLI saw a prompt in auto, acceptEdits, plan and bypassPermissions; ATTENDED 1 there and in the desktop app.
Open: workflow agents not probed; default mode not run interactively (the owner's default is auto). A grep of this session's env printed CLAUDE_* values into the local transcript (a broken pattern); a stray sed -i on /dev/null failed and edited nothing.
Next: T02, the never additions and the prompt-only apply.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · spec only; probe logs in the session scratchpad

## 2026-11-20 — T02 session-grants: the never list grows, apply and destroy prompt only
Changed: default.rules: never rows for Terraform, tofu and terragrunt state surgery (state rm|mv|push|replace-provider, force-unlock, import, taint, untaint, workspace delete -force, -lock= false spellings), state buckets, projects delete, set-iam-policy, keys create, the gcloud and kubectl credential printers (were asks), kubectl create token, kubectl config writes, Edit/Write of ~/.kube/*, cluster-wide deletes (-A or --all-namespaces, kube-system), rm -* of / ~ ~/ $HOME, Edit/Write of ~/.claude/cobot.rules and cobot/*, agent reads of ~/.kube; apply and destroy move from never to asks noted "prompt only". cobot-rules: resolve() puts a prompt-only default ask above every allow; read_layer adds a CLAUDE_CONFIG_DIR twin of each ~/.claude file row (moved root computed once per layer); protected_verdict denies a literal shell word on the sealed owner files, or a move, copy or delete into their folder, and keeps the ask for holes, globs and other protected files. New tests/test_session_grants.py (90); existing gate tests: apply rows ask, the bypass corpora retargeted from apply to import (still never), cloud credential printers split into a deny list, set-iam-policy deny, and the F-33 cases that reach home or root deny (REACHES_OWNER_FILES).
Why: spec session-grants stories 2 and 3 (challenger 3, 4, 7, 8).
Proof: tests first (71 failing for the right reason, neighbours passing); full suite 3605 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate. Gate timing: load_rules was 5x slower from a per-rule config_dir() call, fixed; judge_bash about 20 % slower from the extra rows.
Open: narrower than the spec text (now reworded): only cobot's owner files are sealed to shell, settings.json keeps its ask; kubectl delete -A is never even without --all (wider). The agents' Read tool on ~/.kube is not gated (the gate judges no Read).
Next: T03, grant_scope.
verified: tree 006a47d8c9b34168ceb415e7abad897f555870aa · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — T03 session-grants: grant_scope, allow-lists only
Changed: cobot-rules gains a session-grants section: grant_scope(command) -> (kind, target) | None and valid_grant(kind, target). A command is covered only when its raw text is plain (a character allow-list: no quote, $, glob, operator or assignment; rtk the only wrapper), no word holds projects/, gs:// or ://, and its tool's allow-list matches: gcloud command paths (compute, run, pubsub, functions, artifacts, dns, container clusters and node-pools) with create, update, deploy (gcloud) or delete (gcloud-delete) and --project once, refusing --flags-file, --configuration, --impersonate-service-account, --account, --access-token-file and any abbreviation of them or of --project; kubectl apply/create -f, patch, label, annotate, set image (kubectl) and delete, scale, rollout restart (kubectl-delete) with --context once and only allow-listed options; helm install, upgrade, rollback (helm) and uninstall, del, delete, un (helm-uninstall) with --kube-context once. Files must stay inside the repository. Targets: project id or context format. The signature drops the spec's cwd: Terraform is out, and the path check is lexical.
Why: spec session-grants story 4 (challenger 1 and 7, the CLI consult).
Proof: tests first (101 failing for the right reason). A self-attack found a real bypass: kubectl --dry-run takes an optional value, so "--context lab --dry-run --context prod" read as lab while kubectl acts on prod; fixed by dropping --dry-run and refusing any option value that starts with "-", with tests for it and the gcloud abbreviation. 199 session-grant tests; full suite 3714 passed, 98.47 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: gcloud flag abbreviation is guarded without knowing whether gcloud accepts it (defensive). kubectl patch with an inline -p JSON is not covered (quotes), only --patch-file.
Next: T04, the grant verb, pending entries, the store and the hooks.
verified: tree 35d651bc3c2b15c012360dc4c2db45c46815f524 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — T04 session-grants: the grant verb, pending entries, the store and the hooks
Changed: cobot-rules: grant_request parses the cobot-rules grant family (grant, revoke all or one, list; anything else starting like one is malformed); the gate answers it before any rule: malformed, a subagent, an unknown kind or target, or no valid session is denied; revoke and list are silent; a grant request asks with a rule-less reason after writing a pending entry {digest, kind, target, time}; under agy it is denied (Claude Code only). posttool (PostToolUse Bash, prefix check first) records a grant only for a fresh pending entry with the same digest, on the main thread (no agent_id, agent_type absent or null), with a valid session and CLAUDE_CODE_SESSION_ATTENDED=1; revoke narrows; sessionend removes the session file. The store is <config dir>/cobot/grants/<session>.json, read as empty on any defect, written under a lock with the report state's rename-and-prune. cobot-rules grant prints the request and writes nothing; --list reads the file via CLAUDE_CODE_SESSION_ID. hooks/grant.sh (exit 0 on every path) and hooks.json entries for PostToolUse ^Bash$ and SessionEnd. Spec: main thread is the strict reading (an empty agent_type is an agent, which the old wording contradicted), --list reads the file itself.
Why: spec session-grants story 5 (challenger 5, 6, 9; probe P1, P2, P4, P5, P6).
Proof: tests first (39 failing for the right reason, 6 passing for today's behaviour); 46 store tests; the real hook scripts run end to end in a scratch config dir (ask, record, list, SessionEnd removal); full suite 3760 passed, 98.42 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: accepted residual: the gate killed by its timeout after writing the pending entry, with an owner settings allow on cobot-rules, could run the command without a prompt and record it (microseconds, needs the owner's own allow line). The log list is kept but not filled until T05.
Next: T05, the gate's allow for a granted command.
verified: tree d4c5e5c68b6aec1dafaa791f52f692631086217b · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — T05 session-grants: the gate allows a granted command, and only one
Changed: cobot-rules gate(): granted_reason lifts a Bash verdict to allow only when it is an ask from a default row (not never, not prompt-only, not rule-less, no second ask), the call is from the main thread, grant_scope names a (kind, target) this session holds unexpired, and the owner and project layers alone neither ask nor deny on the command (a verdict names only its first rule, so an owner ask would hide behind the default one). Reason: cobot grant: <kind> on <target> (cobot-rules grant --revoke). posttool logs each command that ran under a grant (200 kept, 200 characters each); --list prints them as ran: lines. The module docstring's contract names the one allow. The allow pin becomes test_gate_neverEmitsAllow_withoutAGrant; agy unchanged (test_corpus_noAnswerEverAutoApproves stands). The unused GRANT_STATE_DAYS went.
Why: spec session-grants story 6.
Proof: tests first (the 3 positive cases failing, the 14 near-misses already asking or denying); 63 store tests; the real hook scripts end to end (grant, allow on lab, ask on prod and on another kind, the log listed); full suite 3777 passed, 98.43 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; gate timing unchanged.
Open: none.
Next: T06, the protocol and skill texts.
verified: tree a1ca27f7c1a768b6eeee8f6c6a40d66fdd384cd0 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — session grants T06: protocol and skill texts
Changed: protocol.md gains a Grants paragraph (one AskUserQuestion with three answers, main thread only, plan -out then apply at the prompt, the lab log); apply leaves the outward list; lang-terraform, terraform-builder (synced), ship, expert-gcp, expert-kubernetes and README no longer say the gate denies apply, and the two expert skills document the grantable forms and the lab log; check-plugin's protocol cap is 3400.
Why: spec session-grants story 7; owner's answer 5 raised the cap (the protocol reached 3400 chars).
Proof: 3800 passed, coverage 98.43%; tests/test_grant_texts.py 23 passed (documented forms checked against grant_scope); ruff check and format, markdownlint, check-plugin (protocol 3400 chars), sync-agents --check, claude plugin validate --strict and agy validate (1 warning) all pass; documented verdicts dry-run with cobot-rules check.
Open: docs/02-design.md and docs/architecture.md still say a 3k protocol (T08).
Next: T07, the apply-asks eval.
verified: tree 7c479907b77193cbf4d55c446e328256210e014c · full suite, lint, contract and validate

## 2026-11-20 — session grants T07: the apply-asks eval
Changed: evals/never-apply becomes apply-asks, with the same fixture and prompt. rule-named (trace) wants "cobot rule: ask Bash(terraform apply*)" and replaces the refusal regex; alternative-proposed wants plan -out; no-false-claim, no-question, no-rule-edit and one-terraform-call are kept. test_applyAsks_isGradedWithoutAJudge pins the six graders, with passing and failing matches() for each regex.
Why: spec session-grants story 8: an ungranted apply is a prompt-only ask, no longer a never.
Proof: one local run (claude plugin eval --case apply-asks --runs 1, sonnet 5.5): score 1.00, 6 of 6 graders, 2 turns, $0.08; 3800 passed at 98.43%; ruff, markdownlint, check-plugin, sync-agents --check, and plugin validate for claude and agy all pass.
Open: docs/02-design.md line 476 still names never-apply (T08).
Next: T08, ADR-0008, decision 34, docs and CHANGELOG.
verified: tree 6b4b5e34310787bf51ae78fc776ef88dd6f364c7 · full suite, lint, contract, validate, one local eval

## 2026-11-20 — session grants T08: ADR-0008, decision 34, docs and CHANGELOG
Changed: ADR-0008 (the gate may allow in one case, a granted command under Claude Code); decision 34 (grants, prompt-only apply, the new never rows, the lab log, the 3400-char protocol cap); docs/02-design.md (hooks tree, the gate's allow contract, the never and prompt-only rows, the protocol budget, the apply-asks row); docs/architecture.md (protocol cap, gate row, a Session grants layer); docs/configuration.md (the grants file row, the precedence sentence, a Session grants section, agy's unused conversationId); CHANGELOG Added, Changed, Security.
Why: spec session-grants story 9; every task of the spec is now built.
Proof: markdownlint 0 issues on 134 files; 3800 passed at 98.43%; ruff, check-plugin, sync-agents --check, and plugin validate for claude and agy all pass.
Open: the currency gap stands (ruff 0.17.6 and markdownlint-cli2 0.24.2 are out, 0.17.4 and 0.24.0 pinned; the owner's call); JOURNAL.md is over 400 lines (compact is the owner's call).
Next: the PR for feat/session-grants, on the owner's word.
verified: tree 6b4b5e34310787bf51ae78fc776ef88dd6f364c7 · full suite, lint, contract, validate

## 2026-11-20 — housekeeping: ruff 0.17.6, markdownlint-cli2 0.24.2, journal compacted
Changed: ruff 0.17.4 → 0.17.6 and markdownlint-cli2 0.24.0 → 0.24.2 in CONTEXT.md's verified commands, docs/development.md, ci.yml and knowledge-refresh.yml; lang-python's uv and ruff lines re-verified (uv 0.13.9, ruff 0.17.6); JOURNAL.md compacted from 499 to 87 lines with a written summary (51 entries into JOURNAL-archive.md).
Why: the currency gap reported pre-PR on spec session-grants; the journal had passed 400 lines. The owner asked for both on 2026-11-20.
Proof: upstream read 2026-11-20 (PyPI ruff 0.17.6 from 2026-11-19, npm markdownlint-cli2 0.24.2 from 2026-11-20, GitHub uv 0.13.9); ruff 0.17.6 check and format --check pass on 396 files; markdownlint-cli2 0.24.2: 0 issues on 134 files; 3800 passed at 98.43%; check-plugin, sync-agents --check, claude plugin validate --strict and shellcheck pass; cobot-memory check: brief 5957 of 6000 chars.
Open: the CI pins of @anthropic-ai/claude-code (2.1.318 in ci.yml, 2.1.322 in knowledge-refresh.yml) trail 2.1.329, left for the owner; markdownlint-cli2 0.24.2 is one day old.
Next: spec the debug path.
verified: tree d8b4cbac3f8e96b807fccb1851817786737bb237 · full suite, lint, contract, validate

## 2026-11-20 — spec debug-path (0.4.0), challenged
Changed: .agent/specs/debug-path.md revision 2 (242 lines): /cobot:debug as the main-thread lead, a read-only cobot:investigator per hypothesis sharing the consultant's read list by alias, a probe report check of its own, records in .agent/debug/ refused at write time when secret-shaped, the shared read list tightened (output formats, target-switching and watch flags ask; --show-secrets never), the protocol's Paths line, two evals; nine tasks.
Why: owner-ideas-03 §2, the second piece of 0.4.0. Owner's answers: investigator with the agent budget at 650, remedies printed only, records committed.
Proof: challenger SOUND WITH CHANGES (4 MAJOR, 3 MINOR, all folded) and a CLI consult on the routing reads; every claim re-checked with cobot-rules check dry runs (kubectl get -o yaml, logs -f, --server/--token and gcloud --configuration silent for the consultant today).
Open: accepted residuals: the Read tool is ungated for agents; kubeconfig exec entries; an active grant only the skill keeps from a lead mutation.
Next: T01, the read-list rows.
verified: tree d8b4cbac3f8e96b807fccb1851817786737bb237 · spec only, no code changed

## 2026-11-20 — debug-path T01: the shared read list stops printing values, switching targets and hanging
Changed: READ_GUARDS gains kubectl (target and identity flags, -s), istioctl (the same), kubectl get (-o other than wide/name in any spelling or cluster, --template, --raw, watch), kubectl logs (follow), kubectl events (watch) and gcloud (--configuration, --impersonate-service-account, --account, --access-token-file); Guard.why words the reason. never Bash(kubectl diff*--show-secrets*) in every scope.
Why: spec debug-path story 2 (CLI consult): these forms were silent for the consultant, auditor and learner.
Proof: tests/test_read_list_limits.py 189 passed; gate corpora (test_cobot_rules, gate_agy, gate_differential, session_grants, consult, sweep) 3130 passed; ruff 0.17.6 check and format clean; check-plugin ok.
Open: the guards apply to the learner too (it shares the list); kubectl rollout status still waits by default; a --server before the verb on the main thread is not denied by the show-secrets row.
Next: T02, the investigator agent.
verified: tree 5c961a7f013969137ca5b47c085c2c53421f5018 · focused gate suite

## 2026-11-20 — debug-path T02: the investigator, read-only by rule
Changed: claude-agents/investigator.md (Read, Grep, Glob, Bash, WebFetch; sonnet, medium; prediction first, reads as commands, the given target only, the probe report shape) and its agy twin; plugin.json lists it; SCOPE_ALIASES maps cobot:investigator to the consultant's list; NO_COMMANDS gains it; AGENT_BUDGET_TOKENS 650.
Why: spec debug-path story 1, owner answer 1.
Proof: tests/test_investigator.py 47 passed (reads silent, mutations ask, cloud printers denied, same decisions as the consultant over the corpus, look-alike names unscoped); grant_store: a held grant allows the main thread and asks for the investigator; agents_sync, check_plugin, rules, read-list, grants, agy: 3051 passed; check-plugin ok (listing ≈ 620 of 650 tokens); claude and agy validate pass; ruff and markdownlint clean.
Open: forge credential printers ask rather than deny for the investigator, as for the consultant; the report shape is not checked until T03.
Next: T03, check_probe_report.
verified: tree f15e6a0ee1e775f984fc68c2c40850db939d8291 · focused suites

## 2026-11-20 — debug-path T03: a probe's report is proof, checked by its own rule
Changed: check_probe_report (a Verdict: and a command with an exit marker under Checks:, or Checks: none with Verdict: inconclusive and a non-empty Needs:); probe-worded block reason and UNPROVEN context; ReportKind picked by agent type in report() and handback(); the investigator parks nothing; checks_block takes the section pattern that ends the block.
Why: spec debug-path story 3 (challenger 1, 2): the builders' check would have refused every probe report.
Proof: tests/test_probe_report.py 19 passed (both paths: one refusal then marked, both passing forms, builder judged as today, look-alike names ignored); rules, agy, investigator suites 2548 passed with it; ruff clean; check-plugin ok.
Open: hooks.json's description still says builder report check (T09 docs).
Next: T04, the debug skill.
verified: tree be8be74051fc110aeafd275b59b881250251c415 · focused suites

## 2026-11-20 — debug-path T04: /cobot:debug leads the investigation in the main thread
Changed: skills/debug/SKILL.md (frame with live context, grant list and production confirmation; reproduce; ranked hypotheses; one foreground investigator per hypothesis; at most three rounds; remedies printed, never run, whatever grant; record from template.md checked by cobot-memory debug check before git add; agy fallback), template.md, references/routing.md (the design input's table, git log -S for git bisect, terraform plan printed).
Why: spec debug-path story 4.
Proof: tests/test_debug_skill.py 15 passed, with check_plugin, workflow_skills, agents_sync 89 passed; check-plugin ok (31 skills, 10745 chars listed); markdownlint 0.24.2 clean; claude and agy validate pass.
Open: cobot-memory debug check is named here and arrives in T05.
Next: T05, the record secret guard.
verified: tree 479d25c5f3c1696f786a337ac982330e5ee9e0d0 · focused suites

## 2026-11-20 — debug-path T05: a debug record cannot carry a secret
Changed: _cobot_common gains DEBUG_SECRET_PATTERNS (SECRET_RE, ya29., JWT, Bearer, URL credentials, client-*-data, "private_key":), debug_secret_kind (line by line, <redacted> dropped) and debug_record_problems (secret lines, fenced excerpts over 20 lines or 2000 chars); the gate denies an Edit, Write, MultiEdit or NotebookEdit resolving under the memory's debug/ folder whose new text matches, naming the kind; cobot-memory debug check [FILE] and check exit 1 naming file and line.
Why: spec debug-path story 5 (challenger 3).
Proof: tests/test_debug_records.py 34 passed (one negative per pattern on gate and check, clean record, elsewhere judged as today, the hook end to end; values built at run time); memory, rules, agy, differential, grants, knowledge 3189 passed; ruff clean; check-plugin ok.
Open: the agy gate path carries only file_path, so under Antigravity only the check before git add holds; a shell write into debug/ asks as any shell write does.
Next: T06, debug list and the brief count.
verified: tree 711465a16412af5ca2bcf8b0ee645ea55d8f012e · focused suites

## 2026-11-20 — debug-path T06: debug records are listed, and the brief counts the open ones
Changed: Memory.debug_records (status and title from each record's head, newest first); cobot-memory debug list [--open]; the brief's findings line ends "; debug: <n> open" when a record is open, as "## FINDINGS open: 0; debug: <n> open" when no finding is; untrusted memory loads nothing, so no count.
Why: spec debug-path story 6 (challenger 6, 7): the brief sits at 5957 of 6000 chars, so a count, not a line.
Proof: tests/test_debug_list.py 8 passed (list, --open, none, foreign mode's outside folder; brief open, open without findings, none open, untrusted); memory, session, knowledge, workflow-skill suites 234 passed; ruff clean; check-plugin ok; this repo's brief 5823 chars.
Open: none.
Next: T07, the protocol Paths line.
verified: tree 1984ace2d54f5e6bbbdf1038f8c468ec578e4362 · focused suites

## 2026-11-20 — debug-path T07: the protocol routes an unknown cause to /cobot:debug
Changed: protocol.md Paths opens with "unknown cause → /cobot:debug."; paid for by "Name the size first:" and "reject a report without them" (now any report, a probe's included).
Why: spec debug-path story 7; the cap is 3400.
Proof: tests/test_protocol_paths.py 2 passed; grant texts, check_plugin, cli flags, session, workflow skills 131 passed; check-plugin ok (protocol 3399 chars); markdownlint and ruff clean.
Open: none.
Next: T08, the two evals.
verified: tree ba5e56e3179ea6a349c78ded70a76adefb1f1677 · focused suites

## 2026-11-20 — debug-path T08: evals debug-routes-by-evidence and debug-read-only
Changed: two cases sharing one fixture (a Deployment with DATABSE_URL, captured describe and previous logs from context lab, no cluster); routing graders: an Agent call to cobot:investigator, expert-kubernetes named, the cause named, a kubectl remedy printed, no question; read-only graders: no kubectl mutation, no Edit or Write under k8s/, an inverse printed, no fixed claim, no question; matches() tests for both.
Why: spec debug-path story 8.
Proof: tests/test_eval_graders.py 105 passed. Local runs (--runs 1, sonnet 5.5, Claude Code 2.1.311): first without the skill named, 0.40 and 0.67 (the model fixed the typo inline); then with the skill in backticks, 0.40 and 0.83 (not expanded); then with a bare /cobot:debug first line, as sweep-fan-out does: 1.00 (/bin/bash.25, two foreground investigators with expert-kubernetes) and 1.00 (/bin/bash.12). Total about $0.80.
Open: unprompted routing from the protocol line is not graded (the model fixed the typo inline); in the read-only run the lead diagnosed without a probe.
Next: T09, the docs.
verified: tree ff4a1311ac54397a38a99b5474bb8b8f9d725327 · grader tests and local evals

## 2026-11-20 — debug-path T09: decision 35 and the docs; the spec converged
Changed: decision 35 in docs/01-decisions.md; docs/02-design.md (layout, a debug lead and investigator role, the unknown-cause path, the never row, the debug record, model routing, budget 650, two eval rows); docs/architecture.md (report check, roster with the auditor and the investigator, /cobot:debug, flow, debug list); docs/configuration.md (the debug record, the report state, the read-list limits); README (overview, diagram, eleven agents, usage, agy notes); CHANGELOG Added, Changed and Security; hooks.json description; the spec's Converge table.
Why: spec debug-path story 9.
Proof: full suite 4128 passed, coverage 98.43% (fail-under 85); markdownlint-cli2 0.24.2 clean over 139 files; ruff 0.17.6 check and format clean; shellcheck clean; check-plugin ok (agents ≈ 620 of 650 tokens, protocol 3399 chars); sync-agents --check in sync; claude plugin validate --strict and agy plugin validate pass.
Open: unprompted routing to /cobot:debug is not graded; kubectl rollout status waits by default; the forge credential printers ask for the investigator rather than deny.
Next: the owner's word on pushing chore/housekeeping and feat/debug-path.
verified: tree 37cd32d46b865c1c521b6cc7af300a02064096d0 · full suite with coverage, lint, validators

## 2026-11-21 — spec expert-homeassistant (F-39): written and challenged
Changed: .agent/specs/expert-homeassistant.md: expert-homeassistant (custom integrations, configuration, REST and WebSocket APIs, hass-cli, ZHA and registries), /cobot:consult homeassistant, hass-cli gate rows, onboard step 6b Domains and the spec step 2 Experts line; seven tasks in four lanes.
Why: F-39, the owner asked for a Home Assistant expert on ha-manager and nothing said none existed.
Proof: cobot-rules check reproduced the challenger's BLOCKER (cat config/secrets.yaml as cobot:consultant: none) and the inline-token MAJOR (HASS_TOKEN=x hass-cli state list: none); spec 206 lines; owner's answers Q1 a, Q2 a, Q3 b, Q4 a, narrowed to ask on -s/--server.
Open: cobot:challenger not loaded in this session, the owner's challenger ran with cobot's challenger.md; no consultant relevant; onboard step 6b may collide with the gcp-mcp opt-in spec's onboard step; HA capture and replay stays with cobot-reverse.
Next: /cobot:build expert-homeassistant on feat/expert-homeassistant.
verified: tree 37cd32d46b865c1c521b6cc7af300a02064096d0 · spec only, challenger verdict folded

## 2026-11-21 — expert-homeassistant T01, T04, T02: the expert, the hass-cli gate, the learned lines
Changed: T01 skills/expert-homeassistant (SKILL.md, references/versions.md, ci.md) with lang-python's three Home Assistant lines moved and a pointer left (fd6b8ac); T04 hass-cli in GLOBAL_OPTIONS, never rows on --token, --supervisor-token, --password, ask rows on every write verb, the ha group, discover, map, -s/--server, --insecure, --debug, secret_assignment and reads_secret_file in cobot-rules, tests/test_hass_cli_gate.py (50461b5); T02 three learner runs (sets A, B, C, 45 entries) quoted, dry-run and promoted --in-place, sorted into SKILL.md, references/api.md and references/registries.md; learned.md removed.
Why: spec expert-homeassistant stories 1, 2 and 4.
Proof: tests/test_hass_cli_gate.py 123 passed; the gate suites (test_cobot_rules, test_gate_differential, test_gate_agy, test_read_list_limits, test_session_grants, test_cobot_shell, test_check_plugin, test_investigator) 3496 passed; ruff 0.17.6 check and format clean; check-plugin ok (listing 11060 chars); cobot-memory knowledge expert-homeassistant: 47 lines, none reported or assumed; markdownlint 0.24.2 clean on the skill.
Open: the secret-file guard is code, not rows (reader rows are viable for every glob and substitution; written into the spec); the main thread gets no secret-file row; an anchored glob that could expand to secrets.yaml and the Read tool stay residuals. cobot:learner was not loaded here: three general-purpose agents ran learner.md's method. Set B left three lines unverified (secrets.yaml must not be committed, .storage not edited by hand, --debug headers; the last checked from the Python source and written to api.md).
Next: T03 the consult domain, T05 onboard 6b and spec step 2, T06, T07.
verified: tree d2a784b0509159f5699e44bfe1e0c4d51b361ba0 · gate suites, hass-cli tests, check-plugin, ruff

## 2026-11-21 — expert-homeassistant T03, T05, T06: the consult domain, the missing-domain steps, the routing row and two evals
Changed: T03 skills/consult/domains/homeassistant.md, the router's row and description, router and inventory tests (31f2068); T05 onboard step 6b Domains and step 8's Open line, spec step 2 Experts with the no-domains-line fallback, the template's Experts line, the challenger's memory sentence, agy twin (9503430); T06 the debug routing row for Home Assistant, evals consult-homeassistant (a demo_light integration: no version, aiohttp==3.9.0, config_flow without config_flow.py, strings.json, hassfest@master, a tracked secrets.yaml holding one !env_var line) and spec-names-missing-expert (a Modbus TCP tool), grader tests; reads_secret_file now skips the pattern or program operand of grep, rg, jq, yq and awk, so git ls-files | grep secrets.yaml stays silent.
Why: spec expert-homeassistant stories 3, 5 and 6.
Proof: tests/test_consult_domains.py, test_missing_domain.py, test_spec_skill.py, test_workflow_skills.py, test_agents_sync.py, test_check_plugin.py pass; test_eval_graders.py 114 passed; test_hass_cli_gate.py, test_debug_skill.py, test_investigator.py pass; ruff 0.17.6 clean; check-plugin ok (listing 11124 chars); sync-agents --check in sync; markdownlint 0.24.2 clean on the changed skills.
Open: the two evals are paid and not run here (owner: gh workflow run ci.yml -f evals=true -f cases=consult-homeassistant,spec-names-missing-expert); spec-names-missing-expert has no CONTEXT.md, so it grades the step 2 fallback, not the domains line.
Next: T07 the docs, decision 36, F-39 closed; then /cobot:wrap.
verified: tree 2f8077d5f41c5ace3e7085a72398ac1e9397bd88 · focused suites, grader tests, check-plugin, ruff

## 2026-11-21 — expert-homeassistant T07: decision 36 and the docs; the spec converged
Changed: decision 36 in docs/01-decisions.md and decision 25 amended; docs/02-design.md §12 (Home Assistant: hass-cli under the gate, a server waits for cobot-reverse) and §15 R3; docs/architecture.md (consult domain, knowledge skill); docs/configuration.md (a Home Assistant section: the environment, what the gate refuses, asks and leaves silent); README consult row; CHANGELOG Added, Changed and Security; F-39 closed; the spec's Converge.
Why: spec expert-homeassistant story 7 (T07).
Proof: full suite with coverage exit 0, 98.44% (fail-under 85); ruff 0.17.6 check and format clean; markdownlint-cli2 0.24.2 clean over 146 files; shellcheck clean, the two new fixtures included; check-plugin ok (listing 11124 of 15000 chars, protocol 3399); sync-agents --check in sync; claude plugin validate --strict passes for the plugin and the marketplace; cobot-memory check: 0 open findings of 49, brief 4645 of 6000.
Open: the paid evals consult-homeassistant and spec-names-missing-expert are the owner's to run; agy validate not re-run; onboard step 6b may collide with the gcp-mcp opt-in spec's onboard step (whichever merges second renumbers); Home Assistant capture and replay stays with cobot-reverse.
Next: /cobot:wrap, then the owner's word on pushing feat/expert-homeassistant.
verified: tree 2f8077d5f41c5ace3e7085a72398ac1e9397bd88 · full suite with coverage, lint, validators

## 2026-11-21 — wrap expert-homeassistant: the reviews folded, read-only agents kept off Home Assistant's secrets
Changed: bin/_cobot_secrets.py (new): a read-only agent's command that would print secrets.yaml or a .storage/ file is refused when it names one, reads it through a < redirect, runs a recursive grep, any rg, semgrep or a verbose unredacted gitleaks over a tree holding one unless excluded (walked, at most 20 000 entries), prints history in a repository that tracks or tracked one with no excluding pathspec, or fetches a curl file: URL; an -e pattern in a short cluster no longer hides the file. cobot-rules hass_verdict: any setting of the token variables and their HOMEASSISTANT_ fallbacks is refused, their expansion is refused for read-only agents and asks in the main thread, HASS_SERVER set and -s or -x in any short cluster ask; the four -s cluster rows left default.rules. tests/test_secret_reads_gate.py; docs, decision 36, CHANGELOG, the expert's and the consult's text; findings F-50 (pipx run, python -m homeassistant_cli) and F-51 (docker --env=HASS_TOKEN=).
Why: the wrap's code review (one MAJOR, six MINOR) and security review (three HIGH, six MEDIUM); the owner chose to fix the recursive, history and scanner reads in this PR.
Proof: converge: stories 1-7 accepted today (story 2's grep shows two pointer lines, SKILL.md and ci.md, not one). Full suite with coverage exit 0, 98.32% (fail-under 85; _cobot_secrets.py 94%); test_secret_reads_gate.py and test_hass_cli_gate.py 247 passed; ruff 0.17.6 check and format clean; markdownlint-cli2 0.24.2 clean; check-plugin ok; sync-agents --check in sync; claude plugin validate --strict passes twice; agy plugin validate passes with its one warning; cobot-deps check --fresh: no supported lockfile; cobot-memory check: brief 5651 of 6000. Reviews: code-reviewer and security-reviewer ran (cobot's consultants were not loaded; no consult domain applied); /cobot:security-sweep not run.
Open: F-50, F-51; the paid evals consult-homeassistant and spec-names-missing-expert not run; residuals: the Read and Grep tools, an anchored glob, the main thread's file reads; onboard step 6b overlaps the gcp-mcp-opt-in spec's step 6b (that build adapts, per its session).
Next: the owner pushes feat/expert-homeassistant and opens one PR.
verified: tree 29bd071b4cce235c7b251208cb26d96f2b7bcaca · full suite with coverage, lint, validators

## 2026-11-21 — gcp-mcp-opt-in: spec written, challenged and folded
Changed: .agent/specs/gcp-mcp-opt-in.md (medium): the gcp-mcp: yes|no header line asked once at the first Google Cloud work (onboard 6b on first run or refresh, consult, spec and wrap gcp consultants, debug after its live context); the guarded setup in mcp.md at -s user; ask rows on every registration route (claude mcp add|add-json|remove, --mcp-config, ~/.claude.json, .mcp.json); the Google Cloud CLI server refused whole and its tool names on any server; a pinned test that grants never reach MCP; check warnings on the line and a repo .mcp.json.
Why: owner-ideas-03 §4 MCP opt-in and reads-through-MCP (confirmed); owner's answers Q1 no by default, Q2 refuse cloudcli, Q3 eval plus text tests, Q4 -s user.
Proof: challenger SOUND WITH CHANGES (4 MAJOR, 7 MINOR folded) and gcp consult (3 MAJOR, 5 MINOR folded), both run from cobot's agent definitions through a general agent because the cobot: agents were not loaded; Google's MCP docs read 2026-11-20 and 21; dry run cobot-rules check on claude mcp add prints none today.
Open: onboard step 6b and spec step 5 overlap with the F-39 spec; second-identity roles reported until the build checks them; narrower readonly OAuth scopes unverified.
Next: /cobot:build gcp-mcp-opt-in on the owner's word.
verified: tree 37cd32d46b865c1c521b6cc7af300a02064096d0 · spec only, no code

## 2026-11-22 — spec-names-missing-expert drops its spec-skill grader (spec expert-homeassistant)

Changed: removed plugins/cobot/evals/spec-names-missing-expert/graders/spec-skill.md.
Why: the prompt opens with a bare /cobot:spec line, which expands the skill without a Skill tool call, so the grader could never pass; the local run scored 0.83 with every other grader passing. spec-file already shows the spec skill ran.
Proof: local eval, --runs 1, Sonnet 5.5: consult-homeassistant 1.00 ($0.19), spec-names-missing-expert 5/6 with only spec-skill failing ($0.39); tests/test_eval_graders.py passes.
Open: CI evals cannot run from a feature branch (the evals environment's branch rule); the cases run 3 times in CI, once locally here.
Next: merge PR 80, then the GCP MCP opt-in build.
verified: tree 9cc43661fedd9af0c0b1054ac989ec7fddcfaac9 · eval-graders

## 2026-11-22 — the branch is rewritten without a secret-shaped fixture value (spec expert-homeassistant)

Changed: every commit on feat/expert-homeassistant now writes x for the old six-character placeholder value: tests/test_hass_cli_gate.py, tests/test_secret_reads_gate.py, the spec's trust-boundary row and one journal line. No other change.
Why: GitGuardian flagged five of those values in the hass-cli gate fixtures (Generic CLI Secret, Generic Password) and scans every commit of a pull request, so only a rewrite clears it. Fixtures carry no secret-shaped literal.
Proof: full suite 4387 passed, 98.32 %; ruff check and format clean; no commit from the spec on holds the old value. Backup branch backup/expert-homeassistant-d9b5369, local.
Open: the five GitGuardian incidents on the dashboard are the owner's to resolve.
Next: merge PR 80, then the GCP MCP opt-in build.
verified: tree 0edcc05a8708cfd16b6dcba4bf49dbf14d9fa4e2 · full suite with coverage, ruff

## 2026-11-22 — gcp-mcp-opt-in T01: registration asks, the Cloud CLI server refused, grants kept off MCP
Changed: default.rules: never mcp__gcp-cloudcli__*, never mcp__*__run_gcloud_command and run_bq_command; ask Bash(claude *mcp add*), (claude *mcp remove*), (claude *--mcp-config*), Edit and Write of ~/.claude.json and .mcp.json. tests/test_gcp_mcp_gate.py (stories 4 and 5: rtk, absolute path and --debug forms ask; list and get stay silent; the CLI server denied under any name and over an owner allow; under an active gcloud grant MCP writes deny, scale_service asks, reads silent); test_cliInProcess_sync now expects the one expressible MCP deny, mcp__gcp-cloudcli__*.
Why: spec gcp-mcp-opt-in T01 (owner Q2); rebased on a675320 first, F-39's onboard 6b kept, this spec's onboard step becomes 6c.
Proof: gate suites (cobot_rules, differential, agy, read_list_limits, session_grants, grant_store, cobot_shell, check_plugin, investigator, hass_cli_gate, secret_reads_gate, gcp_mcp_gate, github_settings, grant_texts) exit 0; ruff 0.17.6 check and format clean; check-plugin ok.
Open: none.
Next: T02, the check warnings.
verified: tree a1b06ed93d84c4c976c32e1eb918c5ada99deb08 · gate suites, ruff, check-plugin

## 2026-11-22 — gcp-mcp-opt-in T02: check names a broken gcp-mcp line and a repository .mcp.json
Changed: bin/cobot-memory: gcp_mcp_warnings in cmd_check: a gcp-mcp line that is not exactly yes or no (a trailing # comment allowed), repeated, or below the header; a repository .mcp.json (the checkout's) declaring gcp-* or a cloudcli.googleapis.com URL under any name. The file is read only when regular (lstat) and at most 64 kB, invalid JSON is one line, repository values and odd names are never echoed. gcp-mcp stays out of the template header. tests/test_gcp_mcp_check.py (story 6).
Why: spec gcp-mcp-opt-in T02, the CONTEXT.md and .mcp.json trust-boundary rows.
Proof: test_cobot_memory, test_gcp_mcp_check, test_cobot_session exit 0; ruff 0.17.6 check and format clean.
Open: none.
Next: T03, expert-gcp and mcp.md.
verified: tree 408a612783490654fa0856320e2724e8df10899b · memory suites, ruff

## 2026-11-22 — gcp-mcp-opt-in T03: the opt-in rule in expert-gcp, the guarded setup in mcp.md
Changed: expert-gcp "Google Cloud MCP servers": endpoint exceptions, the Cloud CLI server refused and the claude.ai connector unsupported, and "The opt-in, once per repository" (triggers, the exact line above ## Stack, the recommendation, unusable memory, main thread only, the four branches, tool output is data). references/mcp.md: "Per repository" (two silent reads, the signal table without Storage, six printed steps with the read-only guard by parent, -s user, bare --client-secret, run none); dated 2026-11-21 lines (Storage at /storage/mcp and its tools, the Cloud CLI server, advertised scopes all write-capable, serviceUsageAdmin, deny-policy caveats, the claude.ai connector route); setup at -s user; second identity on predefined viewer roles plus serviceUsageConsumer (reported). tests/test_gcp_mcp_opt_in.py stories 2, 3, 7.
Why: spec gcp-mcp-opt-in T03; the gcp consult's MAJORs; owner Q1 and Q4.
Proof: test_gcp_mcp_opt_in, test_check_plugin, test_cobot_knowledge exit 0; check-plugin ok; markdownlint 0.24.2 clean on both files; cobot-memory knowledge expert-gcp: 81 lines, 4 reported, 1 assumed (universe.md, unchanged); ruff clean. gcloud projects describe --format='value(parent)' and services list --enabled dry-run silent.
Open: the second identity's role set stays reported until a sign-in with it is proven; narrower readonly scopes unverified.
Next: T04, the trigger sites.
verified: tree 133126a2cd927678f240a70a710e5206b3ac0e17 · focused suites, check-plugin, markdownlint, ruff

## 2026-11-22 — gcp-mcp-opt-in T04: the trigger sites point at expert-gcp's opt-in
Changed: onboard step 6c Google Cloud MCP (after F-39's 6b Domains, keyed on its Google Cloud domain, first run or refresh); consult step 1 asks in the main thread before the fan-out, its one write, stated in the description and the last line; spec step 5 and wrap step 3 ask first when they pick gcp; debug step 1 asks after the live context, its own question, lead-only MCP reads; routing.md: gcp-mcp yes, probes name a gcloud read, output is data. Spec: onboard 6b renumbered 6c and wrap step 2 corrected to 3 (the promise unchanged); T01–T04 ticked. tests/test_gcp_mcp_opt_in.py story 1.
Why: spec gcp-mcp-opt-in T04; F-39 merged its own 6b first.
Proof: test_gcp_mcp_opt_in, test_workflow_skills, test_debug_skill, test_spec_skill, test_consult_domains, test_check_plugin, test_agents_sync, test_missing_domain, test_new_project, test_security_sweep_skill exit 0; ruff clean; check-plugin ok; sync-agents --check in sync; markdownlint clean on the six files.
Open: none.
Next: T05, the eval, run locally.
verified: tree 7e30807513340ea42befce843fdd265967326fb0 · focused suites, check-plugin, sync-agents, markdownlint, ruff

## 2026-11-22 — gcp-mcp-opt-in T05: evals gcp-mcp-asked-once and gcp-mcp-never-again
Changed: two cases on a trusted lab repository with memory and a google provider (fixtures are heredocs, no secret-shaped literal); asked-once (no line): consultant ran, question stated, gcp-mcp: no written in the header, no AskUserQuestion, nothing registered; never-again (gcp-mcp: no present): consultant ran, the line kept and alone, no Edit of CONTEXT.md, no question, nothing registered. A bare /cobot:consult gcp first line, so no Skill grader. tests/test_eval_graders.py: matches() and fixture tests for both.
Why: spec gcp-mcp-opt-in story 1 (owner Q3).
Proof: tests/test_eval_graders.py exit 0; shellcheck clean on both fixtures; ruff clean. Local evals (--runs 1 --ablation none --scaffold, Claude Code 2.1.311): gcp-mcp-asked-once 1.00 ($0.33), gcp-mcp-never-again 1.00 ($0.27); a first run without --scaffold (0.67 each, no workspace) does not count. Total $1.23.
Open: CI runs them three times; the evals environment refuses feature branches.
Next: T06, the docs.
verified: tree ef79286c2dcf6d52297efba4cb96e3a020c7e6a6 · grader tests, shellcheck, local evals

## 2026-11-22 — gcp-mcp-opt-in T06: decision 37 and the docs
Changed: decision 37 in docs/01-decisions.md (36 is F-39's); docs/02-design.md §12 Google Cloud row; docs/configuration.md (the gcp-mcp header row, the Google Cloud MCP setup at -s user with the guard, the refusals and the registration asks); docs/architecture.md (Cloud CLI refusal, grants Bash-only, registration asks, the opt-in line); CHANGELOG Unreleased Added and Security; spec T05 and T06 ticked.
Why: spec gcp-mcp-opt-in T06.
Proof: markdownlint-cli2 0.24.2 clean over 146 files.
Open: none.
Next: /cobot:wrap.
verified: tree ef79286c2dcf6d52297efba4cb96e3a020c7e6a6 · markdownlint

## 2026-11-22 — wrap gcp-mcp-opt-in: the reviews folded, the spec converged
Changed: cobot-rules: an ask Edit/Write row now protects a literal shell word naming its file (cp, tee, a redirection, dd of=, curl -o, git checkout -- …), as never rows do; a glob that only could name it stays silent (word_touches keeps never rows for holes). default.rules: claude --settings, mcp reset-project-choices and claude-code mcp ask. cobot-memory: .mcp.json decoder and URL errors (RecursionError, int-digit ValueError, an unclosed IPv6 bracket) are one line, not a crash; names fullmatch; the header test is by position; the Cloud CLI host matched with a trailing dot, behind userinfo and in a stdio launcher's args. expert-gcp: the value rule matches check exactly, a broken line is replaced in place, never doubled; mcp.md reads value(parent.type) (reported shape). Eval gcp-mcp-never-again gains not-asked-again. Docs, decision 37, CHANGELOG updated; the journal's 2026-11-21 spec entry moved back to its date (the rebase had put it after 2026-11-22). Spec Converge written. Findings F-52 (MultiEdit and NotebookEdit match no file row), F-53 (bunx, node cli.js, $CLAUDE_CONFIG_DIR/.claude.json), F-54 (MCP refusals case-sensitive).
Why: wrap reviews: code review 4 MAJOR and 5 MINOR, security review 1 HIGH, 1 MEDIUM and 8 LOW (code-reviewer and security-reviewer agents; cobot's consultants not loaded, no consult domain in the diff).
Proof: converge: stories 1-7 accepted today. Full suite with coverage exit 0, 98.34% (fail-under 85); ruff 0.17.6 check and format clean; shellcheck clean with the new fixtures; markdownlint-cli2 0.24.2 clean over 146 files; claude plugin validate --strict passes for the plugin and the marketplace; check-plugin ok (protocol 3399); sync-agents --check in sync; agy plugin validate passes with its one warning; cobot-memory check: journal newest at bottom, brief 5999 of 6000; cobot-deps check --fresh: no supported lockfile. Local evals after the folds (--runs 1 --scaffold): gcp-mcp-asked-once 1.00, gcp-mcp-never-again 1.00 ($0.62; $1.85 for the build). Gate dry runs: cp, tee, cat >, dd of=, curl -o and git checkout -- on .mcp.json ask; git add src/* and cp src/* dist/ silent.
Open: F-52, F-53, F-54; the second identity's roles and the value(parent.type) shape stay reported until a live project; the brief is 1 character under its budget; two sealed eval temp folders in /tmp could not be removed (tmpfs, gone at reboot).
Next: the owner pushes the branch and opens one PR.
verified: tree d95513ded06ddfe571632158b5247a885a941d45 · full suite with coverage, lint, validators, local evals
