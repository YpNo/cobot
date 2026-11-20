"""/cobot:debug leads the investigation in the main thread (spec debug-path, story 4): seven
steps, the live context and the grants in the frame, the owner's word on production, probes in
the foreground, remedies printed and never run, a record checked before it is staged."""

from __future__ import annotations

import re

import pytest
from conftest import PLUGIN

SKILL = PLUGIN / "skills" / "debug"


def body() -> str:
    return (SKILL / "SKILL.md").read_text(encoding="utf-8")


def frontmatter() -> str:
    return body().split("---\n")[1]


def test_debugSkill_userAndModelInvocable_forAnUnknownCause():
    head = frontmatter()
    assert "name: debug\n" in head and "disable-model-invocation" not in head
    assert "user-invocable: false" not in head
    assert "unknown cause" in head.lower()


def test_debugSkill_sevenStepsInOrder():
    steps = ["Frame", "Reproduce", "Hypotheses", "Probe", "Converge", "Remedy, printed", "Record"]
    found = [re.search(rf"^{n}\. \*\*{re.escape(s)}", body(), re.M) for n, s in enumerate(steps, 1)]
    assert all(found), [s for s, m in zip(steps, found, strict=True) if not m]
    positions = [m.start() for m in found]
    assert positions == sorted(positions)


@pytest.mark.parametrize(
    "rule",
    [
        "kubectl config current-context",
        "gcloud config get project",
        "cobot-rules grant --list",
        "`prod`",
        "owner confirms",
    ],
)
def test_debugSkill_frame_printsTheLiveContextGrantsAndAsksOnProduction(rule):
    frame = body().split("2. **Reproduce")[0]
    assert rule in frame, rule


def test_debugSkill_probes_oneInvestigatorPerHypothesis_inTheForeground():
    text = body()
    assert "subagent_type: cobot:investigator" in text and "one message" in text
    assert "`run_in_background: false` where the host offers it" in text
    assert "wait for every hand-back" in text


def test_debugSkill_converge_atMostThreeRounds_leadRunsOnlyRoutingReads():
    text = body()
    assert "three rounds" in text and "references/routing.md" in text
    assert "Needs:" in text


def test_debugSkill_remedy_printedNeverRun_whateverGrant():
    text = body()
    assert "printed, never run" in text and "whatever grant" in text
    assert "inverse" in text and "/cobot:spec" in text


def test_debugSkill_record_checkedBeforeGitAdd():
    text = body()
    record = text.split("7. **Record")[1]
    assert "template.md" in record and "cobot-memory debug check" in record
    assert record.index("cobot-memory debug check") < record.index("git add")
    assert "open | resolved | unresolved" in record


def test_debugSkill_excerptCap_andAgyFallback():
    text = body()
    assert "20 lines" in text and "2000 characters" in text
    assert "Antigravity" in text and "runs the read commands itself" in text


def test_debugSkill_buildFailuresStayTheBuilders():
    assert "/cobot:build" in body() and "builder" in body()


def test_routing_noBisect_terraformPlanPrinted_everyDomainNamesASkill():
    routing = (SKILL / "references" / "routing.md").read_text(encoding="utf-8")
    assert "git bisect" not in routing.replace("never `git bisect`", "")
    assert "git log -S" in routing and "terraform plan" in routing and "printed" in routing
    for skill in ("expert-gha", "expert-kubernetes", "expert-gcp", "lang-terraform", "lang-fallback"):
        assert skill in routing, skill
    rows = [line for line in routing.splitlines() if line.startswith("| ") and "---" not in line][1:]
    for row in rows:
        assert re.search(r"`(lang|expert|fw)-[a-z*-]+`", row), row
        for skill in re.findall(r"`((?:expert|fw)-[a-z-]+)`", row):
            assert (PLUGIN / "skills" / skill).is_dir(), skill


def test_template_sectionsAndStatus():
    template = (SKILL / "template.md").read_text(encoding="utf-8")
    for section in ("status:", "Symptom", "Target", "Timeline", "Reproduction", "Hypotheses", "Root cause",
                    "Remedy", "Follow-ups"):  # fmt: skip
        assert section in template, section
    assert "open | resolved | unresolved" in template
