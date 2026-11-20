"""Session grants (spec session-grants, T04): the owner gives a grant, and only a hook records it.

The gate always asks about ``cobot-rules grant`` and leaves a pending entry; the PostToolUse hook
turns a matching, fresh pending entry into a grant, on the main thread of an attended session;
``SessionEnd`` removes the session's file."""

from __future__ import annotations

import json
import time

import pytest

SESSION = "0b3c5d7e-1f2a-4b6c-8d9e-0a1b2c3d4e5f"
SCOPE = "gcloud --target ypno-lab"
REQUEST = f"cobot-rules grant {SCOPE}"
ATTENDED = "CLAUDE_CODE_SESSION_ATTENDED"


@pytest.fixture
def config(tmp_path, monkeypatch):
    folder = tmp_path / "cfg"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(folder))
    monkeypatch.setenv(ATTENDED, "1")
    return folder


def payload(command, event="PreToolUse", session=SESSION, **extra):
    data = {"hook_event_name": event, "tool_name": "Bash", "tool_input": {"command": command}}
    if session is not None:
        data["session_id"] = session
    return json.dumps({**data, **extra})


def decision(rules, command, **extra):
    out = rules.gate(payload(command, **extra))
    return json.loads(out)["hookSpecificOutput"] if out else None


def granted(rules, command=REQUEST, **extra):
    """The owner approved the prompt: the gate asked, then the command ran."""
    decision(rules, command, **extra)
    rules.posttool(payload(command, event="PostToolUse", **extra))
    return rules.active_grants(SESSION)


# ---------------------------------------------------------------- the gate on a grant request


def test_grantRequest_mainThread_asksAndLeavesAPendingEntry(rules, config):
    out = decision(rules, REQUEST)
    assert out["permissionDecision"] == "ask"
    assert "gcloud on ypno-lab" in out["permissionDecisionReason"]
    state = rules.load_grants(rules.grants_path(SESSION))
    assert [(p["kind"], p["target"]) for p in state["pending"]] == [("gcloud", "ypno-lab")]
    assert state["grants"] == []


