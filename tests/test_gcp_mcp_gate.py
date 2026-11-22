"""Google Cloud MCP opt-in at the gate (spec gcp-mcp-opt-in, T01): the owner registers every
server (stories 2 and 5), the Google Cloud CLI server is refused under any name, and a session
grant never reaches an MCP tool (story 4)."""

from __future__ import annotations

import json
import os

import pytest

SESSION = "4d1e2f3a-5b6c-4d7e-8f90-a1b2c3d4e5f6"
GRANT = "cobot-rules grant gcloud --target ypno-lab"


def bash(command, session=None):
    data = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": os.getcwd()}
    if session:
        data["session_id"] = session
    return json.dumps(data)


def tool_call(tool, tool_input=None, session=None):
    data = {"tool_name": tool, "tool_input": tool_input or {}, "cwd": os.getcwd()}
    if session:
        data["session_id"] = session
    return json.dumps(data)


def verdict(rules, raw):
    out = rules.gate(raw)
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None


REGISTRATIONS = [
    "claude mcp add --transport http gcp-logging https://logging.googleapis.com/mcp",
    "claude mcp add --transport http -s user gcp-x https://attacker.example/mcp",
    'claude mcp add-json gcp-x \'{"type":"http","url":"https://attacker.example/mcp"}\'',
    "claude mcp add-from-claude-desktop",
    "claude mcp remove gcp-logging",
    "claude --debug mcp add gcp-x https://attacker.example/mcp",
    "rtk claude mcp add gcp-x https://attacker.example/mcp",
    "/usr/local/bin/claude mcp add gcp-x https://attacker.example/mcp",
    "claude -p hi --mcp-config '{\"mcpServers\":{}}'",
    "claude --mcp-config extra.json -p hi",
    "claude --settings x.json -p hi",
    "claude mcp reset-project-choices",
    "claude-code mcp add g https://attacker.example/mcp",
]


@pytest.mark.parametrize("command", REGISTRATIONS)
def test_gcpMcpGate_serverRegistration_asks(rules, command):
    assert verdict(rules, bash(command)) == "ask", command


SHELL_WRITES = [
    "cp /tmp/e.json .mcp.json",
    "mv /tmp/e.json .mcp.json",
    "tee .mcp.json < /tmp/e.json",
    "ln -s /tmp/e.json .mcp.json",
    "cat x > .mcp.json",
    "dd if=x of=.mcp.json",
    "curl -o .mcp.json https://x.example/m.json",
    "git checkout evil -- .mcp.json",
    "cp /tmp/e.json ~/.claude.json",
    'cp /tmp/e.json "$HOME/.claude.json"',
    "git status && cp x ./.mcp.json",
]


@pytest.mark.parametrize("command", SHELL_WRITES)
def test_gcpMcpGate_shellWordOnAServerList_asksAsAProtectedFile(rules, command):
    raw = bash(command)
    assert verdict(rules, raw) == "ask", command
    assert "protected file" in json.loads(rules.gate(raw))["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.parametrize("command", ["printf x > .mcp.json", "sed -i s/a/b/ ~/.claude.json"])
def test_gcpMcpGate_scriptWriteOfAServerList_staysRefused(rules, command):
    assert verdict(rules, bash(command)) == "deny", command


@pytest.mark.parametrize("command", ["git add src/*", "cp src/* dist/", "ls *.json", "cat */README.md"])
def test_gcpMcpGate_globThatOnlyCouldNameAServerList_staysSilent(rules, command):
    assert verdict(rules, bash(command)) is None, command


@pytest.mark.parametrize("command", ["claude mcp list", "claude mcp get gcp-logging", "claude --version"])
def test_gcpMcpGate_registrationReads_keepTheirVerdict(rules, command):
    assert verdict(rules, bash(command)) is None, command


@pytest.mark.parametrize("tool", ["Edit", "Write"])
@pytest.mark.parametrize("path", ["~/.claude.json", "{home}/.claude.json", ".mcp.json", "{cwd}/.mcp.json"])
def test_gcpMcpGate_editOfAServerConfig_asks(rules, tool, path):
    path = path.format(home=os.path.expanduser("~"), cwd=os.getcwd())
    raw = tool_call(tool, {"file_path": path, "content": "{}", "old_string": "a", "new_string": "b"})
    assert verdict(rules, raw) == "ask", path


@pytest.mark.parametrize(
    "tool",
    [
        "mcp__gcp-cloudcli__list_commands",
        "mcp__gcp-cloudcli__run_gcloud_command",
        "mcp__gcp-cli__run_gcloud_command",
        "mcp__gcloud__run_gcloud_command",
        "mcp__x__run_bq_command",
        "mcp__claude_ai_Google_Cloud_CLI__run_gcloud_command",
    ],
)
def test_gcpMcpGate_cloudCliServer_refusedUnderAnyName(rules, tool):
    assert verdict(rules, tool_call(tool)) == "deny", tool


def test_gcpMcpGate_cloudCliRefusal_beatsAnOwnerAllow(rules, tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    owner.write_text("allow mcp__gcp-cloudcli__*\nallow mcp__gcloud__*\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    assert verdict(rules, tool_call("mcp__gcp-cloudcli__list_commands")) == "deny"
    assert verdict(rules, tool_call("mcp__gcloud__run_gcloud_command")) == "deny"


@pytest.fixture
def granted(rules, tmp_path, monkeypatch):
    """An active gcloud grant on ypno-lab for SESSION: the gate asked, the owner approved."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ATTENDED", "1")
    rules.gate(bash(GRANT, SESSION))
    post = json.loads(bash(GRANT, SESSION)) | {"hook_event_name": "PostToolUse"}
    rules.posttool(json.dumps(post))
    assert rules.active_grants(SESSION) == [("gcloud", "ypno-lab")]
    return SESSION


def test_gcpMcpGate_grant_coversItsGcloudCommand(rules, granted):
    command = "gcloud run deploy api --image x --project ypno-lab"
    assert verdict(rules, bash(command, granted)) == "allow"


@pytest.mark.parametrize(
    ("tool", "expected"),
    [
        ("mcp__gcp-run__deploy_service", "deny"),
        ("mcp__gcp-compute__create_instance", "deny"),
        ("mcp__gcp-run__scale_service", "ask"),
        ("mcp__gcp-cloudcli__run_gcloud_command", "deny"),
        ("mcp__gcp-logging__list_log_entries", None),
    ],
)
def test_gcpMcpGate_grant_neverReachesAnMcpTool(rules, granted, tool, expected):
    assert verdict(rules, tool_call(tool, {"project": "ypno-lab"}, granted)) == expected, tool
