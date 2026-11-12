"""scripts/anthropic-federation.sh: a pipe serving one fresh token per read, key dropped, fails fast.

A fake curl mints numbered tokens; the probe sources the script and reads the pipe like Claude
Code does before each exchange.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "anthropic-federation.sh"
TOKEN_PREFIX = "header.payload-"  # noqa: S105 - fake JWTs: header.payload-<n>.signature

FAKE_CURL = f"""#!/bin/sh
echo "$*" >> "$CURL_LOG"
n=$(( $(cat "$CURL_COUNT" 2> /dev/null || echo 0) + 1 ))
echo "$n" > "$CURL_COUNT"
[ -n "$CURL_FAIL_FROM" ] && [ "$n" -ge "$CURL_FAIL_FROM" ] && exit 22
echo '{{"value":"{TOKEN_PREFIX}'"$n"'.signature"}}'
"""

IDS = {
    "ANTHROPIC_FEDERATION_RULE_ID": "fdrl_x",
    "ANTHROPIC_ORGANIZATION_ID": "org-x",
    "ANTHROPIC_SERVICE_ACCOUNT_ID": "svac_x",
    "ANTHROPIC_WORKSPACE_ID": "wrkspc_x",
}

# what the sourcing step sees afterwards: two reads, as two Claude Code exchanges would make
PROBE = (
    '. "$1"; [ -p "$ANTHROPIC_IDENTITY_TOKEN_FILE" ] && echo "pipe=yes"; '
    'cat "$ANTHROPIC_IDENTITY_TOKEN_FILE" > "$2.1"; cat "$ANTHROPIC_IDENTITY_TOKEN_FILE" > "$2.2"; '
    'echo "key=${ANTHROPIC_API_KEY:-unset}"'
)


@pytest.fixture
def run(tmp_path):
    if not shutil.which("jq") or not shutil.which("mkfifo"):
        pytest.skip("jq and mkfifo are required")
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "curl").write_text(FAKE_CURL)
    (tools / "curl").chmod(0o755)
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    seen = tmp_path / "seen"

    def _run(drop: str = "", **extra: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        env = {
            "PATH": f"{tools}:/usr/bin:/bin",
            "CURL_LOG": str(tmp_path / "curl.log"),
            "CURL_COUNT": str(tmp_path / "curl.count"),
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
        reads = [Path(f"{seen}.{i}").read_text() for i in (1, 2) if Path(f"{seen}.{i}").exists()]
        return proc, reads

    return _run


def test_source_withAllIds_servesAFreshTokenPerRead(run):
    proc, reads = run()
    assert proc.returncode == 0, proc.stderr
    assert "pipe=yes" in proc.stdout
    # the fail-fast probe minted token 1 and threw it away unexchanged
    assert reads == [f"{TOKEN_PREFIX}2.signature", f"{TOKEN_PREFIX}3.signature"]


def test_source_withAllIds_dropsApiKey(run):
    proc, _ = run()
    assert "key=unset" in proc.stdout


def test_source_withAllIds_requestsAnthropicAudienceAndOnlyMasksTokens(run, tmp_path):
    proc, reads = run()
    assert "audience=https://api.anthropic.com" in (tmp_path / "curl.log").read_text()
    printed = [line for line in proc.stdout.splitlines() if TOKEN_PREFIX in line]
    assert printed == [f"::add-mask::{token}" for token in reads]


@pytest.mark.parametrize("missing", sorted(IDS))
def test_source_withMissingId_failsBeforeAnyRequest(run, tmp_path, missing):
    proc, reads = run(drop=missing)
    assert proc.returncode != 0
    assert f"{missing} is empty" in proc.stdout
    assert not (tmp_path / "curl.log").exists() and reads == []


def test_source_withoutOidcEndpoint_namesThePermission(run):
    proc, _ = run(ACTIONS_ID_TOKEN_REQUEST_URL="")
    assert proc.returncode != 0
    assert "id-token: write" in proc.stdout


def test_source_whenGithubRefusesToken_failsBeforeThePipe(run):
    proc, reads = run(CURL_FAIL_FROM="1")
    assert proc.returncode != 0
    assert "GitHub refused an OIDC token" in proc.stdout and reads == []


def test_serve_whenGithubStopsAnswering_warnsAndKeepsServing(run):
    # the probe and the first read succeed, then every fetch fails: the second reader gets
    # nothing after the retries, with a warning, and the server neither hangs nor dies
    proc, reads = run(CURL_FAIL_FROM="3")
    assert proc.returncode == 0, proc.stderr
    assert reads == [f"{TOKEN_PREFIX}2.signature", ""]
    assert "GitHub refused an OIDC token 3 times" in proc.stdout
