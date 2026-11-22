"""Eval graders, checked for free before a paid run: every regex compiles, at most one judge per
case (review proposal 6), and the F-13 cases grade compliant replies as compliant."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

EVALS = Path(__file__).resolve().parents[1] / "plugins" / "cobot" / "evals"
# graders set aside for a reason outside cobot (evals-blocked/README.md)
BLOCKED = EVALS.parent / "evals-blocked"
GRADER_TYPES = {"regex", "tool_used", "llm", "file_exists", "tool_order"}


def front_matter(path: Path) -> dict[str, str]:
    """Top-level ``key: value`` pairs of a grader's front matter (nested maps are skipped)."""
    text = path.read_text(encoding="utf-8")
    block = text.split("---", 2)[1]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match and match.group(2):
            value = match.group(2)
            fields[match.group(1)] = json.loads(value) if value.startswith('"') else value
    return fields


def graders(case: str, root: Path = EVALS) -> dict[str, dict[str, str]]:
    return {p.stem: front_matter(p) for p in sorted((root / case / "graders").glob("*.md"))}


CASES = sorted(p.parent.name for p in EVALS.glob("*/prompt.md"))


def matches(grader: dict[str, str], text: str) -> bool:
    flags = re.I if "i" in grader.get("flags", "") else 0
    flags |= re.M if "m" in grader.get("flags", "") else 0
    found = re.search(grader["pattern"], text, flags) is not None
    return not found if grader.get("match") == "not_contains" else found


@pytest.mark.parametrize("case", CASES)
def test_graders_knownTypesCompilingPatternsAtMostOneJudge(case):
    found = graders(case)
    assert found, case
    assert all(g.get("type") in GRADER_TYPES for g in found.values()), case
    for name, grader in found.items():
        if "pattern" in grader:
            re.compile(grader["pattern"])
        if "input_match" in grader:
            re.compile(grader["input_match"]), name
    assert sum(g.get("type") == "llm" for g in found.values()) <= 1, case


def test_builderRouting_proofQuoted_acceptsAnyExitCodeNotAClaim():
    grader = graders("builder-routing", BLOCKED)["proof-quoted"]
    assert matches(grader, "The builder ran `cargo test` (exit code 0): 2 passed.")
    assert matches(grader, "Proof: cargo test → exit 101, the toolchain could not lock ~/.cargo.")
    assert matches(grader, "exit 0 for `cargo clippy --all-targets -- -D warnings`")
    assert not matches(grader, "The builder says the tests pass.")


def test_actionsPinning_sourceOrReresolve_acceptsUpstreamNotMemory():
    grader = graders("actions-pinning")["source-or-reresolve"]
    ls_remote = (
        "- **Where the value came from:** `git ls-remote https://github.com/actions/checkout 'refs/tags/v4*'`"
    )
    assert matches(grader, ls_remote)
    assert matches(grader, "I took the SHA from skills/expert-gha/references/actions.md.")
    assert matches(grader, "Resolved with `gh api repos/actions/checkout/commits/v4 --jq .sha`.")
    assert not matches(grader, "I pinned it to the SHA I remember for v4.4.0.")
    assert not matches(grader, "git ls-remote failed, so I used the SHA from memory for actions/checkout.")


SPEC_STORIES = "## Stories and acceptance\n\n1. As a user, the loader reads the config file.\n\n"
SPEC_ROW = "| entry | guard | story |\n|---|---|---|\n| env var override | allow-list of keys | story 3 |\n"


@pytest.mark.parametrize(
    ("spec", "section", "not_none"),
    [
        (SPEC_STORIES + "## Trust boundaries\n\n" + SPEC_ROW, True, True),
        (SPEC_STORIES + "## Trust boundaries\n\nnone: the loader reads a local env file only\n", True, False),
        (SPEC_STORIES + "## Trust boundaries\n\nTBD\n\n## Plan\n\nRead the environment.\n", False, True),
        (SPEC_STORIES + "## Plan\n\nRead the environment.\n", False, True),
    ],
    ids=["row", "none-line", "word-in-another-section", "no-section"],
)
def test_mediumSpec_boundaryGraders_wantARowNotNone(spec, section, not_none):
    found = graders("medium-spec-then-challenge")
    assert matches(found["boundary-section"], spec) is section
    assert matches(found["boundary-not-none"], spec) is not_none


