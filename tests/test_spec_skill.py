"""The spec template and skill ask for a change's trust boundaries (spec trust-boundaries, F-49)."""

from __future__ import annotations

import re

from conftest import PLUGIN

SPEC = PLUGIN / "skills" / "spec"
PROCEDURE = PLUGIN / "skills" / "security-sweep" / "references" / "procedure.md"
# one key word per boundary kind: the template and the sweep's inventory name the same kinds
KINDS = (
    "listener",
    "subprocess",
    "paths built",
    "deserialisation",
    "crypto",
    "authz",
    "logging",
    "secret",
    "privilege",
)


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, heading
    return match.group(1)


def test_template_trustBoundaries_afterStoriesWithRowOrNone():
    template = (SPEC / "template.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", template, re.M)
    assert headings.index("Trust boundaries") == headings.index("Stories and acceptance") + 1
    body = section(template, "Trust boundaries")
    assert "entry or crossing" in body and "guard" in body and "story" in body
    assert "none: <why>" in body and "creates or alters" in body


def test_template_andSweepInventory_nameTheSameKinds():
    boundaries = section((SPEC / "template.md").read_text(encoding="utf-8"), "Trust boundaries")
    inventory = section(PROCEDURE.read_text(encoding="utf-8"), "Trust-boundary inventory")
    for kind in KINDS:
        assert kind in boundaries, f"template: {kind}"
        assert kind in inventory, f"inventory: {kind}"


def test_specSkill_coldReadNotesSites_draftFillsBoundaries():
    skill = (SPEC / "SKILL.md").read_text(encoding="utf-8")
    cold, draft = skill.split("2. **Cold read.**")[1].split("3. **Draft**")
    assert "note the sites of each trust-boundary kind the change touches" in cold
    for phrase in (
        "every boundary the change creates or alters",
        "a guard",
        "a negative test",
        "`none:` carries a reason the challenger can check",
    ):
        assert phrase in draft.split("4. **Clarify.**")[0], phrase
