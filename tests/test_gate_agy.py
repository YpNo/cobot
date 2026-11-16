"""The gate under the Antigravity CLI (spec antigravity, story 3): `cobot-rules gate --runtime agy`
maps agy's tool calls onto the rules, answers allow (no opinion), force_ask or deny, and its shim
answers deny on every failure, since agy ignores a hook's exit code."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest
from conftest import PLUGIN

SHIM = PLUGIN / "hooks" / "gate-agy.sh"
DECISIONS = {"allow", "force_ask", "deny"}
CORPUS: list[str] = []  # every answer of this module, for the auto_approve scan


@pytest.fixture(autouse=True)
def agy_home(tmp_path, monkeypatch):
    """No project override (the project comes from workspacePaths) and a HOME of its own, whose
    ~/.gemini holds the MCP configuration a test writes."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    home = tmp_path / "home"
    (home / ".gemini" / "config").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def workspace(tmp_path):
    """A workspace folder (not a git repository) with an empty project rules layer."""
    folder = tmp_path / "ws"
    (folder / ".agent").mkdir(parents=True)
    (folder / ".agent" / "cobot.rules").write_text("")
    return folder


def payload(name, args=None, workspaces=(), cwd=None) -> str:
    call = {"id": "t1", "name": name, "args": args or {}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(w) for w in workspaces]}
    if cwd:
        body["cwd"] = str(cwd)
    return json.dumps(body)


def answer(rules, stdin: str) -> dict:
    out = rules.gate_agy(stdin)
    CORPUS.append(out)
    data = json.loads(out)
    assert data["decision"] in DECISIONS, out
    return data


def decide(rules, name, args=None, workspaces=(), cwd=None) -> str:
    return answer(rules, payload(name, args, workspaces, cwd))["decision"]


# ---------------------------------------------------------------- run_command and manage_task


@pytest.mark.parametrize(
    "command, expected", [("git push --force", "deny"), ("git push", "force_ask"), ("git status", "allow")]
)
def test_runCommand_judgedAsBash_verdictsMapped(rules, workspace, command, expected):
    assert decide(rules, "run_command", {"CommandLine": command}, [workspace]) == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        ("gh release -R o/r create v1", "deny"),
        ("gh release new v1", "deny"),
        ("gh pr new --fill", "force_ask"),
        ("fd -x git push --force", "deny"),
        ("watch git push", "force_ask"),
        ("gh pr -R o/r list", "allow"),
        ("gh release --title x create v1", "deny"),
        ("find . -exec true \\; -exec git push --force \\;", "deny"),
        ("fd -Hx git push --force", "deny"),
        ("pkexec git push", "force_ask"),
        ("gh my-extension", "force_ask"),
    ],
)
def test_runCommand_rowsReachTheirCommand_inBothRuntimes(rules, workspace, command, expected):
    # spec gate-f36-f40-f44, story 0: -R after the group, gh aliases, fd and watch runners
    assert decide(rules, "run_command", {"CommandLine": command}, [workspace]) == expected


def test_runCommand_denyNamesTheRule(rules, workspace):
    data = answer(rules, payload("run_command", {"CommandLine": "git push -f"}, [workspace]))
    assert data["reason"].startswith("cobot rule: never Bash(")


def test_runCommand_withoutCommandLine_forceAsks(rules, workspace):
    assert decide(rules, "run_command", {"Cwd": str(workspace)}, [workspace]) == "force_ask"


def test_projectNever_appliesWhateverCwdSays(rules, workspace, tmp_path):
    (workspace / ".agent" / "cobot.rules").write_text("never Bash(make deploy*)\n")
    args = {"CommandLine": "make deploy", "Cwd": str(tmp_path)}
    assert decide(rules, "run_command", args, [workspace], cwd=tmp_path) == "deny"


