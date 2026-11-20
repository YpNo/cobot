"""Debug records are listed (spec debug-path, story 6): `cobot-memory debug list [--open]` reads the
memory folder `cobot-memory path` resolves, foreign mode's outside folder too, and the brief's
findings line ends `; debug: <n> open` from trusted memory only."""

from __future__ import annotations

import test_cobot_memory as base
from test_cobot_memory import remote, seed

repo = base.repo  # the memory tests' fixture: a fresh git repository with its own home

FINDINGS = "# Findings\n\n| # | seen | observation | status |\n|---|---|---|---|\n| F-01 | a | b | open |\n"


def record(folder, name, status, title):
    debug = folder / "debug"
    debug.mkdir(parents=True, exist_ok=True)
    text = f"# Debug — {title}\n\nstatus: {status} · date: 2026-11-20 · owner: o · rounds: 1\n"
    (debug / f"{name}.md").write_text(text)


def listed(memory, capsys, *flags):
    code = memory.main(["debug", "list", *flags])
    return code, capsys.readouterr().out


def test_debugList_statusAndTitle_newestFirst(memory, repo, capsys):
    agent = seed(repo)
    record(agent, "2026-11-19-ci-red", "resolved", "CI red on main")
    record(agent, "2026-11-20-api-crash", "open", "api CrashLoopBackOff")
    code, out = listed(memory, capsys)
    assert code == 0
    lines = out.strip().splitlines()
    assert lines[0].startswith("open") and "2026-11-20-api-crash" in lines[0]
    assert "api CrashLoopBackOff" in lines[0]
    assert lines[1].startswith("resolved") and "CI red on main" in lines[1]


def test_debugList_open_showsOpenOnly(memory, repo, capsys):
    agent = seed(repo)
    record(agent, "2026-11-19-ci-red", "resolved", "CI red")
    record(agent, "2026-11-20-api", "open", "api")
    record(agent, "2026-11-18-old", "unresolved", "old")
    out = listed(memory, capsys, "--open")[1]
    assert "2026-11-20-api" in out and "ci-red" not in out and "old" not in out


def test_debugList_noRecords_saysSo(memory, repo, capsys):
    seed(repo)
    assert listed(memory, capsys) == (0, "debug: no records\n")


def test_debugList_foreignMode_readsTheOutsideFolder(memory, repo, capsys):
    remote(repo, "origin", "https://example.com/Other/proj.git")
    memory.cmd_init(memory.Memory(), {}, {"foreign"})
    outside = memory.Memory().dir.resolve()
    assert repo not in outside.parents
    record(outside, "2026-11-20-api", "open", "api")
    assert "2026-11-20-api" in listed(memory, capsys)[1]


def test_brief_openRecord_endsTheFindingsLine(memory, repo):
    agent = seed(repo)
    (agent / "FINDINGS.md").write_text(FINDINGS)
    record(agent, "2026-11-20-api", "open", "api")
    record(agent, "2026-11-19-ci", "resolved", "ci")
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "## FINDINGS open: 1; debug: 1 open\n" in brief


def test_brief_openRecordWithoutFindings_isOneLine(memory, repo):
    agent = seed(repo)
    record(agent, "2026-11-20-api", "open", "api")
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert brief.rstrip().splitlines()[-1] == "## FINDINGS open: 0; debug: 1 open"


def test_brief_noOpenRecord_noCount(memory, repo):
    agent = seed(repo)
    (agent / "FINDINGS.md").write_text(FINDINGS)
    record(agent, "2026-11-19-ci", "resolved", "ci")
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "## FINDINGS open: 1\n" in brief and "debug:" not in brief


def test_brief_untrustedMemory_showsNoCount(memory, repo):
    agent = seed(repo)
    record(agent, "2026-11-20-api", "open", "api")
    brief = memory.build_brief(memory.Memory(), 6000)
    assert brief.startswith("cobot memory: UNTRUSTED") and "debug" not in brief
