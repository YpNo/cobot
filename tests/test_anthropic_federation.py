"""scripts/anthropic-federation.sh: token file written, key dropped, fails fast, against a fake curl."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "anthropic-federation.sh"
TOKEN = "header.payload-secret.signature"  # noqa: S105 - a fake JWT for the fake curl

FAKE_CURL = f"""#!/bin/sh
echo "$*" >> "$CURL_LOG"
[ -n "$CURL_FAIL" ] && exit 22
echo '{{"value":"{TOKEN}"}}'
"""

IDS = {
    "ANTHROPIC_FEDERATION_RULE_ID": "fdrl_x",
    "ANTHROPIC_ORGANIZATION_ID": "org-x",
    "ANTHROPIC_SERVICE_ACCOUNT_ID": "svac_x",
    "ANTHROPIC_WORKSPACE_ID": "wrkspc_x",
}

# what the sourcing step sees afterwards; the API key must be gone
PROBE = (
    '. "$1"; echo "file=$ANTHROPIC_IDENTITY_TOKEN_FILE"; '
    'cat "$ANTHROPIC_IDENTITY_TOKEN_FILE" > "$2"; echo "key=${ANTHROPIC_API_KEY:-unset}"'
)


@pytest.fixture
def run(tmp_path):
    if not shutil.which("jq"):
        pytest.skip("jq is required")
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "curl").write_text(FAKE_CURL)
    (tools / "curl").chmod(0o755)
    (tools / "jq").symlink_to(shutil.which("jq"))
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    seen = tmp_path / "seen"

    def _run(drop: str = "", **extra: str) -> tuple[subprocess.CompletedProcess[str], str]:
        env = {
            "PATH": f"{tools}:/usr/bin:/bin",
            "CURL_LOG": str(tmp_path / "curl.log"),
            "RUNNER_TEMP": str(runner_temp),
            "ACTIONS_ID_TOKEN_REQUEST_URL": "https://oidc.example/token?x=1",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
            "ANTHROPIC_API_KEY": "sk-ant-stale",
            **{k: v for k, v in IDS.items() if k != drop},
            **extra,
        }
        proc = subprocess.run(
            ["bash", "-ec", PROBE, "probe", str(SCRIPT), str(seen)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
            check=False,
        )
        return proc, seen.read_text() if seen.exists() else ""

    return _run


def test_source_withAllIds_writesTokenFileAndDropsKey(run):
    proc, seen = run()
    assert proc.returncode == 0, proc.stderr
    assert seen == TOKEN
    assert "file=" in proc.stdout and "anthropic-oidc-token" in proc.stdout
    assert "key=unset" in proc.stdout


def test_source_withAllIds_requestsAnthropicAudienceAndOnlyMasksToken(run, tmp_path):
    proc, _ = run()
    assert "audience=https://api.anthropic.com" in (tmp_path / "curl.log").read_text()
    printed = [line for line in proc.stdout.splitlines() if TOKEN in line]
    assert printed == [f"::add-mask::{TOKEN}"]


@pytest.mark.parametrize("missing", sorted(IDS))
def test_source_withMissingId_failsBeforeAnyRequest(run, tmp_path, missing):
    proc, seen = run(drop=missing)
    assert proc.returncode != 0
    assert f"{missing} is empty" in proc.stdout
    assert not (tmp_path / "curl.log").exists() and seen == ""


def test_source_withoutOidcEndpoint_namesThePermission(run):
    proc, _ = run(ACTIONS_ID_TOKEN_REQUEST_URL="")
    assert proc.returncode != 0
    assert "id-token: write" in proc.stdout


def test_source_whenGithubRefusesToken_fails(run):
    proc, seen = run(CURL_FAIL="1")
    assert proc.returncode != 0
    assert "GitHub refused an OIDC token" in proc.stdout and seen == ""