def test_projectNever_ofEveryWorkspacePathApplies(rules, workspace, tmp_path):
    other = tmp_path / "other"
    (other / ".agent").mkdir(parents=True)
    (other / ".agent" / "cobot.rules").write_text("never Bash(terraform destroy*)\n")
    args = {"CommandLine": "terraform destroy"}
    assert decide(rules, "run_command", args, [workspace, other]) == "deny"


def test_noWorkspacePaths_callNeedingTheProject_forceAsks(rules):
    data = answer(rules, payload("run_command", {"CommandLine": "git status"}))
    assert data["decision"] == "force_ask" and "workspacePaths" in data["reason"]
    assert decide(rules, "view_file", {"AbsolutePath": "/etc/hosts"}) == "allow"


def test_cwdArgument_drivesTheMakefileExpansion(rules, workspace, tmp_path):
    folder = tmp_path / "app"
    folder.mkdir()
    (folder / "Makefile").write_text("deploy:\n\tgit push --force\n")
    assert (
        decide(rules, "run_command", {"CommandLine": "make deploy", "Cwd": str(folder)}, [workspace])
        == "deny"
    )
    assert decide(rules, "run_command", {"CommandLine": "make deploy"}, [workspace], cwd=folder) == "deny"


@pytest.mark.parametrize("action", ["list", "status", "kill"])
def test_manageTask_readOrKill_allows(rules, action):
    assert decide(rules, "manage_task", {"Action": action, "TaskId": "7"}) == "allow"


def test_manageTask_sendInput_neverBelowForceAsk(rules, workspace):
    send = {"Action": "send_input", "TaskId": "7"}
    assert decide(rules, "manage_task", {**send, "Input": "ls"}, [workspace]) == "force_ask"
    assert decide(rules, "manage_task", {**send, "Input": "git push --force"}, [workspace]) == "deny"
    assert decide(rules, "manage_task", {"Action": "restart"}, [workspace]) == "force_ask"


# ---------------------------------------------------------------- file tools


@pytest.fixture
def protected(workspace):
    (workspace / ".agent" / "cobot.rules").write_text("never Edit(*/vault/*)\nnever Write(*/vault/*)\n")
    vault = workspace / "vault"
    vault.mkdir()
    (vault / "key.txt").write_text("k")
    return vault


@pytest.mark.parametrize(
    "tool, key",
    [
        ("write_to_file", "TargetFile"),
        ("replace_file_content", "TargetFile"),
        ("multi_replace_file_content", "TargetFile"),
        ("write_file", "Path"),
        ("edit_file", "Path"),
    ],
)
def test_fileTools_bothFamilies_judgedByTheirPath(rules, workspace, protected, tool, key):
    assert decide(rules, tool, {key: str(protected / "key.txt")}, [workspace]) == "deny"
    assert decide(rules, tool, {key: str(workspace / "notes.txt")}, [workspace]) == "allow"


def test_fileTools_relativeOrMissingPath_forceAsks(rules, workspace):
    assert decide(rules, "write_file", {"Path": "notes.txt"}, [workspace]) == "force_ask"
    assert decide(rules, "write_to_file", {"CodeContent": "x"}, [workspace]) == "force_ask"


def test_fileTools_symlinkedParentOrFile_resolvedBeforeTheRules(rules, workspace, protected):
    (workspace / "door").symlink_to(protected)
    (workspace / "alias.txt").symlink_to(protected / "key.txt")
    assert decide(rules, "write_file", {"Path": str(workspace / "door" / "key.txt")}, [workspace]) == "deny"
    assert decide(rules, "edit_file", {"Path": str(workspace / "alias.txt")}, [workspace]) == "deny"


def test_fileTools_symlinkedHome_stillMatchesATildeRule(rules, workspace, tmp_path, monkeypatch):
    # ~ in a rule expands to HOME as given; the resolved path alone would miss it
    owner = tmp_path / "owner.rules"
    owner.write_text("never Write(~/vault.txt)\n")  # no relative twin that could match instead
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    real = tmp_path / "real-home"
    real.mkdir()
    link = tmp_path / "home-link"
    link.symlink_to(real)
    monkeypatch.setenv("HOME", str(link))
    assert decide(rules, "write_file", {"Path": str(link / "vault.txt")}, [workspace]) == "deny"


