"""The security sweep as a router (spec security-auditor, stories 3, 5 and 7): the skill runs in
the main thread and fans out auditors; the per-unit steps live in references/procedure.md."""

from __future__ import annotations

import re

from conftest import PLUGIN

SKILL = PLUGIN / "skills" / "security-sweep" / "SKILL.md"
PROCEDURE = PLUGIN / "skills" / "security-sweep" / "references" / "procedure.md"
STEPS = ("Trust-boundary inventory", "Packs", "Scanners", "History", "Accepted risks", "Checking", "Ranking")


def frontmatter(text: str) -> str:
    return text.split("---\n", 2)[1]


def test_sweep_isARouter_notAFork():
    head = frontmatter(SKILL.read_text(encoding="utf-8"))
    assert "context: fork" not in head and "agent:" not in head
    assert "disable-model-invocation: true" in head


def test_sweep_fansOutAuditorsInTheForeground_andWaitsForEach():
    text = SKILL.read_text(encoding="utf-8")
    assert "subagent_type: cobot:auditor" in text and "run_in_background: false" in text
    assert "SWEEP_SMALL_FILES = 200" in text and "At most five units" in text
    assert "git ls-files" in text and "git grep -l" in text and "find . -type f" in text
    assert "Async agent" in text and "not run" in text and "unverified" in text


def test_procedure_namesEveryStep_andOneConfidenceScale():
    text = PROCEDURE.read_text(encoding="utf-8")
    for step in STEPS:
        assert f"## {step}" in text, step
    assert "<CONFIRMED | PLAUSIBLE>" in text and "read N of M files" in text
    assert "--diff-filter=A" in text
    assert not re.search(r"\(high/medium/low\)", text)


def test_sweep_reportTemplate_hasNoSecondConfidenceScale():
    text = SKILL.read_text(encoding="utf-8")
    assert "<CONFIRMED | PLAUSIBLE>" in text and "<confidence>" not in text


def test_sweep_underAgy_repoWideUnitNotRun():
    text = SKILL.read_text(encoding="utf-8").split("## Under Antigravity", 1)[1]
    assert "invoke_subagent" in text
    assert "history and scanners: not run (agy, no command tools)" in text
