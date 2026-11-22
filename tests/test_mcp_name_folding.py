"""F-54: a never or ask MCP row matches a tool name without case and with `-` and `_` taken as one,
camelCase split into words, so a renamed or hostile server (GCP-run, gcp_run) or a tool spelled
runGcloudCommand cannot step around a refusal. An allow row still matches exactly: folding may add
a refusal or an ask, never lift one (as F-30 does for file rows)."""

from __future__ import annotations

import pytest


def decide(rules, tool):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_mcp(tool, loaded, None).decision


@pytest.mark.parametrize(
    "tool",
    [
        "mcp__GCP-run__deploy_service",
        "mcp__gcp_run__deploy_service",
        "mcp__Gcp-Run__DeployService",
        "mcp__gcp-gke__apply-k8s-manifest",
        "mcp__GCP-cloudcli__list_x",
        "mcp__gcp_cloudcli__get_x",
        "mcp__x__runGcloudCommand",
        "mcp__x__Run_Gcloud_Command",
        "mcp__x__run-bq-command",
        "mcp__x__RUN_BQ_COMMAND",
    ],
)
def test_mcpFolding_renamedOrRespelled_stillRefused(rules, tool):
    assert decide(rules, tool) == "deny", tool


@pytest.mark.parametrize(
    ("tool", "expected"),
    [
        ("mcp__gcp-logging__list_log_entries", None),
        ("mcp__GCP-Logging__ListLogEntries", None),
        ("mcp__gcp-run__scale_service", "ask"),
        ("mcp__context7__get-library-docs", None),
        ("mcp__srv__deploy_service", "ask"),  # not a gcp-* name: asks, not refused
    ],
)
def test_mcpFolding_readsAndOtherServersKeepTheirVerdict(rules, tool, expected):
    assert decide(rules, tool) == expected, tool


@pytest.mark.parametrize(
    "tool",
    [
        "mcp__x__run_gcloud_command__get",  # a second __ made the suffix look like the tool
        "mcp__gcp-run__DEPLOYService",  # an acronym before the next word
        "mcp__gcp-run__SETIamPolicy",
        "mcp__ＧＣＰ-run__deploy_service",  # fullwidth folds to ASCII (NFKC)
        "mcp__gcp-run__ｄeploy_service",
    ],
)
def test_mcpFolding_bypassReviewSpellings_refused(rules, tool):
    assert decide(rules, tool) == "deny", tool


@pytest.mark.parametrize(
    "tool",
    [
        "mcp__gcp-run__scale_service__list",  # not a read: a second __ is not a tool name
        "mcp__srv__get__delete_all",
        "mcp__gcp-run__dеploy_service",  # Cyrillic е: not ASCII, so never a silent read
        "mcp__srv__gеt_status",
    ],
)
def test_mcpFolding_oddNames_neverASilentRead(rules, tool):
    assert decide(rules, tool) == "ask", tool


PLAIN_READS = ["mcp__gcp-logging__list_log_entries", "mcp__srv__GETService", "mcp__srv__get_status"]


@pytest.mark.parametrize("tool", PLAIN_READS)
def test_mcpFolding_plainReadsStaySilent(rules, tool):
    assert decide(rules, tool) is None, tool


def test_mcpFolding_allowRowStaysExact(rules, tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    owner.write_text("allow mcp__my-srv__do_thing\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    assert decide(rules, "mcp__my-srv__do_thing") is None
    assert decide(rules, "mcp__MY_SRV__DoThing") == "ask"  # a fold never reaches an allow


def test_mcpFolding_hostUiToolsStayExact(rules):
    assert decide(rules, "mcp__ccd_turn__update_plan") is None
    assert decide(rules, "mcp__CCD_Turn__UpdatePlan") == "ask"


def test_mcpFolding_ownerAskFolds(rules, tmp_path, monkeypatch):
    owner = tmp_path / "owner.rules"
    owner.write_text("ask mcp__vault__get_secret*\n")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))
    assert decide(rules, "mcp__Vault__getSecretValue") == "ask"