# ---------------------------------------------------------------- tools decided by name


@pytest.mark.parametrize(
    "tool",
    ["view_file", "read_file", "list_dir", "find_by_name", "grep_search", "read_url_content", "search_web"]
    + ["view_code_item", "ask_question", "send_message", "list_permissions", "ask_permission", "finish"]
    + ["skill_search"],
)
def test_readAndOrchestrationTools_haveNoOpinion(rules, tool):
    assert decide(rules, tool, {"x": "y"}) == "allow"


def test_schedule_withoutATimerCondition_only(rules):
    assert decide(rules, "schedule", {"Prompt": "p", "DurationSeconds": 60}) == "allow"
    assert decide(rules, "schedule", {"Prompt": "p", "TimerCondition": "test -f x"}) == "force_ask"


@pytest.mark.parametrize("action, expected", [("list", "allow"), ("kill", "allow"), ("kill_all", "allow")])
def test_manageSubagents_exactActions(rules, action, expected):
    assert decide(rules, "manage_subagents", {"Action": action}) == expected
    assert decide(rules, "manage_subagents", {"Action": "spawn"}) == "force_ask"


def test_defineSubagent_denies(rules):
    assert decide(rules, "define_subagent", {"Name": "x", "SystemPrompt": "y"}) == "deny"


def test_unknownTool_forceAsks(rules, workspace):
    assert decide(rules, "teleport", {}, [workspace]) == "force_ask"


def test_runWorkflow_forceAsks_namingTheScriptHash(rules, workspace, tmp_path):
    script = tmp_path / "wf.py"
    script.write_text("print('x')\n")
    data = answer(rules, payload("run_workflow", {"ScriptPath": str(script)}, [workspace]))
    assert data["decision"] == "force_ask"
    assert hashlib.sha256(b"print('x')\n").hexdigest()[:16] in data["reason"]
    assert "workflow agents not proven gated" in data["reason"]
    inline = answer(rules, payload("run_workflow", {"Script": "pass"}, [workspace]))
    assert inline["decision"] == "force_ask" and hashlib.sha256(b"pass").hexdigest()[:16] in inline["reason"]


# ---------------------------------------------------------------- invoke_subagent


@pytest.fixture
def git_workspace(workspace):
    git = ["git", "-C", str(workspace), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git[:3], "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
    return workspace


@pytest.mark.parametrize("mode", [None, "inherit"])
def test_invokeSubagent_inheritedWorkspace_allows(rules, workspace, mode):
    args = {"TypeName": "builder", "Prompt": "p"} | ({"Workspace": mode} if mode else {})
    assert decide(rules, "invoke_subagent", args, [workspace]) == "allow"


def test_invokeSubagent_branchOrShare_onlyWhileTheRulesAreCommitted(rules, git_workspace):
    flat = {"TypeName": "builder", "Prompt": "p", "Workspace": "branch"}
    many = {"Subagents": [{"TypeName": "a", "Workspace": "inherit"}, {"TypeName": "b", "Workspace": "share"}]}
    assert decide(rules, "invoke_subagent", flat, [git_workspace]) == "allow"
    assert decide(rules, "invoke_subagent", many, [git_workspace]) == "allow"
    (git_workspace / ".agent" / "cobot.rules").write_text("never Bash(make deploy*)\n")
    assert decide(rules, "invoke_subagent", flat, [git_workspace]) == "force_ask"
    assert decide(rules, "invoke_subagent", many, [git_workspace]) == "force_ask"


def test_invokeSubagent_branchOutsideAGitRepository_forceAsks(rules, workspace):
    args = {"TypeName": "builder", "Workspace": "branch"}
    assert decide(rules, "invoke_subagent", args, [workspace]) == "force_ask"


@pytest.mark.parametrize(
    "args", [{"Workspace": "/elsewhere"}, {"Subagents": "builder"}, {"Subagents": [{"Workspace": "/x"}]}]
)
def test_invokeSubagent_unknownWorkspaceOrShape_forceAsks(rules, workspace, args):
    assert decide(rules, "invoke_subagent", args, [workspace]) == "force_ask"


# ---------------------------------------------------------------- MCP


def mcp_config(home, path, servers):
    file = home / ".gemini" / "config" / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps({"mcpServers": {name: {"command": "x"} for name in servers}}))


