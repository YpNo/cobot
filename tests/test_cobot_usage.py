"""cobot-usage: request-level dedupe, subagent typing, calls, slug and rendering on fixture transcripts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import _cobot_usage as usage
import pytest
from conftest import BIN

USAGE_CLI = BIN / "cobot-usage"


def row(req, model, out, agent=None, content=None, ts="2026-11-07T10:00:00Z"):
    message = {
        "id": f"msg_{req}",
        "model": model,
        "usage": {
            "input_tokens": 10,
            "cache_creation_input_tokens": 100,
            "cache_read_input_tokens": 1000,
            "output_tokens": out,
        },
    }
    if content is not None:
        message["content"] = content
    return json.dumps(
        {"type": "assistant", "requestId": req, "timestamp": ts, "message": message, "agentId": agent}
    )


@pytest.fixture
def project(tmp_path, monkeypatch):
    repo = tmp_path / "work" / "my.repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.chdir(repo)
    folder = tmp_path / "cfg" / "projects" / usage.project_slug(repo)
    folder.mkdir(parents=True)
    session = "11111111-aaaa"
    calls = [
        {"type": "tool_use", "name": "Skill", "input": {"skill": "cobot:spec"}},
        {"type": "tool_use", "name": "Agent", "input": {"subagent_type": "cobot:challenger"}},
    ]
    (folder / f"{session}.jsonl").write_text(
        "\n".join(
            [
                row("req_1", "claude-fable-5-1", 500, content=calls),
                row("req_1", "claude-fable-5-1", 500),  # same request streamed twice: counted once
                row("req_2", "claude-haiku-5-5", 20, ts="2026-11-06T09:00:00Z"),
                json.dumps({"type": "user", "message": {"content": "hi"}}),
                "not json",
                json.dumps({"type": "assistant", "message": {"content": []}}),  # no usage: skipped
            ]
        )
        + "\n"
    )
    sub = folder / session / "subagents"
    sub.mkdir(parents=True)
    (sub / "agent-abc.jsonl").write_text(row("req_9", "claude-sonnet-5-5", 300, agent="abc") + "\n")
    (sub / "agent-abc.meta.json").write_text(json.dumps({"agentType": "cobot:challenger"}))
    (sub / "agent-def.jsonl").write_text(row("req_10", "claude-sonnet-5-5", 7, agent="def") + "\n")
    worktree = tmp_path / "cfg" / "projects" / (usage.project_slug(repo) + "--claude-worktrees-x")
    worktree.mkdir()
    (worktree / "22222222-bbbb.jsonl").write_text(row("req_20", "claude-fable-5-1", 1) + "\n")
    return repo


def test_project_slug_matchesClaudeCodeFolders():
    assert (
        usage.project_slug(Path("/home/ypno/workspace/agentic-partner"))
        == "-home-ypno-workspace-agentic-partner"
    )
    assert usage.project_slug(Path("/w/my.repo")) == "-w-my-repo"


def test_collect_dedupesRequestsAndTypesSubagents(project):
    report = usage.collect(project)
    d = report.as_dict()
    assert d["sessions"]["11111111-aaaa"]["requests"] == 4  # req_1 once, req_2, req_9, req_10
    assert d["sessions"]["11111111-aaaa"]["output_tokens"] == 500 + 20 + 300 + 7
    assert d["agents"]["orchestrator"]["requests"] == 3  # two in the main session, one in the worktree
    assert d["agents"]["cobot:challenger"]["output_tokens"] == 300
    assert d["agents"]["subagent"]["requests"] == 1  # meta.json missing
    assert d["models"]["claude-haiku-5-5"]["requests"] == 1
    assert d["calls"] == {"Agent:cobot:challenger": 1, "Skill:cobot:spec": 1}
    assert d["skipped_rows"] == 2 and d["from"].startswith("2026-11-06") and d["to"].startswith("2026-11-07")
    assert len(d["folders"]) == 2


def test_collect_sinceAndSessionFilters(project):
    assert usage.collect(project, since="2026-11-07").as_dict()["models"].get("claude-haiku-5-5") is None
    only = usage.collect(project, session_filter="22222222").as_dict()
    assert list(only["sessions"]) == ["22222222-bbbb"]


def test_render_isBoundedAndNamesSections(project):
    text = usage.render(usage.collect(project))
    assert text.splitlines()[0].startswith("cobot-usage: ") and "per model" in text and "calls:" in text
    assert "skipped rows: 2" in text and len(text.splitlines()) <= usage.MAX_LINES
    assert "hi" not in text  # never message text


def test_render_withoutTranscripts_saysSo(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "empty"))
    assert usage.render(usage.collect(tmp_path)).startswith("cobot-usage: no transcripts")


def test_cli_jsonAndUsage(project):
    out = subprocess.run(["python3", str(USAGE_CLI), "--json"], capture_output=True, text=True, check=False)
    assert out.returncode == 0 and json.loads(out.stdout)["skipped_rows"] == 2
    bad = subprocess.run(["python3", str(USAGE_CLI), "--bogus"], capture_output=True, text=True, check=False)
    assert bad.returncode == 2 and "cobot-usage" in bad.stderr
