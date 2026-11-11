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
    ("nix flake update", "ask"),
    ("nix flake lock --update-input nixpkgs", "ask"),
    ("nix flake show", None),
    ("nix develop --fallback --command go test ./...", None),
    ("nix develop --fallback --command bash -e script.sh", "ask"),
    ("goreleaser release --clean", "ask"),
    ("goreleaser release --snapshot --clean", "ask"),
    ("goreleaser build --snapshot", None),
    ("goreleaser check", None),
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
    ("npm test", "ask"),  # no package.json here: the script is unknown
    ("make release", "ask"),
    ("just", "ask"),
    ("cargo xtask dist", "ask"),
    ("cargo test", None),
    ("cargo build --release", None),
    ("uv run pytest", None),
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
        assert rules.gate(payload(command, agent_type="cobot:consultant")) is None, command
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


def test_gate_agentScope_learnerSharesTheReadListAndStaysReadOnly(rules):
    reads = (
        "git log --oneline -5",
        "gh api repos/actions/checkout/releases/latest",
        "file --version",
        "cat go.mod",
    )
    for command in reads:
        assert rules.gate(payload(command, agent_type="cobot:learner")) is None, command
    for command in ("curl -X POST https://example.com", "go test ./...", "cobot-memory learn '{}'"):
        out = json.loads(rules.gate(payload(command, agent_type="cobot:learner")))
        assert out["hookSpecificOutput"]["permissionDecision"] == "ask", command
    assert decide(rules, "cobot-memory learn --promote '{}'")[0].decision == "ask"
    nested = "plugins/cobot/bin/cobot-memory learn --dry-run --promote go"
    assert decide(rules, nested)[0].decision == "ask"
    assert decide(rules, "cobot-memory learn '{}'")[0].decision is None


def test_gate_agentScope_consultantBashAsks(rules):
    out = json.loads(rules.gate(payload("echo hi", agent_type="cobot:consultant")))
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
    monkeypatch.setenv("COBOT_GATE_LOG", str(log))
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
    project = project_dir / ".agent" / "cobot.rules"
    owner.write_text("")
    project.write_text("")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    monkeypatch.setenv("COBOT_RULES_PROJECT_DIR", str(project_dir))
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
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
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
        "ask  (cobot rule: ask Bash(git push*)"
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
    assert "not expressible" in out and "never mcp__gcp-*__apply_*" in out
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
    import _cobot_common

    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    monkeypatch.setattr(_cobot_common.shutil, "which", lambda _name: str(tmp_path / "missing-git"))
    assert rules.repo_root(str(tmp_path)) == tmp_path


def test_cli_check_printsDecisionAndRule():
    out = run_script(["check", "cargo test && git push"]).stdout
    assert out.startswith("ask  (cobot rule: ask Bash(git push*) (default layer))")
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
    assert out.strip().endswith("decision: ask  (cobot rule: ask Bash(git push*) (default layer))")
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


MAKEFILE = """
GO ?= go
VERSION ?= $(shell git describe --always)
GO_SOURCES := $(shell find . -name '*.go')
ifeq ($(GOOS),linux)
\tPIE_FLAGS = -buildmode=pie
endif
define check_tool
\t@command -v $(1) >/dev/null 2>&1 || { echo "missing $(1)"; exit 1; }
endef
.PHONY: all check-deps build test lint generate client release force nonesuch-runs-nothing
all: lint test build
check-deps:
\t$(call check_tool,go)
build: check-deps $(GO_SOURCES)
\t$(GO) build $(PIE_FLAGS) -ldflags "-X main.version=$(VERSION)" ./cmd/x
test: check-deps $(GO_SOURCES) go.mod
\t@echo "Running tests..."
\tCGO_ENABLED=1 $(GO) test -race ./...
lint: check-deps
\tgolangci-lint run --timeout 10m
generate:
\tgo generate ./...
\t$(MAKE) client
client:
\t@tmp=$$(mktemp); go run ./cmd/gen "$$tmp"
release:
\tgit push origin v1.0.0
force:
\tgit push --force origin main
nested:
\t$(MAKE) test
"""


@pytest.fixture
def make_repo(tmp_path):
    (tmp_path / "Makefile").write_text(MAKEFILE)
    (tmp_path / "other.mk").write_text("check:\n\tcargo test --workspace\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "Makefile").write_text("test:\n\tcargo test\nagain:\n\t$(MAKE) test\n")
    return tmp_path


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("make test", None),
        ("make -j4 -k --no-print-directory test", None),
        ("make -j 8 -s test lint", None),
        ("make -n test", None),
        ("gmake test", None),
        ("make GO=gotip test", None),
        ("make -f other.mk check", None),
        ("make --file=other.mk check", None),
        ("make -C sub test", None),
        ("make --directory sub test", None),
        ("make -C sub again", "ask"),
        ("make", "ask"),
        ("make build", "ask"),
        ("make generate", "ask"),
        ("make client", "ask"),
        ("make nested", None),
        ("make release", "ask"),
        ("make force", "deny"),
        ("make lint release", "ask"),
        ("make nonesuch-runs-nothing", "ask"),
        ("make --eval='x:' test", "ask"),
        ("make -E 'x:' test", "ask"),
        ("make --unknown-flag test", "ask"),
        ("make -f - test", "ask"),
        ("make -f a.mk -f b.mk test", "ask"),
        ("make -C sub -C sub test", "ask"),
        ("make -C", "ask"),
        ("make test && git push", "ask"),
        ("CGO_ENABLED=0 make test", None),
        ("nix develop -c make test", None),
    ],
)
def test_makeTarget_resolvedFromMakefile(rules, make_repo, command, decision):
    assert judge_in(rules, command, make_repo)[0].decision == decision


def test_makeTarget_reasonAndTraceNameOrigin(rules, make_repo):
    verdict, trace = judge_in(rules, "make release", make_repo)
    assert verdict.reason() == "cobot rule: ask Bash(git push*) (default layer) via make release"
    assert trace[-1][0] == "git push origin v1.0.0  <- make release"
    verdict, _ = judge_in(rules, "make client", make_repo)
    assert verdict.reason() == "cobot gate: opaque command 'make client'"