def test_lazyMcp_judgedAsTheClaudeName(rules, workspace):
    lazy = {"ServerName": "gcp-prod", "ToolName": "delete_instance", "Arguments": {}}
    assert decide(rules, "call_mcp_tool", lazy, [workspace]) == "deny"
    read = {"ServerName": "store", "ToolName": "list_buckets"}
    assert decide(rules, "call_mcp_tool", read, [workspace]) == "allow"
    assert (
        decide(rules, "call_mcp_tool", {"ServerName": "store", "ToolName": "put_object"}, [workspace])
        == "force_ask"
    )
    assert decide(rules, "call_mcp_tool", {"ToolName": "list_x"}, [workspace]) == "force_ask"


def test_eagerMcp_knownServer_splitThere(rules, workspace, agy_home):
    mcp_config(agy_home, "mcp_config.json", ["vertex_search"])
    assert decide(rules, "mcp_vertex_search_list_indexes", {}, [workspace]) == "allow"
    assert decide(rules, "mcp_vertex_search_delete_index", {}, [workspace]) == "force_ask"


def test_eagerMcp_unknownServer_strictestSplitWins(rules, workspace):
    # read as server "vertex" and tool "search_delete_index" it would pass: every split is judged
    assert decide(rules, "mcp_vertex_search_delete_index", {}, [workspace]) == "force_ask"
    assert decide(rules, "mcp_gcp-prod_delete_instance", {}, [workspace]) == "deny"


def test_eagerMcp_pluginServer_namedPluginUnderscoreServer(rules, workspace, agy_home):
    mcp_config(agy_home, "plugins/acme/mcp_config.json", ["db"])
    assert decide(rules, "mcp_acme_db_get_row", {}, [workspace]) == "allow"


def test_eagerMcp_unreadableConfig_treatedAsUnknownServers(rules, workspace, agy_home):
    (agy_home / ".gemini" / "config" / "mcp_config.json").write_text("{not json")
    assert decide(rules, "mcp_vertex_search_delete_index", {}, [workspace]) == "force_ask"


# ---------------------------------------------------------------- failures and the contract


@pytest.mark.parametrize("stdin", ["", "garbage", "[]", '{"toolCall": "x"}', '{"workspacePaths": []}'])
def test_unreadablePayload_denies(rules, stdin):
    data = answer(rules, stdin)
    assert data["decision"] == "deny" and data["reason"].startswith("cobot gate")


def test_main_runtimeAgy_printsOneDecision(rules, workspace, monkeypatch, capsys):
    stdin = payload("run_command", {"CommandLine": "git push --force"}, [workspace])
    monkeypatch.setattr(sys, "stdin", type("S", (), {"read": staticmethod(lambda: stdin)})())
    assert rules.main(["gate", "--runtime", "agy"]) == 0
    assert json.loads(capsys.readouterr().out)["decision"] == "deny"


def test_main_unknownRuntime_isAUsageError(rules, capsys):
    assert rules.main(["gate", "--runtime", "gemini"]) == 2
    assert "runtime" in capsys.readouterr().err


# ---------------------------------------------------------------- shim


