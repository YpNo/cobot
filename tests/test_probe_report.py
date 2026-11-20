"""A probe's report is proof, checked by its own rule (spec debug-path, story 3): a verdict with a
command and an exit marker, or `Checks: none — <reason>` with `Verdict: inconclusive` and what
the lead must run under `Needs:`. Builders keep their own check; the investigator parks nothing."""

from __future__ import annotations

import json

import pytest

SESSION = "7c1d2e3f-4a5b-4c6d-8e7f-9a0b1c2d3e4f"
PROBE = "cobot:investigator"

PROVEN = """Hypothesis: the pod is OOMKilled
Prediction: describe shows Last State Terminated, Reason OOMKilled; refuted by any other reason
Checks:
- `kubectl describe pod api-1 --context lab` → exit 0
  Last State: Terminated  Reason: OOMKilled
Verdict: confirmed
Needs: none
Not checked: node pressure
"""
NONE_INCONCLUSIVE = """Hypothesis: the secret rotated
Prediction: the secret's resourceVersion changed after 10:00
Checks: none — every read of the secret asks
Verdict: inconclusive
Needs:
- `kubectl get secret db -o jsonpath={.metadata.resourceVersion} --context lab`
Not checked: everything else
"""
PROMISE = """Hypothesis: the pod is OOMKilled
Prediction: OOMKilled in describe
Checks: I looked at the pod, it was OOMKilled.
Verdict: confirmed
Needs: none
"""


@pytest.fixture(autouse=True)
def isolated_state(rules, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "share"))
    parked: list[list[str]] = []
    monkeypatch.setattr(rules, "park_noticed", lambda items, cwd, wait=True: parked.append(items))
    return parked


def agent_payload(subagent, content, agent_id="p1"):
    return json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "session_id": SESSION,
            "tool_name": "Agent",
            "tool_input": {"subagent_type": subagent, "prompt": "probe"},
            "tool_response": {"status": "completed", "content": content, "agentId": agent_id},
        }
    )


def handback_payload(message, agent_type=PROBE, agent_id="h1"):
    return json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "session_id": SESSION,
            "tool_name": "SubagentHandback",
            "agent_type": agent_type,
            "agent_id": agent_id,
            "tool_input": {"message": message},
        }
    )


@pytest.mark.parametrize("report", [PROVEN, NONE_INCONCLUSIVE, PROVEN.replace("→ exit 0", "→ 1")])
def test_checkProbeReport_proofOrHonestNone_passes(rules, report):
    assert rules.check_probe_report(report)[0] is True


@pytest.mark.parametrize(
    "report",
    [
        PROMISE,
        PROVEN.replace("Verdict: confirmed\n", ""),  # proof without a verdict
        PROVEN.replace("Verdict: confirmed", "Verdict: probably"),
        NONE_INCONCLUSIVE.replace("Verdict: inconclusive", "Verdict: confirmed"),  # no proof, a claim
        NONE_INCONCLUSIVE.split("Needs:")[0] + "Needs: none\n",  # nothing for the lead to run
        NONE_INCONCLUSIVE.split("Needs:")[0],  # no Needs: at all
        "Verdict: confirmed\n",  # no Checks:
        # the proof must sit under Checks:, not in a later section
        "Checks: looked\nVerdict: refuted\nNeeds:\n- `kubectl get pods -o yaml` → exit 0\n",
    ],
)
def test_checkProbeReport_withoutProof_fails(rules, report):
    assert rules.check_probe_report(report)[0] is False


def test_report_probeWithoutProof_blockedOnce_thenMarkedWithProbeWords(rules, isolated_state):
    first = json.loads(rules.report(agent_payload(PROBE, PROMISE)))
    assert first["decision"] == "block"
    assert "probe" in first["reason"] and "Verdict: inconclusive" in first["reason"]
    second = json.loads(rules.report(agent_payload(PROBE, PROMISE)))
    context = second["hookSpecificOutput"]["additionalContext"]
    assert context.startswith("UNPROVEN: the probe's report") and "builder" not in context
    assert isolated_state == []  # the investigator parks nothing


def test_handback_probeWithoutProof_deniedOnce_thenMarked(rules, isolated_state):
    first = json.loads(rules.handback(handback_payload(PROMISE)))["hookSpecificOutput"]
    assert first["permissionDecision"] == "deny" and "probe" in first["permissionDecisionReason"]
    second = json.loads(rules.handback(handback_payload(PROMISE)))["hookSpecificOutput"]
    assert second["updatedInput"]["message"].startswith("UNPROVEN: ")
    assert isolated_state == []


@pytest.mark.parametrize("report", [PROVEN, NONE_INCONCLUSIVE])
def test_bothPaths_passingProbeReport_allowed(rules, report):
    assert rules.report(agent_payload(PROBE, report)) is None
    assert rules.handback(handback_payload(report, agent_id="h9")) is None


def test_report_builderReport_judgedAsToday(rules):
    # a probe-shaped report from a builder has no Files: or builder Checks: proof: still blocks
    out = json.loads(rules.report(agent_payload("cobot:builder", PROMISE, agent_id="b1")))
    assert out["decision"] == "block" and "builder report" in out["reason"]


@pytest.mark.parametrize("agent", ["investigator", "x:investigator", "cobot:consultant"])
def test_report_otherAgents_areNotProbes(rules, agent):
    assert rules.report(agent_payload(agent, PROMISE)) is None
    assert rules.handback(handback_payload(PROMISE, agent_type=agent)) is None
