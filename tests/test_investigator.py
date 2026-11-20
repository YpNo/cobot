"""The investigator is read-only by rule (spec debug-path, story 1): it shares the consultant's
read list through ``SCOPE_ALIASES``, the hook's namespaced name only."""

from __future__ import annotations

import pytest
from conftest import PLUGIN
from test_cobot_rules import CLOUD_CREDENTIAL_PRINTERS, CREDENTIAL_PRINTERS, corpus_commands

AGENT = "cobot:investigator"
SOURCE = PLUGIN / "claude-agents" / "investigator.md"


def decide(rules, command, agent=AGENT):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent)[0]


@pytest.mark.parametrize(
    "command",
    [
        "kubectl describe pod api-1",
        "kubectl logs api-1 --previous",
        "gcloud logging read 'severity>=ERROR' --limit 20",
        "kubectl get events -n prod",
        "git log --oneline -5",
        "cat -n ./k8s/deploy.yaml",
    ],
)
def test_investigator_reads_staySilent(rules, command):
    assert decide(rules, command).decision is None, command


@pytest.mark.parametrize(
    "command",
    [
        "kubectl rollout restart deploy/api",
        "kubectl delete pod api-1",
        "gcloud run deploy api --image i",
        "curl -X POST https://example.com/hook",
        "kubectl scale deploy/api --replicas 0",
        "cat a > b",
    ],
)
def test_investigator_mutations_ask(rules, command):
    assert decide(rules, command).decision == "ask", command


@pytest.mark.parametrize("command", CLOUD_CREDENTIAL_PRINTERS)
def test_investigator_cloudCredentialPrinters_areDenied(rules, command):
    assert decide(rules, command).decision == "deny", command


@pytest.mark.parametrize("command", CREDENTIAL_PRINTERS)
def test_investigator_forgeCredentialPrinters_neverSilent(rules, command):
    assert decide(rules, command).decision in ("ask", "deny"), command


def test_investigator_sameDecisionsAsTheConsultant_overTheCorpus(rules):
    differ = [
        command
        for command in corpus_commands()
        if decide(rules, command).decision != decide(rules, command, "cobot:consultant").decision
    ]
    assert not differ, differ


@pytest.mark.parametrize("agent", ["investigator", "x:investigator", "investigator:cobot"])
def test_investigator_lookalikeNames_getNoConsultantRow(rules, agent):
    for command in ("git status", "cat README.md", "kubectl describe pod x", "ls"):
        scoped, plain = decide(rules, command, agent), decide(rules, command, None)
        assert scoped.decision == plain.decision, (agent, command)
        assert "@consultant" not in scoped.reason(), (agent, command)


def test_investigatorAgent_readOnlyTools_sonnetMedium():
    head = SOURCE.read_text(encoding="utf-8").split("---\n")[1]
    assert "tools: Read, Grep, Glob, Bash, WebFetch\n" in head
    assert "model: sonnet\n" in head and "effort: medium\n" in head
    assert "Edit" not in head and "Write" not in head and "Agent" not in head