def fake_python(tmp_path, body: str) -> str:
    """A PATH whose python3 passes the version check and then runs ``body``."""
    fake = tmp_path / "bin" / "python3"
    fake.parent.mkdir(exist_ok=True)
    fake.write_text(f'#!/bin/sh\nif [ "$2" = "-c" ]; then exit 0; fi\n{body}\n')
    fake.chmod(0o755)
    return f"{fake.parent}:/usr/bin:/bin"


def run_shim(stdin: str, path: str, **env) -> subprocess.CompletedProcess:
    full = {**os.environ, "PATH": path, **env}
    full.pop("CLAUDE_PLUGIN_ROOT", None)  # agy runs hooks in the plugin folder and sets no root
    return subprocess.run(
        ["/bin/sh", "./hooks/gate-agy.sh"],
        input=stdin,
        capture_output=True,
        text=True,
        env=full,
        cwd=PLUGIN,
        check=False,
        timeout=20,
    )


def shim_decision(result) -> dict:
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    CORPUS.append(result.stdout)
    return data


def test_shim_withPython_forwardsTheDecision(workspace):
    stdin = payload("run_command", {"CommandLine": "git push --force"}, [workspace])
    assert shim_decision(run_shim(stdin, os.environ["PATH"]))["decision"] == "deny"
    stdin = payload("run_command", {"CommandLine": "git status"}, [workspace])
    assert shim_decision(run_shim(stdin, os.environ["PATH"]))["decision"] == "allow"


@pytest.mark.parametrize(
    "body, reason",
    [
        ("exit 1", "exited 1"),
        ("cat >/dev/null; exit 0", "no decision"),
        ("echo garbage", "no decision"),
        ("echo '{\"decisionX\": 1}'", "no decision"),
        ("sleep 5", "exited"),
    ],
)
def test_shim_everyFailure_deniesWithExitZero(tmp_path, body, reason):
    result = run_shim(
        payload("run_command", {"CommandLine": "ls"}), fake_python(tmp_path, body), COBOT_GATE_DEADLINE="1"
    )
    data = shim_decision(result)
    assert data["decision"] == "deny" and reason in data["reason"]


def test_shim_withoutPython_denies(tmp_path):
    (tmp_path / "empty").mkdir()
    data = shim_decision(run_shim("{}", str(tmp_path / "empty")))
    assert data["decision"] == "deny" and "python3 not found" in data["reason"]


def test_shim_oldPython_denies(tmp_path):
    fake = tmp_path / "old" / "python3"
    fake.parent.mkdir()
    fake.write_text("#!/bin/sh\nexit 1\n")
    fake.chmod(0o755)
    data = shim_decision(run_shim("{}", f"{fake.parent}:/usr/bin:/bin"))
    assert data["decision"] == "deny" and "3.12" in data["reason"]


def test_shim_badDeadline_fallsBackAndStillDenies(tmp_path):
    result = run_shim("{}", fake_python(tmp_path, "exit 1"), COBOT_GATE_DEADLINE="soon")
    assert shim_decision(result)["decision"] == "deny"


def test_shim_emptyStdin_deniesThroughTheGate():
    data = shim_decision(run_shim("", os.environ["PATH"]))
    assert data["decision"] == "deny"


def test_rootHooksJson_routesEveryToolThroughTheShim():
    hooks = json.loads((PLUGIN / "hooks.json").read_text())
    group = hooks["cobot"]
    (entry,) = group["PreToolUse"]
    assert entry["matcher"] == ".*"
    (hook,) = entry["hooks"]
    assert hook == {"type": "command", "command": "sh ./hooks/gate-agy.sh", "timeout": 10}


# ---------------------------------------------------------------- workspacePaths shape (wrap review)


def test_noWorkspace_askedPush_asksWithoutCrashing(rules):
    data = answer(rules, payload("run_command", {"CommandLine": "git push origin main"}))
    assert data["decision"] == "force_ask"
    assert "no workspacePaths" in data["reason"]


