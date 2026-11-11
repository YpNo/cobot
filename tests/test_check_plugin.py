"""scripts/check-plugin.py: the listing budget counts what the model sees, caps hold, consult
procedures carry no dated knowledge."""

from __future__ import annotations

import importlib.util
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


@pytest.fixture
def plugin(tmp_path):
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "a.md").write_text("---\nname: a\ndescription: an agent\n---\nbody\n")
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