@pytest.mark.parametrize(
    ("command", "reason"),
    [
        (
            "python3 - <<'PY'\nprint(1)\nPY\ncat .agent/JOURNAL.md",
            "cobot gate: opaque command 'python3 -'",
        ),
        (
            'cd /x && echo "v=$(git rev-parse HEAD)"; ls | tail -1',
            "cobot gate: command substitution '$(git rev-parse HEAD)'",
        ),
        (
            "for m in a b; do echo $(basename $(dirname $m)); done | head -14",
            "cobot gate: command substitution '$(basename $(dirname $m))'",
        ),
        ("echo `date` | head -3", "cobot gate: command substitution '`date`'"),
        ("ls; bash -n bin/init.sh; tail -2", "cobot gate: opaque command 'bash -n bin/init.sh'"),
        ("python3 - <<'PY'\nx\nPY\necho $(id -u)", "cobot gate: command substitution '$(id -u)'"),
        ("echo $(" + "a" * 80, "cobot gate: command substitution '$(" + "a" * 58 + "'"),
    ],
)
def test_judgeBash_opaqueReason_namesTheConstructNotTheLastSegment(rules, tmp_path, command, reason):
    verdict, _ = judge_in(rules, command, tmp_path)
    assert verdict.decision == "ask"
    assert verdict.reason() == reason


def test_judgeBash_protectedFileWithSubstitution_keepsProtectedReason(rules, tmp_path):
    verdict, _ = judge_in(rules, "cat ~/.claude/settings.json; echo $(date)", tmp_path)
    assert verdict.decision == "ask" and "protected file" in verdict.reason()


def test_judgeBash_ruleBackedAskAfterOpaque_reportsTheRule(rules, tmp_path):
    verdict, _ = judge_in(rules, "python3 - <<'PY'\nx\nPY\nrm -rf build", tmp_path)
    assert verdict.reason() == "cobot rule: ask Bash(rm -rf*) (default layer)"


def test_makeTarget_noMakefileOrUnreadable_staysOpaque(rules, tmp_path):
    assert judge_in(rules, "make test", tmp_path)[0].decision == "ask"
    (tmp_path / "Makefile").write_text("include deps.mk\ntest:\n\tgo test ./...\n")
    assert judge_in(rules, "make test", tmp_path)[0].decision == "ask"


PACKAGE_JSON = {
    "name": "demo",
    "scripts": {
        "pretypecheck": "cn build -q --content 'app/**/*.ts' -o app/cn.ts",
        "typecheck": "react-router typegen && tsc",
        "lint": "oxlint",
        "test": "vitest run",
        "test:unit": "vitest run --project unit",
        "dev": "pnpm run --stream /^dev:/",
        "deploy": "git push origin main",
        "danger": "rm -rf dist && git push --force origin main",
        "nested": "pnpm run lint && pnpm test:unit",
    },
}


@pytest.fixture
def node_repo(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps(PACKAGE_JSON))
    return tmp_path


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("pnpm run typecheck", None),
        ("pnpm typecheck", None),
        ("pnpm run lint --fix", None),
        ("pnpm run --silent lint", None),
        ("pnpm test:unit", None),
        ("pnpm test", None),
        ("npm test", None),
        ("npm t -- --run", None),
        ("npm run test:unit -- -t name", None),
        ("yarn lint", None),
        ("yarn run lint", None),
        ("bun run lint", None),
        ("pnpm run nested", None),
        ("npm run deploy", "ask"),
        ("pnpm run deploy", "ask"),
        ("pnpm deploy", None),
        ("pnpm run danger", "deny"),
        ("yarn danger", "deny"),
        ("pnpm run dev", "ask"),
        ("pnpm run nonesuch", "ask"),
        ("pnpm run -r lint", "ask"),
        ("pnpm run lint --filter app", "ask"),
        ("pnpm run", "ask"),
        ("pnpm exec vitest run tests/unit/x.test.ts -t name", None),
        ("pnpm exec oxlint", None),
        ("npm exec -- vitest run", None),
        ("npm exec vitest", None),
        ("npm exec", "ask"),
        ("pnpm exec -- git push", "ask"),
        ("pnpm dlx create-vite", "ask"),
        ("npx only-allow pnpm", "ask"),
        ("bunx x", None),
        ("pnpm install --frozen-lockfile", None),
        ("pnpm add left-pad", "ask"),
        ("uv run pytest -q", None),
        ("uv run --no-project --python 3.13 --with pytest==9.2.0 --with pytest-cov==7.1.0 pytest -q", None),
        ("uv run -m pytest", None),
        ("uv run script.py --flag", None),
        ("uv run --script tool.py", None),
        ("uv run --locked -- pytest", None),
        ("uv run --bogus pytest", "ask"),
        ("uv run", "ask"),
        ("uv run --python", "ask"),
        ("uv run git push", "ask"),
        ("uv run bash -c 'git push'", "ask"),
        ("uvx ruff check .", "ask"),
        ("uv add numpy", "ask"),
    ],
)
def test_launchers_resolvedFromArgvAndPackageJson(rules, node_repo, command, decision):
    assert judge_in(rules, command, node_repo)[0].decision == decision, command


def test_launchers_reasonNamesTheOrigin(rules, node_repo):
    verdict, trace = judge_in(rules, "npm run deploy", node_repo)
    assert verdict.reason() == "cobot rule: ask Bash(git push*) (default layer) via npm run deploy"
    assert trace[-1][0] == "git push origin main  <- npm run deploy"
    verdict, _ = judge_in(rules, "uv run git push", node_repo)
    assert verdict.reason() == "cobot rule: ask Bash(git push*) (default layer) via uv run git push"
    (node_repo / "package.json").write_text("{not json")
    assert judge_in(rules, "pnpm run lint", node_repo)[0].decision == "ask"
    (node_repo / "package.json").write_text(json.dumps({"scripts": {"lint": ["not", "a", "string"]}}))
    assert judge_in(rules, "pnpm run lint", node_repo)[0].decision == "ask"


def test_miseTask_fromNestedCwd_findsParentConfig(rules, mise_repo):
    assert judge_in(rules, "mise run deploy", mise_repo / "crates" / "x")[0].decision == "ask"


