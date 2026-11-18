"""scripts/check-plugin.py: the listing budget counts what the model sees, caps hold, consult
procedures carry no dated knowledge."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-plugin.py"


@pytest.fixture(scope="module")
def contract():
    spec = importlib.util.spec_from_file_location("check_plugin", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skill(root: Path, name: str, description: str, extra: str = "", body: str = "body\n") -> Path:
    folder = root / "skills" / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n{extra}---\n{body}")
    return folder


MANIFEST = {"name": "p", "version": "1.0.0", "description": "d", "license": "MIT", "repository": "r"}


def manifests(root: Path, agents: list[str], **agy) -> None:
    for folder, extra in ((".claude-plugin", {"agents": agents}), (".antigravity-plugin", agy)):
        (root / folder).mkdir(exist_ok=True)
        (root / folder / "plugin.json").write_text(json.dumps({**MANIFEST, **extra}))


AGY_AGENT = (
    "---\nname: {name}\ndescription: d\ntools:\n  - view_file\nmodel: flash\nmainAgent: false\n---\nbody\n"
)


def agent(root: Path, name: str, description: str = "an agent") -> Path:
    """A Claude Code agent in claude-agents/, listed in the manifest, and its agy twin in agents/."""
    path = root / "claude-agents" / f"{name}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(f"---\nname: {name}\ndescription: {description}\n---\nbody\n")
    (root / "agents").mkdir(exist_ok=True)
    (root / "agents" / f"{name}.md").write_text(AGY_AGENT.format(name=name))
    listed = json.loads((root / ".claude-plugin" / "plugin.json").read_text())["agents"]
    manifests(root, sorted({*listed, f"./claude-agents/{name}.md"}))
    return path


@pytest.fixture
def plugin(tmp_path):
    manifests(tmp_path, [])
    agent(tmp_path, "a")
    (tmp_path / "protocol.md").write_text("protocol\n")
    return tmp_path


def test_listingChars_skipsUserOnlySkills_countsWhenToUse(contract, plugin):
    skill(plugin, "spec", "x" * 100)
    skill(plugin, "onboard", "y" * 400, "disable-model-invocation: true\n")
    skill(plugin, "wrap", "z" * 50, "when_to_use: " + "w" * 30 + "\n")
    assert contract.listing_chars(plugin) == 180


def test_check_budgetCountsOnlyModelVisibleSkills(contract, plugin, monkeypatch):
    monkeypatch.setattr(contract, "SKILL_DESCRIPTIONS_TOTAL_MAX", 150)
    skill(plugin, "spec", "x" * 100)
    skill(plugin, "onboard", "y" * 400, "disable-model-invocation: true\n")
    assert not any("total" in p for p in contract.check(plugin))
    skill(plugin, "wrap", "z" * 40, "when_to_use: " + "w" * 30 + "\n")
    assert any("total 170 chars" in p for p in contract.check(plugin))


def test_check_expertAndLangDescriptionsCappedAt350(contract, plugin):
    skill(plugin, "expert-x", "e" * 351, 'paths:\n  - "**/*.x"\n')
    skill(plugin, "lang-y", "l" * 350, 'paths:\n  - "**/*.y"\n')
    skill(plugin, "ship", "s" * 600)
    problems = contract.check(plugin)
    assert any("expert-x" in p and "351 chars (max 350)" in p for p in problems)
    assert not any("lang-y" in p or "ship" in p for p in problems)


def test_check_consultProcedureWithADatedKnowledgeLine_fails(contract, plugin):
    folder = skill(plugin, "consult", "router")
    (folder / "domains").mkdir()
    (folder / "domains" / "gha.md").write_text("- [verified 2026-11-06 · src: https://x] a fact\n")
    assert any("consult" in p and "dated knowledge line" in p for p in contract.check(plugin))
    (folder / "domains" / "gha.md").write_text("Procedure only.\n")
    assert not any("dated knowledge line" in p for p in contract.check(plugin))


def test_learnSkeleton_fixedDescriptionLeavesRoomUnderTheCap(contract):
    # a promoted skeleton is an expert-* skill: its description must fit 350 with the learner's text
    template = SCRIPT.parents[1] / "plugins" / "cobot" / "skills" / "learn" / "templates" / "expert-SKILL.md"
    description = contract.frontmatter(template.read_text())["description"]
    fixed = (
        description.replace("{{DESCRIPTION}}", "").replace("{{WHEN}}", "").replace("{{DATE}}", "2026-11-10")
    )
    assert len(fixed) <= 80, fixed


def test_check_frameworkSkillsAreKnowledgeSkills(contract, plugin):
    skill(plugin, "fw-x", "f" * 351)
    problems = contract.check(plugin)
    assert any("fw-x" in p and "351 chars (max 350)" in p for p in problems)
    assert any("fw-x" in p and "without paths:" in p for p in problems)


def test_check_protocolOverTheCharBudget_isReported(contract, plugin):
    # characters, not bytes: "é" is two bytes but one character
    (plugin / "protocol.md").write_text("é" * (contract.PROTOCOL_MAX_CHARS + 1), encoding="utf-8")
    assert "protocol.md: 3001 chars (max 3000)" in contract.check(plugin)


def test_check_protocolExactlyAtTheCharBudget_passes(contract, plugin):
    (plugin / "protocol.md").write_text("é" * contract.PROTOCOL_MAX_CHARS, encoding="utf-8")
    assert not any("protocol.md" in p for p in contract.check(plugin))


def test_check_protocolMissing_isReportedNotRaised(contract, plugin):
    (plugin / "protocol.md").unlink()
    assert "protocol.md: missing" in contract.check(plugin)


def test_check_skillNamingAnAgentWithoutForegroundFlag_fails(contract, plugin):
    # an Agent call that omits run_in_background started in the background in 22 of 23 calls
    # (eval run 43584857035): the skill then reported before the agent did
    agent(plugin, "consultant", "d")
    skill(plugin, "consult", "router", body="One `Agent` call, `subagent_type: cobot:consultant`.\n")
    skill(plugin, "learn", "forked", "agent: cobot:consultant\n", body="No spawn named here.\n")
    problems = contract.check(plugin)
    assert any("consult" in p and "run_in_background: false" in p for p in problems)
    assert not any("learn" in p for p in problems)
    both = "`run_in_background: false` where the host offers it; wait for every hand-back.\n"
    skill(plugin, "wrap", "fan-out", body="One `cobot:consultant`, " + both)
    assert not any("wrap" in p for p in contract.check(plugin))


FLAG_ONLY = "`cobot:consultant`, `run_in_background: false` where the host offers it.\n"
WAIT_ONLY = "`cobot:consultant`; wait for every hand-back.\n"
OLD_FLAG = "`cobot:consultant` (`run_in_background: false`); wait for every hand-back.\n"


@pytest.mark.parametrize(
    ("body", "missing"),
    [
        (FLAG_ONLY, "wait for every hand-back"),
        (WAIT_ONLY, "where the host offers it"),
        (OLD_FLAG, "where the host offers it"),
    ],
)
def test_check_skillWithOneHostStringWithoutTheOther_fails(contract, plugin, body, missing):
    # F-35: the desktop app has no run_in_background, so a skill also waits for every hand-back
    agent(plugin, "consultant", "d")
    skill(plugin, "wrap", "fan-out", body=body)
    assert any("wrap" in p and missing in p for p in contract.check(plugin))


def test_check_theFixturePlugin_passes(contract, plugin):
    assert contract.check(plugin) == []


def test_check_manifestsDisagree_fails(contract, plugin):
    manifests(plugin, ["./claude-agents/a.md"], version="1.0.1")
    assert any("version" in p and "manifests disagree" in p for p in contract.check(plugin))


def test_check_agyManifestMissing_fails(contract, plugin):
    (plugin / ".antigravity-plugin" / "plugin.json").unlink()
    assert any(".antigravity-plugin/plugin.json: missing" in p for p in contract.check(plugin))


def test_check_manifestAgentsListDiffersFromTheFolder_fails(contract, plugin):
    (plugin / "claude-agents" / "unlisted.md").write_text("---\nname: unlisted\ndescription: d\n---\n")
    manifests(plugin, ["./claude-agents/a.md", "./claude-agents/gone.md"])
    problems = contract.check(plugin)
    assert any("unlisted.md" in p and "not in the manifest" in p for p in problems)
    assert any("gone.md" in p and "no such file" in p for p in problems)


def test_check_agentListingBudget_countsTheManifestListNotAgyAgents(contract, plugin, monkeypatch):
    monkeypatch.setattr(contract, "AGENT_BUDGET_TOKENS", 30)
    twin = AGY_AGENT.format(name="a").replace("description: d", "description: " + "x" * 400)
    (plugin / "agents" / "a.md").write_text(twin)
    assert not any("listing" in p for p in contract.check(plugin))
    agent(plugin, "b", "y" * 120)
    assert any("agents: listing" in p for p in contract.check(plugin))


def test_check_skillBodyOver24000Bytes_fails(contract, plugin):
    skill(plugin, "big", "d", body="é" * 12_001)  # 24 002 bytes, 12 001 characters
    skill(plugin, "edge", "d", body="x" * contract.SKILL_BODY_MAX_BYTES)
    problems = contract.check(plugin)
    assert any("big" in p and "24002 bytes" in p for p in problems)
    assert not any("edge" in p for p in problems)


@pytest.mark.parametrize(
    "frontmatter",
    [
        "argument-hint: [--foreign] [what a new project is for]\n",  # two flow sequences
        "description: keeps the rules: reads the constraints\n",  # a mapping inside a plain scalar
        "description: the gate #1 asks\n",  # a comment silently cuts the value
        'description: "never closed\n',
        "description: [never closed\n",
        "paths:\n  - [a] b\n",
        "description: ends with a colon:\n",
        "tools: @reserved\n",
    ],
)
def test_yamlProblems_notStrictYaml_isReported(contract, frontmatter):
    assert contract.yaml_problems(frontmatter)


@pytest.mark.parametrize(
    "frontmatter",
    [
        'argument-hint: "[--foreign] [what a new project is for]"\n',
        "argument-hint: [spec, slug]\n",
        "description: >-\n  folded: colons and # hashes are text here\n",
        "description: a plain scalar\n  continued on a second line\n",
        'paths:\n  - "**/*.rs"\n  - Cargo.toml\n',
        "description: 'single: quoted'\n",
        "tools: Read, Grep, Glob\n",
        "url: https://example.com/a#b\n",
    ],
)
def test_yamlProblems_strictYaml_isClean(contract, frontmatter):
    assert contract.yaml_problems(frontmatter) == []


def test_check_skillWithNonStrictFrontmatter_fails(contract, plugin):
    skill(plugin, "onboard", "d", "argument-hint: [--foreign] [what]\n")
    assert any("onboard" in p and "strict YAML" in p for p in contract.check(plugin))


def test_realPlugin_everyFrontmatterIsStrictYaml(contract):
    plugin = SCRIPT.parents[1] / "plugins" / "cobot"
    files = [*plugin.glob("skills/*/SKILL.md"), *plugin.glob("*agents/*.md")]
    assert files
    problems = [f"{f}: {p}" for f in files for p in contract.yaml_problems(contract.frontmatter_text(f))]
    assert problems == []


def test_check_claudeAgentWithoutAgyTwin_andTheReverse_fail(contract, plugin):
    (plugin / "agents" / "a.md").unlink()
    (plugin / "agents" / "stray.md").write_text(AGY_AGENT.format(name="stray"))
    problems = contract.check(plugin)
    assert any("claude-agents/a.md" in p and "no agents/a.md" in p for p in problems)
    assert any("agents/stray.md" in p and "no claude-agents/stray.md" in p for p in problems)


@pytest.mark.parametrize(
    "old, new, expected",
    [
        ("  - view_file\n", "  - view_file\n  - teleport\n", "unknown agy tool teleport"),
        ("tools:\n  - view_file\n", "tools: view_file, grep_search\n", "tools must be a YAML list"),
        ("model: flash", "model: sonnet", "model 'sonnet'"),
        ("model: flash", "model: flash_lite", "model 'flash_lite'"),
        ("mainAgent: false\n", "", "mainAgent: false"),
        ("name: a\n", "name: b\n", "name 'b'"),
    ],
)
def test_check_agyAgentContract_isHeld(contract, plugin, old, new, expected):
    twin = plugin / "agents" / "a.md"
    twin.write_text(twin.read_text().replace(old, new))
    assert any("agents/a.md" in p and expected in p for p in contract.check(plugin))


def test_installNames_aLiveHookGroupNameInTheTree_fails(tmp_path):
    import importlib.machinery
    import importlib.util

    loader = importlib.machinery.SourceFileLoader("check_plugin_names", "scripts/check-plugin.py")
    spec = importlib.util.spec_from_loader("check_plugin_names", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    name = "cobot-" + "a1" * 8  # built, so this file never holds one
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "run.md").write_text(f"group {name} installed\n")
    (tmp_path / "ok.md").write_text("group cobot-<random> installed\n")
    assert module.install_name_problems(tmp_path) == [
        f"docs/run.md: an installed hook group name ({name}): redact it"
    ]
    assert module.install_name_problems(tmp_path / "docs" / "..") != []
