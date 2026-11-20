"""Session grants (spec session-grants): the hard never list, cobot's sealed owner files, the
config-dir twins of the file rows, and apply and destroy as prompt-only asks (T02)."""

from __future__ import annotations

import os

import pytest

# story 2: no grant and no prompt reaches these
NEVER_ADDITIONS = [
    "terraform state rm google_project.lab",
    "terraform -chdir=envs/lab state mv a b",
    "tofu state push old.tfstate",
    "terraform state replace-provider a b",
    "terragrunt state rm x",
    "terraform force-unlock 1234",
    "terraform import google_project.p lab",
    "tofu taint a.b",
    "terraform untaint a.b",
    "terraform workspace delete -force lab",
    "terraform apply -lock=false plan.tfplan",
    "terraform plan -lock=0",
    "tofu apply --lock=F x.tfplan",
    "terraform destroy -lock=FALSE",
    "gcloud storage rm -r gs://lab-tfstate",
    "gsutil -m rm -r gs://lab-tfstate/*",
    "gcloud storage buckets delete gs://lab-tfstate",
    "gcloud projects delete ypno-lab",
    "gcloud projects set-iam-policy ypno-lab policy.json",
    "gcloud iam service-accounts keys create k.json --iam-account sa@p.iam.gserviceaccount.com",
    "gcloud auth print-access-token",
    "gcloud auth print-identity-token",
    "gcloud auth application-default print-access-token",
    "gcloud config config-helper",
    "gcloud secrets versions access latest --secret db",
    "kubectl get secret db -o yaml",
    "kubectl create token builder",
    "kubectl config view --raw",
    "kubectl config view --flatten",
    "kubectl config rename-context prod lab",
    "kubectl config set-context lab --cluster=prod",
    "kubectl config set-cluster lab --server=https://x",
    "kubectl config set-credentials me --token=x",
    "kubectl config delete-context lab",
    "kubectl delete pods --all --all-namespaces",
    "kubectl delete deploy --all -A",
    "kubectl --context lab delete namespace kube-system",
    "kubectl delete ns kube-system",
    "rm -rf /",
    "rm -fr ~",
    "rm -r -f ~/",
    "rm -rf $HOME",
    "rm --recursive --force $HOME/",
]
# what keeps today's verdict
KEPT = [
    ("terraform state list", None),
    ("terraform state show a.b", None),
    ("terraform plan -lock=true", None),
    ("terraform plan -out=lab.tfplan", None),
    ("rm -rf build/", "ask"),
    ("rm -rf /tmp/x", "ask"),
    ("rm -rf ~/scratch", "ask"),
    ("gcloud storage rm gs://b/x", "ask"),
    ("gcloud projects add-iam-policy-binding p --member=user:x --role=roles/viewer", "ask"),
    ("kubectl delete pod x", "ask"),
    ("kubectl delete pod x -n kube-system", "ask"),
    ("kubectl config use-context lab", None),
    ("kubectl config get-contexts", None),
    ("gh auth token", "ask"),
]
APPLY_FORMS = [
    "terraform apply -auto-approve",
    "terraform -chdir=envs/prod apply",
    "terraform apply lab.tfplan",
    "tofu destroy",
    "terraform destroy -auto-approve",
    "terragrunt run-all apply",
    "terragrunt destroy",
]
KUBE_READS = ["cat ~/.kube/config", "head -5 ~/.kube/config", "tail $HOME/.kube/config"]


def judge(rules, command, agent=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent, os.getcwd())[0]


def judge_file(rules, tool, path):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_file(tool, path, os.getcwd(), loaded, None).decision


@pytest.mark.parametrize("command", NEVER_ADDITIONS)
def test_neverAdditions_eachDenied(rules, command):
    assert judge(rules, command).decision == "deny"


@pytest.mark.parametrize(("command", "expected"), KEPT)
def test_neverAdditions_neighboursKeepTheirVerdict(rules, command, expected):
    assert judge(rules, command).decision == expected


@pytest.mark.parametrize("agent", ["cobot:consultant", "cobot:learner"])
@pytest.mark.parametrize("command", KUBE_READS)
def test_readOnlyAgents_kubeconfigRead_denied(rules, agent, command):
    assert judge(rules, command, agent).decision == "deny"


@pytest.mark.parametrize("command", APPLY_FORMS)
def test_applyAndDestroy_askNotDeny(rules, command):
    verdict = judge(rules, command)
    assert verdict.decision == "ask" and "prompt only" in verdict.reason()


@pytest.mark.parametrize("command", APPLY_FORMS)
def test_applyAndDestroy_ownerAllow_doesNotSilence(rules, tmp_path, monkeypatch, command):
    owner = tmp_path / "owner.rules"
    owner.write_text("allow Bash(terraform*)\nallow Bash(tofu*)\nallow Bash(terragrunt*)\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    assert judge(rules, command).decision == "ask"
    assert judge(rules, "terraform plan -out=x.tfplan").decision is None


@pytest.mark.parametrize("tool", ["Edit", "Write"])
@pytest.mark.parametrize("path", ["~/.claude/cobot.rules", "~/.claude/cobot/grants/a.json", "~/.kube/config"])
def test_ownerAndKubeFiles_editAndWrite_denied(rules, tool, path):
    assert judge_file(rules, tool, path) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cp x ~/.claude/cobot/grants/a.json",
        "mv x ~/.claude/cobot.rules",
        "cat ~/.claude/cobot/trusted",
        "ln -s /tmp/x ~/.claude/cobot/grants",
    ],
)
def test_sealedOwnerFiles_shellAccess_denied(rules, command):
    verdict = judge(rules, command)
    assert verdict.decision == "deny" and "cobot's owner files" in verdict.reason()


def test_otherProtectedFiles_shellAccess_stillAsks(rules):
    assert judge(rules, "cp x ~/.claude/settings.json").decision == "ask"


def test_configDir_rowsFollowClaudeConfigDir(rules, tmp_path, monkeypatch):
    config = tmp_path / "cfg"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))
    for path in (config / "cobot" / "grants" / "a.json", config / "cobot.rules", config / "settings.json"):
        assert judge_file(rules, "Edit", str(path)) == "deny", path
    assert judge(rules, f"cp x {config}/cobot/grants/a.json").decision == "deny"
    assert judge_file(rules, "Edit", "~/.claude/cobot.rules") == "deny"  # the literal rows stay


def test_configDir_unset_addsNoTwin(rules, monkeypatch):
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    loaded, _, _ = rules.load_rules(None)
    assert not [r for r in loaded if r.tool in rules.FILE_TOOLS and r.pattern.startswith(os.sep)]
