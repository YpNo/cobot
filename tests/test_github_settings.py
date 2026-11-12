"""scripts/github-settings.sh: --check reads only, --apply writes what differs, against a fake gh."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "github-settings.sh"

FAKE_GH = """#!/bin/sh
echo "$*" >> "$GH_LOG"
case "$*" in
  "repo view --json nameWithOwner --jq .nameWithOwner") echo "o/r" ;;
  *"repos/o/r/actions/oidc/customization/sub"*) echo "repo:o@1/r@2" ;;
  *"-X PUT"*|*"-X POST"*|"repo edit "*) exit 0 ;;
  *"repos/o/r/actions/permissions/workflow")
    echo '{"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}' ;;
  *"repos/o/r/actions/permissions")
    echo '{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}' ;;
  *"repos/o/r/automated-security-fixes --jq .enabled") echo false ;;
  *"repos/o/r/vulnerability-alerts"|*"repos/o/r/environments/"*|*"repos/o/r/rulesets"*)
    echo '{"message":"Not Found"}'; exit 1 ;;
  *"repos/o/r")
    echo '{"delete_branch_on_merge":false,"allow_squash_merge":true,"has_wiki":false,"has_projects":true}' ;;
  *) echo "unexpected: $*" >&2; exit 9 ;;
esac
"""


@pytest.fixture
def run(tmp_path):
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "gh").write_text(FAKE_GH)
    (tools / "gh").chmod(0o755)
    log = tmp_path / "gh.log"

    def _run(*args: str) -> tuple[subprocess.CompletedProcess[str], str]:
        env = {"PATH": f"{tools}:/usr/bin:/bin", "GH_LOG": str(log), "REPO": "o/r", "HOME": str(tmp_path)}
        proc = subprocess.run(
            ["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env, cwd=tmp_path, check=False
        )
        return proc, log.read_text() if log.exists() else ""

    return _run


def test_check_withDefaults_reportsDiffsAndWritesNothing(run):
    proc, log = run("--check")
    assert proc.returncode == 0, proc.stderr
    assert "10 change(s) pending" in proc.stdout
    assert "rulesets unavailable" in proc.stdout
    assert "rule  subject repo:o@1/r@2:environment:evals (exact), claim ref = refs/heads/main" in proc.stdout
    rule_id_hint = "gh variable set ANTHROPIC_FEDERATION_RULE_ID --repo o/r --env knowledge-refresh"
    assert rule_id_hint in proc.stdout
    assert "ANTHROPIC_API_KEY" not in proc.stdout
    assert "-X PUT" not in log and "-X POST" not in log and "repo edit" not in log


def test_apply_withDefaults_issuesEachWrite(run):
    proc, log = run("--apply")
    assert proc.returncode == 0, proc.stderr
    assert "applied 10 change(s)" in proc.stdout
    for needle in (
        "repo edit o/r --delete-branch-on-merge",
        "repo edit o/r --enable-squash-merge=false",
        "repo edit o/r --enable-projects=false",
        "-X PUT repos/o/r/actions/permissions -F enabled=true -f allowed_actions=all -F sha_pinning_required=true",  # noqa: E501
        "-X PUT repos/o/r/vulnerability-alerts",
        "-X PUT repos/o/r/automated-security-fixes",
        "-X PUT repos/o/r/environments/evals",
        "-X POST repos/o/r/environments/knowledge-refresh/deployment-branch-policies -f name=main -f type=branch",  # noqa: E501
    ):
        assert needle in log, needle
    assert "repo edit o/r --enable-wiki" not in log


def test_badArgument_exitsTwo(run):
    proc, _ = run("--nuke")
    assert proc.returncode == 2
    assert "usage" in proc.stderr


def test_script_isExecutable():
    assert os.access(SCRIPT, os.X_OK)
