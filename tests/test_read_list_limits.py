"""The read-only agents' read list stops printing values, switching targets and hanging (spec
debug-path, story 2). The consultant, the auditor (by alias) and the learner share it."""

from __future__ import annotations

import pytest

READ_ONLY_AGENTS = ("cobot:consultant", "cobot:auditor", "cobot:learner")

PRINTS_VALUES = [
    "kubectl get pods -o yaml",
    "kubectl get pods -oyaml",
    "kubectl get pods -o=json",
    "kubectl get pods --output yaml",
    "kubectl get pods --output=jsonpath={.items}",
    "kubectl get pods -o go-template={{.}}",
    "kubectl get pods -o custom-columns=E:.spec.containers[*].env",
    "kubectl get pods -o kyaml",
    "kubectl -n prod get cm app -o yaml",
    "kubectl get pods -Ao yaml",
    "kubectl get pods -Aojson",
    "kubectl get pods --template={{.}}",
    "kubectl get --raw /api/v1/namespaces/prod/pods",
]

NEVER_EXITS = [
    "kubectl logs api-1 -f",
    "kubectl logs api-1 --follow",
    "kubectl logs api-1 -pf",
    "kubectl -n prod logs deploy/api --follow=true",
    "kubectl get events -w",
    "kubectl get pods --watch",
    "kubectl get pods --watch-only",
    "kubectl get pods -Aw",
    "kubectl events --watch",
    "kubectl events -n prod -w",
]

SWITCHES_TARGET = [
    "kubectl get pods --server https://10.0.0.1 --token abc",
    "kubectl get pods -s https://10.0.0.1",
    "kubectl get pods --token=abc",
    "kubectl get pods --as admin",
    "kubectl get pods --as=system:admin",
    "kubectl get pods --as-group system:masters",
    "kubectl get pods --as-uid 1",
    "kubectl describe pod api-1 --client-key k.pem",
    "kubectl logs api-1 --as admin",
    "kubectl get pods --kubeconfig ./kc",
    "istioctl proxy-status --kubeconfig ./kc",
    "istioctl proxy-status --as admin",
    "gcloud run services list --configuration prod",
    "gcloud run services list --configuration=prod",
    "gcloud --impersonate-service-account sa@p.iam.gserviceaccount.com run services list",
    "gcloud projects list --account other@example.com",
    "gcloud logging read 'severity>=ERROR' --access-token-file t.txt",
]

STAY_SILENT = [
    "kubectl get pods -o wide",
    "kubectl get pods -owide",
    "kubectl get pods -o=name",
    "kubectl get pods --output=name",
    "kubectl get pods --context lab",
    "kubectl --context lab get pods",
    "kubectl get pods -A",
    "kubectl get pods -l app=web -n kube-system",
    "kubectl logs api-1 --tail 50",
    "kubectl logs api-1 --previous",
    "kubectl logs api-1 -p -c app",
    "kubectl describe pod api-1",
    "kubectl events -n prod",
    "istioctl -n prod proxy-config listeners api-1",
    "gcloud logging read 'severity>=ERROR' --limit 5",
    "gcloud --project p run services list",
]


def decide(rules, command, agent=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent)[0]


@pytest.mark.parametrize("agent", READ_ONLY_AGENTS)
@pytest.mark.parametrize("command", PRINTS_VALUES + NEVER_EXITS + SWITCHES_TARGET)
def test_readList_valuesTargetsAndWatches_ask(rules, command, agent):
    assert decide(rules, command, agent).decision == "ask", command


@pytest.mark.parametrize("agent", READ_ONLY_AGENTS)
@pytest.mark.parametrize("command", STAY_SILENT)
def test_readList_plainReads_staySilent(rules, command, agent):
    assert decide(rules, command, agent).decision is None, command


@pytest.mark.parametrize(
    ("command", "cause"),
    [
        ("kubectl get pods -o yaml", "kubectl get '-o' prints values or never exits"),
        ("kubectl logs api-1 -f", "kubectl logs '-f' never exits"),
        ("kubectl events --watch", "kubectl events '--watch' never exits"),
        ("kubectl get pods --token abc", "kubectl '--token' switches the cluster or identity"),
        ("gcloud projects list --account a@b.c", "gcloud '--account' switches the account or configuration"),
    ],
)
def test_readList_limitReason_namesTheCause(rules, command, cause):
    reason = decide(rules, command, "cobot:consultant").reason()
    assert reason == f"cobot gate: {cause}; the read list does not cover it"


@pytest.mark.parametrize("agent", [None, *READ_ONLY_AGENTS, "cobot:python-builder"])
@pytest.mark.parametrize(
    "command",
    [
        "kubectl diff --show-secrets -f m.yaml",
        "kubectl diff -f m.yaml --show-secrets=true",
        "kubectl -n prod diff -f m.yaml --show-secrets",
    ],
)
def test_showSecrets_inEveryScope_isDenied(rules, command, agent):
    assert decide(rules, command, agent).decision == "deny", command


def test_mainThread_outputFormat_isJudgedAsBefore(rules):
    assert decide(rules, "kubectl get pods -o yaml").decision is None
