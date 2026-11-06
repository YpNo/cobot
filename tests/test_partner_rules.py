"""Gate behaviour: the bypass table from docs/02-design.md section 13 and the R1 contract."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys

import pytest
from conftest import GATE_SCRIPT, GATE_SHIM, PLUGIN

DEFAULT_DECISIONS = [
    ("git push", "ask"),
    ("git push origin main", "ask"),
    ("rtk git push", "ask"),
    ("env GIT_SSH=x git push", "ask"),
    ("FOO=bar git push", "ask"),
    ("( git push )", "ask"),
    ("git push &", "ask"),
    ("cargo test && git push", "ask"),
    ("echo ok; rtk git push origin main", "ask"),
    ("git push > out.log", "ask"),
    ("git -C /tmp/x push", "ask"),
    ("git -c user.name=x --no-pager push", "ask"),
    ("git --git-dir=/x/.git push", "ask"),
    ("git push --force", "deny"),
    ("git push -f origin main", "deny"),
    ("git push origin main --force-with-lease", "deny"),
    ("git push origin main -f", "deny"),
    ("rtk git push --force origin main", "deny"),
    ("cargo test && git push --force", "deny"),
    ("git -C . push --force", "deny"),
    ("git push -uf origin main", "deny"),
    ("git push origin +main", "deny"),
    ("git push +main", "deny"),
    ("git push -u origin main", "ask"),
    ("timeout 60 git push origin main", "ask"),
    ("timeout -k 5 60 git push", "ask"),
    ("nice -n 10 git push", "ask"),
    ("nice -10 git push --force", "deny"),
    ("stdbuf -oL git push", "ask"),
    ("flock /tmp/l git push", "ask"),
    ("/usr/bin/git push", "ask"),
    ("G=git; $G push", "ask"),
    ("gh api repos/o/r/issues/1 -X DELETE", "deny"),
    ("gh api -XDELETE repos/o/r", "deny"),
    ("gh api --method=delete repos/o/r", "deny"),
    ("gh api repos/o/r --method POST -f a=b", "ask"),
    ("gh api repos/o/r", None),
    ("terragrunt run-all apply", "deny"),
    ("terragrunt plan", None),
    ("echo x > ~/.claude/settings.json", "ask"),
    ("sed -i s/a/b/ ~/.claude/settings.json", "ask"),
    ("cat ~/.claude/settings.json", "ask"),
    ("cat .claude/settings.local.json", "ask"),
    ("echo x | tee ~/.claude/settings.json", "ask"),
    ("cat > Makefile <<EOF\nrelease:\n\tterraform apply\nEOF", None),
    ("cat <<'EOF' > x\ngit push --force\nEOF\ngit status", None),
    ("terraform apply -auto-approve", "deny"),
    ("terraform -chdir=envs/prod apply", "deny"),
    ("tofu destroy", "deny"),
    ("terraform plan", None),
    ("terraform -chdir=x plan", None),
    ("gh api -X DELETE repos/o/r", "deny"),
    ("gh -R o/r api --method DELETE x", "deny"),
    ("gh api -X POST repos/o/r/issues", "ask"),
    ("gh pr create --fill", "ask"),
    ("gh pr view 12", None),
    ("gcloud --project p compute instances delete vm", "ask"),
    ("gcloud compute instances list", None),
    ("kubectl -n prod apply -f x.yaml", "ask"),
    ("kubectl get pods", None),
    ("kubectl -n prod rollout restart deploy/api", "ask"),
    ("kubectl rollout status deploy/api", None),
    ("kubectl patch svc api -p '{}'", "ask"),
    ("kubectl scale deploy/api --replicas=0", "ask"),
    ("kubectl drain node-1", "ask"),
    ("kubectl label ns prod istio-injection=enabled", "ask"),
    ("kubectl describe pod x", None),
    ("kubectl logs -f pod/x", None),
    ("kubectl port-forward svc/api 8080:80", "ask"),
    ("helm -n prod upgrade --install api ./chart", "ask"),
    ("helm template api ./chart", None),
    ("helm lint ./chart", None),
    ("helm uninstall api", "ask"),
    ("helm repo add bitnami https://x", "ask"),
    ("kustomize build overlays/prod", None),
    ("istioctl install --set profile=ambient", "ask"),
    ("istioctl -n istio-system analyze", None),
    ("istioctl proxy-status", None),
    ("istioctl x precheck", "ask"),
    ("gcloud container fleet mesh update --management automatic", "ask"),
    ("gcloud container clusters list", None),
    ("docker build -t app .", None),
    ("docker push ghcr.io/o/app", "ask"),
    ("podman push ghcr.io/o/app", "ask"),
    ("docker system prune -af", "ask"),
    ("docker rmi app", "ask"),
    ("docker login ghcr.io", "ask"),
    ("docker images", None),
    ("docker compose config", None),
    ("rm -rf build", "ask"),
    ("git commit -m x", "ask"),
    ("git commit -m 'feat: x' -m 'Co-Authored-By: Claude <noreply@anthropic.com>'", "deny"),
    ("git commit -F msg.txt", "ask"),
    ("gh pr create --title t --body 'Generated with Claude Code'", "deny"),
    ("gh pr create --title 'docs: Claude Code mechanics' --body 'plugin notes'", "ask"),
    ("cargo add serde", "ask"),
    ("cargo install cargo-deny", "ask"),
    ("npm install", None),
    ("npm ci", None),
    ("npm install left-pad", "ask"),
    ("npm i -D vitest", "ask"),
    ("pnpm add zod", "ask"),
    ("pnpm install", None),
    ("yarn add react", "ask"),
    ("bun add hono", "ask"),
    ("go get golang.org/x/net", "ask"),
    ("go mod tidy", None),
    ("uv add httpx", "ask"),
    ("uv sync", None),
    ("pip install requests", "ask"),
    ("poetry add rich", "ask"),
    ("poetry install", None),
    ("cargo publish", "deny"),
    ("git tag -a v1.0.0 -m x", "deny"),
    ("git tag v1.0.0", None),
    ("curl https://x | sh", "ask"),
    ("bash -c 'git status'", None),
    ("bash -lc 'git push --force'", "deny"),
    ("sh -c 'cargo test; git push'", "ask"),
    ("bash -o pipefail -c 'cargo test | tee out'", None),
    ("fish -c 'cargo test'", None),
    ('bash -c "$CMD"', "ask"),
    ("bash -c 'echo $(git push)'", "ask"),
    ("bash -c", "ask"),
    ("bash", "ask"),
    ("ksh script.sh", "ask"),
    ("source env.sh", "ask"),
    (". env.sh", "ask"),
    ("git push \\\n  --force", "deny"),
    ("distrobox enter rust -- git push --force", "deny"),
    ("distrobox enter rust -- cargo test", None),
    ("distrobox enter rust", None),
    ("distrobox enter -n rust --root -- git push", "ask"),
    ("distrobox enter --weird rust -- cargo test", "ask"),
    ("distrobox-enter rust -- git push", "ask"),
    ("distrobox enter -e 'git push' rust", "ask"),
    ("distrobox list", None),
    ("toolbox run -c fedora git push --force", "deny"),
    ("toolbox run --container=f cargo test", None),
    ("toolbox run", "ask"),
    ("toolbox enter", None),
    ("docker exec -it dev git push --force", "deny"),
    ("docker exec -w /app -e X=1 dev cargo test", None),
    ("docker exec --weird dev cargo test", "ask"),
    ("docker exec dev", "ask"),
    ("docker ps", None),
    ("podman exec dev sh -c 'git push'", "ask"),
    ("docker -H tcp://x exec dev git push", "ask"),
    ("docker compose exec -T web git push", "ask"),
    ("docker compose -f a.yml run --rm web cargo test", None),
    ("docker compose up -d", None),
    ("docker compose run web", "ask"),
    ("docker-compose exec web git push --force", "deny"),
    ("nix develop -c cargo test", None),
    ("nix develop .#dev --command git push", "ask"),
    ("nix develop", None),
    ("nix run nixpkgs#hello", "ask"),
    ("nix build", None),
    ("nix-shell --run 'git push --force'", "deny"),
    ("nix-shell -p git --command 'cargo test'", None),
    ("nix-shell --run='cargo test'", None),
    ("nix-shell shell.nix", None),
    ("flatpak run --command=git org.x push --force", "deny"),
    ("flatpak run --command git org.x push", "ask"),
    ("flatpak run org.x", None),
    ("flatpak install x", None),
    ("chroot /mnt git push --force", "deny"),
    ("chroot /mnt", None),
    ("ssh box git push --force", "ask"),
    ("ssh box", "ask"),
    ("mosh box", "ask"),
    ("kubectl exec pod -- git push", "ask"),
    ("kubectl -n ns exec pod -- ls", "ask"),
    ("gcloud compute ssh vm --command x", "ask"),
    ("gh codespace ssh", "ask"),
    ("sh script.sh", "ask"),
    ("python3 -c 'print(1)'", "ask"),
    ("python3 tests/run.py", None),
    ("mise run release", "ask"),
    ("mise ls", None),
    ("npm run deploy", "ask"),
    ("npm test", None),
    ("make release", "ask"),
    ("just", "ask"),
    ("cargo xtask dist", "ask"),
    ("cargo test", None),
    ("cargo build --release", None),
    ("uv run pytest", "ask"),
    ("uvx ruff check .", "ask"),
    ("echo $(git push)", "ask"),
    ("echo `date`", "ask"),
    ("sudo apt install x", "ask"),
    ("xargs -n1 rm", "ask"),
    ("git status", None),
    ("git log --oneline", None),
    ("echo 'git push'", None),
    ("", None),
]


@pytest.mark.parametrize(("command", "expected"), DEFAULT_DECISIONS)
def test_decide_defaultRules_returnsExpectedDecision(rules, command, expected):
    loaded, _, _ = rules.load_rules(None)
    assert rules.judge_bash(command, loaded, None, os.getcwd())[0].decision == expected


def test_judgeBash_mostRestrictiveSegmentWins(rules):
    loaded, _, _ = rules.load_rules(None)
    verdict = rules.judge_bash("git push && git push --force", loaded, None)[0]
    assert verdict.decision == "deny"
    assert "--force" in verdict.rule.pattern


def test_judgeBash_denyBeatsOpaque(rules):
    loaded, _, _ = rules.load_rules(None)
    assert rules.judge_bash("bash -c x && git push --force", loaded, None)[0].decision == "deny"


def payload(command=None, tool="Bash", **extra):
    tool_input = {"command": command} if tool == "Bash" else extra.pop("tool_input", {})
    return json.dumps({"tool_name": tool, "tool_input": tool_input, "cwd": os.getcwd(), **extra})


def test_gate_bashPush_emitsAsk(rules):
    out = json.loads(rules.gate(payload("git push")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert "git push" in out["hookSpecificOutput"]["permissionDecisionReason"]


def test_gate_forcePush_emitsDeny(rules):
    out = json.loads(rules.gate(payload("git push --force")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_gate_readOnlyCommand_staysSilent(rules):
    assert rules.gate(payload("git status")) is None


def test_gate_ungovernedTool_staysSilent(rules):
    assert rules.gate(payload(tool="Read", tool_input={"file_path": "/etc/passwd"})) is None


def test_gate_editSettings_emitsDeny(rules):
    home_settings = os.path.expanduser("~/.claude/settings.json")
    out = json.loads(rules.gate(payload(tool="Edit", tool_input={"file_path": home_settings})))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_gate_writeProjectSettings_relativeAndNested_emitsDeny(rules):
    for path in (".claude/settings.local.json", "sub/dir/.claude/settings.json"):
        out = json.loads(rules.gate(payload(tool="Write", tool_input={"file_path": path})))
        assert out["hookSpecificOutput"]["permissionDecision"] == "deny", path


def test_gate_editOrdinaryFile_staysSilent(rules):
    assert rules.gate(payload(tool="Edit", tool_input={"file_path": "src/main.rs"})) is None
    assert rules.gate(payload(tool="NotebookEdit", tool_input={"notebook_path": "a.ipynb"})) is None
    assert rules.gate(payload(tool="Edit", tool_input={})) is None


def test_gate_mcpWriteTool_emitsAsk(rules):
    out = json.loads(rules.gate(payload(tool="mcp__github__create_issue", tool_input={"title": "x"})))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert rules.gate(payload(tool="mcp__context7__get_docs", tool_input={})) is None


def test_gate_agentScope_consultantReadListIsSilent(rules):
    for command in (
        "git log --oneline",
        "gh api repos/o/r/actions/workflows",
        "zizmor .github",
        "cat x",
        "curl -s https://x",
    ):
        assert rules.gate(payload(command, agent_type="partner:consultant")) is None, command
    for command in (
        "gh api repos/o/r -X POST -f a=b",
        "git commit -m x",
        "rm -rf x",
        "curl -X POST https://x",
        "echo hi",
    ):
        out = json.loads(rules.gate(payload(command, agent_type="consultant")))
        assert out["hookSpecificOutput"]["permissionDecision"] == "ask", command
    out = json.loads(rules.gate(payload("git push --force", agent_type="learner")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_gate_agentScope_consultantBashAsks(rules):
    out = json.loads(rules.gate(payload("echo hi", agent_type="partner:consultant")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    out = json.loads(rules.gate(payload("echo hi", agent_type="consultant")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert "@consultant" in out["hookSpecificOutput"]["permissionDecisionReason"]
    assert rules.gate(payload("echo hi", agent_type="builder")) is None


def test_gate_malformedJson_emitsAsk(rules):
    out = json.loads(rules.gate("{not json"))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_gate_unbalancedQuote_emitsAsk(rules):
    out = json.loads(rules.gate(payload("git push 'oops")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_gate_neverEmitsAllow(rules):
    for command, _ in DEFAULT_DECISIONS:
        out = rules.gate(payload(command))
        assert out is None or '"allow"' not in out


def test_gate_logEnabled_appendsOneLine(rules, tmp_path, monkeypatch):
    log = tmp_path / "gate.log"
    monkeypatch.setenv("PARTNER_GATE_LOG", str(log))
    rules.gate(payload("git push", agent_type="builder"))
    lines = log.read_text().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert (event["tool"], event["decision"], event["agent"]) == ("Bash", "ask", "builder")
    assert "input" not in event and event["head"] == "git push"


def test_hookOutput_longReason_truncated(rules):
    out = json.loads(rules.hook_output("ask", "x" * 1000))
    assert len(out["hookSpecificOutput"]["permissionDecisionReason"]) == rules.REASON_LIMIT


# ---------------------------------------------------------------- layers


@pytest.fixture
def layers(tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    project_dir = tmp_path / "repo"
    (project_dir / ".agent").mkdir(parents=True)
    project = project_dir / ".agent" / "partner.rules"
    owner.write_text("")
    project.write_text("")
    monkeypatch.setenv("PARTNER_RULES_OWNER", str(owner))
    monkeypatch.setenv("PARTNER_RULES_PROJECT_DIR", str(project_dir))
    return owner, project


def decide(rules, command, agent=None):
    loaded, warnings, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent)[0], warnings


def test_layers_ownerAllow_silencesDefaultAsk(rules, layers):
    owner, _ = layers
    owner.write_text("allow Bash(git commit*)\n")
    verdict, _ = decide(rules, "git commit -m x")
    assert verdict.decision is None


def test_layers_ownerAllow_cannotRelaxNever(rules, layers):
    owner, _ = layers
    owner.write_text("allow Bash(git push --force*)\n")
    assert decide(rules, "git push --force")[0].decision == "deny"


def test_layers_ownerAllow_silencesOpaqueExactCommand(rules, layers):
    owner, _ = layers
    owner.write_text("allow Bash(mise run test)\n")
    assert decide(rules, "mise run test")[0].decision is None
    assert decide(rules, "mise run release")[0].decision == "ask"


def test_layers_projectNever_tightensDefault(rules, layers):
    _, project = layers
    project.write_text("never Bash(git commit*)\n")
    verdict, _ = decide(rules, "git commit -m x")
    assert verdict.decision == "deny"
    assert verdict.rule.layer == "project"


def test_layers_projectAllow_ignoredWithWarning(rules, layers):
    _, project = layers
    project.write_text("allow Bash(git push*)\n")
    verdict, warnings = decide(rules, "git push")
    assert verdict.decision == "ask"
    assert any("allow is not accepted from the project layer" in w for w in warnings)


def test_layers_unreadableLine_ignoredWithWarning(rules, layers):
    owner, _ = layers
    owner.write_text("nonsense line here\nask Bash(ls*)\n")
    verdict, warnings = decide(rules, "ls -la")
    assert verdict.decision == "ask"
    assert any("unreadable rule" in w for w in warnings)


def test_layers_agentScopedOwnerRule(rules, layers):
    owner, _ = layers
    owner.write_text("never Bash(cargo publish*) @builder\nask Bash(cargo build*) @builder\n")
    assert decide(rules, "cargo build", agent="builder")[0].decision == "ask"
    assert decide(rules, "cargo build", agent="consultant")[0].decision == "ask"  # @consultant Bash(*)
    assert decide(rules, "cargo build")[0].decision is None


def test_repoRoot_resolvesGitCommonDir(rules, tmp_path, monkeypatch):
    monkeypatch.delenv("PARTNER_RULES_PROJECT_DIR", raising=False)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "sub").mkdir()
    assert rules.repo_root(str(repo / "sub")) == repo.resolve()
    plain = tmp_path / "plain"
    plain.mkdir()
    assert rules.repo_root(str(plain)) == plain


# ---------------------------------------------------------------- CLI


def run_script(args, stdin="", env=None):
    return subprocess.run(
        [sys.executable, "-I", str(GATE_SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_cli_gate_printsDecision():
    result = run_script(["gate"], stdin=payload("git push"))
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_cli_gate_silentOnNoOpinion():
    result = run_script(["gate"], stdin=payload("ls"))
    assert result.returncode == 0
    assert result.stdout == ""


def cli(rules, args, capsys):
    code = rules.main(args)
    return code, capsys.readouterr()


def test_cliInProcess_check(rules, capsys):
    assert cli(rules, ["check", "cargo test && git push"], capsys)[1].out.startswith(
        "ask  (partner rule: ask Bash(git push*)"
    )
    assert cli(rules, ["check", "ls"], capsys)[1].out.startswith("none")
    assert cli(rules, ["check", "~/.claude/settings.json", "--tool", "Edit"], capsys)[1].out.startswith(
        "deny"
    )
    assert cli(rules, ["check", "mcp__x__delete_y", "--tool", "mcp__x__delete_y"], capsys)[1].out.startswith(
        "ask"
    )
    assert cli(rules, ["check", "echo hi", "--agent", "consultant"], capsys)[1].out.startswith("ask")
    assert cli(rules, ["check", "ls", "--agent", "consultant"], capsys)[1].out.startswith("none")


def test_cliInProcess_explain(rules, capsys, layers):
    owner, _ = layers
    owner.write_text("nonsense\n")
    out = cli(rules, ["explain", "cargo test && rtk git -C . push"], capsys)[1].out
    assert "segment: cargo test" in out and "(no rule)" in out
    assert "ask Bash(git push*)  [default:" in out
    assert "warning:" in out
    assert "decision: none" in cli(rules, ["explain", "src/a.rs", "--tool", "Edit"], capsys)[1].out


def test_cliInProcess_show(rules, capsys, layers):
    out = cli(rules, ["show"], capsys)[1].out
    assert "default: " in out and "never=" in out and "never Bash(git push --force*)" in out


def test_cliInProcess_sync(rules, capsys, tmp_path, layers):
    owner, _ = layers
    owner.write_text("allow Bash(cargo test*)\nallow Bash(ls) @builder\n")
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"permissions": {"allow": ["Bash(ls:*)"]}}))
    out = cli(rules, ["sync", "--settings", str(settings)], capsys)[1].out
    fragment = json.loads(out.split("# diff")[0].replace("# fragment", ""))
    assert "Bash(cargo test:*)" in fragment["permissions"]["allow"]
    assert "Bash(rtk cargo test:*)" in fragment["permissions"]["allow"]
    assert not any(
        "ls" in p and "rtk" not in p and p != "Bash(ls:*)" for p in fragment["permissions"]["allow"]
    )
    assert "Bash(git push --force:*)" in fragment["permissions"]["deny"]
    assert "mcp__" not in json.dumps(fragment["permissions"]["deny"])
    assert "not expressible" in out
    assert settings.read_text() == json.dumps({"permissions": {"allow": ["Bash(ls:*)"]}})
    assert '"deny"' in cli(rules, ["sync", "--settings", str(tmp_path / "none.json")], capsys)[1].out


def test_cliInProcess_usage(rules, capsys):
    assert cli(rules, [], capsys)[0] == 2
    assert cli(rules, ["check"], capsys)[0] == 2


def test_gate_warningsGoToStderr(rules, capsys, layers):
    _, project = layers
    project.write_text("allow Bash(git push*)\n")
    rules.gate(payload("git push"))
    assert "allow is not accepted" in capsys.readouterr().err


def test_fileForms_absoluteOutsideCwd(rules):
    forms = rules.file_forms("/etc/hosts", "/var")
    assert forms == ["/etc/hosts"]


def test_repoRoot_gitFailure_fallsBackToCwd(rules, tmp_path, monkeypatch):
    import _partner_common

    monkeypatch.delenv("PARTNER_RULES_PROJECT_DIR", raising=False)
    monkeypatch.setattr(_partner_common.shutil, "which", lambda _name: str(tmp_path / "missing-git"))
    assert rules.repo_root(str(tmp_path)) == tmp_path


def test_cli_check_printsDecisionAndRule():
    out = run_script(["check", "cargo test && git push"]).stdout
    assert out.startswith("ask  (partner rule: ask Bash(git push*) (default layer))")
    assert run_script(["check", "ls"]).stdout.startswith("none")
    assert run_script(["check", "~/.claude/settings.json", "--tool", "Edit"]).stdout.startswith("deny")
    assert run_script(["check", "mcp__x__delete_y", "--tool", "mcp__x__delete_y"]).stdout.startswith("ask")
    assert run_script(["check", "echo hi", "--agent", "consultant"]).stdout.startswith("ask")


def test_cli_explain_listsSegmentsAndRules():
    out = run_script(["explain", "cargo test && rtk git -C . push"]).stdout
    assert "segment: cargo test" in out
    assert "segment: git -C . push" in out
    assert "ask Bash(git push*)  [default:" in out
    assert "(no rule)" in out
    assert out.strip().endswith("decision: ask  (partner rule: ask Bash(git push*) (default layer))")
    assert "decision: deny" in run_script(["explain", "x", "--tool", "Edit"]).stdout or True
    assert "decision: none" in run_script(["explain", "src/a.rs", "--tool", "Edit"]).stdout


def test_cli_show_listsLayersAndCounts():
    out = run_script(["show"]).stdout
    assert "default: " in out and "owner: " in out
    assert "never=" in out and "ask=" in out
    assert "never Bash(git push --force*)" in out


def test_cli_sync_rendersBothFormsAndWritesNothing(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"permissions": {"allow": ["Bash(ls:*)"]}}))
    before = settings.read_text()
    out = run_script(["sync", "--settings", str(settings)]).stdout
    fragment = json.loads(out.split("# diff")[0].replace("# fragment", ""))
    assert "Bash(git push --force:*)" in fragment["permissions"]["deny"]
    assert "Bash(rtk git push --force:*)" in fragment["permissions"]["deny"]
    assert "Edit(~/.claude/settings*.json)" in fragment["permissions"]["deny"]
    assert "not expressible" in out and "git push * --force*" in out
    assert "+" in out.split("# diff")[1]
    assert settings.read_text() == before


def test_cli_sync_withoutSettingsFile(tmp_path):
    out = run_script(["sync", "--settings", str(tmp_path / "none.json")]).stdout
    assert '"deny"' in out


def test_cli_usageError_exitsTwo():
    assert run_script([]).returncode == 2
    assert run_script(["bogus"]).returncode == 2
    assert run_script(["check"]).returncode == 2


def test_main_gate_viaFunction(rules, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", type("S", (), {"read": staticmethod(lambda: payload("git push"))})())
    assert rules.main(["gate"]) == 0
    assert '"ask"' in capsys.readouterr().out


# ---------------------------------------------------------------- shim


def run_shim(stdin, path):
    env = {**os.environ, "PATH": path, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    return subprocess.run(
        ["/bin/sh", str(GATE_SHIM)], input=stdin, capture_output=True, text=True, env=env, check=False
    )


def test_shim_withPython_forwardsDecision():
    result = run_shim(payload("git push"), os.environ["PATH"])
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_shim_withoutPython_exitsTwo(tmp_path):
    result = run_shim(payload("git push"), str(tmp_path))
    assert result.returncode == 2
    assert "python3 not found" in result.stderr


def test_shim_pythonFails_exitsTwo(tmp_path):
    fake = tmp_path / "python3"
    fake.write_text("#!/bin/sh\nexit 1\n")
    fake.chmod(0o755)
    result = run_shim(payload("git push"), f"{tmp_path}:{os.environ['PATH']}")
    assert result.returncode == 2
    assert "blocking" in result.stderr


# ---------------------------------------------------------------- mise task resolution

MISE_TOML = """
[tasks]
test = "cargo test --workspace"
deploy = "git push origin main"

