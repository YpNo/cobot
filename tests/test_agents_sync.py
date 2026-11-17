"""scripts/sync-agents.py: the Antigravity agents in agents/ are the Claude Code agents of
claude-agents/, with agy's tools and model tiers (spec antigravity, story 2)."""

from __future__ import annotations

import importlib.util

import pytest
from conftest import PLUGIN, REPO

SCRIPT = REPO / "scripts" / "sync-agents.py"


@pytest.fixture(scope="module")
def sync():
    spec = importlib.util.spec_from_file_location("sync_agents", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def claude(name: str, tools: str, model: str = "sonnet", extra: str = "", body: str = "Body.\n") -> str:
    head = f"---\nname: {name}\ndescription: Does one thing: well.\ntools: {tools}\nmodel: {model}\n"
    return f"{head}{extra}---\n{body}"


def fields(sync, text: str) -> dict:
    return sync.agy_fields(text)


def test_agents_committedCopies_matchTheSync(sync):
    stale = sync.sync(PLUGIN, check=True)
    assert stale == [], f"agents/ is out of date for {stale}: run `python3 scripts/sync-agents.py`"


def test_agents_everyClaudeAgentHasAnAgyTwin():
    claude_names = {p.stem for p in (PLUGIN / "claude-agents").glob("*.md")}
    assert claude_names == {p.stem for p in (PLUGIN / "agents").glob("*.md")}
    assert len(claude_names) == 10  # the auditor joined in spec security-auditor


def test_agents_builderTools_mappedToBothFileToolFamilies_skillDropped(sync):
    out = fields(
        sync, sync.render(claude("builder", "Read, Edit, Write, Bash, Grep, Glob, Skill"), "builder")
    )
    assert out["tools"] == [
        "view_file",
        "read_file",
        "replace_file_content",
        "multi_replace_file_content",
        "edit_file",
        "write_to_file",
        "write_file",
        "run_command",
        "manage_task",
        "grep_search",
        "find_by_name",
        "list_dir",
    ]
    assert out["model"] == "flash" and out["mainAgent"] == "false"
    assert "commandExecutionPolicy" not in out


@pytest.mark.parametrize("name", ["consultant", "learner", "auditor"])
def test_agents_readOnlyResearchers_getNoRunCommand_andCommandsOff(sync, name):
    out = fields(sync, sync.render(claude(name, "Read, Grep, Glob, Bash, WebFetch, WebSearch"), name))
    assert "run_command" not in out["tools"] and "manage_task" not in out["tools"]
    assert {"read_url_content", "search_web", "view_file"} <= set(out["tools"])
    assert out["commandExecutionPolicy"] == "off"
    assert "no command tool: read files and pages only" in sync.render(claude(name, "Read, Bash"), name)


def test_agents_models_sonnetToFlash_inheritKept_learnerOnPro(sync):
    assert fields(sync, sync.render(claude("x", "Read"), "x"))["model"] == "flash"
    assert (
        fields(sync, sync.render(claude("challenger", "Read", "inherit"), "challenger"))["model"] == "inherit"
    )
    assert fields(sync, sync.render(claude("learner", "Read"), "learner"))["model"] == "pro"


def test_agents_descriptionWithAColon_isQuotedStrictYaml(sync):
    text = sync.render(claude("x", "Read"), "x")
    assert 'description: "Does one thing: well."' in text


@pytest.mark.parametrize(
    "line",
    [
        "When the brief names a skill, call it with the Skill tool before you write code.\n",
        "Names a framework skill, call it with the Skill tool (`cobot:fw-react` …) before you write code.\n",
    ],
)
def test_agents_skillToolLine_becomesAViewFileRead(sync, line):
    body = sync.render(claude("x", "Read, Skill", body=line), "x")
    assert "Skill tool" not in body and "cobot:fw-react" not in body
    assert "read its `skills/<name>/SKILL.md` under the plugin path in your brief with `view_file`" in body


def test_agents_preloadedSkill_becomesAnExplicitRead(sync):
    body = sync.render(claude("rust-builder", "Read", extra="skills: [lang-rust]\n"), "rust-builder")
    assert "read `skills/lang-rust/SKILL.md` under the plugin path in your brief with `view_file`" in body
    assert "skills:" not in body.split("---")[1]  # agy's own preload is not relied on


def test_agents_reportHookSentence_saysNoHookChecksIt(sync):
    body = sync.render(
        claude("builder", "Read", body="a report without this shape is sent back by the hook.\n"), "b"
    )
    assert "sent back by the hook" not in body
    assert "no hook checks this shape under Antigravity" in body


def test_agents_everyBodyRewriteStillMatchesAClaudeAgent(sync):
    bodies = "".join(p.read_text(encoding="utf-8") for p in (PLUGIN / "claude-agents").glob("*.md"))
    for pattern, _ in sync.REWRITES:
        assert pattern.search(bodies), f"rewrite {pattern.pattern!r} matches no Claude agent any more"


@pytest.mark.parametrize("tools, model", [("Read, Teleport", "sonnet"), ("Read", "opus")])
def test_agents_unknownToolOrModel_failsFast(sync, tools, model):
    with pytest.raises(ValueError, match="Teleport|opus"):
        sync.render(claude("x", tools, model), "x")


def test_agents_syncWritesThenChecksClean(sync, tmp_path):
    (tmp_path / "claude-agents").mkdir()
    (tmp_path / "claude-agents" / "x.md").write_text(claude("x", "Read, Bash"))
    assert sync.sync(tmp_path, check=True) == ["x"]
    assert sync.sync(tmp_path, check=False) == ["x"]
    assert sync.sync(tmp_path, check=True) == []
    (tmp_path / "agents" / "orphan.md").write_text("---\nname: orphan\n---\n")
    assert sync.sync(tmp_path, check=True) == ["orphan"]


def test_agents_mainCheckMode_exitsOneAndNamesTheCommand(sync, tmp_path, capsys):
    (tmp_path / "claude-agents").mkdir()
    (tmp_path / "claude-agents" / "x.md").write_text(claude("x", "Read"))
    assert sync.main(["--check", str(tmp_path)]) == 1
    assert "python3 scripts/sync-agents.py" in capsys.readouterr().out
    assert sync.main([str(tmp_path)]) == 0
    assert sync.main(["--check", str(tmp_path)]) == 0


def test_agents_generatedFileNamesItsSource(sync):
    assert "claude-agents/x.md" in sync.render(claude("x", "Read"), "x")


def test_agents_auditorTwin_hasNoCommandTool_andCommandsOff(sync):
    # spec security-auditor, story 1: the auditor runs the consultant's read list, never agy commands
    twin = fields(sync, (PLUGIN / "agents" / "auditor.md").read_text(encoding="utf-8"))
    assert "run_command" not in twin["tools"] and "manage_task" not in twin["tools"]
    assert twin["commandExecutionPolicy"] == "off" and twin["model"] == "inherit"
    source = sync.claude_fields((PLUGIN / "claude-agents" / "auditor.md").read_text(encoding="utf-8"))
    assert source["model"] == "inherit" and source["effort"] == "high"


def test_agents_realTwinsKeepTheirClaudeBody(sync):
    # the copy is the Claude body: only the rewrites and the header differ
    source = (PLUGIN / "claude-agents" / "challenger.md").read_text(encoding="utf-8")
    twin = (PLUGIN / "agents" / "challenger.md").read_text(encoding="utf-8")
    assert source.split("---\n", 2)[2].strip() in twin