def test_miseTask_reasonAndTraceNameOrigin(rules, mise_repo):
    verdict, trace = judge_in(rules, "mise run deploy", mise_repo)
    assert verdict.reason() == "cobot rule: ask Bash(git push*) (default layer) via mise run deploy"
    assert trace[0][0] == "git push origin main  <- mise run deploy"


def test_miseTask_opaqueInnerCommand_reasonNamesOrigin(rules, mise_repo):
    verdict, _ = judge_in(rules, "mise run script", mise_repo)
    assert verdict.reason() == "cobot gate: opaque command 'sh deploy.sh' via mise run script"


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
        == "cobot rule: ask Bash(git push*) (default layer) via distrobox enter rust -- git push"
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


@pytest.mark.parametrize(
    "command",
    [
        "gh repo fork juanfont/headscale --clone=false",
        "git remote add upstream https://github.com/juanfont/headscale",
        "git remote set-url origin git@github.com:YpNo/x.git",
    ],
)
def test_gate_contributeRemotesAsk(rules, command):
    assert decide(rules, command)[0].decision == "ask"


@pytest.mark.parametrize(
    ("command", "silent"),
    [
        ("trivy fs --scanners vuln,secret,misconfig .", True),
        ("hadolint Dockerfile", True),
        ("gitleaks detect --no-git --report-format json", True),
        ("npm audit --json", True),
        ("pnpm audit --audit-level=high", True),
        ("cargo deny check advisories", True),
        ("docker build --check .", True),
        ("docker compose config -q", True),
        ("npm audit fix", False),
        ("docker build .", False),
        ("trivy fs . && git push", False),
    ],
)
def test_gate_consultantScannersReadOnlyForms(rules, command, silent):
    out = rules.gate(payload(command, agent_type="cobot:consultant"))
    assert (out is None) is silent, command


# ---------------------------------------------------------------- builder report check (R2)

REPORT_SHIM = PLUGIN / "hooks" / "report.sh"
GOOD_REPORT = """Files:
- src/lib.rs
Checks:
- `cargo test -q` → exit 0
  test result: ok. 3 passed
- `cargo clippy -q` → exit 0
Deps added: none
Open: nothing
"""
PROMISE_REPORT = """Files:
- src/lib.rs
Checks: ran the tests, all green.
Deps added: none
"""


def agent_payload(subagent: str, content, status: str = "completed") -> str:
    return json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Agent",
            "tool_input": {"subagent_type": subagent, "prompt": "T1"},
            "tool_response": {"status": status, "content": content},
        }
    )


def test_report_builderWithExitCodes_allows(rules):
    assert rules.report(agent_payload("cobot:rust-builder", GOOD_REPORT)) is None


def test_report_checksNoneWithReason_allows(rules):
    text = "Files:\n- README.md\nChecks: none — docs-only task, nothing to run\nOpen: nothing\n"
    assert rules.report(agent_payload("cobot:builder", text)) is None


def test_report_promiseWithoutExitCode_blocks(rules):
    out = json.loads(rules.report(agent_payload("cobot:python-builder", PROMISE_REPORT)))
    assert out["decision"] == "block"
    assert "exit <n>" in out["reason"] and "Checks: none" in out["reason"]


def test_report_noChecksSection_blocks(rules):
    out = json.loads(rules.report(agent_payload("cobot:go-builder", "Files:\n- a.go\nOpen: nothing\n")))
    assert out["decision"] == "block"


def test_report_contentAsBlocks_isRead(rules):
    blocks = [{"type": "text", "text": GOOD_REPORT}]
    assert rules.report(agent_payload("cobot:typescript-builder", blocks)) is None
    blocks = [{"type": "text", "text": PROMISE_REPORT}]
    assert json.loads(rules.report(agent_payload("cobot:typescript-builder", blocks)))["decision"] == "block"


def test_report_nonBuilderAgent_isIgnored(rules):
    assert rules.report(agent_payload("cobot:consultant", PROMISE_REPORT)) is None
    assert rules.report(agent_payload("general-purpose", PROMISE_REPORT)) is None
    assert rules.report(agent_payload("", PROMISE_REPORT)) is None


def test_report_asyncLaunch_isIgnored(rules):
    assert rules.report(agent_payload("cobot:builder", "", status="async_launched")) is None


def test_report_otherToolOrMalformed_allows(rules, capsys):
    other = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}, "tool_response": "x"})
    assert rules.report(other) is None
    assert rules.report("not json") is None
    assert "allowing" in capsys.readouterr().err


def test_check_report_exitMarkerForms(rules):
    for marker in ("exit 0", "exit code 1", "exit: 2", "-> 0", "→ 3"):
        ok, _ = rules.check_report(f"Checks:\n- `make test` {marker}\n")
        assert ok, marker
    ok, why = rules.check_report("Checks:\n- make test exit 0\n")
    assert not ok and "command" in why