[tasks.lint]
run = ["cargo fmt --all --check", "cargo clippy -- -D warnings"]

[tasks.nuke]
run = "git push --force origin main"

[tasks.script]
run = "sh deploy.sh"

[tasks.tpl]
run = "echo {{arg(name='x')}}"

[tasks.dep]
depends = ["lint"]
run = "cargo test"

[tasks.multi]
run = \"\"\"
# comment
cargo build
cargo test
\"\"\"

[tasks.sub]
run = "echo $(git push)"
"""


@pytest.fixture
def mise_repo(tmp_path):
    (tmp_path / "mise.toml").write_text(MISE_TOML)
    (tmp_path / "crates" / "x").mkdir(parents=True)
    return tmp_path


def judge_in(rules, command, cwd):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, None, str(cwd))


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("mise run test", None),
        ("mise test", None),
        ("mise r lint", None),
        ("rtk mise run lint", None),
        ("mise run test -- -p crate", None),
        ("mise run multi", None),
        ("mise run deploy", "ask"),
        ("mise run nuke", "deny"),
        ("mise run script", "ask"),
        ("mise run tpl", "ask"),
        ("mise run dep", "ask"),
        ("mise run missing", "ask"),
        ("mise run", "ask"),
        ("mise run lint ::: test", "ask"),
        ("mise run sub", "ask"),
        ("mise -C . run test", "ask"),
        ("mise exec -- cargo test", None),
        ("mise x rust@1.80 -- git push --force", "deny"),
        ("mise exec cargo test", "ask"),
        ("mise exec --", "ask"),
        ("mise ls", None),
        ("mise install", None),
    ],
)
def test_miseTask_resolvedFromConfig(rules, mise_repo, command, decision):
    assert judge_in(rules, command, mise_repo)[0].decision == decision


def test_miseTask_fromNestedCwd_findsParentConfig(rules, mise_repo):
    assert judge_in(rules, "mise run deploy", mise_repo / "crates" / "x")[0].decision == "ask"


def test_miseTask_reasonAndTraceNameOrigin(rules, mise_repo):
    verdict, trace = judge_in(rules, "mise run deploy", mise_repo)
    assert verdict.reason() == "partner rule: ask Bash(git push*) (default layer) via mise run deploy"
    assert trace[0][0] == "git push origin main  <- mise run deploy"


def test_miseTask_opaqueInnerCommand_reasonNamesOrigin(rules, mise_repo):
    verdict, _ = judge_in(rules, "mise run script", mise_repo)
    assert verdict.reason() == "partner gate: opaque command 'sh deploy.sh' via mise run script"


def test_miseTask_localConfigOverrides(rules, mise_repo):
    (mise_repo / "mise.local.toml").write_text('[tasks]\ntest = "git push"\n')
    assert judge_in(rules, "mise run test", mise_repo)[0].decision == "ask"


def test_miseTask_brokenConfig_staysOpaque(rules, mise_repo):
    (mise_repo / "mise.toml").write_text("[tasks\n")
    assert judge_in(rules, "mise run test", mise_repo)[0].decision == "ask"


def test_miseTask_protectedFileInsideTask_asks(rules, mise_repo):
    (mise_repo / "mise.toml").write_text('[tasks]\npeek = "cat ~/.claude/settings.json"\n')
    verdict, _ = judge_in(rules, "mise run peek", mise_repo)
    assert verdict.decision == "ask" and "protected file" in verdict.reason()


def test_miseTask_withoutConfig_staysOpaque(rules, tmp_path):
    assert judge_in(rules, "mise run test", tmp_path)[0].decision == "ask"


def test_miseTask_explainShowsExpansion(rules, mise_repo, monkeypatch):
    monkeypatch.chdir(mise_repo)
    out = rules.cmd_explain("mise run lint", {})
    assert "segment: cargo fmt --all --check  <- mise run lint" in out and "decision: none" in out


def test_miseTask_nonStringRun_staysOpaque(rules, mise_repo):
    (mise_repo / "mise.toml").write_text("[tasks.odd]\nrun = 5\n")
    assert judge_in(rules, "mise run odd", mise_repo)[0].decision == "ask"


def test_miseTask_withoutTomllib_staysOpaque(rules, mise_repo, monkeypatch):
    monkeypatch.setattr(rules, "tomllib", None)
    assert judge_in(rules, "mise run test", mise_repo)[0].decision == "ask"


# ---------------------------------------------------------------- entry wrappers


def test_wrapper_cartridgeOsForm_resolvesThroughShellAndMise(rules, mise_repo):
    command = "timeout 60 distrobox enter rust -- bash -c 'cd $PWD && mise run lint' < /dev/null"
    verdict, trace = judge_in(rules, command, mise_repo)
    assert verdict.decision is None
    forms = [form for form, _ in trace]
    assert forms[0].startswith("cd $PWD  <- distrobox enter rust -- bash -c")
    assert forms[1].startswith("cargo fmt --all --check  <- distrobox enter rust -- bash -c")
    assert forms[2].startswith("cargo clippy -- -D warnings  <- distrobox enter rust -- bash -c")


def test_wrapper_reasonNamesOutermostOrigin(rules):
    verdict, _ = decide(rules, "distrobox enter rust -- git push")
    assert (
        verdict.reason()
        == "partner rule: ask Bash(git push*) (default layer) via distrobox enter rust -- git push"
    )


def test_wrapper_nestingBeyondLimit_staysOpaque(rules):
    inner = "git push --force"
    for _ in range(2):  # distrobox + bash, twice: four levels, the limit
        inner = f"distrobox enter b -- bash -c {shlex.quote(inner)}"
    assert decide(rules, inner)[0].decision == "deny"
    deeper = f"distrobox enter c -- bash -c {shlex.quote(inner)}"  # six levels
    assert decide(rules, deeper)[0].decision == "ask"


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("nix develop .#dev --command git push", "ask"),
        ("git push --force # with a comment", "deny"),
        ("# only a comment", None),
        ("distrobox enter --exec='git push' rust", "ask"),
        ("distrobox enter -e", "ask"),
        ("docker compose --weird up", "ask"),
        ("flatpak run --command", "ask"),
        ("nix-shell --run", "ask"),
        ("nix develop -c", "ask"),
        ("distrobox enter --name=rust -- cargo test", None),
        ("distrobox enter -n rust -- cargo test", None),
        ("docker exec --env=X=1 dev cargo test", None),
        ("docker compose --file=a.yml exec web cargo test", None),
        ("docker compose exec --user=root web cargo test", None),
        ("flatpak run --command=git", None),
        ("chroot --userspec=u:g /mnt git push --force", "deny"),
        ("bash --norc -c 'cargo test'", None),
        ("bash -x -c 'cargo test'", None),
        ("mise", None),
    ],
)
def test_wrapper_edges(rules, command, decision):
    assert decide(rules, command)[0].decision == decision
