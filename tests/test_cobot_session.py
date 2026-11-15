"""The SessionStart brief under the Antigravity CLI (spec antigravity, story 5): one injectSteps
system message, the project from workspacePaths, the agy section after the protocol."""

from __future__ import annotations

import json
import subprocess

import pytest
from conftest import PLUGIN

SHIM = PLUGIN / "hooks" / "session-agy.sh"


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A git repository with cobot memory, and a cwd elsewhere: agy runs hooks in the plugin folder."""
    home = tmp_path / "home"
    home.mkdir()
    for name, value in {
        "HOME": home,
        "CLAUDE_CONFIG_DIR": home / ".claude",
        "XDG_DATA_HOME": home / ".local" / "share",
    }.items():
        monkeypatch.setenv(name, str(value))
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    root = tmp_path / "repo"
    (root / ".agent").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    (root / ".agent" / "CONTEXT.md").write_text("# x\n\nprofile: cli\ngoal: g\n")
    (root / ".agent" / "JOURNAL.md").write_text("# Journal\n\n## 2026-01-01 — one\nNext: n1\n")
    elsewhere = tmp_path / "plugin-folder"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    return root


def agy_payload(workspaces=()) -> str:
    return json.dumps({"hookEventName": "SessionStart", "workspacePaths": [str(w) for w in workspaces]})


def message(out: str) -> str:
    """The one system message of an agy SessionStart answer, its shape checked on the way."""
    data = json.loads(out)
    assert list(data) == ["injectSteps"]
    (step,) = data["injectSteps"]
    assert list(step) == ["systemMessage"] and list(step["systemMessage"]) == ["systemMessage"]
    return step["systemMessage"]["systemMessage"]


def test_agy_answer_isOneSystemMessageWithinTheCap(session, project):
    out = session.agy_answer(agy_payload([project]))
    text = message(out)
    assert len(out) <= session.TOTAL_CAP
    assert "userMessage" not in out
    assert text.startswith("# cobot protocol")


def test_agy_sectionOrder_protocolAgyRulesBrief(session, project):
    text = message(session.agy_answer(agy_payload([project])))
    protocol = text.index("# cobot protocol")
    agy = text.index(session.AGY_HEADING)
    rules = text.index("\nrules: ")
    brief = text.index("UNTRUSTED")
    assert protocol < agy < rules < brief
    assert "\nknowledge: " in text and "\ndeps: " in text


def test_agy_section_givesAbsoluteBinPathAndTheGaps(session):
    section = session.agy_section()
    root = session.plugin_root()
    assert len(section) <= session.AGY_SECTION_CAP
    assert f"`{root}`" in section and "<plugin folder>/bin/<tool>" in section
    assert "python3 -I" in section
    for tool in ("cobot-memory", "cobot-rules", "cobot-deps"):
        assert tool in section
    for name in ("invoke_subagent", "ask_question", "SKILL.md"):
        assert name in section
    for skill in ("onboard", "rules", "security-sweep", "learn"):
        assert skill in section
    assert "AGENTS.md" in section and "GEMINI.md" in section
    assert "not enforced" in section and "not proven gated" in section


@pytest.mark.parametrize("width", [60, 300])
def test_agy_section_longPluginPath_keepsEveryGapWithinItsCap(session, monkeypatch, tmp_path, width):
    deep = tmp_path / ("p" * width) / ".gemini" / "config" / "plugins" / "cobot"
    monkeypatch.setattr(session, "plugin_root", lambda: deep)
    section = session.agy_section()
    assert len(section) <= session.AGY_SECTION_CAP
    assert section.rstrip().endswith("review their diff before any outward step.")
    assert f"`{deep}`" in section and "<plugin folder>/bin/<tool>" in section


def test_agy_deepWorkspaceWarning_staysWithinTheSerialisedCap(session, tmp_path, monkeypatch):
    deep = tmp_path
    for _ in range(6):
        deep = deep / ("d" * 200)
    deep.mkdir(parents=True)
    import subprocess as sp

    sp.run(["git", "init", "-q", str(deep)], check=True)
    for root in ("_agents", "_agent", ".agents", ".agent"):
        (deep / root).mkdir()
        for name in ("hooks.json", "plugins.json"):
            (deep / root / name).write_text("{}")
    monkeypatch.setattr(session, "run_tool", lambda *_a, **_k: "")
    out = session.agy_answer(agy_payload([deep]))
    assert len(out) <= session.TOTAL_CAP
    assert len(session.workspace_warning([str(deep)])) <= session.WORKSPACE_WARNING_CAP


def test_agy_projectFromWorkspacePaths_notTheHookFolder(session, project, monkeypatch):
    seen = []
    real = session.run_tool

    def record(name, args, cwd, clock=None):
        seen.append(cwd)
        return real(name, args, cwd, clock)

    monkeypatch.setattr(session, "run_tool", record)
    session.agy_answer(agy_payload([project, project.parent]))
    assert seen and set(seen) == {str(project)}


@pytest.mark.parametrize("workspaces", [(), ("relative/dir",), ("/no/such/folder",)])
def test_agy_noUsableWorkspace_saysProjectUnknown(session, project, monkeypatch, workspaces):
    monkeypatch.setattr(session, "run_tool", lambda *_a, **_k: pytest.fail("no tool without a project"))
    text = message(session.agy_answer(agy_payload(workspaces)))
    assert text.startswith("# cobot protocol")
    assert session.AGY_HEADING in text
    assert "project unknown" in text


def test_agy_briefBudget_shrinksByTheAgySection(session, project, monkeypatch):
    budgets = []

    def fake(name, args, cwd, clock=None):
        if args[:1] == ["brief"] and name == "cobot-memory":
            budgets.append(int(args[args.index("--budget") + 1]))
            return "B" * budgets[-1]
        return "rules: never=1" if name == "cobot-rules" else ""

    monkeypatch.setattr(session, "run_tool", fake)
    out = session.agy_answer(agy_payload([project]))
    protocol, section = session.protocol_text(), session.agy_section()
    assert budgets[0] <= session.TOTAL_CAP - len(protocol) - len(section) - session.LINES_RESERVE
    assert session.AGY_HEADING in message(out)


def test_agy_serialisedCap_cutsTheTailNeverTheAgySection(session, project, monkeypatch):
    noisy = '"\\\n' * 5000  # each character escapes to two in JSON

    def fake(name, args, cwd, clock=None):
        return noisy if name == "cobot-memory" and args[:1] == ["brief"] else ""

    monkeypatch.setattr(session, "run_tool", fake)
    out = session.agy_answer(agy_payload([project]))
    assert len(out) <= session.TOTAL_CAP
    assert session.agy_section() in message(out)


def test_agy_errorPath_stillPrintsTheProtocol(session, project, monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("down")

    monkeypatch.setattr(session, "run_tool", boom)
    text = message(session.agy_answer(agy_payload([project])))
    assert text.startswith("# cobot protocol")
    assert "brief unavailable (RuntimeError: down)" in text
    text = message(session.agy_answer("not json"))
    assert text.startswith("# cobot protocol") and "brief unavailable" in text


def test_agy_cli_runtimeFlag(session, capsys, monkeypatch, project):
    class Stdin:
        @staticmethod
        def read():
            return agy_payload([project])

    monkeypatch.setattr("sys.stdin", Stdin)
    assert session.main(["start", "--runtime", "agy"]) == 0
    assert message(capsys.readouterr().out).startswith("# cobot protocol")
    assert session.main(["start", "--runtime", "claude"]) == 0
    assert "hookSpecificOutput" in json.loads(capsys.readouterr().out)
    for bad in (["start", "--runtime"], ["start", "--runtime", "gemini"], ["start", "--x"]):
        assert session.main(bad) == 2


def test_agy_shim_printsOneAnswerFromThePluginFolder(project, monkeypatch):
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", "/elsewhere/not/cobot")
    done = subprocess.run(
        ["sh", str(SHIM)], input=agy_payload([project]), capture_output=True, text=True, check=False
    )
    assert done.returncode == 0
    text = message(done.stdout)
    assert f"`{PLUGIN.resolve()}`" in text


def test_agy_hooksJson_runsTheSessionShimFlat():
    hooks = json.loads((PLUGIN / "hooks.json").read_text())["cobot"]
    (handler,) = hooks["SessionStart"]
    assert handler["command"] == "sh ./hooks/session-agy.sh"
    assert "matcher" not in handler and handler["timeout"] == 30


@pytest.mark.parametrize(
    "found",
    [
        ".agents/hooks.json",
        ".agent/hooks.json",
        "_agents/plugins.json",
        "_agent/plugins",
        "sub/.agents/hooks.json",
    ],
)
def test_agy_workspaceHooksOrPlugins_warnBeforeTheBrief(session, project, found):
    workspace = project / "sub" if found.startswith("sub/") else project
    target = project / found
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir() if found.endswith("plugins") else target.write_text("{}")
    text = message(session.agy_answer(agy_payload([workspace])))
    warning = text.index(session.WORKSPACE_WARNING)
    assert text.index(session.AGY_HEADING) < warning < text.index("\nrules: ")
    assert str(target) in text
    assert "Tell the owner" in text


def test_agy_workspaceParentAboveTheRepository_isNotScanned(session, project):
    (project.parent / ".agents").mkdir()
    (project.parent / ".agents" / "hooks.json").write_text("{}")
    (project / ".agents").mkdir()
    (project / ".agents" / "skills.json").write_text("{}")
    assert session.WORKSPACE_WARNING not in message(session.agy_answer(agy_payload([project])))


def test_agy_workspaceWarning_listsAtMostAFew(session, project):
    for root in ("_agents", "_agent", ".agents", ".agent"):
        (project / root).mkdir(exist_ok=True)
        for name in ("hooks.json", "plugins.json"):
            (project / root / name).write_text("{}")
    line = session.workspace_warning([str(project)])
    assert line.count(str(project)) == session.WORKSPACE_SHOWN
    assert line.endswith("and 3 more")
