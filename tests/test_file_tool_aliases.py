"""F-52: MultiEdit and NotebookEdit write files too, so an Edit row covers both and a Write row
covers NotebookEdit (a notebook cell can be inserted, which creates content). Before this, no file
row matched them and a MultiEdit of a never-protected settings file got no decision."""

from __future__ import annotations

import json
import os

import pytest


def file_call(tool, path):
    if tool == "MultiEdit":
        tool_input = {"file_path": path, "edits": [{"old_string": "a", "new_string": "b"}]}
    elif tool == "NotebookEdit":
        tool_input = {"notebook_path": path, "new_source": "x", "edit_mode": "insert"}
    else:
        tool_input = {"file_path": path, "content": "x", "old_string": "a", "new_string": "b"}
    return json.dumps({"tool_name": tool, "tool_input": tool_input, "cwd": os.getcwd()})


def verdict(rules, raw):
    out = rules.gate(raw)
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None


HOME = os.path.expanduser("~")


@pytest.mark.parametrize("tool", ["Edit", "Write", "MultiEdit", "NotebookEdit"])
@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (f"{HOME}/.claude/settings.json", "deny"),
        (".claude/settings.local.json", "deny"),
        (f"{HOME}/.claude.json", "ask"),
        (".mcp.json", "ask"),
        ("src/app.py", None),
    ],
)
def test_fileToolAliases_everyFileToolGetsTheRowsVerdict(rules, tool, path, expected):
    assert verdict(rules, file_call(tool, path)) == expected, (tool, path)


def test_fileToolAliases_editRowCoversMultiEditAndNotebookEdit_writeRowCoversNotebookEdit(rules):
    loaded, _, _ = rules.load_rules(None)
    edit = next(r for r in loaded if r.tool == "Edit")
    write = next(r for r in loaded if r.tool == "Write")
    assert all(rules.applies(edit, tool, None) for tool in ("Edit", "MultiEdit", "NotebookEdit"))
    assert rules.applies(write, "NotebookEdit", None) and not rules.applies(write, "MultiEdit", None)
    assert not rules.applies(edit, "Write", None) and not rules.applies(write, "Edit", None)


def test_fileToolAliases_ownerAllowOfEdit_reachesMultiEdit_neverStillWins(rules, tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    owner.write_text("allow Edit(docs/*)\nallow Edit(~/.claude/settings.json)\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    assert verdict(rules, file_call("MultiEdit", f"{HOME}/.claude/settings.json")) == "deny"