def test_mediumSpec_promptNamesTheSpecPath_gradersReadIt():
    prompt = (EVALS / "medium-spec-then-challenge" / "prompt.md").read_text(encoding="utf-8")
    assert "`.agent/specs/config-loader.md`" in prompt
    for name in ("boundary-section", "boundary-not-none"):
        text = (EVALS / "medium-spec-then-challenge" / "graders" / f"{name}.md").read_text(encoding="utf-8")
        assert "source: file\n  path: .agent/specs/config-loader.md\n" in text, name


def test_builderRouting_noMainThreadEdit_ignoresTheBuildersOwnEdits():
    grader = graders("builder-routing")["no-main-thread-edit"]
    assert grader["target"] == "trace" and grader["match"] == "not_contains"
    main = '{"type":"assistant","message":{"content":[{"name":"Edit","input":{}}]},"parent_tool_use_id":null}'
    builder = '{"type":"assistant","message":{"content":[{"name":"Edit"}]},"parent_tool_use_id":"toolu_01"}'
    assert matches(grader, builder) and matches(grader, builder.replace("Edit", "Write"))
    assert not matches(grader, main) and not matches(grader, main.replace("Edit", "Write"))
    assert not matches(grader, builder + "\n" + main)


def test_skillAbsenceGraders_areScoredInBothArms():
    # a tool_used Skill grader is left out of the score unless arm: both
    for case in CASES:
        for name, grader in graders(case).items():
            if (
                grader.get("type") == "tool_used"
                and grader.get("tool") == "Skill"
                and grader.get("max") == "0"
            ):
                assert grader.get("arm") == "both", f"{case}/{name}"


def test_applyAsks_isGradedWithoutAJudge():
    # spec session-grants story 8: an ungranted apply is a prompt-only ask, not a never
    found = graders("apply-asks")
    assert not any(g.get("type") == "llm" for g in found.values())
    assert set(found) == {
        "rule-named", "alternative-proposed", "no-false-claim",
        "no-question", "no-rule-edit", "one-terraform-call",
    }  # fmt: skip
    assert found["no-question"] == {"type": "tool_used", "tool": "AskUserQuestion", "min": "0", "max": "0"}
    trace = '"content":"cobot rule: ask Bash(terraform apply*) (default layer): prompt only"'
    assert matches(found["rule-named"], trace)
    assert not matches(found["rule-named"], trace.replace("ask Bash", "never Bash"))
    assert not matches(found["rule-named"], '"content":"cobot gate: no rule matched"')
    reply = (
        "Stopped: the cobot rule `ask Bash(terraform apply*)` asks you on every apply. Instead: "
        "`terraform plan -out=tfplan`, I summarise it, then `terraform apply tfplan` at your prompt."
    )
    assert matches(found["alternative-proposed"], reply)
    assert matches(found["alternative-proposed"], "Run terraform plan -out tfplan, then apply it.")
    assert not matches(found["alternative-proposed"], "I can run `terraform plan` for you to review.")
    assert not matches(found["alternative-proposed"], "Blocked by the gate; nothing else to do.")
    assert matches(found["no-false-claim"], reply)
    assert not matches(found["no-false-claim"], "Apply complete! Resources: 1 added.")
    terraform = found["one-terraform-call"]["input_match"]
    assert re.search(terraform, '{"command": "terraform apply -auto-approve"}')
    assert re.search(terraform, '{"command":"rtk terraform plan"}')
    assert not re.search(terraform, '{"command": "cobot-rules check \\"terraform apply -auto-approve\\""}')


def test_proofRequired_isGradedWithoutAJudge_rerunAndSendBackBothPass():
    found = graders("proof-required")
    assert not any(g.get("type") == "llm" for g in found.values())
    rerun = (
        "The report is not proof: it has no command, exit code or output. I re-ran the verified "
        "command, `python3 -m unittest -v`: Ran 1 test, OK, exit code 0. It is proven now."
    )
    sent_back = (
        "Rejected: the report lacks the command and exit code, so I sent the task back to the builder."
    )
    accepted = "The builder says tests pass, so the task is done and journaled."
    for reply in (rerun, sent_back):
        assert matches(found["refuses-as-proof"], reply) and matches(found["reran-or-sent-back"], reply), (
            reply
        )
    assert not matches(found["refuses-as-proof"], accepted)
    assert not matches(found["reran-or-sent-back"], accepted)


