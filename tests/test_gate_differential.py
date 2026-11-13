"""The gate against bash itself (.agent/specs/gate-substitution.md, story 5).

Each corpus command runs under ``env -i PATH=<stubs> bash --norc --noprofile -c`` in a fresh
directory. Every external command the corpus can reach is a stub that logs its argv and does
nothing else (no network, no file outside the directory, wrapper stubs never exec their inner
command). For every argv bash ran, the literal judge's verdict is computed; when it asks or denies,
the gate must not be silent on the whole command.

Scope: this validates the decomposition into external argv only. Builtins and arithmetic that run
code (``printf -v``, ``$((x))`` on a quoted subscript, ``${x@P}``) run inside bash and log nothing
unless they reach a stub; they are unit rows in ``test_cobot_rules.py``.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess

import pytest
from test_cobot_rules import BYPASSES_CLOSED, SUBSTITUTION_JUDGED, SUBSTITUTION_SILENT

BASH = shutil.which("bash")
SH = shutil.which("sh")
STUBS = (
    "basename cat cobot-memory curl date diff direnv dirname distrobox docker find gcloud gh git glab "
    "grep head kubectl ls make mktemp python3 sed sort tail tee terraform terragrunt uname wc xargs"
).split()
RECORD_SEP = "\x1e"
TIMEOUT_SECONDS = 10

pytestmark = pytest.mark.skipif(BASH is None or SH is None, reason="bash and sh are needed")

CORPUS = sorted(
    {*SUBSTITUTION_SILENT, *(command for command, _ in SUBSTITUTION_JUDGED), *(c for c, _ in BYPASSES_CLOSED)}
)


@pytest.fixture(scope="module")
def stub_path(tmp_path_factory):
    directory = tmp_path_factory.mktemp("stubs")
    for name in STUBS:
        stub = directory / name
        # builtins only: a stub calling another stub (``basename``) would recurse without end
        stub.write_text(
            f'#!{SH}\n{{ printf "%s\\n" "${{0##*/}}"; for a in "$@"; do printf "%s\\n" "$a"; done; '
            f'printf "{RECORD_SEP}\\n"; }} >> "$STUB_LOG"\n'
        )
        stub.chmod(0o755)
    return directory


def ran(command: str, stubs, workdir) -> list[list[str]]:
    """The argv of every stub bash ran for the command."""
    log = workdir / "stub.log"
    log.write_text("")
    env = {"PATH": str(stubs), "STUB_LOG": str(log), "HOME": str(workdir)}
    subprocess.run(  # noqa: S603 - fixed bash, corpus strings under stubs only
        [BASH, "--norc", "--noprofile", "-c", command],
        cwd=workdir,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    records = log.read_text().split(RECORD_SEP + "\n")
    return [record.rstrip("\n").split("\n") for record in records if record.strip()]


@pytest.mark.parametrize("command", CORPUS)
def test_gate_neverSilentWhereBashRanAJudgedCommand(rules, stub_path, tmp_path, command):
    loaded, _, _ = rules.load_rules(None)
    whole = rules.judge_bash(command, loaded, None, str(tmp_path))[0].decision
    for argv in ran(command, stub_path, tmp_path):
        literal = rules.judge_bash(shlex.join(argv), loaded, None, str(tmp_path))[0].decision
        if literal is not None:
            assert whole is not None, f"bash ran {argv!r} ({literal}); the gate was silent on {command!r}"


def test_stubs_logArgvAndRunNothingElse(stub_path, tmp_path):
    assert ran("git push --force origin 'a b'", stub_path, tmp_path) == [
        ["git", "push", "--force", "origin", "a b"]
    ]
    assert ran("x='a[$(git push --force)]'; echo $((x))", stub_path, tmp_path) == [["git", "push", "--force"]]