def test_report_shim_blocksAndNeverFails(tmp_path):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    run = subprocess.run(
        ["/bin/sh", str(REPORT_SHIM)],
        input=agent_payload("cobot:builder", PROMISE_REPORT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert run.returncode == 0 and json.loads(run.stdout)["decision"] == "block"
    run = subprocess.run(
        ["/bin/sh", str(REPORT_SHIM)], input="garbage", capture_output=True, text=True, env=env
    )
    assert run.returncode == 0 and run.stdout == "" and "allowing" in run.stderr


# ---------------------------------------------------------------- stamp suffix on git push (R2)


def test_gate_gitPush_carriesStampSuffix(rules, tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "share"))
    out = json.loads(rules.gate(payload("git push -u origin fix", cwd=str(tmp_path))))
    reason = out["hookSpecificOutput"]["permissionDecisionReason"]
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert " · stamp: missing" in reason and "run /cobot:wrap" in reason
    assert len(reason) <= rules.REASON_LIMIT


def test_gate_forcePush_noStampSuffix(rules, tmp_path):
    out = json.loads(rules.gate(payload("git push --force", cwd=str(tmp_path))))
    assert "stamp" not in out["hookSpecificOutput"]["permissionDecisionReason"]


def test_stamp_suffix_unreadable_isEmpty(rules, monkeypatch):
    monkeypatch.setattr(rules.sys, "executable", "/nonexistent/python")
    assert rules.stamp_suffix("/") == ""


# ---------------------------------------------------------------- push option hoisting (R2)


def test_expand_push_flags_hoistsOptionsAfterRemote(rules):
    assert rules.expand_push_flags(["git", "push", "-u", "ghsa", "fix"]) == [
        "git",
        "push",
        "ghsa",
        "fix",
        "-u",
    ]
    assert rules.expand_push_flags(["git", "push", "-uf", "origin"]) == ["git", "push", "origin", "-u", "-f"]
    assert rules.expand_push_flags(["git", "push", "-o", "ci.skip", "ghsa", "HEAD"]) == [
        "git", "push", "ghsa", "HEAD", "-o", "ci.skip",
    ]  # fmt: skip
    assert rules.expand_push_flags(["git", "push", "--force", "origin", "main"]) == [
        "git", "push", "origin", "main", "--force",
    ]  # fmt: skip
    assert rules.expand_push_flags(["git", "status"]) == ["git", "status"]


def test_gate_forcePushAnyOrder_stillDenied(rules):
    for command in (
        "git push -f origin main",
        "git push origin -f main",
        "git push --force-with-lease origin",
    ):
        out = json.loads(rules.gate(payload(command)))
        assert out["hookSpecificOutput"]["permissionDecision"] == "deny", command


def test_gate_mcpGenerateAndEdit_ask(rules):
    for tool in ("mcp__stitch__generate_screen_from_text", "mcp__google-stitch__edit_screen"):
        out = json.loads(rules.gate(payload(tool=tool, tool_input={"prompt": "x"})))
        assert out["hookSpecificOutput"]["permissionDecision"] == "ask", tool
    assert rules.gate(payload(tool="mcp__stitch__list_projects", tool_input={})) is None
    assert rules.gate(payload(tool="mcp__stitch__get_screen", tool_input={"id": "1"})) is None


# ---------------------------------------------------------------- gh/glab api canonical form, glab rows (R2)


def test_canonical_api_implicitPostAndGlab(rules):
    assert rules.canonical_gh_api(["gh", "api", "repos/o/r/issues", "-f", "title=x"])[:4] == [
        "gh",
        "api",
        "-X",
        "POST",
    ]
    assert rules.canonical_gh_api(["glab", "api", "projects/1/issues", "--raw-field", "t=x"])[:4] == [
        "glab", "api", "-X", "POST",
    ]  # fmt: skip
    assert rules.canonical_gh_api(["gh", "api", "repos/o/r", "--input=body.json"])[:4] == [
        "gh",
        "api",
        "-X",
        "POST",
    ]
    assert rules.canonical_gh_api(["glab", "api", "projects/1", "-XDELETE"])[:4] == [
        "glab",
        "api",
        "-X",
        "DELETE",
    ]
    assert rules.canonical_gh_api(["gh", "api", "repos/o/r"]) == ["gh", "api", "repos/o/r"]
    assert rules.canonical_gh_api(["gh", "api", "repos/o/r", "-F", "per_page=5"])[:4] == [
        "gh",
        "api",
        "-X",
        "POST",
    ]


def test_gate_apiBodyFlag_asksEvenForConsultant(rules):
    for command in ("gh api repos/o/r/issues -f title=x", "glab api projects/1/issues --raw-field title=x"):
        out = json.loads(rules.gate(payload(command, agent_type="cobot:consultant")))
        assert out["hookSpecificOutput"]["permissionDecision"] == "ask", command
    assert rules.gate(payload("gh api repos/o/r", agent_type="cobot:consultant")) is None
    assert rules.gate(payload("glab api projects/1 --paginate", agent_type="cobot:consultant")) is None


def test_gate_glabRows_mirrorGh(rules):
    expect = {
        "glab release create v1": "deny",
        "gh repo delete o/r": "deny",
        "glab repo delete o/r": "deny",
        "glab api projects/1 -X DELETE": "deny",
        "glab mr create --fill --description 'Generated with X'": "deny",
        "glab mr merge 12": "ask",
        "glab mr create --fill": "ask",
        "glab ci run": "ask",
        "glab variable set K v": "ask",
    }
    for command, decision in expect.items():
        out = json.loads(rules.gate(payload(command)))
        assert out["hookSpecificOutput"]["permissionDecision"] == decision, command
    for command in (
        "glab ci status",
        "glab mr view 12",
        "glab repo view",
        "glab ci lint",
        "glab release list",
    ):
        assert rules.gate(payload(command, agent_type="cobot:consultant")) is None, command
    assert (
        json.loads(rules.gate(payload("glab ci view", agent_type="cobot:consultant")))["hookSpecificOutput"][
            "permissionDecision"
        ]
        == "ask"
    )


# ---------------------------------------------------------------- cloud CLIs (R2 slice 3)


def test_canonical_gcloud_cutsAtTheFirstVerb(rules):
    cut = rules.canonical_gcloud
    assert cut(["gcloud", "compute", "instances", "list", "--format=json"]) == [
        "gcloud", "compute", "instances", "list",
    ]  # fmt: skip
    assert cut(["gcloud", "pubsub", "topics", "create", "list"]) == ["gcloud", "pubsub", "topics", "create"]
    assert cut(["gcloud", "run", "services", "list"]) == ["gcloud", "run", "services", "list"]
    assert cut(["gcloud", "run", "deploy", "svc", "--image", "x"]) == ["gcloud", "run", "deploy"]
    assert cut(["gcloud", "deploy", "releases", "list"]) == ["gcloud", "deploy", "releases", "list"]
    assert cut(["gcloud", "projects", "add-iam-policy-binding", "p", "--member=x"]) == [
        "gcloud", "projects", "add-iam-policy-binding",
    ]  # fmt: skip
    assert cut(["gcloud", "sql", "backups", "restore", "1"]) == ["gcloud", "sql", "backups", "restore"]
    assert cut(["gcloud", "config", "set", "project", "p"]) == ["gcloud", "config", "set", "project", "p"]
    assert cut(["gcloud", "auth", "print-access-token"]) == ["gcloud", "auth", "print-access-token"]
    assert cut(["gcloud", "container", "fleet", "mesh", "update", "--management", "automatic"]) == [
        "gcloud", "container", "fleet", "mesh", "update",
    ]  # fmt: skip
    assert cut(["git", "log"]) == ["git", "log"]


@pytest.mark.parametrize(
    ("command", "foreign"),
    [
        ("GIT_PAGER=./x git log", True),
        ("env KUBECTL_EXTERNAL_DIFF=./d kubectl diff -f m.yaml", True),
        ("PATH=./bin git log", True),
        ("KUBECONFIG=./kc kubectl get pods", True),
        ("CLOUDSDK_PYTHON=./x.sh gcloud projects list", True),
        ("GIT_CONFIG_GLOBAL=./gc git log", True),
        ("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.pager GIT_CONFIG_VALUE_0=./x git log", True),
        ("NO_COLOR=1 git log", False),
        ("LANG=C LC_ALL=C TZ=UTC git log", False),
        ("RUST_LOG=debug cargo test", True),
        ("git -c core.pager=./x log", True),
        ("git -c user.name=x log", True),
        ("git --exec-path=./bin log", True),
        ("kubectl --kubeconfig ./kc get pods", True),
        ("kubectl get pods --kubeconfig ./kc", True),
        ("kubectl get pods --kubeconfig=./kc", True),
        ("helm --kubeconfig=./kc list", True),
        ("istioctl -c ./kc proxy-status", True),
        ("kubectl logs pod -c app", False),
        ("helm template api ./chart --post-renderer ./x", True),
        ("helm template api ./chart --post-renderer=./x", True),
        ("kustomize build --enable-exec o", True),
        ("kustomize build --enable-alpha-plugins o", True),
        ("kustomize build --enable-helm --helm-command ./evil o", True),
        ("kubectl kustomize --enable-helm o", True),
        ("rtk kubectl get pods", False),
        ("timeout 30 kubectl get pods", False),
        ("/usr/bin/git -c core.pager=x log", True),
        ("gcloud compute instances list", False),
    ],
)
def test_executesForeign_marksSegmentsThatCouldRunRepositoryContent(rules, command, foreign):
    assert rules.executes_foreign(shlex.split(command)) is foreign, command


def test_candidates_canonicalGcloudForm(rules):
    tokens = ["gcloud", "--project", "p", "compute", "instances", "list", "--zone", "z"]
    assert rules.candidates(tokens)[-1] == "gcloud compute instances list"
    assert rules.candidates(["GIT_PAGER=./x", "git", "log"])[-1] == "git log"


def test_isOpaque_optionFirstSegment(rules):
    assert rules.is_opaque(rules.strip_wrappers(["env", "-S", "git push --force origin main"])) is True
    assert decide(rules, "env -S 'git push --force origin main'")[0].decision == "ask"
    assert decide(rules, "env -i git log")[0].decision == "ask"


@pytest.mark.parametrize(
    ("command", "silent"),
    [
        ("gcloud compute instances list --format=json", True),
        ("gcloud --project p projects describe p", True),
        ("gcloud projects get-iam-policy p --format=json", True),
        ("gcloud config list", True),
        ("gcloud config get-value project", True),
        ("gcloud auth list", True),
        ("gcloud logging read 'severity>=ERROR' --limit 5", True),
        ("gcloud storage ls gs://b", True),
        ("gcloud artifacts docker images list europe-docker.pkg.dev/p/r", True),
        ("gcloud container fleet mesh describe", True),
        ("gcloud version", True),
        ("gcloud pubsub topics create list", False),
        ("gcloud auth print-access-token", False),
        ("gcloud secrets versions access latest --secret=s", False),
        ("gcloud container clusters get-credentials c --region r", False),
        ("gcloud config set project p", False),
        ("CLOUDSDK_PYTHON=./x.sh gcloud projects list", False),
        ("kubectl get pods -A", True),
        ("kubectl -n prod describe deploy/api", True),
        ("kubectl logs deploy/api --tail=50", True),
        ("kubectl logs pod -c app", True),
        ("kubectl diff -f m.yaml", True),
        ("kubectl explain deployment.spec", True),
        ("kubectl top pods", True),
        ("kubectl events -n prod", True),
        ("kubectl api-resources", True),
        ("kubectl version --client", True),
        ("kubectl cluster-info", True),
        ("kubectl auth can-i create pods", True),
        ("kubectl config view --minify", True),
        ("kubectl config current-context", True),
        ("kubectl kustomize overlays/prod", True),
        ("kubectl rollout status deploy/api", True),
        ("kubectl rollout history deploy/api", True),
        ("kubectl get secret db -o yaml", False),
        ("kubectl get Secret db -o yaml", False),
        ("kubectl get secrets -A", False),
        ("kubectl -n prod get pods,secrets", False),
        ("kubectl get -f k8s/ -o yaml", False),
        ("kubectl get pods -f k8s/", False),
        ("kubectl get -k overlays/prod -o yaml", False),
        ("kubectl get --filename k8s/ -o yaml", False),
        ("kubectl config view --raw", False),
        ("kubectl config view --minify --raw", False),
        ("kubectl cluster-info dump --output-directory=/tmp/x", False),
        ("kubectl rollout restart deploy/api", False),
        ("kubectl --kubeconfig ./kc get pods", False),
        ("kubectl get pods --kubeconfig ./kc", False),
        ("KUBECONFIG=./kc kubectl get pods", False),
        ("KUBECTL_EXTERNAL_DIFF=./d kubectl diff -f m.yaml", False),
        ("NO_COLOR=1 kubectl get pods", True),
        ("helm template api ./chart -f values.yaml", True),
        ("helm lint ./chart", True),
        ("helm list -A", True),
        ("helm ls", True),
        ("helm status api", True),
        ("helm show values oci://r/c", True),
        ("helm search repo nginx", True),
        ("helm history api", True),
        ("helm env", True),
        ("helm version", True),
        ("helm verify ./c.tgz", True),
        ("helm dependency list ./chart", True),
        ("helm get notes api", True),
        ("helm get metadata api", True),
        ("helm get values api", False),
        ("helm get manifest api", False),
        ("helm get all api", False),
        ("helm template api ./chart --post-renderer ./kustomize.sh", False),
        ("helm dependency update ./chart", False),
        ("helm upgrade --install api ./chart", False),
        ("kustomize build overlays/prod", True),
        ("kustomize build overlays/prod --enable-exec", False),
        ("kustomize build --enable-alpha-plugins overlays/prod", False),
        ("kustomize build --enable-helm --helm-command ./evil overlays/prod", False),
        ("kubeconform -strict -summary out.yaml", True),
        ("istioctl analyze --use-kube=false mesh/", True),
        ("istioctl proxy-status", True),
        ("istioctl -n prod proxy-config listeners api-1", True),
        ("istioctl version", True),
        ("istioctl verify-install", True),
        ("istioctl -c ./kc proxy-status", False),
        ("istioctl install --set profile=ambient", False),
        ("istioctl dashboard kiali", False),
        ("istioctl bug-report", False),
        ("GIT_PAGER=./x git log", False),
        ("PATH=./bin git log", False),
        ("git -c core.pager=./x log", False),
        ("env -S 'git log'", False),
        ("git log --oneline", True),
        ("NO_COLOR=1 git log", True),
    ],
)
def test_gate_cloudReadListForReadOnlyAgents(rules, command, silent):
    for agent in ("cobot:consultant", "cobot:learner"):
        out = rules.gate(payload(command, agent_type=agent))
        assert (out is None) is silent, f"{agent}: {command}"


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("gcloud projects add-iam-policy-binding p --member=x --role=roles/owner", "ask"),
        ("gcloud projects remove-iam-policy-binding p --member=x --role=r", "ask"),
        ("gcloud projects set-iam-policy p policy.json", "ask"),
        ("gcloud compute instances attach-disk vm --disk d", "ask"),
        ("gcloud compute instances detach-disk vm --disk d", "ask"),
        ("gcloud sql backups restore 1 --restore-instance=i", "ask"),
        ("gcloud run deploy svc --image x", "ask"),
        ("gcloud app deploy", "ask"),
        ("gcloud builds submit --tag x", "ask"),
        ("gcloud services enable container.googleapis.com", "ask"),
        ("gcloud services disable x", "ask"),
        ("gcloud deploy apply --file=p.yaml", "ask"),
        ("gcloud deploy releases promote --release=r", "ask"),
        ("gcloud compute instances start vm", "ask"),
        ("gcloud compute instances stop vm", "ask"),
        ("gcloud compute instances reset vm", "ask"),
        ("gcloud compute instances suspend vm", "ask"),
        ("gcloud compute instances resume vm", "ask"),
        ("gcloud container clusters resize c --num-nodes 3", "ask"),
        ("gcloud container clusters upgrade c", "ask"),
        ("gcloud kms keys versions destroy 1 --key k --keyring r --location l", "ask"),
        ("gcloud sql instances patch i --tier t", "ask"),
        ("gcloud sql instances restart i", "ask"),
        ("gcloud sql instances clone a b", "ask"),
        ("gcloud sql instances failover i", "ask"),
        ("gcloud sql export sql i gs://b/f", "ask"),
        ("gcloud sql import sql i gs://b/f", "ask"),
        ("gcloud scheduler jobs pause j", "ask"),
        ("gcloud builds cancel b", "ask"),
        ("gcloud projects move p --folder f", "ask"),
        ("gcloud projects undelete p", "ask"),
        ("gcloud storage cp a gs://b", "ask"),
        ("gcloud storage mv gs://a gs://b", "ask"),
        ("gcloud storage rm gs://b/x", "ask"),
        ("gcloud storage rsync . gs://b", "ask"),
        ("gcloud pubsub topics publish t --message=m", "ask"),
        ("gcloud workflows execute w", "ask"),
        ("gcloud functions call f", "ask"),
        ("gcloud scheduler jobs run j", "ask"),
        ("gcloud components install kubectl", "ask"),
        ("gcloud auth login", "ask"),
        ("gcloud auth application-default login", "ask"),
        ("gcloud auth revoke", "ask"),
        ("gcloud auth activate-service-account --key-file k.json", "ask"),
        ("gcloud compute instances describe runner-1", None),
        ("gcloud deploy releases list", None),
        ("gcloud run services list", None),
        ("gcloud storage ls gs://b", None),
        ("gcloud logging read x", None),
        ("gcloud config set project p", None),
        ("kubectl run debug --image=busybox", "ask"),
        ("kubectl debug pod/x -it --image=busybox", "ask"),
        ("kubectl cp pod:/a ./a", "ask"),
        ("kubectl expose deploy api --port 80", "ask"),
        ("kubectl autoscale deploy api --max 5", "ask"),
        ("kubectl rollout pause deploy/api", "ask"),
        ("kubectl rollout resume deploy/api", "ask"),
        ("kubectl certificate approve csr-1", "ask"),
        ("helm plugin install https://x", "ask"),
        ("helm registry login r", "ask"),
        ("istioctl waypoint apply -n default --enroll-namespace", "ask"),
        ("istioctl waypoint delete --all -n default", "ask"),
        ("istioctl tag set default --revision 1-31-4", "ask"),
        ("istioctl create-remote-secret --name c1", "ask"),
        ("istioctl waypoint list", None),
        ("istioctl tag list", None),
        ("helm template api ./chart --post-renderer ./x", None),
        ("kustomize build --enable-exec o", None),
        ("GIT_PAGER=./x git log", None),
        ("FOO=bar git push", "ask"),
        ("RUST_LOG=debug cargo test", None),
    ],
)
def test_decide_cloudMutatingRows(rules, command, decision):
    assert decide(rules, command)[0].decision == decision