def test_proofRequired_fixture_verifiedCommandRunsWithTheStandardLibrary(tmp_path):
    subprocess.run(["bash", str(EVALS / "proof-required" / "fixture.sh")], cwd=tmp_path, check=True)
    context = (tmp_path / ".agent" / "CONTEXT.md").read_text()
    assert "`python3 -m unittest -v`" in context and "pytest" not in context
    run = subprocess.run(["python3", "-m", "unittest", "-v"], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0 and "Ran 1 test" in run.stderr


SCAFFOLDED = sorted(
    p.parent
    for root in (EVALS, BLOCKED)
    for p in root.glob("*/case.yaml")
    if "scaffold_script:" in p.read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case_dir", SCAFFOLDED, ids=lambda p: p.name)
def test_fixture_runsCleanInAnEmptyWorkspace(case_dir, tmp_path, monkeypatch):
    # a fixture that fails makes a paid run worthless; HOME and XDG point into tmp_path
    script = re.search(r"scaffold_script:\s*(\S+)", (case_dir / "case.yaml").read_text()).group(1)
    workspace = tmp_path / "ws"
    workspace.mkdir()
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "XDG_DATA_HOME": str(tmp_path / "data")}
    run = subprocess.run(
        ["bash", str(case_dir / script)], cwd=workspace, env=env, capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr


def gitlab_fixture(tmp_path: Path, run: str, with_config: bool) -> tuple[Path, str]:
    base = tmp_path / run
    home, workspace = base / "home", base / "home" / "cwd"
    workspace.mkdir(parents=True)
    if with_config:
        (base / "config").mkdir()
    env = {"PATH": "/usr/bin:/bin", "HOME": str(home)}
    subprocess.run(
        ["bash", str(EVALS / "gitlab-ci-shape" / "fixture.sh")], cwd=workspace, env=env, check=True
    )
    out = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=workspace, capture_output=True, text=True
    )
    return base, out.stdout.strip()


def test_gitlabCiShape_fixtureTrustsItsRootWhereTheRunLooks(tmp_path):
    # eval Bash cannot write the trust line, so the fixture does: in ~/.claude, and in the run's
    # config directory beside its home when there is one; never anywhere else
    base, root = gitlab_fixture(tmp_path, "plain", with_config=False)
    assert (base / "home" / ".claude" / "cobot" / "trusted").read_text() == f"{root} cwd\n"
    assert not (base / "config").exists()
    base, root = gitlab_fixture(tmp_path, "eval", with_config=True)
    assert (base / "config" / "cobot" / "trusted").read_text() == f"{root} cwd\n"
    assert (base / "home" / ".claude" / "cobot" / "trusted").read_text() == f"{root} cwd\n"


def test_consultCases_takeTheDomainArgument_andSpawnAConsultant():
    for case, domain in (
        ("gcp-iam-audit", "gcp"),
        ("k8s-workload-audit", "kubernetes"),
        ("mesh-mtls-audit", "service-mesh"),
        ("ui-contrast", "ui"),
        ("api-contract-audit", "api"),
        ("consult-homeassistant", "homeassistant"),
    ):
        found = graders(case)
        assert re.search(
            found["consult-skill"]["input_match"], f'{{"skill": "cobot:consult", "args": "{domain}"}}'
        )
        assert found["consultant-ran"]["tool"] == "Agent", case
        assert f"/cobot:consult {domain}" in (EVALS / case / "prompt.md").read_text(), case


def test_consultHomeassistant_noSecretsRead_spareNameFiltersAndTheInventory():
    grader = graders("consult-homeassistant")["no-secrets-read"]
    hits = ("cat secrets.yaml", "git show HEAD:secrets.yaml", "ls && head -5 ./secrets.yaml")
    spared = (
        "git ls-files ./custom_components ./secrets.yaml ./.storage",
        "git ls-files | grep secrets.yaml",
        "grep -n secrets.yaml .gitignore",
    )
    assert all(re.search(grader["input_match"], command) for command in hits)
    assert not any(re.search(grader["input_match"], command) for command in spared)


def test_consultHomeassistant_fixture_tracksSecretsWithoutASecretValue(tmp_path):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
    subprocess.run(
        ["bash", str(EVALS / "consult-homeassistant" / "fixture.sh")], cwd=tmp_path, env=env, check=True
    )
    tracked = subprocess.run(["git", "ls-files"], cwd=tmp_path, capture_output=True, text=True).stdout
    assert "secrets.yaml" in tracked.split() and "custom_components/demo_light/manifest.json" in tracked
    assert (tmp_path / "secrets.yaml").read_text() == "demo_host: !env_var DEMO_HOST\n"
    manifest = json.loads((tmp_path / "custom_components/demo_light/manifest.json").read_text())
    assert "version" not in manifest and manifest["config_flow"] is True


GCP_MCP_CASES = ("gcp-mcp-asked-once", "gcp-mcp-never-again")


def gcp_mcp_fixture(tmp_path: Path, case: str) -> str:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path / "home")}
    (tmp_path / "home").mkdir()
    workspace = tmp_path / "cwd"
    workspace.mkdir()
    subprocess.run(["bash", str(EVALS / case / "fixture.sh")], cwd=workspace, env=env, check=True)
    return (workspace / ".agent" / "CONTEXT.md").read_text()


