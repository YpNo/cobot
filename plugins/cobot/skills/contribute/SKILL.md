---
name: contribute
description: >-
  Drive a change in someone else's repository to a pull request under the maintainers' rules. Invoke in a foreign repository (memory outside the tree) once /cobot:wrap has stamped the work: reads the constraints onboard copied (AI policy, DCO or CLA, target branch), keeps .agent/UPSTREAM.md current, prepares the branch on the upstream base with a sign-off when required, prepares the facts for the PR body, and prints the push and gh pr create commands for the owner. Never pushes, never opens or comments on anything, never writes PR text the maintainers forbid.
argument-hint: [spec slug or branch]
---

# /cobot:contribute — upstream work under the maintainers' rules

You run in the main thread. Nothing outward happens here: `git push`, `gh pr create`, `gh pr
comment` and `gh repo fork` are asked by the gate and are proposed as commands, never run on your
own initiative (decision 6). Small PRs are the rule upstream (decision 20): one concern, the
maintainers' size.

1. **Constraints first.** Read CONTEXT.md's Constraints and `.agent/UPSTREAM.md`. On first use,
   create `UPSTREAM.md` from `<plugin root>/skills/contribute/templates/UPSTREAM.md`
   (`${CLAUDE_PLUGIN_ROOT}` or the brief's plugin folder; the same sections in the same order if absent) and fill it from
   `CONTRIBUTING.md`, `AI_POLICY.md` or its equivalent, `.github/PULL_REQUEST_TEMPLATE*`, the DCO
   or CLA note, the project's agent instructions and `git log` (commit style, sign-offs, branch
   the maintainers merge into). Record every remote other than `origin` under `never push to:`;
   `onboard --foreign` already wrote a `never Bash(git push <remote>*)` line for each into the
   project rules. Memory is outside the tree, so this file never reaches upstream.
   If the policy forbids autonomous contributions, stop here and say so: the owner contributes,
   the cobot only prepares.
2. **Proof on HEAD.** Run `cobot-memory stamp`. `ok <sha>` means the last wrap covers HEAD
   (equal, or only `.agent/**`, `docs/**`, `CHANGELOG.md`, `README.md` changed since in
   committed mode). `missing — <reason>` means unverified work: run `/cobot:wrap` first; never
   propose a push of unverified work.
3. **Topology.** Resolve the upstream, never guess it: `gh repo view --json parent,nameWithOwner`
   names the parent of the fork; `git remote -v` shows which remote is the fork (the owner's
   identity) and which others exist (headscale carries a private advisory remote that nothing
   may push to). If no remote points at the parent, propose `git remote add upstream <url>`
   (asked). Base the branch
   on the upstream's default branch (`git fetch upstream`, then `git rebase upstream/<main>`, or
   a merge when the project forbids rebases); name it the way UPSTREAM.md records.
4. **Commits.** Rewrite nothing the owner did not ask to rewrite. When the DCO applies, every
   commit needs `Signed-off-by: <the owner's name and email>` — that is the owner's own
   attestation and is not the attribution footer decision 18 bans; use `git commit -s` for new
   commits and propose `git rebase --signoff upstream/<main>` for existing ones. Check the log for
   `Co-Authored-By` or an AI named as author and remove it before anything leaves.
5. **The PR body.** Record the facts in UPSTREAM.md under *Open PRs*: what changed and why, how
   it was tested (the wrap proof lines), the issue it closes, the maintainers' checklist. When
   the policy allows generated text, draft the body into `.agent/pr-body.md` from those facts;
   when it forbids AI-written PR or comment text (headscale does), stop at the facts and tell
   the owner the body is theirs to write. Never put `Generated with` or an AI author in a body
   (the gate denies it).
6. **Hand over.** Print, in order, the commands the owner runs or approves:
   `git push -u <fork> <branch>`, then `gh pr create --repo <upstream> --base <main> --head
   <owner>:<branch> --title "<conventional title>" --body-file .agent/pr-body.md` (or `--web`
   when the owner writes the body). Draft PRs when the maintainers ask for them. After the PR
   exists, every reply to a maintainer is the owner's; the cobot may prepare facts, never post.
7. **Memory.** Update UPSTREAM.md (branch, PR URL once known, review state) and journal one line.
