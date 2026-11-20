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

# story 4: what a grant could cover, as (command, kind, target)
GKE_CONTEXT = "gke_ypno-lab_europe-west1_c1"
GRANT_COVERED = [
    ("gcloud compute instances create vm1 --zone=europe-west1-b --project ypno-lab", "gcloud", "ypno-lab"),
    ("gcloud --project=ypno-lab run deploy api --image=europe-docker.pkg.dev/x/y/z:1", "gcloud", "ypno-lab"),
    ("gcloud pubsub topics create t1 --project=ypno-lab", "gcloud", "ypno-lab"),
    ("gcloud functions deploy f --runtime=python313 --project ypno-lab", "gcloud", "ypno-lab"),
    ("gcloud artifacts repositories update r --location=eu --project ypno-lab", "gcloud", "ypno-lab"),
    ("gcloud dns record-sets create a.lab. --zone=z --type=A --project ypno-lab", "gcloud", "ypno-lab"),
    ("gcloud container clusters create c1 --region=europe-west1 --project ypno-lab", "gcloud", "ypno-lab"),
    ("gcloud compute instances delete vm1 --zone=z --project ypno-lab", "gcloud-delete", "ypno-lab"),
    ("rtk gcloud pubsub topics delete t1 --project ypno-lab", "gcloud-delete", "ypno-lab"),
    ("kubectl apply -f k8s/app.yaml --context lab", "kubectl", "lab"),
    ("kubectl --context=lab -n web create -f k8s/job.yaml", "kubectl", "lab"),
    ("kubectl label pod p tier=web --context lab --overwrite", "kubectl", "lab"),
    ("kubectl annotate deploy d note=x --context lab", "kubectl", "lab"),
    ("kubectl set image deploy/api api=img:2 --context lab -n web", "kubectl", "lab"),
    ("kubectl patch deploy d --patch-file k8s/p.yaml --context lab", "kubectl", "lab"),
    (f"kubectl delete pod p --context {GKE_CONTEXT}", "kubectl-delete", GKE_CONTEXT),
    ("kubectl scale deploy d --replicas=0 --context lab", "kubectl-delete", "lab"),
    ("kubectl rollout restart deploy/d --context lab", "kubectl-delete", "lab"),
    ("helm install web charts/web --kube-context lab -n web --create-namespace", "helm", "lab"),
    ("helm upgrade --install web charts/web -f values/lab.yaml --set n=2 --kube-context lab", "helm", "lab"),
    ("helm rollback web 3 --kube-context lab --wait --timeout 5m", "helm", "lab"),
    ("helm uninstall web --kube-context lab -n web", "helm-uninstall", "lab"),
    ("helm del web --kube-context=lab", "helm-uninstall", "lab"),
]
GRANT_NOT_COVERED = [
    # not a plain simple command
    "gcloud pubsub topics create t --project ypno-lab && echo ok",
    "gcloud pubsub topics create t --project ypno-lab | tee x",
    "gcloud pubsub topics create $T --project ypno-lab",
    "gcloud pubsub topics create t --project ypno-lab > out",
    "CLOUDSDK_CORE_PROJECT=other gcloud pubsub topics create t --project ypno-lab",
    "env gcloud pubsub topics create t --project ypno-lab",
    "gcloud pubsub topics create 't' --project ypno-lab",
    "gcloud pubsub topics create t* --project ypno-lab",
    "KUBECONFIG=x kubectl apply -f a.yaml --context lab",
    # gcloud: no target, two targets, other groups, verbs, resource paths, identity flags
    "gcloud pubsub topics create t",
    "gcloud pubsub topics create t --project ypno-lab --project ypno-family",
    "gcloud pubsub topics create t --project=ypno-lab --project ypno-family",
    "gcloud storage rm gs://b/x --project ypno-lab",
    "gcloud projects add-iam-policy-binding ypno-family --role=roles/owner --project ypno-lab",
    "gcloud iam service-accounts create sa --project ypno-lab",
    "gcloud container clusters get-credentials c1 --project ypno-lab",
    "gcloud compute instances add-access-config vm1 --project ypno-lab",
    "gcloud compute instances reset vm1 --project ypno-lab",
    "gcloud compute ssh vm1 --project ypno-lab",
    "gcloud beta run deploy api --project ypno-lab",
    "gcloud pubsub topics delete projects/ypno-family/topics/t --project ypno-lab",
    "gcloud run deploy api --source=gs://b/src.tgz --project ypno-lab",
    "gcloud run deploy api --flags-file=f.yaml --project ypno-lab",
    "gcloud run deploy api --configuration=family --project ypno-lab",
    "gcloud run deploy api --impersonate-service-account=sa@x --project ypno-lab",
    "gcloud run deploy api --account=a@b --project ypno-lab",
    "gcloud run deploy api --access-token-file=t --project ypno-lab",
    "gcloud compute --zone z instances create vm --project ypno-lab",
    "gcloud pubsub topics create t --project Bad_Project",
    # kubectl: no or two contexts, other verbs and options, paths
    "kubectl apply -f a.yaml",
    "kubectl apply -f a.yaml --context lab --context prod",
    "kubectl apply -k overlays/lab --context lab",
    "kubectl apply -f a.yaml --prune --context lab",
    "kubectl apply -f a.yaml --force --context lab",
    "kubectl apply -f https://x/a.yaml --context lab",
    "kubectl apply -f /etc/a.yaml --context lab",
    "kubectl apply -f ../a.yaml --context lab",
    "kubectl apply -f - --context lab",
    "kubectl create deployment d --image=x --context lab",
    "kubectl create token sa --context lab",
    "kubectl exec p --context lab",
    "kubectl edit deploy d --context lab",
    "kubectl drain node1 --context lab",
    "kubectl apply -f a.yaml --context lab --kubeconfig other",
    "kubectl apply -f a.yaml --context lab -s https://x",
    "kubectl apply -f a.yaml --context lab --server=https://x",
    "kubectl apply -f a.yaml --context lab --as=admin",
    "kubectl apply -f a.yaml --context lab --token=x",
    "kubectl apply -f a.yaml --context lab --insecure-skip-tls-verify",
    "kubectl delete pod p --context lab --all",
    "kubectl rollout undo deploy/d --context lab",
    # an option's value read differently from the CLI: an optional-value flag, a value that is a flag
    "kubectl delete pod p --context lab --dry-run --context prod",
    "kubectl delete pod p --context lab --dry-run=client",
    "kubectl delete pod p -n --context prod --context lab",
    "kubectl delete pod p -nweb --context lab",
    "helm uninstall web --namespace --kube-context prod --kube-context lab",
    "gcloud pubsub topics create t --project ypno-lab --proj=ypno-family",
    "gcloud pubsub topics create t --project --zone=z",
    "gcloud run deploy api --impersonate=sa@x --project ypno-lab",
    # helm: no context, other flags and verbs
    "helm install web charts/web",
    "helm install web charts/web --kube-context lab --kube-context prod",
    "helm install web charts/web --kube-context lab --kubeconfig x",
    "helm install web charts/web --kube-context lab --kube-apiserver=https://x",
    "helm install web charts/web --kube-context lab --post-renderer ./r",
    "helm upgrade web charts/web --kube-context lab --cleanup-on-fail",
    "helm upgrade web charts/web --kube-context lab --force-replace",
    "helm install web oci://registry/web --kube-context lab",
    "helm install web charts/web -f ../x.yaml --kube-context lab",
    "helm repo add x https://x --kube-context lab",
    "helm plugin install x --kube-context lab",
    # never grantable at all
    "terraform apply lab.tfplan",
    "terraform -chdir=envs/lab apply lab.tfplan",
    "tofu apply lab.tfplan",
    "terragrunt apply",
    "cobot-rules grant gcloud --target ypno-lab",
    "git push",
]


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