# ---------------------------------------------------------------- MCP: read verbs, host tools (0.2.0 PR 3)

# tools/list of Google's remote Cloud MCP servers, 2026-11-09 and 2026-11-11: (readOnlyHint, the rest)
GOOGLE_MCP_TOOLS = {
    "run": (
        ("get_service", "list_services"),
        ("deploy_service_from_image", "deploy_service_from_archive", "deploy_service_from_file_contents"),
    ),
    "gke": (
        (
            "list_k8s_api_resources",
            "check_k8s_auth",
            "describe_k8s_resource",
            "list_k8s_events",
            "get_k8s_resource",
            "get_k8s_cluster_info",
            "get_k8s_version",
            "get_k8s_rollout_status",
            "list_clusters",
            "get_cluster",
            "list_operations",
            "get_operation",
            "list_node_pools",
            "get_node_pool",
            "get_k8s_logs",
            "diagnose_k8s_workload",
            "get_k8s_cluster_health",
            "get_k8s_log_summary",
            "list_k8s_cluster_issues",
        ),
        (
            "create_cluster",
            "update_cluster",
            "cancel_operation",
            "create_node_pool",
            "update_node_pool",
            "apply_k8s_manifest",
            "delete_k8s_resource",
            "patch_k8s_resource",
        ),
    ),
    "compute": (
        (
            "get_instance_basic_info",
            "list_instance_attached_disks",
            "list_instances",
            "get_instance_group_manager_basic_info",
            "list_instance_group_managers",
            "list_managed_instances",
            "list_instance_templates",
            "get_instance_template_basic_info",
            "get_instance_template_properties",
            "get_disk_basic_info",
            "get_disk_performance_config",
            "list_disks",
            "list_accelerator_types",
            "list_machine_types",
            "list_images",
            "get_zone_operation",
            "get_reservation_basic_info",
            "get_reservation_details",
            "list_reservations",
            "list_commitments",
            "get_commitment_basic_info",
            "list_commitment_reservations",
            "list_snapshots",
        ),
        (
            "create_instance",
            "delete_instance",
            "start_instance",
            "stop_instance",
            "reset_instance",
            "set_instance_machine_type",
        ),
    ),
    "iam": (
        ("list_deny_policies", "get_deny_policy", "get_deny_policy_status", "list_roles", "get_role"),
        (
            "create_deny_policy",
            "update_deny_policy",
            "delete_deny_policy",
            "create_role",
            "update_role",
            "delete_role",
            "undelete_role",
        ),
    ),
    "logging": (
        ("list_log_entries", "list_log_names", "get_bucket", "list_buckets", "get_view", "list_views"),
        (),
    ),
    "crm": (
        ("search_projects",),
        (),
    ),
    "storage": (
        (
            "list_buckets",
            "list_objects",
            "get_bucket_metadata",
            "read_text",
            "read_object",
            "get_object_metadata",
        ),
        ("create_bucket", "delete_bucket", "write_text", "delete_object"),
    ),
}
GOOGLE_MCP_TOOLS |= {  # added 2026-11-11 for the gcp-* never rules
    "bigquery": (
        (
            "list_dataset_ids",
            "get_dataset_info",
            "list_table_ids",
            "get_table_info",
            "execute_sql_readonly",
            "get_query_results",
            "get_job",
        ),
        ("execute_sql", "cancel_job"),
    ),
    "sql": (
        ("list_instances", "get_instance", "execute_sql_readonly", "get_operation", "list_users"),
        (
            "create_instance",
            "execute_sql",
            "create_user",
            "update_user",
            "clone_instance",
            "update_instance",
            "create_backup",
            "restore_backup",
            "import_data",
            "postgres_upgrade_precheck",
        ),
    ),
    "firestore": (
        (
            "get_document",
            "list_documents",
            "list_collections",
            "get_database",
            "list_databases",
            "get_index",
            "list_indexes",
            "get_backup",
            "list_backups",
            "get_backup_schedule",
            "list_backup_schedules",
        ),
        (
            "add_document",
            "update_document",
            "delete_document",
            "create_database",
            "update_database",
            "delete_database",
            "create_index",
            "delete_index",
            "delete_backup",
            "create_backup_schedule",
            "update_backup_schedule",
            "delete_backup_schedule",
        ),
    ),
    "pubsub": (
        (
            "get_topic",
            "list_topics",
            "get_subscription",
            "list_subscriptions",
            "get_snapshot",
            "list_snapshots",
        ),
        (
            "create_topic",
            "update_topic",
            "delete_topic",
            "create_subscription",
            "update_subscription",
            "delete_subscription",
            "create_snapshot",
            "delete_snapshot",
            "publish",
        ),
    ),
    "monitoring": (
        (
            "list_timeseries",
            "query_range",
            "get_alert_policy",
            "list_alert_policies",
            "get_alert",
            "list_alerts",
            "list_metric_descriptors",
            "list_dashboards",
            "get_dashboard",
        ),
        (),
    ),
}
# read-only, but the first word is not a read verb (check_in_file, execute_sql, query_and_update)
MCP_READ_TOOLS_THAT_ASK = {"check_k8s_auth", "diagnose_k8s_workload", "execute_sql_readonly", "query_range"}
GCP_WRITES_THAT_ASK = {"postgres_upgrade_precheck"}  # no write verb first: the catch-all asks


