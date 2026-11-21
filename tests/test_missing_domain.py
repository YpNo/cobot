"""A domain no expert covers is said, not skipped: onboard step 6b, spec step 2, the template's
Experts line and the challenger (spec expert-homeassistant, T05; F-39)."""

from __future__ import annotations

import re

import pytest
from conftest import PLUGIN

SKILLS = PLUGIN / "skills"


def flat(text: str) -> str:
    return " ".join(text.split())


def test_onboard_domainsStep_followsContextAndFeedsTheJournal():
    onboard = (SKILLS / "onboard" / "SKILL.md").read_text(encoding="utf-8")
    steps = re.findall(r"^(\d+b?)\. \*\*([^*]+)\*\*", onboard, re.M)
    names = [name for name, _ in steps]
    assert names.index("6b") == names.index("6") + 1 and names.index("7") == names.index("6b") + 1
    domains = flat(onboard.split("6b. **Domains.**")[1].split("7. **Rules.**")[0])
    for phrase in (
        "`- domains: <domain> → <skill> · <domain> → none`",
        "A client of a platform's API counts",
        "/cobot:learn <topic> --new-expert",
        "never skip it",
    ):
        assert phrase in domains, phrase
    journal = flat(onboard.split("8. **Journal.**")[1])
    assert "domains without an expert" in journal and "the domains line" in journal


def test_spec_coldRead_readsTheDomainsLineWithAFallback():
    spec = (SKILLS / "spec" / "SKILL.md").read_text(encoding="utf-8")
    cold = flat(spec.split("2. **Cold read.**")[1].split("3. **Draft**")[0])
    for phrase in (
        "`domains:` bullet of CONTEXT.md's Stack in the file itself",
        "the brief may drop the Stack",
        "match the goal, the Stack and the files the change touches",
        "propose an onboard refresh",
        "Call each matching expert by name",
        "write its facts as questions",
        "/cobot:learn <topic> --new-expert",
    ):
        assert phrase in cold, phrase


def test_template_principlesCheck_carriesAnExpertsLine():
    template = (SKILLS / "spec" / "template.md").read_text(encoding="utf-8")
    principles = template.split("## Principles check")[1].split("## Stories")[0]
    assert re.search(r"^- Experts: .*none.*/cobot:learn", principles, re.M)


@pytest.mark.parametrize("folder", ["claude-agents", "agents"])
def test_challenger_domainWithoutExpert_saysMemoryOnce(folder):
    body = flat((PLUGIN / folder / "challenger.md").read_text(encoding="utf-8"))
    assert "`Experts:` line says a domain has none" in body
    assert "say so once and name `/cobot:learn` as the fix" in body