@pytest.mark.parametrize("paths", ["/repo", ["relative/ws"], [7], {"a": 1}])
def test_workspacePaths_notAListOfAbsolutePaths_asks(rules, workspace, paths):
    body = json.loads(payload("write_to_file", {"TargetFile": str(workspace / "x")}))
    body["workspacePaths"] = paths
    data = answer(rules, json.dumps(body))
    assert data["decision"] == "force_ask"
    assert "no workspacePaths" in data["reason"]


def test_loadRulesAgy_runsNoGitForTheDefaultAndOwnerLayers(rules, workspace, monkeypatch):
    seen = []
    real = rules.repo_root
    monkeypatch.setattr(rules, "repo_root", lambda cwd=None: seen.append(cwd) or real(cwd))
    rules.load_rules_agy([str(workspace)])
    assert seen == [str(workspace)]


# ---------------------------------------------- security review: Cwd, aliases, committed rules


def commit_all(folder):
    subprocess.run(["git", "init", "-q", str(folder)], check=True)
    subprocess.run(["git", "-C", str(folder), "add", "-A"], check=True)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@x",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@x",
    }
    subprocess.run(["git", "-C", str(folder), "commit", "-qm", "init"], check=True, env=env)


@pytest.mark.parametrize(
    "cwd, command",
    [("{home}/.gemini/config/plugins", "rm -r cobot"), ("{ws}/.agents", "tee hooks.json")],
)
def test_runCommand_cwdInsideAProtectedFolder_asks(rules, workspace, agy_home, cwd, command):
    (workspace / ".agents").mkdir(exist_ok=True)
    (agy_home / ".gemini" / "config" / "plugins").mkdir(parents=True, exist_ok=True)
    folder = cwd.replace("{home}", str(agy_home)).replace("{ws}", str(workspace))
    assert decide(rules, "run_command", {"CommandLine": command, "Cwd": folder}, [workspace]) == "force_ask"


@pytest.mark.parametrize("root", [".agents", ".agent"])
def test_fileTools_throughASymlinkedCustomizationRoot_deny(rules, workspace, tmp_path, root):
    real = tmp_path / "elsewhere"
    real.mkdir()
    target = workspace / root
    if target.exists():
        import shutil

        shutil.rmtree(target)
    target.symlink_to(real, target_is_directory=True)
    for name in ("hooks.json", "plugins/x/hooks.json"):
        assert decide(rules, "write_to_file", {"TargetFile": str(real / name)}, [workspace]) == "deny", name
    assert decide(rules, "write_to_file", {"TargetFile": str(real / "notes.md")}, [workspace]) == "allow"


def test_invokeSubagent_branch_ignoredRulesFileCountsAsUncommitted(rules, workspace):
    (workspace / ".agent" / "cobot.rules").write_text("never Bash(make deploy*)\n")
    commit_all(workspace)
    branch = {"Workspace": "branch", "Prompt": "x"}
    assert decide(rules, "invoke_subagent", branch, [workspace]) == "allow"
    ignored = workspace.parent / "ignored"
    (ignored / ".agent").mkdir(parents=True)
    (ignored / ".agent" / "cobot.rules").write_text("never Bash(make deploy*)\n")
    (ignored / "a").write_text("a")
    subprocess.run(["git", "init", "-q", str(ignored)], check=True)
    (ignored / ".git" / "info" / "exclude").write_text(".agent\n")
    commit_all(ignored)
    assert decide(rules, "invoke_subagent", branch, [ignored]) == "force_ask"