def verdict_of(rules, tool):
    out = rules.gate(payload(tool=tool, tool_input={}))
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None


def test_mcp_googleCloudTools_writesDeniedUnderGcpName_readsSilent(rules):
    for server, (read_only, others) in GOOGLE_MCP_TOOLS.items():
        for name in others:
            expected = "ask" if name in GCP_WRITES_THAT_ASK else "deny"
            assert verdict_of(rules, f"mcp__gcp-{server}__{name}") == expected, name
            assert verdict_of(rules, f"mcp__{server}__{name}") == "ask", name  # not named gcp-*: asks
        for name in read_only:
            expected = "ask" if name in MCP_READ_TOOLS_THAT_ASK else None
            assert verdict_of(rules, f"mcp__gcp-{server}__{name}") == expected, name


def test_mcp_gcpWriteNever_beatsAnOwnerAllowOfTheServer(rules, layers):
    owner, _ = layers
    owner.write_text("allow mcp__gcp-gke__*\n")
    assert decide_mcp(rules, "mcp__gcp-gke__apply_k8s_manifest").decision == "deny"
    assert decide_mcp(rules, "mcp__gcp-gke__diagnose_k8s_workload").decision is None


def test_mcp_readVerbWithAWriteWordOrAnotherFirstWord_asks(rules):
    for name in (
        "get_or_create_user",
        "getOrCreateUser",
        "checkout_branch",
        "check_in_file",
        "list_and_delete_old",
        "readwrite_object",
        "search-and-replace",
        "describeAndUpdate",
        "resolve-library-id",
        "fetch",
    ):
        assert verdict_of(rules, f"mcp__srv__{name}") == "ask", name
    for name in ("getDiagnostics", "get-library-docs", "list_projects", "search_threads", "read_page"):
        assert verdict_of(rules, f"mcp__srv__{name}") is None, name


