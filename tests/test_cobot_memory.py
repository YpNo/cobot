"""cobot-memory: init, trust, brief, journal, findings, learn, check; cobot-session payload."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import date

import pytest

LONG_PROOF = "Proof: " + "x" * 3000


@pytest.fixture
def repo(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(home / ".claude"))
    monkeypatch.setenv("XDG_DATA_HOME", str(home / ".local" / "share"))
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    monkeypatch.delenv("COBOT_RULES_OWNER", raising=False)
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@x"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    monkeypatch.chdir(root)
    return root


def commit(root):
    (root / "a").write_text("a")
    subprocess.run(["git", "-C", str(root), "add", "a"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)


def remote(root, name, url):
    subprocess.run(["git", "-C", str(root), "remote", "add", name, url], check=True)


def config(name):
    return os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "cobot", name)


def write_config(name, text):
    path = config(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)


# ---------------------------------------------------------------- init and trust


def test_init_writesTemplatesOnce(memory, repo):
    mem = memory.Memory()
    out = memory.cmd_init(mem, {"profile": "cli"}, set())
    assert out.count("wrote") == 3
    assert "profile: cli" in (repo / ".agent" / "CONTEXT.md").read_text()
    assert "# Journal" in (repo / ".agent" / "JOURNAL.md").read_text()
    assert memory.cmd_init(mem, {}, set()).count("kept") == 3


def test_trust_noRemoteNoCommit_untrusted(memory, repo):
    trusted, reason = memory.Memory().trust()
    assert not trusted and "no remote and no commit" in reason


def test_trust_identityCoversEveryRemote(memory, repo):
    remote(repo, "origin", "git@github.com:YpNo/thing.git")
    write_config("identities", "github.com/ypno\n")
    assert memory.Memory().trust()[0]
    remote(repo, "upstream", "https://github.com/juanfont/thing")
    trusted, reason = memory.Memory().trust()
    assert not trusted and "no identity matches every remote" in reason
    assert "(upstream -> github.com/juanfont)" in reason and "origin" not in reason
    write_config("identities", "github.com/ypno\ngithub.com/juanfont\n")
    assert memory.Memory().trust()[0]


def test_trust_rootCommitListedOutsideRepo(memory, repo):
    commit(repo)
    assert not memory.Memory().trust()[0]
    (repo / ".agent").mkdir()
    (repo / ".agent" / ".trusted").write_text("planted")  # a clone can ship this; it must not count
    assert not memory.Memory().trust()[0]
    mem = memory.Memory()
    assert "root commit added" in memory.add_trusted_root(mem)
    assert "already present" in memory.add_trusted_root(mem)
    trusted, reason = mem.trust()
    assert trusted and "trusted" in reason


def test_init_foreign_symlinksAndExcludes(memory, repo):
    remote(repo, "origin", "ssh://git@gitea.example.com:2222/Other/proj.git")
    mem = memory.Memory()
    out = memory.cmd_init(mem, {}, {"foreign"})
    assert "foreign mode" in out
    assert (repo / ".agent").is_symlink()
    expected = os.path.join(
        os.environ["XDG_DATA_HOME"], "cobot", "repos", "gitea.example.com", "other", "proj"
    )
    assert os.path.realpath(repo / ".agent") == os.path.realpath(expected)
    assert ".agent" in (repo / ".git" / "info" / "exclude").read_text()
    assert memory.Memory().trust() == (True, "foreign mode, memory outside the tree")
    assert "kept" in memory.cmd_init(memory.Memory(), {}, {"foreign"})


def test_init_foreign_refusesWithoutOriginOrOverExistingDir(memory, repo):
    assert "needs an origin" in memory.cmd_init(memory.Memory(), {}, {"foreign"})
    remote(repo, "origin", "git@github.com:a/b.git")
    (repo / ".agent").mkdir()
    assert "not a symlink" in memory.cmd_init(memory.Memory(), {}, {"foreign"})


def test_trust_symlinkToWrongPlace_untrusted(memory, repo, tmp_path):
    remote(repo, "origin", "git@github.com:a/b.git")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (repo / ".agent").symlink_to(elsewhere)
    trusted, reason = memory.Memory().trust()
    assert not trusted and "does not resolve" in reason


def test_init_addIdentity(memory, repo):
    assert "no origin" in memory.add_identity(memory.Memory())
    remote(repo, "origin", "https://github.com/YpNo/x")
    assert "identity added: github.com/ypno" in memory.cmd_init(memory.Memory(), {}, {"add-identity"})
    assert "already present" in memory.add_identity(memory.Memory())
    commit(repo)
    assert "root commit added" in memory.cmd_init(memory.Memory(), {}, {"trust-root"})
    assert "no commit yet" not in memory.add_trusted_root(memory.Memory())


# ---------------------------------------------------------------- brief


def seed(repo, journal=None, context="# x\n\nprofile: cli\ngoal: g\n\n## Shape\n- hidden\n"):
    agent = repo / ".agent"
    agent.mkdir(exist_ok=True)
    (agent / "CONTEXT.md").write_text(context)
    (agent / "JOURNAL.md").write_text(
        journal or "# Journal\n\n## 2026-01-01 — one\nChanged: a\nWhy: b\nProof: c\nOpen: —\nNext: n1\n"
    )
    return agent


def test_brief_untrusted_isOneLine(memory, repo):
    seed(repo)
    brief = memory.build_brief(memory.Memory(), 6000)
    assert brief.startswith("cobot memory: UNTRUSTED")
    assert "profile" not in brief


def test_brief_contentAndShapeHidden(memory, repo):
    seed(repo)
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "profile: cli" in brief and "hidden" not in brief
    assert "## JOURNAL (latest)" in brief and "n1" in brief


def test_brief_picksLatestTwoEntriesInLegacyOrder(memory, repo):
    journal = (
        "# J\n\n## 2026-03-01 — newest\nChanged: c3\nWhy: w\nProof: p\n\n"
        "## 2026-02-01 — mid\nChanged: c2\n\n## 2026-01-01 — old\nChanged: c1\n"
    )
    seed(repo, journal)
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "c3" in brief and "c2" in brief and "c1" not in brief
    assert brief.index("newest") < brief.index("mid")


def test_brief_trimsLongEntryKeepingOpenAndNext(memory, repo):
    journal = f"# J\n\n## 2026-01-01 — big\nChanged: c\nWhy: w\n{LONG_PROOF}\nOpen: o-line\nNext: n-line\n"
    seed(repo, journal)
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "o-line" in brief and "n-line" in brief and "(entry truncated)" in brief
    assert len(brief) < 2500


def test_trimEntry_multiLineField_keepsContinuationWithItsField(memory):
    # the legacy journal layout (arlo-camera-streamer-rs): a field, then indented continuation lines
    entry = (
        "## 2026-01-01 — legacy\n"
        "Changed:  first change line\n"
        "  change continued\n"
        "Why: because\n"
        "  why continued\n"
        "Proof: " + "p" * 1100 + "\n"
        "Next: n-line"
    )
    lines = memory.trim_entry(entry).splitlines()
    assert lines[1] == "Next: n-line"
    assert lines[lines.index("Changed:  first change line") + 1] == "  change continued"
    assert lines[lines.index("Why: because") + 1] == "  why continued"


def test_brief_findingsFloorAndTail(memory, repo):
    agent = seed(repo, journal="# J\n\n## 2026-01-01 — e\n" + "Changed: " + "y" * 7000 + "\n")
    rows = "".join(f"| F-{i:02d} | s{i} | obs{i} | |\n" for i in range(1, 6))
    (agent / "FINDINGS.md").write_text(
        "# F\n| # | Seen | Observation | Goes to |\n|---|---|---|---|\n"
        + rows
        + "| F-06 | s | o | closed — x |\n"
    )
    (agent / "knowledge").mkdir()
    (agent / "knowledge" / "gha.md").write_text("# k\n")
    (agent / "specs").mkdir()
    (agent / "specs" / "r1.md").write_text("# s\n")
    (agent / "ARCHITECTURE.md").write_text("# a\n")
    brief = memory.build_brief(memory.Memory(), 3000, trust_check=False)
    assert "## FINDINGS open: 5" in brief and "F-05" in brief and "F-01" not in brief
    assert "knowledge: gha" in brief and "specs: r1" in brief and "ARCHITECTURE.md present" in brief
    assert "(entry truncated)" in brief
    assert len(brief) <= 3000 + 600


def test_brief_longContextIsCapped(memory, repo):
    seed(repo, context="# x\n\nprofile: cli\n" + "\n".join(f"- constraint {i}" for i in range(400)))
    brief = memory.build_brief(memory.Memory(), 1500, trust_check=False)
    assert "(truncated)" in brief and len(brief) <= 1500 + 200


def test_brief_emptyMemory(memory, repo):
    assert memory.build_brief(memory.Memory(), 6000, trust_check=False) == ""


# ---------------------------------------------------------------- journal and findings


def test_journalAdd_validatesAndAppends(memory, repo):
    seed(repo)
    mem = memory.Memory()
    assert "must start with" in memory.cmd_journal_add(mem, "no heading")
    assert "missing fields Proof:" in memory.cmd_journal_add(mem, "## 2026-02-02 — t\nChanged: a\nWhy: b\n")
    out = memory.cmd_journal_add(mem, "## 2026-02-02 — t\nChanged: a\nWhy: b\nProof: c\n")
    assert "appended" in out
    assert mem.journal_entries()[0][0] == "2026-02-02"
    (repo / ".agent" / "JOURNAL.md").unlink()
    memory.cmd_journal_add(mem, "## 2026-02-03 — t\nChanged: a\nWhy: b\nProof: c\n")
    assert (repo / ".agent" / "JOURNAL.md").read_text().startswith("# Journal")


def test_findings_addListClose(memory, repo):
    mem = memory.Memory()
    assert memory.cmd_findings_list(mem, True) == "findings: none open"
    assert memory.cmd_findings_add(mem, "ci.yml", "pipe | in text\nnewline", "") == "findings: F-01 added"
    assert memory.cmd_findings_add(mem, "x", "y", "E2") == "findings: F-02 added"
    listing = memory.cmd_findings_list(mem, False)
    assert "pipe / in text newline" in listing and "F-02 · x · y · open → E2" in listing
    assert memory.cmd_findings_list(mem, True).count("F-") == 2
    assert memory.cmd_findings_close(mem, "F-01", "closed — dup") == "findings: F-01 -> closed — dup"
    assert memory.cmd_findings_close(mem, "F-09", "x") == "findings: F-09 not found"
    assert memory.cmd_findings_list(mem, True).count("F-") == 1


# ---------------------------------------------------------------- learn


def delta(entries, topic="GitHub Actions", **extra):
    return json.dumps({"topic": topic, "entries": entries, **extra})


def entry(claim, status="verified", source="https://x", scope="project", checked="2026-11-06"):
    return {"claim": claim, "status": status, "source": source, "scope": scope, "checked": checked}


def test_learn_filtersAndWrites(memory, repo):
    mem = memory.Memory()
    raw = delta(
        [
            entry("checkout v7.0.1 is current"),
            entry("Checkout v7.0.1 is current!"),  # duplicate after normalisation
            entry("guess", status="assumed", source=""),
            entry("no source here", source=""),
            entry("general fact", scope="general"),
            {"claim": "", "status": "verified"},
            {"claim": "bad status", "status": "maybe"},
        ],
        unverified=["zizmor on reusable inputs"],
    )
    out = memory.cmd_learn(mem, raw, dry_run=True, keep_assumed=False)
    assert "2 new line(s)" in out and "  written:" not in out
    assert "duplicate in delta" in out and "assumed, not written" in out and "no source" in out
    assert "malformed" in out and "? unverified: zizmor" in out
    out = memory.cmd_learn(mem, raw, dry_run=False, keep_assumed=True)
    path = repo / ".agent" / "knowledge" / "github-actions.md"
    assert path.is_file() and "written" in out
    text = path.read_text()
    assert text.startswith("# knowledge: github-actions")
    assert "- [verified 2026-11-06 · src: https://x] checkout v7.0.1 is current" in text
    assert "general fact (general)" in text and "[assumed 2026-11-06 · src: unsourced] guess" in text
    again = memory.cmd_learn(mem, raw, dry_run=False, keep_assumed=False)
    assert "0 new line(s)" in again and "already known" in again


def test_learn_refusals(memory, repo):
    mem = memory.Memory()
    assert "not JSON" in memory.cmd_learn(mem, "{", False, False)
    assert "needs a topic" in memory.cmd_learn(mem, json.dumps({"entries": []}), False, False)
    secret = delta([entry("token = ghp_abcdefghijklmnopqrstuvwxyz0123456789")])
    assert "secret-like" in memory.cmd_learn(mem, secret, False, False)
    assert not (repo / ".agent" / "knowledge").exists()


def test_learn_capAtEightyLines(memory, repo):
    mem = memory.Memory()
    first = delta([entry(f"fact number {i}") for i in range(78)])
    assert "78 new line(s)" in memory.cmd_learn(mem, first, False, False)
    second = delta([entry(f"late fact {i}") for i in range(5)])
    out = memory.cmd_learn(mem, second, False, False)
    assert "2 new line(s)" in out and out.count("over the 80-line cap") == 3
    lines = (repo / ".agent" / "knowledge" / "github-actions.md").read_text().splitlines()
    assert sum(1 for line in lines if line.startswith("- [")) == 80


# ---------------------------------------------------------------- check and CLI


def test_check_reportsAndWarns(memory, repo):
    agent = seed(repo, journal="# J\n\n## 2026-02-01 — b\nChanged: x\n\n## 2026-01-01 — a\nChanged: y\n")
    (agent / "CONTEXT.md").write_text("\n".join(["l"] * 130))
    (agent / "JOURNAL.md").write_text((agent / "JOURNAL.md").read_text() + "\n" * 400)
    out = memory.cmd_check(memory.Memory())
    assert "mode: committed" in out and "trust: untrusted" in out
    assert "journal: newest on top" in out
    assert "warning: CONTEXT.md has 130 lines" in out and "JOURNAL.md over 400 lines" in out
    assert "brief:" in out


def test_journalOrder_variants(memory, repo):
    seed(repo, journal="# J\n")
    assert memory.journal_order(memory.Memory()) == "no entries"
    seed(repo, journal="# J\n## 2026-01-01 — a\n")
    assert memory.journal_order(memory.Memory()) == "single entry"
    seed(repo, journal="# J\n## 2026-01-01 — a\n## 2026-02-01 — b\n")
    assert memory.journal_order(memory.Memory()) == "newest at bottom"
    seed(repo, journal="# J\n## 2026-02-01 — a\n## 2026-01-01 — b\n## 2026-03-01 — c\n")
    assert memory.journal_order(memory.Memory()) == "mixed order"


def fake_stdin(text: str, tty: bool = False):
    return type("S", (), {"read": staticmethod(lambda: text), "isatty": staticmethod(lambda: tty)})()


def test_cli_journalAdd_takesTheArgumentAndNeverWaitsOnATerminal(memory, repo, capsys, monkeypatch):
    seed(repo)
    entry = "## 2026-05-06 — by argument\nChanged: a\nWhy: b\nProof: c\n"
    monkeypatch.setattr("sys.stdin", fake_stdin("", tty=True))
    assert memory.main(["journal", "add", entry]) == 0
    assert "appended" in capsys.readouterr().out
    assert memory.Memory().journal_entries()[0][0] == "2026-05-06"
    assert memory.main(["journal", "add"]) == 0
    assert "must start with" in capsys.readouterr().out
    assert memory.main(["learn", "--dry-run", '{"topic": "x", "lines": []}']) == 0


def test_cli_allCommands(memory, repo, capsys, monkeypatch):
    assert memory.main(["path"]) == 0 and str(repo / ".agent") in capsys.readouterr().out
    assert memory.main(["init", "--profile", "script"]) == 0
    capsys.readouterr()
    assert memory.main(["trust"]) == 0 and capsys.readouterr().out.startswith("untrusted")
    assert memory.main(["check"]) == 0
    assert memory.main(["brief", "--budget", "500", "--no-trust-check"]) == 0
    assert "profile: script" in capsys.readouterr().out
    monkeypatch.setattr(
        "sys.stdin",
        fake_stdin("## 2026-05-05 — t\nChanged: a\nWhy: b\nProof: c\n"),
    )
    assert memory.main(["journal", "add"]) == 0 and "appended" in capsys.readouterr().out
    assert memory.main(["findings", "add", "seen", "obs", "--goes-to", "T1"]) == 0
    assert memory.main(["findings", "list", "--open"]) == 0
    assert memory.main(["findings", "close", "F-01", "done"]) == 0
    monkeypatch.setattr("sys.stdin", fake_stdin(delta([entry("c")])))
    assert memory.main(["learn", "--dry-run"]) == 0 and "1 new line" in capsys.readouterr().out
    assert memory.main(["bogus"]) == 2
    assert memory.main([]) == 2


# ---------------------------------------------------------------- session


def test_session_payloadHasProtocolRulesAndBrief(session, repo):
    seed(repo)
    context = session.build_payload(json.dumps({"cwd": str(repo), "source": "startup"}))
    assert context.startswith("# cobot protocol")
    assert "rules: " in context and "never=" in context
    assert "UNTRUSTED" in context
    assert len(context) <= session.TOTAL_CAP


def test_session_trustedRepoGetsBrief(session, memory, repo):
    seed(repo)
    remote(repo, "origin", "git@github.com:YpNo/x.git")
    write_config("identities", "github.com/ypno\n")
    context = session.build_payload(json.dumps({"cwd": str(repo)}))
    assert "## CONTEXT" in context and "profile: cli" in context


def test_session_payloadCarriesKnowledgeAndDepsLines(session, repo):
    seed(repo)
    context = session.build_payload(json.dumps({"cwd": str(repo), "source": "startup"}))
    assert "\nknowledge: " in context and "\ndeps: " in context
    assert "deps: no lockfile" in context
    (repo / "go.mod").write_text("module x\n")
    context = session.build_payload(json.dumps({"cwd": str(repo)}))
    assert "deps: not checked; run cobot-deps check" in context


def test_session_sharedDeadline_andTimeoutLine(session, monkeypatch):
    clock = session.Clock(seconds=0.6)
    assert 0.5 <= clock.left() <= 0.6
    import subprocess as sp

    def slow(*_args, **kwargs):
        raise sp.TimeoutExpired(cmd="x", timeout=kwargs.get("timeout", 0))

    monkeypatch.setattr(session.subprocess, "run", slow)
    assert session.run_tool("cobot-deps", ["brief"], None, clock) == "cobot-deps brief: timed out"
    lines = session.status_lines(None, clock).splitlines()
    assert lines[0].startswith("cobot-memory knowledge: timed out")
    assert lines[1].startswith("cobot-deps brief: timed out")


def test_session_errorStillPrintsProtocol(session, monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("down")

    monkeypatch.setattr(session, "run_tool", boom)
    context = session.build_payload("")
    assert context.startswith("# cobot protocol") and "brief unavailable (RuntimeError: down)" in context


def test_session_cli(session, capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", fake_stdin("{}"))
    assert session.main(["start"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert session.main([]) == 2


def test_brief_longContextDropsWholeSectionsAndNamesThem(memory, repo):
    filler = "\n".join(f"- line {i}" for i in range(200))
    context = (
        f"# x\n\nprofile: cli\n\n## Stack\n{filler}\n\n## Commands\n{filler}\n\n## Where things are\n- a: b\n"
    )
    seed(repo, context=context)
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "## Stack" in brief and "## Commands" not in brief
    assert "…(truncated) sections dropped: Commands, Where things are" in brief


def test_capSections_keepsVerifiedCommandsAndConstraintsBeforeEarlierSections(memory):
    # the template order puts Environment first: on arlo-camera-streamer-rs a 108-line CONTEXT.md
    # lost Verified commands and Constraints from the brief while Environment stayed
    filler = "\n".join(f"- env {i}" for i in range(120))
    text = (
        "# x\n\nprofile: service\n\n## Stack\n- rust\n\n## Environment\n"
        + filler
        + "\n\n## Verified commands\n| t | `cargo test` | 2026-11-09 |\n\n## Constraints\n- no unwrap\n"
        + "\n## Shape\n- six crates\n"
    )
    capped = memory.cap_sections(text, 1200)
    assert "## Verified commands" in capped and "## Constraints" in capped and "## Stack" in capped
    assert capped.index("## Stack") < capped.index("## Verified commands") < capped.index("## Constraints")
    assert "## Environment" not in capped
    assert capped.endswith("sections dropped: Environment, Shape")


def test_capSections_firstSectionTooBig_fallsBackToHardCap(memory):
    text = "## A\n" + "x" * 3000
    capped = memory.cap_sections(text, 2500)
    assert capped.endswith("…(truncated)") and len(capped) <= 2500


def test_capSections_shortTextUnchanged(memory):
    assert memory.cap_sections("## A\nshort", 2500) == "## A\nshort"


LONG_CONTEXT = (
    "# x\n\nprofile: cli\n\n## Stack\n"
    + "\n".join(f"- line {i}" for i in range(150))
    + "\n\n## Commands\n"
    + "\n".join(f"- line {i}" for i in range(150))
    + "\n\n## Where things are\n- a: b\n"
)


def test_brief_contextGrowsIntoRoomLeftByShortJournal(memory, repo):
    assert len(LONG_CONTEXT) > memory.CONTEXT_CAP
    seed(repo, context=LONG_CONTEXT)
    brief = memory.build_brief(memory.Memory(), 6000, trust_check=False)
    assert "## Where things are" in brief and "truncated" not in brief


def test_brief_contextFallsBackToFloorWhenJournalIsLong(memory, repo):
    entry = "\n".join(f"- did {i}" for i in range(150))
    journal = f"# Journal\n\n## 2026-01-02 — two\n{entry}\n\n## 2026-01-01 — one\n{entry}\n"
    seed(repo, journal=journal, context=LONG_CONTEXT)
    brief = memory.build_brief(memory.Memory(), 5000, trust_check=False)
    assert "sections dropped" in brief and len(brief) <= 5000 + 600


# ---------------------------------------------------------------- compact and accepted risks


def long_journal(repo, newest_bottom=True, entries=14):
    body = []
    for i in range(entries):
        day = f"2026-01-{i + 1:02d}"
        filler = "\n".join(f"detail line {j}" for j in range(30))
        body.append(
            f"## {day} — entry {i}\nChanged: did thing {i}. Then more.\nWhy: w\nProof: p\n{filler}\nverified: sha{i} · cmd\n"  # noqa: E501
        )
    if not newest_bottom:
        body.reverse()
    seed(repo, journal="# Journal\n\nintro line\n\n" + "\n".join(body))
    return repo / ".agent" / "JOURNAL.md"


def test_compact_foldsOldEntriesKeepsTenAndArchives(memory, repo):
    path = long_journal(repo)
    mem = memory.Memory()
    dry = memory.cmd_compact(mem, 10, "", dry_run=True, force=False)
    assert "folding 4 of 14 entries (2026-01-01 → 2026-01-04), keeping 10" in dry and "dry run" in dry
    assert len(path.read_text().splitlines()) > 400 and not (repo / ".agent" / "JOURNAL-archive.md").exists()
    out = memory.cmd_compact(mem, 10, "", dry_run=False, force=False)
    text = path.read_text()
    assert "written:" in out and text.startswith(
        "# Journal\n\nintro line\n\n## 2026-01-04 — compacted 2026-01-01 → 2026-01-04 (4 entries)\n"
    )
    assert "- 2026-01-01 entry 0: did thing 0." in text and "- 2026-01-04 entry 3: did thing 3." in text
    assert (
        "## 2026-01-05 — entry 4" in text and "verified: sha13 · cmd" in text and "verified: sha0" not in text
    )
    assert memory.journal_order(mem) == "newest at bottom"
    archive = (repo / ".agent" / "JOURNAL-archive.md").read_text()
    assert (
        archive.startswith("# Journal archive")
        and "verified: sha0 · cmd" in archive
        and "detail line 29" in archive
    )
    assert mem.journal_entries()[0][0] == "2026-01-14"
    again = memory.cmd_compact(mem, 8, "", False, True)
    assert "folding 3 of 11" in again
    text = path.read_text()
    assert (
        text.count("compacted") == 1
        and "- 2026-01-01 entry 0: did thing 0." in text
        and "- 2026-01-06 entry 5" in text
    )


def test_compact_legacyOrderSummaryAndRefusals(memory, repo):
    path = long_journal(repo, newest_bottom=False)
    mem = memory.Memory()
    out = memory.cmd_compact(mem, 10, "The first four days set up the crate.", False, True)
    assert "summary: provided" in out
    text = path.read_text()
    assert text.index("## 2026-01-14 — entry 13") < text.index(
        "## 2026-01-04 — compacted 2026-01-01 → 2026-01-04 (4 entries)\nThe first four days set up the crate."
    )
    assert memory.journal_order(mem) == "newest on top (legacy order, read correctly)"
    seed(
        repo,
        journal="# J\n## 2026-02-01 — a\nChanged: x\n## 2026-01-01 — b\nChanged: y\n## 2026-03-01 — c\nChanged: z\n",  # noqa: E501
    )
    assert "mixes both orders" in memory.cmd_compact(mem, 10, "", False, True)
    seed(repo, journal="# J\n## 2026-02-01 — a\nChanged: x\n")
    assert "nothing to fold" in memory.cmd_compact(mem, 10, "", False, True)
    assert "nothing to do" in memory.cmd_compact(mem, 10, "", False, False)


def test_digest_variants(memory):
    assert memory.digest("## 2026-01-01 — t\nChanged: a; b\n") == ["- 2026-01-01 t: a;"]
    assert memory.digest("## 2026-01-01 — t\nWhy: only\n") == ["- 2026-01-01 t"]
    assert memory.digest("## 2026-01-02 — compacted x → y (2 entries)\n- one\n- two\nProof: p\n") == [
        "- one",
        "- two",
    ]


def test_check_acceptedRisksAndCompactWarning(memory, repo):
    agent = seed(repo)
    (agent / "accepted-risks.md").write_text(
        "# Accepted risks\n\n| # | rule | file | symbol | why accepted | by | accepted | expires |\n|---|---|---|---|---|---|---|---|\n"  # noqa: E501
        "| R-01 | PY-SUBPROC-01 | tool.py | run_tool | input is a constant | YpNo | 2026-01-01 | 2026-02-01 |\n"  # noqa: E501
        "| R-02 | GO-TLS-02 | main.go | dial | internal only | YpNo | 2026-11-01 | 2099-01-01 |\n"
    )
    out = memory.cmd_check(memory.Memory())
    assert "accepted risks: 2; expired: R-01 (2026-02-01)" in out
    assert [r[0] for r in memory.accepted_risks(memory.Memory())] == ["R-01", "R-02"]
    listing = memory.cmd_risks_list(memory.Memory())
    assert (
        "R-01 · PY-SUBPROC-01 · tool.py · run_tool · expires 2026-02-01 (expired) · input is a constant"
        in listing
    )
    assert "R-02 · GO-TLS-02 · main.go · dial · expires 2099-01-01 (ok)" in listing
    added = memory.cmd_risks_add(
        memory.Memory(), "TS-EVAL-01", "app/x.ts", "render|pipe", "sanitised upstream", "", 120
    )
    assert added.startswith("risks: R-03 accepted until ") and "TS-EVAL-01 · app/x.ts · render/pipe" in added
    row = memory.accepted_risks(memory.Memory())[-1]
    assert row[5] == "owner" and (date.fromisoformat(row[7]) - date.fromisoformat(row[6])).days == 90
    assert memory.cmd_risks_add(memory.Memory(), "r", "f", "s", "", "", 10).startswith(
        "risks: --why is required"
    )
    long_journal(repo)
    assert "run cobot-memory compact" in memory.cmd_check(memory.Memory())


def test_risks_add_createsFileFromTemplate(memory, repo, capsys):
    (repo / ".agent").mkdir()
    assert memory.cmd_risks_list(memory.Memory()) == "risks: none accepted"
    out = memory.cmd_risks_add(memory.Memory(), "SH-CURL-01", "install.sh", "main", "pinned sha", "YpNo", 30)
    assert out.startswith("risks: R-01")
    text = (repo / ".agent" / "accepted-risks.md").read_text()
    assert (
        text.startswith("# Accepted risks")
        and "| R-01 | SH-CURL-01 | install.sh | main | pinned sha | YpNo |" in text
    )
    assert memory.main(["risks", "add", "GO-X", "a.go", "f", "--why", "w", "--days", "5"]) == 0
    assert "R-02" in capsys.readouterr().out
    assert memory.main(["risks", "list"]) == 0 and "R-02 · GO-X" in capsys.readouterr().out


def test_compact_keepsTheBriefAndOpenItems(memory, repo):
    long_journal(repo)
    path = repo / ".agent" / "JOURNAL.md"
    path.write_text(
        path.read_text().replace(
            "## 2026-01-02 — entry 1\nChanged: did thing 1. Then more.\nWhy: w\n",
            "## 2026-01-02 — entry 1\nChanged: did thing 1. Then more.\nWhy: w\nOpen: F-07 still open\n",
        )
    )
    mem = memory.Memory()
    before = memory.build_brief(mem, 6000, trust_check=False)
    memory.cmd_compact(mem, 10, "", False, False)
    assert memory.build_brief(mem, 6000, trust_check=False) == before
    text = path.read_text()
    assert "- 2026-01-02 entry 1: did thing 1.\n  open: F-07 still open" in text
    memory.cmd_compact(mem, 8, "", False, True)
    assert "  open: F-07 still open" in path.read_text()


def test_cli_compact(memory, repo, capsys):
    long_journal(repo)
    assert memory.main(["compact", "--keep", "12", "--dry-run", "--force"]) == 0
    assert "folding 2 of 14" in capsys.readouterr().out


def test_check_oldRulesFile_warnsToRename(memory, repo):
    mem = memory.Memory()
    memory.cmd_init(mem, {"profile": "cli"}, set())
    (mem.dir / "partner.rules").write_text("ask Bash(x*)\n")
    out = memory.cmd_check(mem)
    assert "partner.rules is not read since the rename" in out and "rename it to cobot.rules" in out


# ---------------------------------------------------------------- stamp (R2)


def stamped(memory, repo, stamp_line):
    remote(repo, "origin", "https://github.com/o/r.git")
    write_config("identities", "github.com/o\n")
    commit(repo)
    mem = memory.Memory()
    memory.cmd_init(mem, {"profile": "cli"}, set())
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    with open(mem.dir / "JOURNAL.md", "a") as handle:
        handle.write(f"\n## 2026-11-07 — wrap\nChanged: x\n{stamp_line.replace('HEAD', head[:7])}\n")
    return mem, head


def add_commit(repo, path, text="x"):
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text(text)
    subprocess.run(["git", "-C", str(repo), "add", str(path)], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", f"touch {path}"], check=True)


def test_stamp_equalsHead_ok(memory, repo):
    mem, head = stamped(memory, repo, "verified: HEAD · pytest")
    assert memory.cmd_stamp(mem) == f"ok {head[:7]}"


def test_stamp_docsOnlyAfter_ok(memory, repo):
    mem, _ = stamped(memory, repo, "verified: HEAD")
    add_commit(repo, "docs/x.md")
    add_commit(repo, "CHANGELOG.md")
    assert memory.cmd_stamp(mem).startswith("ok ")


def test_stamp_codeAfter_missing(memory, repo):
    mem, _ = stamped(memory, repo, "verified: HEAD · pytest")
    add_commit(repo, "src/main.py")
    assert memory.cmd_stamp(mem) == "missing — HEAD moved since the stamp"


def test_stamp_dirtyTreeStamp_missing(memory, repo):
    mem, _ = stamped(memory, repo, "verified: HEAD+working-tree · pytest")
    assert memory.cmd_stamp(mem) == "missing — dirty-tree stamp; commit, then wrap"


def test_stamp_noStamp_missing(memory, repo):
    mem, _ = stamped(memory, repo, "Proof: none yet")
    assert memory.cmd_stamp(mem) == "missing — no stamp"


def test_stamp_untrustedMemory_missingWithoutReadingJournal(memory, repo):
    remote(repo, "origin", "https://github.com/stranger/r.git")
    commit(repo)
    mem = memory.Memory()
    (mem.dir).mkdir(exist_ok=True)
    (mem.dir / "JOURNAL.md").write_text("verified: 0000000 · <script>evil</script>\n")
    assert memory.cmd_stamp(mem) == "missing — untrusted memory"


# ---------------------------------------------------------------- never-push rules at foreign init (R2)


def test_never_push_rules_everyRemoteExceptOrigin(memory):
    rules = memory.never_push_rules(
        {
            "origin": "https://github.com/YpNo/headscale.git",
            "ghsa": "git@github.com:juanfont/headscale-ghsa-8598-8grw-c4hv.git",
            "upstream": "https://github.com/juanfont/headscale",
        }
    )
    assert rules == [
        "never Bash(git push ghsa*)",
        "never Bash(git push *headscale-ghsa-8598-8grw-c4hv*)",
        "never Bash(git push upstream*)",
        "never Bash(git push *headscale*)",
    ]


def test_init_foreign_writesNeverPushRules_gateDeniesBothForms(memory, rules, repo):
    remote(repo, "origin", "https://github.com/other/proj.git")
    remote(repo, "ghsa", "git@github.com:other/proj-ghsa-1234.git")
    commit(repo)
    out = memory.cmd_init(memory.Memory(), {}, {"foreign"})
    assert "rules: never Bash(git push ghsa*)" in out
    external = memory.Memory().external_path()
    text = (external / "cobot.rules").read_text()
    assert "never Bash(git push *proj-ghsa-1234*)" in text
    assert "kept" in memory.cmd_init(memory.Memory(), {}, {"foreign"})  # idempotent: no second copy
    assert text == (external / "cobot.rules").read_text()
    for command in ("git push -u ghsa fix", "git push git@github.com:other/proj-ghsa-1234.git HEAD:fix"):
        verdict = json.loads(
            rules.gate(
                json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(repo)})
            )
        )
        assert verdict["hookSpecificOutput"]["permissionDecision"] == "deny", command
        assert "project layer" in verdict["hookSpecificOutput"]["permissionDecisionReason"]
    origin = json.loads(
        rules.gate(
            json.dumps(
                {"tool_name": "Bash", "tool_input": {"command": "git push -u origin fix"}, "cwd": str(repo)}
            )
        )
    )
    assert origin["hookSpecificOutput"]["permissionDecision"] == "ask"


# ---------------------------------------------------------------- onboarding follow-ups (arlo)


def test_findingsAdd_goesTo_recordsRoutingAndStaysOpen(memory, repo):
    mem = memory.Memory()
    memory.cmd_findings_add(mem, "x", "y", "E2")
    assert "| F-01 | x | y | open → E2 |" in (repo / ".agent" / "FINDINGS.md").read_text()
    assert memory.cmd_findings_list(mem, True) == "F-01 · x · y · open → E2"
    memory.cmd_findings_close(mem, "F-01", "fixed in PR 4")
    assert memory.cmd_findings_list(mem, True) == "findings: none open"


def test_openFindings_closeReasonStartingWithOpened_isClosed(memory, repo):
    agent = seed(repo)
    (agent / "FINDINGS.md").write_text(
        "| # | Seen | Observation | Goes to |\n|---|---|---|---|\n"
        "| F-01 | s | o | opened issue 12 |\n| F-02 | s | o | open |\n| F-03 | s | o | |\n"
    )
    assert [f[0] for f in memory.Memory().open_findings()] == ["F-02", "F-03"]
