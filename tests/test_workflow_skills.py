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


def test_onboard_untrustedAfterInit_namesInitWithTheConfigDir():
    # story 6 (F-47): both paths, the prefixed init command, never `cobot-memory trust`
    onboard = text("onboard")
    assert "run `cobot-memory check` again" in onboard and "trust file:" in onboard
    assert "CLAUDE_CONFIG_DIR=<path>" in onboard and "Never send the owner to `cobot-memory trust`" in onboard


def test_wrapAndBuild_clearTheParkedNotices():
    # story 3: wrap files or drops each parked item, build parks an async hand-back's itself
    wrap = text("wrap")
    assert "cobot-memory noticed list" in wrap and "cobot-memory noticed clear" in wrap
    build = text("build")
    assert "Async agent launched" in build and "cobot-memory noticed add" in build
