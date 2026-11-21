"""hass-cli and a Home Assistant configuration under the gate (spec expert-homeassistant, T04).

hass-cli 1.0.0 reads its token from HASS_TOKEN (or HASSIO_TOKEN), HASS_SUPERVISOR_TOKEN and
HASS_PASSWORD; a value on argv or in a literal assignment lands in the transcript. Writes to the
live instance ask; reads stay silent in the main thread only while the server comes from
HASS_SERVER; no read-only agent gets hass-cli. secrets.yaml and .storage/ hold credentials.
"""

from __future__ import annotations

import pytest


def decide(rules, command, agent=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent)[0].decision


@pytest.mark.parametrize(
    "command",
    [
        "hass-cli --token x state list",
        "hass-cli --token=x state list",
        "hass-cli -o json --token x state list",
        "hass-cli --supervisor-token x ha core info",
        "hass-cli --password x state list",
        'hass-cli --token "$HASS_TOKEN" state list',
    ],
)
def test_hassCli_secretOnArgv_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "HASS_TOKEN=x hass-cli state list",
        "export HASS_TOKEN=x",
        "env HASS_TOKEN=x hass-cli state list",
        "export HASSIO_TOKEN=x",
        "HASS_SUPERVISOR_TOKEN=x hass-cli ha core info",
        "export HASS_PASSWORD='x'",
        "declare -x HASS_TOKEN=x",
    ],
)
def test_hassCli_literalSecretAssignment_isRefused(rules, command):
    assert decide(rules, command) == "deny"


def test_hassCli_serverAssignment_isNotRefused(rules):
    """Setting the server names no secret; it asks (test_secret_reads_gate.py), never refuses."""
    assert decide(rules, "export HASS_SERVER=http://homeassistant.local:8123") != "deny"


@pytest.mark.parametrize(
    "command",
    [
        "hass-cli service call light.turn_on --arguments entity_id=light.kitchen",
        "hass-cli -o json service call light.turn_on",
        "hass-cli --timeout 5 state edit light.kitchen on",
        "hass-cli state delete sensor.old",
        "hass-cli state toggle light.kitchen",
        "hass-cli state turn_on light.kitchen",
        "hass-cli state turn_off light.kitchen",
        "hass-cli event fire my_event",
        "hass-cli raw post /api/services/light/turn_on",
        "hass-cli raw ws config/device_registry/update",
        "hass-cli entity rename light.a light.b",
        "hass-cli entity assign kitchen light.a",
        "hass-cli entity delete light.a",
        "hass-cli entity disable light.a",
        "hass-cli entity enable light.a",
        "hass-cli device assign kitchen lamp",
        "hass-cli device rename lamp lamp2",
        "hass-cli device delete lamp",
        "hass-cli area create attic",
        "hass-cli area delete attic",
        "hass-cli area rename attic loft",
        "hass-cli integration reload abc",
        "hass-cli integration delete abc",
        "hass-cli integration disable abc",
        "hass-cli integration enable abc",
        "hass-cli ha core restart",
        "hass-cli ha host reboot",
        "hass-cli ha core info",
        "hass-cli discover",
        "hass-cli map",
        "hass-cli --insecure state list",
        "hass-cli --debug state list",
        "hass-cli -s https://other.example state list",
        "hass-cli -o json -s http://ha.local:8123 state list",
        "hass-cli --server=https://other.example state list",
        "hass-cli -vs https://other.example state list",
    ],
)
def test_hassCli_writeOrTokenExposure_asksInMainThread(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "hass-cli state list",
        "hass-cli -o json state get light.kitchen",
        "hass-cli --sort-by last_changed state list",
        "hass-cli entity list",
        "hass-cli device list",
        "hass-cli area list",
        "hass-cli service list",
        "hass-cli system log",
        "hass-cli config release",
        "hass-cli info",
    ],
)
def test_hassCli_readWithServerFromEnvironment_isSilentInMainThread(rules, command):
    assert decide(rules, command) is None


@pytest.mark.parametrize(
    "agent", ["cobot:consultant", "cobot:learner", "cobot:investigator", "cobot:auditor"]
)
def test_hassCli_read_asksForReadOnlyAgents(rules, agent):
    assert decide(rules, "hass-cli state list", agent) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "cat config/secrets.yaml",
        "cat secrets.yaml",
        "cat -n ./secrets.yaml",
        "head -20 config/secrets.yaml",
        "tail secrets.yaml",
        "grep -n api config/secrets.yaml",
        "rg api secrets.yaml",
        "yq . secrets.yaml",
        "sort secrets.yaml",
        "diff secrets.yaml old.yaml",
        "git show HEAD:secrets.yaml",
        "git diff HEAD~1 -- secrets.yaml",
        "jq . .storage/auth",
        "cat config/.storage/core.config_entries",
        "grep -r token .storage/",
        "grep -e api secrets.yaml",
        "grep --regexp=api secrets.yaml",
        "jq -r .x .storage/core.config_entries",
    ],
)
@pytest.mark.parametrize("agent", ["cobot:consultant", "cobot:learner", "cobot:investigator"])
def test_secretFile_readByAgent_isRefused(rules, command, agent):
    assert decide(rules, command, agent) == "deny"


@pytest.mark.parametrize(
    "command", ['for f in $(git ls-files); do cat "$f"; done', "git log $(git merge-base main HEAD)"]
)
def test_secretFile_rows_leaveMainThreadSubstitutionsSilent(rules, command):
    """No main-thread row on the readers: a wildcard ask would make any substituted argument ask."""
    assert decide(rules, command) is None


@pytest.mark.parametrize("command", ["cat ./k8s/*.yaml", "grep -rn x --include=*.py ."])
def test_secretFile_check_leavesAnchoredGlobReadsSilentForAgent(rules, command):
    """The residual: a glob that could expand to secrets.yaml is not judged as naming it."""
    assert decide(rules, command, "cobot:consultant") is None


@pytest.mark.parametrize("agent", [None, "cobot:python-builder"])
def test_secretFile_readOutsideReadOnlyAgents_isNotRefused(rules, agent):
    assert decide(rules, "cat config/secrets.yaml", agent) != "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git ls-files secrets.yaml",
        "git ls-files --error-unmatch config/secrets.yaml",
        "cat .gitignore",
        "git ls-files | grep secrets.yaml",
        "grep -n secrets.yaml .gitignore",
        "jq '.secrets.yaml' ./config.json",
    ],
)
@pytest.mark.parametrize("agent", [None, "cobot:consultant"])
def test_secretFile_namedWithoutReading_staysSilent(rules, command, agent):
    assert decide(rules, command, agent) is None


@pytest.mark.parametrize(
    "command",
    [
        "hass --script check_config -c .",
        "pip install -r requirements.txt",
        "uv pip install -r requirements.txt",
    ],
)
def test_integrationCode_runByConsultant_asks(rules, command):
    assert decide(rules, command, "cobot:consultant") == "ask"