def test_invokeSubagent_branch_symlinkedAgentFolderCountsAsUncommitted(rules, workspace, tmp_path):
    """cobot's foreign mode: .agent is a symlink to memory outside the tree, and excluded."""
    import shutil

    shutil.rmtree(workspace / ".agent")
    (workspace / "a").write_text("a")
    subprocess.run(["git", "init", "-q", str(workspace)], check=True)
    (workspace / ".git" / "info" / "exclude").write_text(".agent\n")
    commit_all(workspace)
    external = tmp_path / "memory"
    external.mkdir()
    (external / "cobot.rules").write_text("never Bash(git push*)\n")
    (workspace / ".agent").symlink_to(external, target_is_directory=True)
    branch = {"Workspace": "branch", "Prompt": "x"}
    assert decide(rules, "invoke_subagent", branch, [workspace]) == "force_ask"


def test_invokeSubagent_topLevelWorkspaceBesideSubagents_counts(rules, workspace):
    args = {"Workspace": "branch", "Subagents": [{"Prompt": "x"}]}
    assert decide(rules, "invoke_subagent", args, [workspace]) == "force_ask"


def test_runWorkflow_reasonNamesRelativePathsBothFormsAndLargeFiles(rules, tmp_path):
    relative = answer(rules, payload("run_workflow", {"ScriptPath": "hooks.json"}))["reason"]
    assert "relative path" in relative and "sha256" not in relative
    both = answer(rules, payload("run_workflow", {"ScriptPath": "/x/a.py", "Script": "print(1)"}))["reason"]
    assert "/x/a.py" in both and "inline script sha256" in both
    big = tmp_path / "big.py"
    big.write_bytes(b"x" * (agy_module().WORKFLOW_READ_MAX + 1))
    large = answer(rules, payload("run_workflow", {"ScriptPath": str(big)}))["reason"]
    assert "not a small regular file" in large
    assert (
        "not a small regular file"
        in answer(rules, payload("run_workflow", {"ScriptPath": "/dev/zero"}))["reason"]
    )


def test_mcpEager_serverOfAWorkspacePlugin_isKnown(rules, workspace, agy_home):
    (agy_home / ".gemini" / "config" / "mcp_config.json").write_text(
        json.dumps({"mcpServers": {"github": {}}})
    )
    plugin = workspace / ".agents" / "plugins" / "github"
    plugin.mkdir(parents=True)
    (plugin / "mcp_config.json").write_text(json.dumps({"mcpServers": {"admin": {}}}))
    (workspace / ".agent" / "cobot.rules").write_text("never mcp__github_admin__*\n")
    assert decide(rules, "mcp_github_admin_delete_repo", {}, [workspace]) == "deny"


def test_schedule_withoutTimer_hasAReason(rules, workspace):
    assert answer(rules, payload("schedule", {"Prompt": "x"}, [workspace]))["reason"] != "cobot gate: "


def agy_module():
    import _cobot_agy

    return _cobot_agy


# ---------------------------------------------------------------- self-protection under agy (T04)


@pytest.mark.parametrize(
    "name, args",
    [
        ("write_to_file", {"TargetFile": "~/.gemini/config/hooks.json"}),
        ("replace_file_content", {"TargetFile": "~/.gemini/antigravity-cli/settings.json"}),
        ("edit_file", {"Path": "~/.gemini/jetski/grants.json"}),
        ("write_file", {"Path": "{ws}/.agents/plugins/p/hooks.json"}),
        ("multi_replace_file_content", {"TargetFile": "{ws}/sub/_agent/hooks.json"}),
        ("run_command", {"CommandLine": "agy plugins uninstall cobot"}),
    ],
)
def test_agySelf_underAgy_denied(rules, workspace, agy_home, name, args):
    def fill(value):
        return value.replace("{ws}", str(workspace)).replace("~", str(agy_home))

    assert decide(rules, name, {k: fill(v) for k, v in args.items()}, [workspace]) == "deny"


def test_agySelf_underAgy_agyCallAsksWithTheReason(rules, workspace):
    data = answer(rules, payload("run_command", {"CommandLine": "agy plugin list"}, [workspace]))
    assert data["decision"] == "force_ask"
    assert data["reason"].endswith("may replace or bypass the cobot gate")