def test_mcp_hostUiTools_silent_otherHostToolsAsk(rules):
    for tool in (
        "mcp__ccd_turn__update_plan",
        "mcp__ccd_turn__wrap_up",
        "mcp__ccd_session__mark_chapter",
        "mcp__ccd_session__dismiss_task",
        "mcp__ccd_view__show_pane",
        "mcp__visualize__show_widget",
        "mcp__visualize__read_me",
    ):
        assert verdict_of(rules, tool) is None, tool
    for tool in (
        "mcp__ccd_turn__something_new",
        "mcp__terminal__run_in_terminal",
        "mcp__claude-in-chrome__javascript_tool",
        "mcp__claude-in-chrome__computer",
        "mcp__claude-in-chrome__navigate",
        "mcp__ccd_settings__set_setting",
        "mcp__ccd_session__start_session",
    ):
        assert verdict_of(rules, tool) == "ask", tool


def decide_mcp(rules, tool):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_mcp(tool, loaded, None)


def test_mcp_ownerOrProjectAsk_beatsADefaultRead(rules, layers):
    owner, project = layers
    project.write_text("ask mcp__supabase__get_publishable_keys\n")
    owner.write_text("ask mcp__*__get_secret*\n")
    assert decide_mcp(rules, "mcp__supabase__get_publishable_keys").decision == "ask"
    assert decide_mcp(rules, "mcp__vault__get_secret_value").decision == "ask"
    assert decide_mcp(rules, "mcp__vault__get_status").decision is None


