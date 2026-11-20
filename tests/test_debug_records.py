"""A debug record cannot carry a secret (spec debug-path, story 5): the gate refuses an Edit or
Write under the memory's debug/ folder whose new text is secret-shaped, and `cobot-memory debug
check` and `cobot-memory check` fail on a secret-shaped line or an excerpt over the cap.

Every secret-shaped value here is assembled at run time: no fixture holds one as a literal."""

from __future__ import annotations

import json
import subprocess

import pytest

FILLER = "Q7w" * 10  # 30 characters, no pattern of its own


def shaped(kind: str) -> str:
    """One line per pattern kind, built from parts."""
    parts = {
        "a known token format": "gh" + "p_" + FILLER,
        "a Google access token": "ya" + "29." + FILLER,
        "a JWT": "ey" + "J" + FILLER[:12] + ".ey" + "J" + FILLER[:12] + "." + FILLER[:8],
        "a Bearer header": "Authorization: Bear" + "er " + FILLER,
        "URL credentials": "https://ops" + ":" + FILLER[:10] + "@db.internal/x",
        "kubeconfig key data": "client-" + "key-data: " + FILLER,
        "a service-account key": '"private' + '_key": "' + FILLER + '"',
    }
    return parts[kind]


KINDS = [
    "a known token format",
    "a Google access token",
    "a JWT",
    "a Bearer header",
    "URL credentials",
    "kubeconfig key data",
    "a service-account key",
]
CLEAN_LINES = [
    "# Debug — api crash",
    "",
    "status: open",
    "",
    "- `kubectl describe pod api-1` → exit 0",
    "  token: <redacted>",
]
CLEAN = "\n".join(CLEAN_LINES) + "\n"


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / ".agent" / "debug").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "share"))
    return root


# ---------------------------------------------------------------- the shared pattern


@pytest.mark.parametrize("kind", KINDS)
def test_debugSecretKind_eachPattern_isNamed(memory, kind):
    from _cobot_common import debug_secret_kind

    assert debug_secret_kind(f"evidence: {shaped(kind)}\n") == kind


def test_debugSecretKind_redactedAndPlainText_areClean(memory):
    from _cobot_common import debug_secret_kind

    assert debug_secret_kind(CLEAN) is None
    assert debug_secret_kind("https://ops:<redacted>@db.internal/x\nBearer <redacted>\n") is None


# ---------------------------------------------------------------- the gate at write time


def judge(rules, checkout, tool, tool_input):
    loaded, _, _ = rules.load_rules(str(checkout))
    return rules.judge(tool, tool_input, str(checkout), loaded, None)


@pytest.mark.parametrize("kind", KINDS)
def test_gate_debugWriteWithASecret_isDenied_namingTheKindNotTheText(rules, checkout, kind):
    path = str(checkout / ".agent" / "debug" / "2026-11-20-api.md")
    verdict = judge(rules, checkout, "Write", {"file_path": path, "content": CLEAN + shaped(kind) + "\n"})
    assert verdict.decision == "deny"
    assert kind in verdict.reason() and shaped(kind) not in verdict.reason()


@pytest.mark.parametrize(
    ("tool", "field"),
    [
        ("Edit", lambda text: {"old_string": "x", "new_string": text}),
        ("MultiEdit", lambda text: {"edits": [{"new_string": "ok"}, {"new_string": text}]}),
    ],
)
def test_gate_debugEditWithASecret_isDenied(rules, checkout, tool, field):
    tool_input = {"file_path": ".agent/debug/2026-11-20-api.md", **field(shaped("a JWT"))}
    assert judge(rules, checkout, tool, tool_input).decision == "deny"


def test_gate_cleanDebugRecord_isJudgedAsToday(rules, checkout):
    path = str(checkout / ".agent" / "debug" / "2026-11-20-api.md")
    assert judge(rules, checkout, "Write", {"file_path": path, "content": CLEAN}).decision is None


@pytest.mark.parametrize("path", ["README.md", ".agent/specs/x.md", "debug/notes.md"])
def test_gate_secretShapedTextElsewhere_isJudgedAsToday(rules, checkout, path):
    tool_input = {"file_path": str(checkout / path), "content": shaped("a Bearer header")}
    assert judge(rules, checkout, "Write", tool_input).decision is None


# ---------------------------------------------------------------- the check before git add


def run(memory, capsys, *argv):
    code = memory.main(list(argv))
    return code, capsys.readouterr().out


@pytest.mark.parametrize("kind", KINDS)
def test_debugCheck_secretShapedLine_failsNamingFileAndLine(memory, checkout, capsys, kind):
    record = checkout / ".agent" / "debug" / "2026-11-20-api.md"
    record.write_text(CLEAN + shaped(kind) + "\n")
    code, out = run(memory, capsys, "debug", "check", str(record))
    assert code == 1
    assert "2026-11-20-api.md:7" in out and kind in out and shaped(kind) not in out


@pytest.mark.parametrize(
    "excerpt",
    ["\n".join(f"line {n}" for n in range(21)), "x" * 2001],
)
def test_debugCheck_excerptOverTheCap_fails(memory, checkout, capsys, excerpt):
    record = checkout / ".agent" / "debug" / "2026-11-20-api.md"
    record.write_text(f"{CLEAN}\n```text\n{excerpt}\n```\n")
    code, out = run(memory, capsys, "debug", "check")
    assert code == 1 and "excerpt" in out


def test_debugCheck_cleanRecords_pass(memory, checkout, capsys):
    record = checkout / ".agent" / "debug" / "2026-11-20-api.md"
    record.write_text(f"{CLEAN}\n```text\n" + "\n".join(["ok"] * 20) + "\n```\n")
    code, out = run(memory, capsys, "debug", "check")
    assert code == 0 and "1 record" in out


def test_memoryCheck_failsOnABadRecord_passesOnAClean(memory, checkout, capsys):
    record = checkout / ".agent" / "debug" / "2026-11-20-api.md"
    record.write_text(CLEAN)
    assert run(memory, capsys, "check")[0] == 0
    record.write_text(CLEAN + shaped("a Google access token") + "\n")
    code, out = run(memory, capsys, "check")
    assert code == 1 and "debug:" in out and "a Google access token" in out


def test_debugCheck_noRecordFolder_passes(memory, checkout, capsys):
    (checkout / ".agent" / "debug").rmdir()
    assert run(memory, capsys, "debug", "check")[0] == 0


def test_gateHookPayload_endToEnd_denies(rules, checkout):
    payload = {
        "tool_name": "Write",
        "cwd": str(checkout),
        "tool_input": {"file_path": str(checkout / ".agent/debug/a.md"), "content": shaped("a JWT")},
    }
    out = json.loads(rules.gate(json.dumps(payload)))["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny"
