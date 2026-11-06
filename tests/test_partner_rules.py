"""Gate behaviour: the bypass table from docs/02-design.md section 13."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest
from conftest import GATE_SCRIPT, GATE_SHIM

DECISIONS = [
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
    ("git push --force", "deny"),
    ("git push -f origin main", "deny"),
    ("git push origin main --force-with-lease", "deny"),
    ("git push origin main -f", "deny"),
    ("rtk git push --force origin main", "deny"),
    ("cargo test && git push --force", "deny"),
    ("git status", None),
    ("git log --oneline", None),
    ("echo 'git push'", None),
    ("", None),
]


@pytest.mark.parametrize(("command", "expected"), DECISIONS)
def test_decide_command_returnsExpectedDecision(rules, command, expected):
    assert rules.decide(command)[0] == expected


def test_decide_mostRestrictiveSegmentWins(rules):
    decision, rule = rules.decide("git push && git push --force")
    assert decision == "deny"
    assert "--force" in rule


def payload(command, tool="Bash", **extra):
    return json.dumps({"tool_name": tool, "tool_input": {"command": command}, **extra})


def test_gate_bashPush_emitsAsk(rules):
    out = json.loads(rules.gate(payload("git push")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert "git push" in out["hookSpecificOutput"]["permissionDecisionReason"]


def test_gate_forcePush_emitsDeny(rules):
    out = json.loads(rules.gate(payload("git push --force")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_gate_readOnlyCommand_staysSilent(rules):
    assert rules.gate(payload("git status")) is None


def test_gate_otherTool_staysSilent(rules):
    assert rules.gate(payload("git push", tool="Edit")) is None


def test_gate_malformedJson_emitsAsk(rules):
    out = json.loads(rules.gate("{not json"))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_gate_unbalancedQuote_emitsAsk(rules):
    out = json.loads(rules.gate(payload("git push 'oops")))
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_gate_neverEmitsAllow(rules):
    for command, _ in DECISIONS:
        out = rules.gate(payload(command))
        assert out is None or '"allow"' not in out


def test_gate_logEnabled_appendsOneLine(rules, tmp_path, monkeypatch):
    log = tmp_path / "gate.log"
    monkeypatch.setenv("PARTNER_GATE_LOG", str(log))
    rules.gate(payload("git push", agent_type="builder"))
    lines = log.read_text().splitlines()
    assert len(lines) == 1
    expected = {"command": "git push", "decision": "ask", "rule": "ask Bash(git push*)", "agent": "builder"}
    assert json.loads(lines[0]) == expected


def test_hookOutput_longReason_truncated(rules):
    out = json.loads(rules.hook_output("ask", "x" * 1000))
    assert len(out["hookSpecificOutput"]["permissionDecisionReason"]) == rules.REASON_LIMIT


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


def test_cli_check_printsDecisionAndRule():
    result = run_script(["check", "cargo test && git push"])
    assert result.stdout.strip() == "ask  (ask Bash(git push*))"
    assert run_script(["check", "ls"]).stdout.strip() == "none"


def test_cli_usageError_exitsTwo():
    assert run_script([]).returncode == 2
    assert run_script(["bogus"]).returncode == 2


def test_main_gate_viaFunction(rules, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", type("S", (), {"read": staticmethod(lambda: payload("git push"))})())
    assert rules.main(["gate"]) == 0
    assert '"ask"' in capsys.readouterr().out


def run_shim(stdin, path):
    env = {**os.environ, "PATH": path, "CLAUDE_PLUGIN_ROOT": str(GATE_SHIM.parents[1])}
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