@pytest.mark.parametrize(("command", "kind", "target"), GRANT_COVERED)
def test_grantScope_coveredForm_namesKindAndTarget(rules, command, kind, target):
    assert rules.grant_scope(command) == (kind, target)


@pytest.mark.parametrize("command", GRANT_NOT_COVERED)
def test_grantScope_anyOtherForm_isNotCovered(rules, command):
    assert rules.grant_scope(command) is None


def test_grantScope_kinds_areTheSpecsSix(rules):
    kinds = {"gcloud", "gcloud-delete", "kubectl", "kubectl-delete", "helm", "helm-uninstall"}
    assert set(rules.GRANT_KINDS) == kinds


@pytest.mark.parametrize(
    ("kind", "target", "valid"),
    [
        ("gcloud", "ypno-lab", True),
        ("gcloud", "Ypno-lab", False),
        ("gcloud", "lab", False),
        ("gcloud", "a" * 31, False),
        ("kubectl", "gke_ypno-lab_europe-west1_c1", True),
        ("kubectl", "arn:aws:eks:eu-west-1:1:cluster/c", True),
        ("kubectl", "lab;rm", False),
        ("helm", "", False),
        ("terraform", "envs/lab", False),
    ],
)
def test_grantTarget_formatPerKind(rules, kind, target, valid):
    assert rules.valid_grant(kind, target) is valid
