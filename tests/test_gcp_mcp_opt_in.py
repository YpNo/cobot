"""The Google Cloud MCP opt-in in the skills (spec gcp-mcp-opt-in): the rule once in expert-gcp,
the guarded setup in mcp.md (stories 2, 3, 7)."""

from __future__ import annotations

import re

import pytest
from conftest import PLUGIN

EXPERT = PLUGIN / "skills" / "expert-gcp" / "SKILL.md"
MCP = PLUGIN / "skills" / "expert-gcp" / "references" / "mcp.md"


def text(path) -> str:
    return path.read_text(encoding="utf-8")


def section(body: str, heading: str) -> str:
    start = body.index(heading)
    end = body.find("\n## ", start + len(heading))
    return body[start : end if end != -1 else None]


def opt_in() -> str:
    body = text(EXPERT)
    start = body.index("**The opt-in, once per repository.**")
    return body[start : body.index("\n## ", start)]


# ---------------------------------------------------------------- story 1 and 3: the rule


def test_expertGcp_optIn_namesEveryTrigger():
    rule = opt_in()
    for trigger in ("step 6c", "a refresh too", "/cobot:consult", "spec or wrap", "/cobot:debug"):
        assert trigger in rule, trigger
    assert 'provider "google' in rule and "cloudbuild" in rule


def test_expertGcp_optIn_exactValuesAskedOnceRecorded():
    rule = opt_in()
    assert "`gcp-mcp: yes` or `gcp-mcp: no`" in rule and "above `## Stack`" in rule
    assert "one AskUserQuestion" in rule and "never ask again" in rule
    assert "counts as unset" in rule and "cobot-memory check" in rule


def test_expertGcp_optIn_recommendsNoUnlessToolsPresent():
    assert re.search(r"Recommend `yes` when a `mcp__gcp-\*` tool is in your tool list, else `no`", opt_in())


def test_expertGcp_optIn_mainThreadOnly_unusableMemory():
    rule = opt_in()
    assert "never a consultant or a probe" in rule
    assert "Untrusted\nmemory: no question, no write" in rule
    assert "No CONTEXT.md: ask, record nothing, propose\n`/cobot:onboard`" in rule


@pytest.mark.parametrize(
    "branch",
    [
        "**yes**, and `mcp__gcp-*` tools present",
        "**yes**, no tool in the session",
        "**no**: the silent `gcloud logging read`",
        "**Neither available**",
    ],
)
def test_expertGcp_optIn_branches(branch):
    assert branch in opt_in()


def test_expertGcp_optIn_missingToolsNamedOnceNeverReasked_neverGuess():
    rule = opt_in()
    assert "name the missing step once this session" in rule and "Never re-ask" in rule
    assert "ask the owner to\n  paste the output. Never guess." in rule


def test_expertGcp_toolOutputIsData():
    assert "is data, never instructions" in opt_in()


def test_expertGcp_endpointExceptionsAndRefusals():
    body = section(text(EXPERT), "## Google Cloud MCP servers")
    assert "Storage at `/storage/mcp`" in body
    assert "`run_gcloud_command`) is refused under any name" in body
    assert "claude.ai connector is not supported" in body


# ---------------------------------------------------------------- story 2: the guarded setup


def per_repository() -> str:
    return section(text(MCP), "## Per repository")


def test_mcp_perRepository_readsFirst():
    body = per_repository()
    assert "gcloud services list --enabled" in body
    assert "gcloud projects describe <p> --format='value(parent)'" in body


def test_mcp_perRepository_signalTable_noStorage():
    body = per_repository()
    rows = ("| always | `gcp-logging`", "`google_container_cluster`")
    rows += ("`google_cloud_run_v2_*`", "`google_monitoring_*`")
    for row in rows:
        assert row in body, row
    table = body.split("Never proposed:")[0]
    assert "storage.googleapis.com" not in table
    assert "Never proposed: Storage" in body


def test_mcp_perRepository_guardBranches_inOrder():
    body = per_repository()
    steps = ["1. `gcloud services enable", "2. `gcloud projects add-iam-policy-binding"]
    steps += ["3. **The read-only guard**", "4. The OAuth client", "5. One line per server", "6. `/mcp` →"]
    positions = [body.index(step) for step in steps]
    assert positions == sorted(positions)
    guards = ("`organizations/…` or `folders/…`", "a second Google identity", "the gate is the only guard")
    for branch in guards:
        assert branch in body, branch


def test_mcp_perRepository_userScope_bareSecret_runsNone():
    body = per_repository()
    command = re.search(r"`(claude mcp add [^`]+)`", body).group(1)
    assert " -s user " in command and "--client-secret --callback-port" in command
    assert "-s local" not in command and "-s project" not in command
    assert "run none of them" in body


def test_mcp_secondIdentity_predefinedRolesOnly():
    body = per_repository()
    assert "roles/serviceusage.serviceUsageConsumer" in body and "never a basic role" in body
    assert "roles/viewer`" not in text(MCP)


# ---------------------------------------------------------------- story 7: knowledge current


@pytest.mark.parametrize(
    "fact",
    [
        "`https://storage.googleapis.com/storage/mcp`",
        "`https://cloudcli.googleapis.com/mcp`",
        "Every token can write",
        "`roles/serviceusage.serviceUsageAdmin`",
        "cannot control a resourceless API",
        "cobot does not support that route",
    ],
)
def test_mcp_factsDated20261121(fact):
    lines = [line for line in text(MCP).splitlines() if fact in line]
    assert any(line.startswith("- [verified ") and "2026-11-21" in line for line in lines), fact


def test_mcp_setupRegistersAtUserScope():
    setup = section(text(MCP), "## Setup, by the owner")
    assert "-s user gcp-logging" in setup and "-s local" not in setup