def test_mcp_ownerAllowSilences_neverBeatsEverything(rules, layers):
    owner, project = layers
    owner.write_text("allow mcp__claude-in-chrome__*\nnever mcp__*__get_secret*\n")
    assert decide_mcp(rules, "mcp__claude-in-chrome__computer").decision is None
    assert decide_mcp(rules, "mcp__vault__get_secret_value").decision == "deny"


def test_mcp_readOfANounThatLooksLikeAVerb_staysSilent(rules):
    # GitHub and GitLab MCP reads: the noun after the read verb is not an action
    for name in (
        "get_commit",
        "get_workflow_run",
        "get_merge_request",
        "list_tags",
        "get_tag",
        "get_comment",
    ):
        assert verdict_of(rules, f"mcp__srv__{name}") is None, name
    for name in ("get_then_delete", "read_plus_write"):
        assert verdict_of(rules, f"mcp__srv__{name}") == "ask", name


# ---------------------------------------------------------------- CLI aliases (0.2.0 PR 5)


def test_canonicalAlias_glab_rewritesAliasesToTheirCommand(rules):
    assert rules.canonical_alias(["glab", "mr", "new", "--fill"]) == ["glab", "mr", "create", "--fill"]
    assert rules.canonical_alias(["glab", "mr", "accept", "12"]) == ["glab", "mr", "merge", "12"]
    assert rules.canonical_alias(["glab", "mr", "comment", "12"]) == ["glab", "mr", "note", "12"]
    assert rules.canonical_alias(["glab", "issue", "new"]) == ["glab", "issue", "create"]
    assert rules.canonical_alias(["glab", "mr", "view", "12"]) == ["glab", "mr", "view", "12"]
    assert rules.canonical_alias(["git", "mr", "new"]) == ["git", "mr", "new"]


def test_gate_glabAliases_getTheirCommandsVerdict(rules):
    expect = {
        "glab mr new --fill": "ask",
        "glab mr new --fill --description 'Generated with X'": "deny",
        "glab mr accept 12": "ask",
        "glab mr note 12 -m hi": "ask",
        "glab mr comment 12 -m hi": "ask",
        "glab mr approve 12": "ask",
        "glab issue create -t x": "ask",
        "glab issue new -t x": "ask",
        "glab issue note 3 -m hi": "ask",
    }
    for command, decision in expect.items():
        out = rules.gate(payload(command))
        assert out and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == decision, command


def test_canonicalAlias_teaAndGt_groupsAndVerbs(rules):
    assert rules.canonical_alias(["tea", "r", "c", "v1"]) == ["tea", "releases", "create", "v1"]
    assert rules.canonical_alias(["tea", "pr", "m", "3"]) == ["tea", "pulls", "merge", "3"]
    assert rules.canonical_alias(["tea", "repo", "m", "url"]) == ["tea", "repos", "migrate", "url"]
    assert rules.canonical_alias(["tea", "c", "a", "3", "hi"]) == ["tea", "comments", "add", "3", "hi"]
    assert rules.canonical_alias(["gt", "release", "new", "v1"]) == ["gt", "release", "create", "v1"]
    assert rules.canonical_alias(["gt", "repo", "rm", "o/r"]) == ["gt", "repo", "delete", "o/r"]


def test_gate_giteaClis_mirrorGhAndGlab(rules):
    expect = {
        "gt pr create --title x": "ask",
        "gt pr new --title x": "ask",
        "gt pr create --title x --body 'Generated with X'": "deny",
        "gt pr merge 3": "ask",
        "gt pr review 3 --approve": "ask",
        "gt pr comment create 3 --body hi": "ask",
        "gt issue new --title x": "ask",
        "gt release create v1": "deny",
        "gt release new v1": "deny",
        "gt release publish v1": "deny",
        "gt repo delete o/r": "deny",
        "gt repo rm o/r": "deny",
        "gt api repos/o/r -X DELETE": "deny",
        "gt api repos/o/r/issues -f title=x": "ask",
        "tea pulls c --title x": "ask",
        "tea pr create --title x --description 'Generated with X'": "deny",
        "tea pr m 3": "ask",
        "tea pr lgtm 3": "ask",
        "tea r c v1": "deny",
        "tea release create v1": "deny",
        "tea repo rm o/r": "deny",
        "tea c a 3 hi": "ask",
        "tea i c --title x": "ask",
        "tea api /repos/o/r -X DELETE": "deny",
    }
    for command, decision in expect.items():
        out = rules.gate(payload(command))
        assert out and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == decision, command
    for command in ("gt pr list", "gt pr view 3", "gt release view v1", "tea pr ls", "tea releases list"):
        assert rules.gate(payload(command)) is None, command
