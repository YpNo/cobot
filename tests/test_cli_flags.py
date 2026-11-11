"""CLI hygiene: --help never runs a command, unknown flags are refused (spec new-project, story 7)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import _cobot_common as common
import pytest
from conftest import BIN, PLUGIN, REPO, load_script

BINS = ("cobot-memory", "cobot-rules", "cobot-deps")
FLAG_MENTION = re.compile(r"cobot-(memory|rules|deps)[ \t]+([a-z]+)([^\"'`|;&)\n]*)")


@pytest.fixture(scope="module")
def scripts():
    return {name: load_script(name, name.replace("-", "_") + "_cli") for name in BINS}


def run(name, *args, cwd):
    argv = [sys.executable, "-I", str(BIN / name), *args]
    return subprocess.run(argv, capture_output=True, text=True, cwd=cwd, check=False)


def test_help_afterInit_printsUsageWritesNothing(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for flag in ("--help", "-h"):
        out = run("cobot-memory", "init", flag, cwd=tmp_path)
        assert out.returncode == 0 and "Commands" in out.stdout
    assert not (tmp_path / ".agent").exists()


@pytest.mark.parametrize("name", BINS)
def test_help_bareAndAfterACommand_exitZeroOnStdout(scripts, name, capsys):
    module = scripts[name]
    command = {"cobot-memory": "check", "cobot-rules": "show", "cobot-deps": "check"}[name]
    for argv in (["--help"], [command, "--help"], [command, "-h"]):
        assert module.main(argv) == 0
        assert "Commands" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("name", "argv"),
    [
        ("cobot-memory", ["init", "--bogus"]),
        ("cobot-memory", ["brief", "--spec", "x"]),
        ("cobot-memory", ["journal", "add", "--force"]),
        ("cobot-rules", ["check", "ls", "--bogus", "x"]),
        ("cobot-rules", ["sync", "--tool", "Bash"]),
        ("cobot-deps", ["check", "--bogus"]),
    ],
)
def test_unknownFlag_isRefusedWithUsage(scripts, name, argv, capsys):
    assert scripts[name].main(argv) == 2
    err = capsys.readouterr().err
    assert "unknown option --" in err and "Commands" in err


def test_unknownFlag_valueOptionWithoutValue_isRefused(scripts, capsys):
    assert scripts["cobot-memory"].main(["init", "--profile"]) == 2
    assert "--profile needs a value" in capsys.readouterr().err


def test_profile_onlyTheSixAreAccepted(scripts, tmp_path, monkeypatch, capsys):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    for bad in ("embedded", "Library", ""):
        assert scripts["cobot-memory"].main(["init", "--profile", bad]) == 2
        assert "profile must be one of spike, script, cli, library, service, infra" in capsys.readouterr().err
    assert not (tmp_path / ".agent").exists()


def test_parseCli_valuesSwitchesAndPositionals():
    positional, options, flags = common.parse_cli(
        ["learn", "--promote", "--source", ".", "--in-place", "lang-rust"],
        {"learn": {"source"}},
        {"learn": {"promote", "in-place"}},
    )
    assert positional == ["learn", "lang-rust"]
    assert options == {"source": "."}
    assert flags == {"promote", "in-place"}


def test_parseCli_valueMayStartWithDashes():
    _, options, _ = common.parse_cli(["compact", "--summary", "--odd text"], {"compact": {"summary"}}, {})
    assert options == {"summary": "--odd text"}


def mentions():
    roots = [PLUGIN / "hooks", PLUGIN / "skills", PLUGIN / "agents", REPO / "scripts"]
    roots.append(REPO / ".github" / "workflows")
    tree = [p for root in roots if root.is_dir() for p in root.rglob("*") if p.is_file()]
    files = [PLUGIN / "protocol.md", *tree]
    found = set()
    for path in files:
        for name, command, tail in FLAG_MENTION.findall(path.read_text(encoding="utf-8", errors="replace")):
            for flag in re.findall(r"(?<!\S)--([a-z][a-z-]*)", tail):
                found.add((f"cobot-{name}", command, flag, path.name))
    return sorted(found)


def test_flagsInUse_everyMentionedFlagIsAccepted(scripts):
    tables = {name: (scripts[name].VALUE_OPTIONS, scripts[name].SWITCHES) for name in BINS}
    found = mentions()
    assert found, "the collector found no mention at all"
    for name, command, flag, where in found:
        values, switches = tables[name]
        accepted = values.get(command, set()) | switches.get(command, set())
        assert flag in accepted, f"{name} {command} --{flag} ({where})"


def test_flagsInUse_sessionArgumentListsParse(scripts, session):
    source = Path(session.__file__).read_text(encoding="utf-8")
    calls = re.findall(r'run_tool\("(cobot-[a-z]+)", \[([^\]]*)\]', source)
    assert len(calls) >= 4
    for name, args in calls:
        argv = [a.strip().strip('"') for a in args.split(",")]
        argv = [a if not a.startswith("str(") else "1" for a in argv]
        common.parse_cli(argv, scripts[name].VALUE_OPTIONS, scripts[name].SWITCHES)