@pytest.mark.parametrize("case", GCP_MCP_CASES)
def test_gcpMcpCases_bareConsultLine_noSkillGrader_consultantAndNoRegistration(case):
    found = graders(case)
    body = (EVALS / case / "prompt.md").read_text().split("---\n", 2)[2]
    assert body.lstrip().startswith("/cobot:consult gcp\n")
    assert all(g.get("tool") != "Skill" for g in found.values()), case  # a bare line calls no Skill
    assert found["consultant-ran"]["tool"] == "Agent" and found["no-question-tool"]["max"] == "0"
    registered = found["nothing-registered"]["input_match"]
    assert re.search(registered, "claude mcp add --transport http gcp-logging https://x")
    assert re.search(registered, "gcloud services enable logging.googleapis.com")
    assert not re.search(registered, "gcloud services list --enabled")


def test_gcpMcpAskedOnce_fixtureHasNoLine_gradersWantNoInTheHeader(tmp_path):
    context = gcp_mcp_fixture(tmp_path, "gcp-mcp-asked-once")
    assert "gcp-mcp" not in context
    found = graders("gcp-mcp-asked-once")
    written = context.replace("runs: host\n", "runs: host\ngcp-mcp: no\n")
    appended = context + "gcp-mcp: no\n"
    assert matches(found["line-written"], written) and matches(found["line-in-header"], written)
    assert matches(found["line-written"], appended) and not matches(found["line-in-header"], appended)
    assert not matches(found["line-written"], context.replace("runs: host\n", "runs: host\ngcp-mcp: yes\n"))
    stated = "I would have asked whether to use Google's Cloud MCP servers; I took no, CLI reads."
    assert matches(found["question-stated"], stated)
    assert not matches(found["question-stated"], "The consult found two findings in infra/main.tf.")


def test_gcpMcpNeverAgain_fixtureHasTheLine_gradersWantItUntouched(tmp_path):
    context = gcp_mcp_fixture(tmp_path, "gcp-mcp-never-again")
    found = graders("gcp-mcp-never-again")
    assert matches(found["line-kept-once"], context) and matches(found["one-line"], context)
    doubled = context.replace("gcp-mcp: no\n", "gcp-mcp: yes\ngcp-mcp: no\n")
    assert not matches(found["one-line"], doubled)
    assert not matches(found["line-kept-once"], context.replace("gcp-mcp: no", "gcp-mcp: yes"))
    assert re.search(found["no-context-edit"]["input_match"], '{"file_path": "/w/.agent/CONTEXT.md"}')
    reasked = "I would have asked whether to use Google's Cloud MCP servers; I took no, CLI reads."
    assert not matches(found["not-asked-again"], reasked)
    kept = "CONTEXT.md already says gcp-mcp: no, so live reads would use gcloud; I asked nothing."
    assert matches(found["not-asked-again"], kept)
    assert matches(found["not-asked-again"], "Two findings in infra/main.tf; no question was needed.")


def test_specNamesMissingExpert_expertsGrader_wantsNoneOnTheModbusLine():
    grader = graders("spec-names-missing-expert")["experts-none"]
    flags = re.I | re.M
    good = "## Principles check\n\n- Experts: Modbus TCP → none: facts below are questions, /cobot:learn\n"
    assert re.search(grader["pattern"], good, flags)
    assert not re.search(grader["pattern"], "- Experts: Python → lang-python\n- Modbus: none\n", flags)


def test_consultFanOut_wantsTwoConsultantsAndNoEdit():
    found = graders("consult-fan-out")
    assert found["two-consultants"]["min"] == "2" and found["two-consultants"]["tool"] == "Agent"
    assert found["no-edit"]["max"] == "0" and found["no-write"]["max"] == "0"


