"""Session grants (spec session-grants, story 7, T06): the protocol asks once with three answers,
keeps grants on the main thread and applies a saved plan; no skill or agent text still says the
gate denies apply; the grantable forms the expert skills name are the ones the gate covers."""

from __future__ import annotations

import pytest
from conftest import PLUGIN, REPO

SKILLS = PLUGIN / "skills"
LAB_LOG = ".agent/labs/<slug>.md"
# the wording T06 replaced: apply and destroy now ask at the prompt (story 3)
DENIES_APPLY = ("denies `terraform|tofu apply`", "denied by the gate", "the gate denies it")
TEXTS_ABOUT_APPLY = [
    SKILLS / "lang-terraform" / "SKILL.md",
    SKILLS / "ship" / "SKILL.md",
    SKILLS / "expert-gcp" / "SKILL.md",
    PLUGIN / "claude-agents" / "terraform-builder.md",
    PLUGIN / "agents" / "terraform-builder.md",
    PLUGIN / "protocol.md",
    REPO / "README.md",
]
# one documented example per kind, as expert-gcp and expert-kubernetes write them
DOCUMENTED_FORMS = [
    ("gcloud run deploy api --project lab-sandbox-1 --image x", "gcloud", "lab-sandbox-1"),
    ("gcloud run services delete api --project lab-sandbox-1", "gcloud-delete", "lab-sandbox-1"),
    ("kubectl apply -f k8s/app.yaml --context lab -n demo", "kubectl", "lab"),
    ("kubectl delete -f k8s/app.yaml --context lab -n demo", "kubectl-delete", "lab"),
    ("helm upgrade --install app charts/app --kube-context lab -f charts/app/lab.yaml", "helm", "lab"),
    ("helm uninstall app --kube-context lab -n demo", "helm-uninstall", "lab"),
]


def read(path) -> str:
    return path.read_text(encoding="utf-8")


def test_protocol_asksOnceWithThreeAnswers():
    protocol = read(PLUGIN / "protocol.md")
    for answer in ("this command only", "every <kind> on <target> this session", "· no."):
        assert answer in protocol, answer
    assert "AskUserQuestion once" in protocol
    assert "`cobot-rules grant <kind> --target <t>`" in protocol


def test_protocol_grantsMainThreadOnly_savedPlan_labLog():
    protocol = read(PLUGIN / "protocol.md")
    assert "Grants. " in protocol and "Main thread only." in protocol
    assert "`plan -out <f>` in the folder, journal its summary, `apply <f>` at the prompt" in protocol
    assert LAB_LOG in protocol and "teardown" in protocol and "budget alert" in protocol


def test_protocol_applyIsNoLongerAnOutwardAction():
    # apply runs at the owner's prompt from a saved plan; the outward list stays proposed only
    outward = "Outward actions (push, PR, comment, release, publish) are proposed only."
    assert outward in read(PLUGIN / "protocol.md")


@pytest.mark.parametrize("path", TEXTS_ABOUT_APPLY, ids=lambda p: str(p.relative_to(REPO)))
def test_texts_neverSayTheGateDeniesApply(path):
    text = read(path)
    for wording in DENIES_APPLY:
        assert wording not in text, wording


def test_langTerraform_appliesASavedPlanOnTheMainThread():
    skill = read(SKILLS / "lang-terraform" / "SKILL.md")
    assert "On the main thread only: `plan -out=tfplan` inside the" in skill
    assert "Never apply without a saved plan" in skill and "`plan -destroy -out=tfplan`" in skill
    assert "no rule or session grant silences it" in skill


@pytest.mark.parametrize("folder", ["claude-agents", "agents"])
def test_terraformBuilder_neverApplies_handsBackThePlan(folder):
    builder = read(PLUGIN / folder / "terraform-builder.md")
    assert "`apply` and `destroy` ask the owner and are never yours: hand back the saved plan." in builder


@pytest.mark.parametrize("skill", ["expert-gcp", "expert-kubernetes"])
def test_expertSkills_grantOnTheMainThreadWithALabLog(skill):
    text = read(SKILLS / skill / "SKILL.md")
    assert "ession grants (main thread only)" in text
    assert LAB_LOG in text and "teardown" in text and "A builder never holds a grant" in text
    assert "cobot-rules grant --revoke" in text


@pytest.mark.parametrize(("command", "kind", "target"), DOCUMENTED_FORMS)
def test_documentedForms_areTheOnesTheGateCovers(rules, command, kind, target):
    assert rules.grant_scope(command) == (kind, target)


@pytest.mark.parametrize("kind", ["gcloud", "kubectl"])
def test_expertSkills_nameTheGrantCommandTheGateKnows(rules, kind):
    skill = "expert-gcp" if kind == "gcloud" else "expert-kubernetes"
    target = "<project>" if kind == "gcloud" else "<context>"
    assert f"`cobot-rules grant {kind} --target {target}`" in read(SKILLS / skill / "SKILL.md")
    assert rules.grant_request(f"cobot-rules grant {kind} --target lab-sandbox-1")[:2] == ("grant", kind)