def test_grantRequest_ownerAllowLine_doesNotLiftTheAsk(rules, config, tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    owner.write_text("allow Bash(cobot-rules*)\nallow Bash(cobot-rules grant*)\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    assert decision(rules, REQUEST)["permissionDecision"] == "ask"


SUBAGENTS = [
    {"agent_type": "general-purpose", "agent_id": "a1"},
    {"agent_id": "a1"},
    {"agent_type": ""},
    {"agent_name": "x"},
]


@pytest.mark.parametrize("extra", SUBAGENTS)
def test_grantRequest_fromASubagent_isDenied(rules, config, extra):
    out = decision(rules, REQUEST, **extra)
    assert out["permissionDecision"] == "deny" and "main thread" in out["permissionDecisionReason"]
    assert not rules.grants_path(SESSION).exists()


@pytest.mark.parametrize(
    "command",
    [
        "cobot-rules grant terraform --target envs/lab",
        "cobot-rules grant gcloud --target Bad_Project",
        "cobot-rules grant gcloud",
        "cobot-rules grant gcloud --target ypno-lab && rm -rf x",
        "cobot-rules grant gcloud --target ypno-lab --target ypno-family",
        "cobot-rules grant gcloud --target=ypno-lab",
        "rtk cobot-rules grant gcloud --target $P",
    ],
)
def test_grantRequest_malformedOrUnknown_isDenied(rules, config, command):
    assert decision(rules, command)["permissionDecision"] == "deny"


@pytest.mark.parametrize("session", [None, "../x", "not-a-uuid"])
def test_grantRequest_withoutAValidSession_isDenied(rules, config, session):
    assert decision(rules, REQUEST, session=session)["permissionDecision"] == "deny"


QUIET = ["cobot-rules grant --revoke", "cobot-rules grant --list", f"cobot-rules grant --revoke {SCOPE}"]


@pytest.mark.parametrize("command", QUIET)
def test_revokeAndList_mainThread_areSilent(rules, config, command):
    assert decision(rules, command) is None


def test_grantRequest_underAgy_isDenied(rules, config, tmp_path):
    call = {"name": "run_command", "args": {"CommandLine": REQUEST}}
    agy = {"toolCall": call, "workspacePaths": [str(tmp_path)]}
    out = json.loads(rules.gate_agy(json.dumps(agy)))
    assert out["decision"] == "deny" and "Claude Code" in out["reason"]


# ---------------------------------------------------------------- the hook records


def test_posttool_afterTheAsk_recordsTheGrant(rules, config):
    assert granted(rules) == [("gcloud", "ypno-lab")]
    assert rules.load_grants(rules.grants_path(SESSION))["pending"] == []  # consumed


def test_posttool_withoutAPendingEntry_recordsNothing(rules, config):
    rules.posttool(payload(REQUEST, event="PostToolUse"))
    assert rules.active_grants(SESSION) == []


def test_posttool_stalePendingEntry_recordsNothing(rules, config):
    decision(rules, REQUEST)
    path = rules.grants_path(SESSION)
    state = json.loads(path.read_text())
    state["pending"][0]["time"] -= rules.PENDING_SECONDS + 1
    path.write_text(json.dumps(state))
    rules.posttool(payload(REQUEST, event="PostToolUse"))
    assert rules.active_grants(SESSION) == []


def test_posttool_pendingForAnotherCommand_recordsNothing(rules, config):
    decision(rules, "cobot-rules grant kubectl --target lab")
    rules.posttool(payload(REQUEST, event="PostToolUse"))
    assert rules.active_grants(SESSION) == []


@pytest.mark.parametrize("attended", [None, "0", "true"])
def test_posttool_unattendedSession_recordsNothing(rules, config, monkeypatch, attended):
    decision(rules, REQUEST)
    if attended is None:
        monkeypatch.delenv(ATTENDED)
    else:
        monkeypatch.setenv(ATTENDED, attended)
    rules.posttool(payload(REQUEST, event="PostToolUse"))
    assert rules.active_grants(SESSION) == []


def test_posttool_fromASubagent_recordsNothing(rules, config):
    decision(rules, REQUEST)
    rules.posttool(payload(REQUEST, event="PostToolUse", agent_id="a1", agent_type="general-purpose"))
    assert rules.active_grants(SESSION) == []


def test_posttool_badSessionId_writesNothing(rules, config):
    rules.posttool(payload(REQUEST, event="PostToolUse", session="../x"))
    assert not (config / "cobot" / "grants").exists() or not list((config / "cobot" / "grants").iterdir())


def test_posttool_otherCommand_touchesNoFile(rules, config):
    rules.posttool(payload("gcloud pubsub topics list", event="PostToolUse"))
    assert not rules.grants_path(SESSION).exists()


def test_revoke_one_thenAll(rules, config):
    granted(rules)
    granted(rules, "cobot-rules grant kubectl --target lab")
    rules.posttool(payload("cobot-rules grant --revoke gcloud --target ypno-lab", event="PostToolUse"))
    assert rules.active_grants(SESSION) == [("kubectl", "lab")]
    rules.posttool(payload("cobot-rules grant --revoke", event="PostToolUse"))
    assert rules.active_grants(SESSION) == []


def test_grant_expires_afterGrantHours(rules, config):
    granted(rules)
    path = rules.grants_path(SESSION)
    state = json.loads(path.read_text())
    state["grants"][0]["expires"] = time.time() - 1
    path.write_text(json.dumps(state))
    assert rules.active_grants(SESSION) == []


MALFORMED = ["not json", "[]", '{"grants": "x"}', '{"grants": [{"kind": "root", "target": "x"}]}']


@pytest.mark.parametrize("text", MALFORMED)
def test_malformedFile_grantsNothing(rules, config, text):
    path = rules.grants_path(SESSION)
    path.parent.mkdir(parents=True)
    path.write_text(text)
    assert rules.active_grants(SESSION) == []


def test_sessionEnd_removesTheSessionsFile(rules, config):
    granted(rules)
    rules.sessionend(json.dumps({"hook_event_name": "SessionEnd", "session_id": SESSION, "reason": "exit"}))
    assert not rules.grants_path(SESSION).exists()
    assert rules.active_grants(SESSION) == []


def test_grantFile_editAndShellWrite_denied(rules, config):
    path = str(rules.grants_path(SESSION))
    edit = json.loads(rules.gate(payload(None, tool_name="Edit", tool_input={"file_path": path})))
    assert edit["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert decision(rules, f"cp x {path}")["permissionDecision"] == "deny"


# ---------------------------------------------------------------- the command itself


def test_cli_grant_printsTheRequest_writesNothing(rules, config, capsys):
    assert rules.main(["grant", "gcloud", "--target", "ypno-lab"]) == 0
    assert "gcloud on ypno-lab" in capsys.readouterr().out
    assert not (config / "cobot" / "grants").exists()


@pytest.mark.parametrize("argv", [["grant", "terraform", "--target", "x"], ["grant", "gcloud"], ["grant"]])
def test_cli_grant_malformed_exitsTwo(rules, config, argv):
    assert rules.main(argv) == 2


def test_cli_list_printsTheSessionsGrants(rules, config, monkeypatch, capsys):
    granted(rules)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SESSION)
    assert rules.main(["grant", "--list"]) == 0
    assert "gcloud on ypno-lab" in capsys.readouterr().out


def test_cli_list_noSession_saysSo(rules, config, monkeypatch, capsys):
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    assert rules.main(["grant", "--list"]) == 0
    assert "no grant" in capsys.readouterr().out


# ---------------------------------------------------------------- the gate honours a grant (T05)

COVERED = "gcloud pubsub topics create t1 --project ypno-lab"


def test_grantedCommand_isAllowed_namingTheGrant(rules, config):
    granted(rules)
    out = decision(rules, COVERED)
    assert out["permissionDecision"] == "allow"
    assert out["permissionDecisionReason"].startswith("cobot grant: gcloud on ypno-lab")


@pytest.mark.parametrize(
    "command",
    [
        "gcloud pubsub topics create t1 --project ypno-family",  # another target
        "gcloud pubsub topics create t1",  # no target
        "gcloud pubsub topics delete t1 --project ypno-lab",  # another kind
        "gcloud pubsub topics create t1 --project ypno-lab && echo ok",  # compound
        "gcloud storage rm gs://b/x --project ypno-lab",  # not coverable
        "gcloud projects set-iam-policy ypno-lab p.json --project ypno-lab",  # a never row
    ],
)
def test_nearMiss_underAGrant_isNotAllowed(rules, config, command):
    granted(rules)
    assert decision(rules, command)["permissionDecision"] in ("ask", "deny")


def test_neverRow_insideAGrantedKind_staysDenied(rules, config):
    granted(rules, "cobot-rules grant kubectl-delete --target lab")
    assert decision(rules, "kubectl delete ns kube-system --context lab")["permissionDecision"] == "deny"
    assert decision(rules, "kubectl delete pod p --context lab")["permissionDecision"] == "allow"


@pytest.mark.parametrize("extra", SUBAGENTS)
def test_subagent_underTheSessionsGrant_stillAsks(rules, config, extra):
    granted(rules)
    assert decision(rules, COVERED, **extra)["permissionDecision"] == "ask"


@pytest.mark.parametrize(
    ("grant", "command"),
    [
        (REQUEST, COVERED),
        ("cobot-rules grant kubectl-delete --target lab", "kubectl delete pod p --context lab"),
        ("cobot-rules grant kubectl-delete --target lab", "kubectl rollout restart deploy/api --context lab"),
        ("cobot-rules grant kubectl --target lab", "kubectl apply -f m.yaml --context lab"),
    ],
)
def test_investigator_underTheSessionsGrant_stillAsks(rules, config, grant, command):
    # spec debug-path, story 1: a grant the session holds allows nothing to a probe
    granted(rules, grant)
    assert decision(rules, command)["permissionDecision"] == "allow"
    out = decision(rules, command, agent_type="cobot:investigator", agent_id="i1")
    assert out["permissionDecision"] == "ask"


def test_expiredOrRevokedGrant_asksAgain(rules, config):
    granted(rules)
    rules.posttool(payload("cobot-rules grant --revoke", event="PostToolUse"))
    assert decision(rules, COVERED)["permissionDecision"] == "ask"
    granted(rules)
    path = rules.grants_path(SESSION)
    state = json.loads(path.read_text())
    state["grants"][0]["expires"] = time.time() - 1
    path.write_text(json.dumps(state))
    assert decision(rules, COVERED)["permissionDecision"] == "ask"


def test_ownerAskRow_isNotLiftedByAGrant(rules, config, tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    owner.write_text("ask Bash(gcloud pubsub*)\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    granted(rules)
    assert decision(rules, COVERED)["permissionDecision"] == "ask"


def test_anotherSessionsGrant_doesNotCover(rules, config):
    granted(rules)
    other = "1b3c5d7e-1f2a-4b6c-8d9e-0a1b2c3d4e5f"
    assert decision(rules, COVERED, session=other)["permissionDecision"] == "ask"


def test_noGrant_gateNeverAllows(rules, config):
    from test_session_grants import GRANT_COVERED

    for command, _, _ in GRANT_COVERED:
        out = rules.gate(payload(command))
        assert out is None or '"allow"' not in out, command


def test_grantedCommand_isLogged_andListed(rules, config, monkeypatch, capsys):
    granted(rules)
    decision(rules, COVERED)
    rules.posttool(payload(COVERED, event="PostToolUse"))
    rules.posttool(payload("gcloud pubsub topics create t2 --project ypno-family", event="PostToolUse"))
    log = rules.load_grants(rules.grants_path(SESSION))["log"]
    assert [entry["command"] for entry in log] == [COVERED]
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SESSION)
    rules.main(["grant", "--list"])
    assert f"ran: {COVERED}" in capsys.readouterr().out


def test_hooks_wirePostToolUseBashAndSessionEnd():
    from conftest import PLUGIN

    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
    post = {entry["matcher"]: entry["hooks"][0]["command"] for entry in hooks["PostToolUse"]}
    assert post["^Bash$"].endswith('grant.sh" posttool')
    assert hooks["SessionEnd"][0]["hooks"][0]["command"].endswith('grant.sh" sessionend')
    assert (PLUGIN / "hooks" / "grant.sh").stat().st_mode & 0o111


def test_mainThread_strictReading(rules):
    assert rules.main_thread({"session_id": SESSION})
    assert rules.main_thread({"agent_type": None})
    assert not rules.main_thread({"agent_type": ""})
    assert not rules.main_thread({"agent_id": "a"})
    assert not rules.main_thread({"agent_type": "Explore"})