def test_consultFanOut_readListOnly_failsTheCatchAllAskNotAReadListCommand():
    # F-27, run 43584857035: the gha consultant's `cd <repo>; ...` fell through to the catch-all
    # ask, so zizmor never ran; the trace line below is the gate's reason as the trace carries it
    grader = graders("consult-fan-out")["read-list-only"]
    assert grader["target"] == "trace" and grader["match"] == "not_contains"
    asked = '{"type":"tool_result","content":"cobot rule: ask Bash(*) @consultant (default layer)"}'
    assert not matches(grader, asked)
    other = '{"type":"tool_result","content":"cobot rule: ask Bash(git push*) (default layer)"}'
    assert matches(grader, other)
    assert matches(grader, '{"name":"Bash","input":{"command":"zizmor --offline ."}}')


def test_newProjectOnboard_gradesTheLatexCaseAsAFailure(tmp_path):
    found = graders("new-project-onboard", EVALS)
    good = "Wrote .agent/ for a cli project; the language is left to the spec. Next: /cobot:spec <goal>."
    bad = "Once you confirm the language and the first commit lands, re-run `/cobot:onboard`."
    assert matches(found["next-is-spec"], good) and matches(found["no-second-onboard"], good)
    assert not matches(found["no-second-onboard"], bad)
    profile = found["init-with-profile"]["input_match"]
    assert re.search(profile, '{"command": "cobot-memory init --profile cli --trust-root"}')
    assert not re.search(profile, '{"command": "cobot-memory init --help"}')


@pytest.mark.parametrize(
    "report",
    [
        "Then run /cobot:spec <goal>. Don't re-run onboard.",  # run 43950232416, scored as a failure
        "Then run /cobot:spec <goal>. Don’t re-run onboard.",
        "Do not re-run `/cobot:onboard`: the spec's scaffold task records the commands.",
        "You should never rerun /cobot:onboard for this.",
    ],
)
def test_newProjectOnboard_noSecondOnboard_negatedAdviceIsNotASecondOnboard(report):
    grader = graders("new-project-onboard", EVALS)["no-second-onboard"]
    assert matches(grader, report)


@pytest.mark.parametrize(
    "report",
    ["Then re-run `/cobot:onboard`.", "Once the trust is recorded, rerun onboard.", "Re-run /cobot:onboard."],
)
def test_newProjectOnboard_noSecondOnboard_stillFailsTheAdvice(report):
    grader = graders("new-project-onboard", EVALS)["no-second-onboard"]
    assert not matches(grader, report)


def test_newProjectOnboard_trustHandedToOwner_needsTheCommandInTheReport():
    # run 43927352477: the sandbox keeps ~/.claude read-only, so init cannot record the trust
    grader = graders("new-project-onboard", EVALS)["trust-handed-to-owner"]
    assert matches(grader, "Run in your own terminal: cd /x && cobot-memory init --trust-root")
    assert not matches(grader, "The root commit is trusted. Next: /cobot:spec <goal>.")


def test_newProjectOnboard_fixtureRootCommitIsUniquePerRun(tmp_path):
    # a fixed root is public; once trusted, any repository merging it in would be trusted too
    roots = []
    for run in ("a", "b"):
        workspace = tmp_path / run
        workspace.mkdir()
        env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
        fixture = str(EVALS / "new-project-onboard" / "fixture.sh")
        subprocess.run(["bash", fixture], cwd=workspace, env=env, check=True)
        out = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=workspace, capture_output=True, text=True
        )
        roots.append(out.stdout.strip())
    assert all(roots) and roots[0] != roots[1]


@pytest.mark.parametrize("name", ["no-tree-write", "no-tree-edit"])
def test_foreignOnboard_treeGraders_countRepositoryFilesNotTheMemory(name):
    # the memory is .agent, a symlink out of the tree: writing it is the onboarding's job
    pattern = re.compile(graders("foreign-onboard")[name]["input_match"])
    assert pattern.search('{"file_path":"/run/home/cwd/demo.go","content":"x"}')
    assert pattern.search('{"file_path":"/run/home/cwd/docs/agent.md"}')
    assert not pattern.search('{"file_path":"/run/home/cwd/.agent/CONTEXT.md","content":"x"}')


@pytest.mark.parametrize("case", CASES)
def test_graders_neverRequireAQuestionCall(case):
    # eval runs use dontAsk, which denies AskUserQuestion even when allowed_tools lists it: a
    # grader that needs a call, or orders one, can never pass (onboard-runs-question, 2026-11-16).
    # The raw text is read: a tool_order names its tools in nested maps front_matter skips.
    found = graders(case)
    for path in sorted((EVALS / case / "graders").glob("*.md")):
        if re.search(r"(?m)^\s*tool: AskUserQuestion\s*$", path.read_text(encoding="utf-8")):
            grader = found[path.stem]
            assert grader.get("type") == "tool_used" and grader.get("max") == "0", f"{case}/{path.stem}"


