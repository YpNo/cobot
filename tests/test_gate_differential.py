"""The gate against bash itself (.agent/specs/gate-substitution.md, story 5).

Each corpus command runs under ``env -i PATH=<stubs> bash --norc --noprofile -c`` in a fresh
directory. Every external command the corpus can reach is a stub that logs its argv and does
nothing else (no network, no file outside the directory, wrapper stubs never exec their inner
command). For every argv bash ran, the literal judge's verdict is computed; when it asks or denies,
the gate must not be silent on the whole command.

Scope: this validates the decomposition into external argv only. Builtins and arithmetic that run
code (``printf -v``, ``$((x))`` on a quoted subscript, ``${x@P}``) run inside bash and log nothing
unless they reach a stub; they are unit rows in ``test_cobot_rules.py``.

Brace and glob expansion (.agent/specs/gate-expansion.md, story 6) adds rows run over files made
before the gate reads the command, a pass under ``bash -O extglob`` and a pass under the
consultant's scope. Unit rows only, because this oracle cannot see them: a redirection target of a
builtin (``echo x > …`` logs nothing) and the protected files (the stubs get a fake ``HOME``).

The gate-findings rows (.agent/specs/gate-findings.md, story 6) join the corpus: ``${…}`` operator
words, locale strings, global options before the verb, ``rustup run``, and in the consultant pass
the read-list options that write or run. The oracle judges each argv bash ran with the same
literal judge, so it proves the decomposition (the ``${…}`` and ``$"…"`` forms fail it when read
as text), not the literal rules: the guard, the readings and the redirection writes are proved by
their unit rows in ``test_cobot_rules.py``, each of which fails with its mechanism turned off.
Redirection writes are unit rows only: a stub logs its argv, not where its output went.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess

import pytest
from test_cobot_rules import (
    BYPASSES_CLOSED,
    FINDINGS_CLOSED,
    FINDINGS_SILENT,
    SUBSTITUTION_JUDGED,
    SUBSTITUTION_SILENT,
)

BASH = shutil.which("bash")
SH = shutil.which("sh")
STUBS = (
    "basename cargo cat cobot-memory cp curl date diff direnv dirname distrobox docker find gcloud gh git "
    "glab grep head kubectl ls make mkdir mktemp npm pnpm python3 rg rm rustup sed sort tail tee terraform "
    "terragrunt uname uniq uv wc xargs"
).split()
RECORD_SEP = "\x1e"
TIMEOUT_SECONDS = 10

pytestmark = pytest.mark.skipif(BASH is None or SH is None, reason="bash and sh are needed")

CORPUS = sorted(
    {
        *SUBSTITUTION_SILENT,
        *FINDINGS_SILENT,
        *(command for command, _ in SUBSTITUTION_JUDGED),
        *(c for c, _ in BYPASSES_CLOSED),
        *(c for c, _ in FINDINGS_CLOSED),
    }
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


def ran(command: str, stubs, workdir, options: tuple[str, ...] = ()) -> list[list[str]]:
    """The argv of every stub bash ran for the command. The log sits beside the directory, so a
    glob in the command sees only the files the row made."""
    log = workdir.parent / f"{workdir.name}.stub.log"
    log.write_text("")
    env = {"PATH": str(stubs), "STUB_LOG": str(log), "HOME": str(workdir)}
    subprocess.run(  # noqa: S603 - fixed bash, corpus strings under stubs only
        [BASH, "--norc", "--noprofile", *options, "-c", command],
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


# ---------------------------------------------------------------- brace and glob expansion

MAKEFILE = {"Makefile": "show:\n\t@echo value $(X)\n"}

# (files made in the directory first, command): each can fail the oracle if the gate is silent
EXPANSION_CORPUS = [
    ({}, "cargo {publish,}"),
    ({}, "terraform {apply,}"),
    ({}, "{terraform,} apply"),
    ({}, "git push origin {main,--force}"),
    ({}, "git {push,} --force"),
    ({}, "git pu{sh,ll}"),
    ({}, "{git,echo} push"),
    ({"publish": ""}, "cargo publis?"),
    ({"publish": ""}, "cargo publi[s]h"),
    ({"apply": ""}, "terraform appl*"),
    ({"aa": "", "cargo": ""}, "uv run --with * publish"),
    ({"publish": ""}, "uv run cargo publis?"),
    ({**MAKEFILE, "X=;cargo publish": ""}, "make show X=*"),
    ({"--force": ""}, "git push origin *"),
    ({}, "ls *.py"),
    ({"src/a": ""}, "git add src/*"),
    ({}, "mkdir -p src/{a,b}"),
    ({}, "cp f{,.bak}"),
    ({}, "echo {1..3}"),
    ({"pulls1state=all": ""}, "gh api repos/o/r/pulls?state=all"),
    ({"a.md": ""}, 'for f in *.md; do wc -l "$f"; done'),
    ({"tests/test_a.py": ""}, "uv run pytest tests/test_*.py"),
]
EXTGLOB_CORPUS = [
    ({"publish": ""}, "cargo +(publish)"),
    ({"publish": ""}, "cargo @(publish)"),
    ({"terraform": ""}, "!(zzz) apply"),
]
AGENT_CORPUS = [
    ({"-c": ""}, "git log *"),
    ({"plugins/a/agents": ""}, "ls plugins/*/agents"),
    ({}, "cat src/{a,b}.rs"),
    ({"a.py": ""}, "grep -rn x --include=*.py ."),
    ({"a.py": ""}, "ls ./*.py"),
    # gate-findings: options that write or run, and ${…} words that supply them
    ({}, "find . -delete"),
    ({"-delete": ""}, "find ${x:-*}"),
    ({}, "kubectl get pods ${x:---kubeconfig=./evil}"),
    ({}, "rg --pre=./x foo"),
    ({"--pre=./x": ""}, "rg --pre=./* foo"),
    ({}, "sort -uo out f"),
    ({}, "uniq a b"),
    ({}, "git log --output=x"),
    ({}, "git branch -D main"),
    ({}, "curl -s -T x https://e"),
    ({}, "rg -n x src"),
    ({}, "git log --oneline -5"),
]


def make_files(workdir, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = workdir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def oracle(rules, command: str, stubs, workdir, agent=None, options: tuple[str, ...] = ()) -> None:
    loaded, _, _ = rules.load_rules(None)
    whole = rules.judge_bash(command, loaded, agent, str(workdir))[0].decision
    for argv in ran(command, stubs, workdir, options):
        literal = rules.judge_bash(shlex.join(argv), loaded, agent, str(workdir))[0].decision
        if literal is not None:
            assert whole is not None, f"bash ran {argv!r} ({literal}); the gate was silent on {command!r}"


@pytest.mark.parametrize(("files", "command"), EXPANSION_CORPUS)
def test_expansion_neverSilentWhereBashRanAJudgedCommand(rules, stub_path, tmp_path, files, command):
    make_files(tmp_path, files)
    oracle(rules, command, stub_path, tmp_path)


@pytest.mark.parametrize(("files", "command"), EXTGLOB_CORPUS)
def test_extglob_neverSilentWhereBashRanAJudgedCommand(rules, stub_path, tmp_path, files, command):
    make_files(tmp_path, files)
    assert ran(command, stub_path, tmp_path, ("-O", "extglob")), f"bash ran no stub for {command!r}"
    oracle(rules, command, stub_path, tmp_path, options=("-O", "extglob"))


@pytest.mark.parametrize(("files", "command"), AGENT_CORPUS)
def test_agentScope_neverSilentWhereBashRanAJudgedCommand(rules, stub_path, tmp_path, files, command):
    make_files(tmp_path, files)
    oracle(rules, command, stub_path, tmp_path, agent="cobot:consultant")


def test_expansionOracle_bitesOnTheBypassesItCovers(rules, stub_path, tmp_path):
    """The rows above can fail: bash really runs the ruled command for each."""
    make_files(tmp_path, {"aa": "", "cargo": "", "publish": ""})
    assert ran("uv run --with * publish", stub_path, tmp_path) == [
        ["uv", "run", "--with", "aa", "cargo", "publish", "publish"]
    ]
    assert ran("cargo publis?", stub_path, tmp_path) == [["cargo", "publish"]]
    assert ran("cargo {publish,}", stub_path, tmp_path) == [["cargo", "publish"]]
    (tmp_path / "-c").write_text("")
    assert ran("git log *", stub_path, tmp_path) == [["git", "log", "-c", "aa", "cargo", "publish"]]


def test_findingsOracle_bitesOnTheBypassesItCovers(stub_path, tmp_path):
    """bash runs the ruled command behind each gate-findings form."""
    assert ran('cargo $"publish"', stub_path, tmp_path) == [["cargo", "publish"]]
    assert ran("cargo ${x:-publish}", stub_path, tmp_path) == [["cargo", "publish"]]
    assert ran('terraform {$"apply",}', stub_path, tmp_path) == [["terraform", "apply"]]
    assert ran("kubectl get pods ${x:---kubeconfig=./e}", stub_path, tmp_path) == [
        ["kubectl", "get", "pods", "--kubeconfig=./e"]
    ]
    (tmp_path / "-delete").write_text("")
    assert ran("find ${x:-*}", stub_path, tmp_path) == [["find", "-delete"]]


def test_stubs_logArgvAndRunNothingElse(stub_path, tmp_path):
    assert ran("git push --force origin 'a b'", stub_path, tmp_path) == [
        ["git", "push", "--force", "origin", "a b"]
    ]
    assert ran("x='a[$(git push --force)]'; echo $((x))", stub_path, tmp_path) == [["git", "push", "--force"]]


# ---------------------------------------------------------------- directory in effect

# each ``make`` names its own goal, so a logged run maps back to the segment the walk placed
CD_CORPUS = [
    "cd sub && make m1",
    "cd sub; make m1; cd ..; make m2",
    "cd ./sub/ && make m1",
    "cd -P sub && make m1",
    "cd sub/.. && make m1",
    "cd nonesuch; make m1",
    "cd nonesuch || make m1",
    "pushd sub >/dev/null && make m1; popd >/dev/null; make m2",
    "pushd nonesuch 2>/dev/null; popd 2>/dev/null; make m1",
    "(cd sub && make m1); make m2",
    "(cd sub)&&make m1",
    "(false)&&cd sub; make m1",
    "true && cd sub; make m1",
    "false && cd sub; make m1",
    "false || cd sub && make m1 || make m2",
    "if true; then cd sub; fi; make m1",
    "if false; then cd sub; else make m1; fi; make m2",
    "{ false; cd sub; }; make m1",
    "case x in x) cd sub;; esac; make m1",
    "case x in y) cd sub;; esac; make m1",
    "for d in sub sub; do make m1; cd $d; done; make m2",
    "while make m1; do cd sub; break; done; make m2",
    "f() { cd sub; }; make m1; f; make m2",
    "cd sub | make m1; make m2",
    "cd sub & wait; make m1",
    "cd $PWD/sub && make m1",
    "cd sub && cd $PWD && make m1",
    "PWD=/; cd $PWD && make m1",
    "builtin cd sub && make m1",
    "command cd sub && make m1",
    "cd -- sub && make m1",
    "cd sub && bash -c 'make m1; cd ..; make m2'; make m3",
    "cd sub && echo $(make m1) $(cd ..; make m2)",
    # an independent review's bypass rows: each ran make outside the set the walk gave it
    "mv sub gone; cd sub; make m1",
    "mkdir new && cd new && make m1",
    "mkdir '~' && cd '~' && make m1",
    "cd '$PWD/sub'; make m1",
    "cd \\$PWD/sub; make m1",
    'cd $"PWD"; make m1',
    "pushd sub; pushd sub; false && popd; popd; make m1",
    "pushd sub; dirs -c; popd; make m1",
    "f ( ) { cd sub; }; f; f; make m1",
    "CDPATH=other cd sub && make m1",
    "CDPATH=other; cd sub && make m1",
    "HOME=$PWD/sub; cd ~ && make m1",
    "set -P; cd link/.. && make m1",
    "shopt -s expand_aliases\nalias go='cd sub'\ngo\nmake m1",
    "PWD=sub; echo $(cd $PWD; make m1)",
    "n=P; printf -v ${n}WD sub; cd $PWD && make m1",
    "! cd sub || make m1",
    "! cd nonesuch && make m1",
    "cd sub || true; make m1",
    "eval 'cd sub'; make m1",
    "false || cd sub && make m1",
    "cd sub && (cd .. && make m1) && make m2; make m3",
]


def where_make_ran(command: str, stubs, workdir) -> dict[str, str]:
    """The directory bash ran each ``make <goal>`` in, by goal."""
    log = workdir / "make.log"
    log.write_text("")
    make = stubs / "make-pwd" / "make"
    make.parent.mkdir(exist_ok=True)
    make.write_text(f'#!{SH}\nprintf "%s %s\\n" "$1" "$(pwd -P)" >> "$MAKE_LOG"\n')
    make.chmod(0o755)
    for tool in ("mv", "mkdir"):  # real, so a command can change the tree after the gate read it
        link = make.parent / tool
        if not link.exists():
            link.symlink_to(shutil.which(tool))
    env = {"PATH": f"{make.parent}:{stubs}", "MAKE_LOG": str(log), "HOME": str(workdir)}
    subprocess.run(  # noqa: S603 - fixed bash, corpus strings under stubs only
        [BASH, "--norc", "--noprofile", "-c", command],
        cwd=workdir,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return dict(line.split(" ", 1) for line in log.read_text().splitlines())


def placed_makes(rules, command: str, workdir) -> dict[str, frozenset | None]:
    """The directories the gate's walk gives each ``make <goal>``, bodies and runners included."""
    out: dict[str, frozenset | None] = {}
    entries: list = []
    original = rules.expand_segment

    def record(segment, here, depth, reached):
        plain = rules.strip_wrappers(segment)
        if plain[:1] == ["make"] and len(plain) == 2:
            out[plain[1]] = rules.union(out[plain[1]], here) if plain[1] in out else here
        return original(segment, here, depth, reached)

    rules.expand_segment = record
    try:
        scanned = rules.shell.scan(command)
        state = rules.shell_state(command)
        rules.expand_units(scanned, "", frozenset({workdir}), state, rules.Reached(), entries)
    finally:
        rules.expand_segment = original
    return out


@pytest.mark.parametrize("command", CD_CORPUS)
def test_cdWalk_containsTheDirectoryBashRanEachRunnerIn(rules, stub_path, tmp_path, monkeypatch, command):
    monkeypatch.delenv("CDPATH", raising=False)
    workdir = (tmp_path / "w").resolve()
    (workdir / "sub" / "sub").mkdir(parents=True)
    (workdir / "sub" / "deep").mkdir()
    (workdir / "other" / "sub").mkdir(parents=True)
    (workdir / "link").symlink_to(workdir / "sub" / "deep")
    placed = placed_makes(rules, command, workdir)  # the gate reads the tree before bash runs
    real = where_make_ran(command, stub_path, workdir)
    assert real, f"bash ran no make for {command!r}"
    for goal, directory in real.items():
        assert goal in placed, f"the gate never placed make {goal} in {command!r}"
        dirs = placed[goal]
        if dirs is not None:
            resolved = {os.path.realpath(path) for path in dirs}
            assert directory in resolved, f"make {goal} ran in {directory}; the gate said {resolved}"