def test_corpus_noAnswerEverAutoApproves():
    # defined last: pytest runs a module's tests in definition order, so CORPUS holds every answer
    assert len(CORPUS) > 50
    assert not any("auto_approve" in out for out in CORPUS)


# ---------------------------------------------- residuals (spec gate-residuals, story 9)


@pytest.mark.parametrize(
    "command",
    [
        "tee $HOME/.gemini/config/settings.json",
        "rm -r $HOME/.gemini/config",
        "cd .agents && tee hooks.json",
        "cd .agents && echo x > hooks.json",
        'cd "$d" && tee hooks.json',
        "rm -r ~/.gemini",
        "mv ~/.GEMINI ~/g",
        "cat al*",
    ],
)
@pytest.mark.parametrize("with_cwd", [False, True])
def test_runCommand_residualRows_forceAsk(rules, workspace, agy_home, command, with_cwd):
    (workspace / ".agents").mkdir(exist_ok=True)
    (workspace / "alias").symlink_to(agy_home / ".gemini" / "config" / "x")
    args = {"CommandLine": command, **({"Cwd": str(workspace)} if with_cwd else {})}
    assert decide(rules, "run_command", args, [workspace], cwd=workspace) == "force_ask", command


@pytest.mark.parametrize("with_cwd", [False, True])
def test_runCommand_casedProgram_deniesLikeTheLowercaseForm(rules, workspace, with_cwd):
    args = {"CommandLine": "GIT push --force origin main", **({"Cwd": str(workspace)} if with_cwd else {})}
    assert decide(rules, "run_command", args, [workspace], cwd=workspace) == "deny"


def test_runCommand_cwdInAProtectedFolder_namesTheFolder(rules, workspace, agy_home):
    folder = agy_home / ".gemini" / "config" / "plugins"
    folder.mkdir(parents=True, exist_ok=True)
    out = answer(rules, payload("run_command", {"CommandLine": "ls", "Cwd": str(folder)}, [workspace]))
    assert out["decision"] == "force_ask"
    assert "is inside a protected folder" in json.dumps(out)


@pytest.mark.parametrize(
    "command",
    [
        'for f in hooks.json; do cp /tmp/evil "$f"; done',
        "flock hooks.json true",
        "case x in hooks.json) :;; esac",
    ],
)
def test_runCommand_headOperandsInACustomizationRoot_forceAsk(rules, workspace, command):
    (workspace / ".agents").mkdir(exist_ok=True)
    args = {"CommandLine": command, "Cwd": str(workspace / ".agents")}
    assert decide(rules, "run_command", args, [workspace]) == "force_ask", command


def test_runCommand_pwdTilde_inHome_forceAsks(rules, workspace, agy_home):
    args = {"CommandLine": "tee ~+/.gemini/config/x", "Cwd": str(agy_home)}
    assert decide(rules, "run_command", args, [workspace]) == "force_ask"


# ---------------------------------------------- F-33 and F-34 (spec gate-f33-f34, story 4)


@pytest.mark.parametrize(
    "command",
    [
        "find ~/.gemini -delete",
        "gio trash ~/.gemini",
        "rm -r ~",
        "tar -C ~/.gemini -xf /tmp/e.tar config/x",
        "git -C ~/.gemini apply /tmp/p",
        "unzip -d ~/.gemini /tmp/e.zip",
    ],
)
def test_runCommand_f33Rows_forceAsk(rules, workspace, command):
    args = {"CommandLine": command, "Cwd": str(workspace)}
    assert decide(rules, "run_command", args, [workspace]) == "force_ask", command


def test_runCommand_projectWarning_keepsItsTextOffStderr(rules, workspace, capsys):
    (workspace / ".agent" / "cobot.rules").write_text("ask Bash(approve-it-is-safe\n")
    decide(rules, "run_command", {"CommandLine": "ls"}, [workspace])
    err = capsys.readouterr().err
    assert "unreadable rule ignored" in err and "approve" not in err