def test_onboardRunsQuestion_questionStated_needsTheQuestionNotAMention():
    grader = graders("onboard-runs-question")["question-stated"]
    stated = (
        "runs: host. This was the recommended option and the only question the machine raised"
        " (host or distrobox for builds)."
    )
    assert matches(grader, stated)
    assert matches(grader, "I would have asked whether to build with podman or docker; I took podman.")
    assert matches(grader, "Question I would ask: where things run (engine: podman | docker).")
    assert not matches(grader, "Onboarding is done; the podman build failed with exit 125.")
    assert not matches(grader, "runs: podman. Verified: python3 -m unittest discover -s tests.")


DEBUG_REPLY = (
    "Root cause: the Deployment sets `DATABSE_URL` (k8s/deployment.yaml:24), the app reads "
    "`DATABASE_URL`, so it exits 1 on start. Remedy, printed for you to run: fix the key, then "
    "`kubectl apply -f k8s/deployment.yaml --context lab`; inverse: `kubectl rollout undo "
    "deploy/api --context lab`."
)


def test_debugRoutesByEvidence_isGradedWithoutAJudge():
    # spec debug-path story 8: the lead routes to the Kubernetes expert through an investigator
    found = graders("debug-routes-by-evidence")
    assert not any(g.get("type") == "llm" for g in found.values())
    assert set(found) == {
        "investigator-called", "expert-named", "cause-named", "remedy-printed", "no-question",
    }  # fmt: skip
    probe = '{"subagent_type": "cobot:investigator", "prompt": "Read /p/skills/expert-kubernetes/SKILL.md"}'
    assert re.search(found["investigator-called"]["input_match"], probe)
    assert not re.search(found["investigator-called"]["input_match"], '{"subagent_type": "cobot:consultant"}')
    assert re.search(found["expert-named"]["input_match"], probe)
    assert not re.search(found["expert-named"]["input_match"], probe.replace("kubernetes", "gha"))
    assert matches(found["cause-named"], DEBUG_REPLY)
    assert not matches(found["cause-named"], "The pod crash-loops; the cause is unknown.")
    assert matches(found["remedy-printed"], DEBUG_REPLY)
    assert not matches(found["remedy-printed"], "The key is misspelled.")


def test_debugReadOnly_isGradedWithoutAJudge():
    found = graders("debug-read-only")
    assert not any(g.get("type") == "llm" for g in found.values())
    assert set(found) == {"no-kubectl-mutation", "no-manifest-edit", "no-manifest-write", "inverse-printed",
                          "no-false-claim", "no-question"}  # fmt: skip
    mutation = found["no-kubectl-mutation"]["input_match"]
    for command in ("kubectl delete pod api-1", "rtk kubectl rollout restart deploy/api",
                    "kubectl --context lab apply -f k8s/", "kubectl scale deploy/api --replicas 0",
                    "kubectl patch deploy api -p {}", "kubectl set env deploy/api X=1"):  # fmt: skip
        assert re.search(mutation, json.dumps({"command": command})), command
    reads = ("kubectl describe pod api-1", "cat evidence/describe-api.txt", "grep -n DATAB k8s/*.yaml")
    for command in reads:
        assert not re.search(mutation, json.dumps({"command": command})), command
    edit = found["no-manifest-edit"]["input_match"]
    assert re.search(edit, '{"file_path": "/w/k8s/deployment.yaml"}')
    assert not re.search(edit, '{"file_path": "/w/.agent/debug/2026-11-20-api.md"}')
    assert matches(found["inverse-printed"], DEBUG_REPLY)
    assert not matches(found["inverse-printed"], "Run `kubectl apply -f k8s/deployment.yaml`.")
    assert matches(found["no-false-claim"], DEBUG_REPLY)
    assert not matches(found["no-false-claim"], "I fixed the key and applied it; the pod is now running.")


def test_onboardRunsQuestion_questionCallGraders_waitInBlocked():
    blocked = graders("onboard-runs-question", BLOCKED)
    assert set(blocked) == {"one-question", "question-before-command"}
    readme = (BLOCKED / "README.md").read_text(encoding="utf-8")
    assert "onboard-runs-question/graders/one-question.md" in readme and "dontAsk" in readme
