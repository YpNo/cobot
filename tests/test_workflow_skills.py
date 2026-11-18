"""Workflow skill texts that name cobot-memory commands keep naming the commands that exist
(spec memory-and-ship)."""

from __future__ import annotations

from conftest import PLUGIN

SKILLS = PLUGIN / "skills"


def text(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")


def test_wrap_namesTheOneCommitFlow():
    # story 1: stage, key the tree, journal with the key, one commit; foreign mode skips the add
    wrap = text("wrap")
    steps = ("cobot-memory stamp --tree", "verified: tree <key>", "journal add --check", "one `git commit`")
    for step in steps:
        assert step in wrap, step
    assert "foreign mode" in wrap and "+working-tree" in wrap


def test_build_journalsWithTheTreeStamp():
    assert "cobot-memory stamp --tree" in text("build")
