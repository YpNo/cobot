"""_cobot_knowledge: dated lines, staleness, promotion into the plugin checkout, and the memory CLI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import date, timedelta
from pathlib import Path

import _cobot_knowledge as knowledge
import pytest
from conftest import PLUGIN

TODAY = date(2026, 11, 7)
TEMPLATE = PLUGIN / "skills" / "learn" / "templates" / "expert-SKILL.md"
SKELETON = {
    "skeleton": {
        "paths": ["**/*.yaml", "esphome/**"],
        "description": "ESPHome firmware YAML.",
        "when_to_use": "when an esphome/ folder exists",
    }
}


def dated(days_ago: int, status="verified", claim="plain idiom claim", source="https://x") -> str:
    when = (TODAY - timedelta(days=days_ago)).isoformat()
    src = f" · src: {source}" if source else ""
    return f"- [{status} {when}{src}] {claim}"


def make_plugin(root: Path, skills: dict[str, dict[str, list[str]]]) -> Path:
    """``{skill: {file: [lines]}}`` -> a plugin dir; ``file`` is SKILL.md or references/<name>.md."""
    plugin = root / "plugins" / "cobot"
    for skill, files in skills.items():
        folder = plugin / "skills" / skill
        folder.mkdir(parents=True, exist_ok=True)
        if "SKILL.md" not in files:
            (folder / "SKILL.md").write_text(
                f"---\nname: {skill}\ndescription: d\npaths:\n  - '**/x'\n---\n# {skill}\n"
            )
        for name, lines in files.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {name}\n\n" + "\n".join(lines) + "\n")
    (plugin / "skills" / "learn" / "templates").mkdir(parents=True, exist_ok=True)
    shutil.copy(TEMPLATE, plugin / "skills" / "learn" / "templates" / "expert-SKILL.md")
    return plugin


def dated_lines(path: Path) -> list[str]:
    return [line for line in path.read_text().splitlines() if line.lstrip().startswith("- [")]


# ---------------------------------------------------------------- lines


def test_parseLine_formsAndRejections():
    line = knowledge.parse_line(
        "s", Path("f"), 3, "- [verified 2026-11-06 · src: https://a] Go 1.27.3 current"
    )
    assert line and (line.status, line.source, line.claim, line.kind) == (
        "verified",
        "https://a",
        "Go 1.27.3 current",
        "version",
    )
    bare = knowledge.parse_line("s", Path("f"), 1, "  - [reported 2026-11-06] no source form")
    assert bare and bare.source == "" and bare.kind == "idiom" and bare.indent == "  "
    assert knowledge.parse_line("s", Path("f"), 1, "- [verified 2026-13-40 · src: x] bad date") is None
    assert knowledge.parse_line("s", Path("f"), 1, "- plain bullet") is None


@pytest.mark.parametrize(
    ("file", "claim", "kind"),
    [
        ("actions.md", "actions/checkout v7.0.1 is current", "version"),
        ("SKILL.md", "golangci-lint v2.15.0 is the current major", "version"),
        ("versions.md", "Rust stable 1.99.1 (2026-10-16); six-week cadence", "version"),
        ("versions.md", "golangci-lint v2.15.0; config needs version 2", "version"),
        ("ci.md", "setup-go v7.0.0 = b7ad1dad31e06c5925ef5d2fc7ad053ef454303e", "version"),
        ("SKILL.md", "ubuntu-24.04 ships rustup 1.29.2", "version"),
        ("versions.md", "Edition 2024 stable since 1.85.0: unsafe extern", "idiom"),
        ("versions.md", "Let chains stable in 1.88.0, edition 2024 only", "idiom"),
        ("versions.md", "1.27 (Aug 2026): generic methods; json/v2", "idiom"),
        ("versions.md", "POSIX.1-2024 is what shellcheck follows", "idiom"),
        ("testing.md", "mock_provider since 1.7.0", "idiom"),
        ("SKILL.md", "wrap errors with %w, lowercase, no trailing punctuation", "idiom"),
        ("snippets.md", "`groups` with `pattern` in dependabot 2.0 config", "idiom"),
        ("SKILL.md", "masking is exact-match only", "idiom"),
    ],
)
def test_lineKind_byClaimAndFile(file, claim, kind):
    assert knowledge.parse_line("s", Path(file), 1, f"- [verified 2026-11-06 · src: x] {claim}").kind == kind


def test_lineKind_onTheRealSkills_keepsHistoryAsIdiom():
    lines = [line for lines in knowledge.scan_plugin(PLUGIN).values() for line in lines]
    assert lines, "the plugin carries dated lines"
    history = [line for line in lines if knowledge.HISTORY_RE.search(line.claim)]
    assert history and all(line.kind == "idiom" for line in history)
    versions = [line for line in lines if line.kind == "version"]
    assert 20 <= len(versions) < len(lines), f"{len(versions)} of {len(lines)} lines are version lines"


@pytest.mark.parametrize(
    ("days", "claim", "stale", "due"),
    [
        (30, "v1.2.3 is current", False, False),
        (31, "v1.2.3 is current", True, False),
        (31, "an idiom", False, False),
        (90, "an idiom", False, False),
        (91, "an idiom", True, False),
        (180, "an idiom", True, True),
    ],
)
def test_staleness_thresholds(days, claim, stale, due):
    line = knowledge.parse_line("s", Path("f"), 1, dated(days, claim=claim))
    assert line.stale(TODAY) is stale
    assert (line.age(TODAY) >= knowledge.DROP_DAYS) is due


# ---------------------------------------------------------------- scanning and summaries


def test_scanPlugin_knowledgeSkillsOnly_andMemoryTopics(tmp_path):
    plugin = make_plugin(
        tmp_path,
        {
            "lang-x": {
                "SKILL.md": [
                    "---\nname: lang-x\ndescription: d\npaths: ['**/x']\n---",
                    dated(1, claim="in skill"),
                ],
                "references/versions.md": [dated(40, claim="tool 2.0 current"), dated(100)],
            },
            "expert-y": {"references/a.md": [dated(5, status="reported")]},
            "consult-y": {"SKILL.md": ["---\nname: consult-y\ndescription: d\n---", dated(2)]},
            "spec": {"SKILL.md": ["---\nname: spec\ndescription: d\n---", dated(400, claim="never counted")]},
            "lang-empty": {"references/none.md": ["no dated line here"]},
        },
    )
    groups = knowledge.scan_plugin(plugin)
    assert sorted(groups) == ["consult-y", "expert-y", "lang-x"]
    assert [line.file.name for line in groups["lang-x"]] == ["SKILL.md", "versions.md", "versions.md"]
    memory = tmp_path / ".agent"
    (memory / "knowledge").mkdir(parents=True)
    (memory / "knowledge" / "radio.md").write_text("# k\n" + dated(3, claim="freq 868.3 MHz") + "\n")
    (memory / "knowledge" / "empty.md").write_text("# k\n")
    assert list(knowledge.scan_memory(memory)) == ["knowledge/radio"]
    assert knowledge.scan_file("s", tmp_path / "missing.md") == []


def test_summaries_reportAndBrief(tmp_path):
    plugin = make_plugin(
        tmp_path,
        {
            "lang-x": {
                "references/versions.md": [
                    dated(40, claim="tool 2.0 current"),
                    dated(100),
                    dated(200, status="assumed", source=""),
                    dated(1),
                ]
            },
            "expert-y": {"references/a.md": [dated(5, status="reported")]},
            "expert-fresh": {"references/a.md": [dated(2)]},
        },
    )
    items = knowledge.summaries(knowledge.scan_plugin(plugin), TODAY)
    by_name = {s.skill: s for s in items}
    x = by_name["lang-x"]
    assert (x.total, x.stale, x.stale_version, x.assumed, x.due, x.oldest) == (
        4,
        3,
        1,
        1,
        1,
        TODAY - timedelta(days=200),
    )
    text = knowledge.report(items, TODAY)
    assert (
        "lang-x: 4 line(s), 3 stale (1 version, 2 idiom), 1 assumed, 1 due for re-verification (>= 180 days); oldest"  # noqa: E501
        in text
    )
    assert "expert-fresh: 1 line(s); oldest" in text and text.endswith("re-verify or drop at 180")
    stale_only = knowledge.report(items, TODAY, stale_only=True)
    assert "expert-fresh" not in stale_only and "expert-y: 1 line(s), 1 reported" in stale_only
    data = json.loads(knowledge.report(items, TODAY, as_json=True))
    assert {d["skill"]: d["stale"] for d in data} == {"lang-x": 3, "expert-y": 0, "expert-fresh": 0}
    assert next(d for d in data if d["skill"] == "lang-x")["oldest"] == x.oldest.isoformat()
    brief = knowledge.brief_line(items, TODAY)
    assert brief == "knowledge: stale -> lang-x (3); refresh with /cobot:learn <skill>; 1 reported line(s)"
    fresh = [s for s in items if s.skill == "expert-fresh"]
    assert knowledge.brief_line(fresh, TODAY) == "knowledge: fresh (oldest 2 days)"
    assert knowledge.brief_line([], TODAY) == "knowledge: no dated lines"
    assert knowledge.report([], TODAY, stale_only=True) == "knowledge: nothing stale"
    assert knowledge.report([], TODAY) == "knowledge: no dated lines found"


def test_briefLine_capsTheNamedSkills():
    items = [knowledge.Summary(f"expert-{i}", 3, 3 - (i % 2), 1, 0, 0, TODAY, 0) for i in range(6)]
    brief = knowledge.brief_line(items, TODAY)
    assert brief.count("expert-") == 4 and "+2 more" in brief and len(brief) <= knowledge.BRIEF_MAX


# ---------------------------------------------------------------- claims, placement and targets


def test_claimKey_andFormatLine():
    assert knowledge.claim_key("Checkout v7.0.1 is current! (general)") == "checkout v7 0 1 is current"
    entry = {"claim": " c ", "status": "verified", "source": "", "scope": "plugin"}
    assert knowledge.format_line(entry, TODAY) == "- [verified 2026-11-07 · src: unsourced] c (general)"
    assert knowledge.format_line(entry, TODAY, tag_general=False, indent="  ").startswith(
        "  - ["
    ) and knowledge.format_line(entry, TODAY, False).endswith("] c")


def test_place_redatesSupersedesAppendsAndSkips(tmp_path):
    file = tmp_path / "v.md"
    file.write_text(
        "# v\n\n"
        + dated(60, claim="Go 1.27.3 current (general)")
        + "\n  "
        + dated(60, claim="nested idiom")
        + "\n"
        + dated(1, claim="fresh fact")
        + "\n"
    )
    index = knowledge.Index([file])
    kind, text, where = knowledge.place(
        {
            "claim": "go 1.27.3 current",
            "status": "verified",
            "source": "https://go.dev",
            "checked": "2026-11-07",
        },
        index,
        TODAY,
        True,
    )
    assert (kind, where) == (
        "redated",
        file,
    ) and text == "- [verified 2026-11-07 · src: https://go.dev] Go 1.27.3 current (general)"
    kind, text, _ = knowledge.place(
        {"claim": "fresh fact", "status": "verified", "source": "s", "checked": "2026-11-01"},
        index,
        TODAY,
        True,
    )
    assert kind == "skipped" and text.startswith("already known")
    kind, text, _ = knowledge.place(
        {"claim": "fresh fact", "status": "reported", "source": "s", "checked": "2026-11-01"},
        index,
        TODAY,
        True,
    )
    assert kind == "redated" and text.startswith("- [reported 2026-11-01")
    kind, text, where = knowledge.place(
        {
            "claim": "Go 1.27.4 current",
            "status": "verified",
            "source": "https://go.dev",
            "supersedes": "go 1.27.3",
        },
        index,
        TODAY,
        True,
    )
    assert (kind, where) == (
        "superseded",
        file,
    ) and text == "- [verified 2026-11-07 · src: https://go.dev] Go 1.27.4 current (general)"
    kind, text, _ = knowledge.place(
        {"claim": "nested rewrite", "status": "verified", "source": "s", "supersedes": "nested"},
        index,
        TODAY,
        True,
    )
    assert (
        kind == "superseded" and dated_lines(file)[1] == "  - [verified 2026-11-07 · src: s] nested rewrite"
    )
    kind, text, _ = knowledge.place(
        {"claim": "x", "status": "verified", "source": "s", "supersedes": "zzz"}, index, TODAY, True
    )
    assert kind == "new" and text == "- [verified 2026-11-07 · src: s] x"
    file.write_text(file.read_text() + dated(1, claim="twin a") + "\n" + dated(1, claim="twin b") + "\n")
    index = knowledge.Index([file])
    kind, text, _ = knowledge.place(
        {"claim": "y", "status": "verified", "source": "s", "supersedes": "twin"}, index, TODAY, True
    )
    assert kind == "skipped" and "matches 2 lines" in text
    assert dated_lines(file)[0] == "- [verified 2026-11-07 · src: https://go.dev] Go 1.27.4 current (general)"
    dry = knowledge.Index([file], dry=True)
    before = file.read_text()
    assert (
        knowledge.place({"claim": "fresh fact", "status": "verified", "source": "s"}, dry, TODAY, True)[0]
        == "redated"
    )
    assert file.read_text() == before


def test_formatLine_survivesBracketsAndNewlines(tmp_path):
    entry = {
        "claim": "Dependabot `groups`\n  applies to github-actions",
        "status": "reported",
        "source": 'https://docs.github.com/x (a community example shows patterns ["*"])',
    }
    text = knowledge.format_line(entry, TODAY, False)
    line = knowledge.parse_line("s", Path("f"), 1, text)
    assert line and line.claim == "Dependabot `groups` applies to github-actions"
    assert line.source == 'https://docs.github.com/x (a community example shows patterns ["*"))'
    file = tmp_path / "k.md"
    file.write_text("# k\n" + dated(1, claim="old") + "\n")
    index = knowledge.Index([file])
    kind, _text, _ = knowledge.place(entry, index, TODAY, False)
    assert kind == "new"
    index.add(file, text)
    assert len(index.lines) == 2 and index.by_claim(entry["claim"]) is not None
    index.add(file, "not a dated line")
    assert len(index.lines) == 2
    assert index.replace(index.lines[0], "garbage") is None and dated_lines(file) == [dated(1, claim="old")]


def test_skillName_mapping(tmp_path):
    plugin = make_plugin(tmp_path, {"lang-go": {}, "expert-gha": {}})
    assert knowledge.skill_name("go", None, plugin) == ("lang-go", True)
    assert knowledge.skill_name("gha", None, plugin) == ("expert-gha", True)
    assert knowledge.skill_name("github-actions", "expert-gha", plugin) == ("expert-gha", True)
    assert knowledge.skill_name("esphome", None, plugin) == ("expert-esphome", False)
    assert knowledge.skill_name("esphome", "expert-home", plugin) == ("expert-home", False)


def test_writeLines_dedupesRedatesCapsAndSkeleton(tmp_path):
    plugin = make_plugin(
        tmp_path,
        {
            "lang-go": {
                "SKILL.md": [
                    "---\nname: lang-go\ndescription: d\npaths: ['**/*.go']\n---",
                    dated(40, claim="Go 1.27.3 current"),
                ],
                "references/v.md": [dated(1, claim="in refs")],
            }
        },
    )
    entries = [
        {"claim": "go 1.27.3 current", "status": "verified", "source": "https://go.dev", "scope": "general"},
        {
            "claim": "In refs.",
            "status": "verified",
            "source": "https://go.dev",
            "scope": "general",
            "checked": "2026-11-06",
        },
        {
            "claim": "fresh fact",
            "status": "reported",
            "source": "https://go.dev",
            "scope": "general",
            "checked": "2026-11-07",
        },
    ]
    result = knowledge.write_lines(plugin, "go", entries, {}, TODAY)
    assert (result.skill, result.created, len(result.written), result.redated, len(result.skipped)) == (
        "lang-go",
        False,
        1,
        1,
        1,
    )
    skill = plugin / "skills" / "lang-go" / "SKILL.md"
    learned = plugin / "skills" / "lang-go" / "references" / "learned.md"
    assert result.files == [skill, learned]
    assert dated_lines(skill) == ["- [verified 2026-11-07 · src: https://go.dev] Go 1.27.3 current"]
    text = learned.read_text()
    assert text.startswith("# lang-go — learned lines") and text.endswith(
        "- [reported 2026-11-07 · src: https://go.dev] fresh fact\n"
    )
    assert "promote: lang-go, 1 new, 1 re-dated, 0 superseded" in result.lines()[0]
    assert "claim`.\n\n- [reported" in text  # a blank line separates the header from the list (MD032)
    again = knowledge.write_lines(
        plugin,
        "go",
        [*entries, {"claim": "second", "status": "verified", "source": "s", "scope": "general"}],
        {},
        TODAY,
    )
    assert (
        again.written == ["- [verified 2026-11-07 · src: s] second"]
        and len(dated_lines(learned)) == 2
        and again.redated == 0
    )
    (plugin / "skills" / "lang-go" / "references" / "bulk.md").write_text(
        "\n".join(dated(1, claim=f"bulk {i}") for i in range(296)) + "\n"
    )
    capped = knowledge.write_lines(
        plugin, "go", [{"claim": "over", "status": "verified", "source": "s", "scope": "general"}], {}, TODAY
    )
    assert capped.written == [] and "over the 300-line cap of lang-go" in capped.skipped[0]
    # no skill and no skeleton block: refused, nothing created
    missing = knowledge.write_lines(
        plugin, "esphome", [{"claim": "c", "status": "verified", "source": "s"}], {}, TODAY
    )
    assert (
        missing
        == 'promote: no skill matches \'esphome\': set "skill" in the delta, or a "skeleton" with description and paths'  # noqa: E501
    )
    assert (
        knowledge.write_lines(plugin, "esphome", [], {"skeleton": {"description": "d"}}, TODAY)
        == "promote: skeleton needs paths"
    )
    assert (
        knowledge.write_lines(plugin, "esphome", [], {"skeleton": {"description": "d", "paths": "x"}}, TODAY)
        == "promote: skeleton needs paths as a list"
    )
    assert not (plugin / "skills" / "expert-esphome").exists()
    made = knowledge.write_lines(
        plugin,
        "esphome",
        [
            {
                "claim": "api encryption key is base64",
                "status": "verified",
                "source": "https://esphome.io",
                "scope": "general",
            }
        ],
        SKELETON,
        TODAY,
    )
    head = (plugin / "skills" / "expert-esphome" / "SKILL.md").read_text()
    assert made.created and made.files[0].name == "SKILL.md" and made.files[1].name == "learned.md"
    assert (
        "name: expert-esphome" in head
        and '  - "**/*.yaml"\n  - "esphome/**"' in head
        and "ESPHome firmware YAML." in head
    )
    assert "Use when an esphome/ folder exists." in head and "stays reported" in head
    explicit = knowledge.write_lines(
        plugin,
        "zwave",
        [],
        {"skill": "expert-zwave", "skeleton": {"description": "d", "paths": ["**/*zwave*"]}},
        TODAY,
    )
    assert (
        explicit.created
        and "Use when zwave is read, changed or discussed."
        in (plugin / "skills" / "expert-zwave" / "SKILL.md").read_text()
    )


# ---------------------------------------------------------------- promote


def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    make_plugin(root, {"lang-go": {"references/v.md": [dated(1, claim="known")]}})
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(["config", "user.email", "t@x"], root)
    git(["config", "user.name", "t"], root)
    git(["add", "."], root)
    git(["commit", "-qm", "init"], root)
    return root


ENTRIES = [{"claim": "new fact 1.2", "status": "verified", "source": "https://s", "scope": "general"}]


def test_promote_worktreeBranchAndCommit(source, tmp_path):
    worktrees = tmp_path / "wt"
    result = knowledge.promote(source, "go", ENTRIES, {}, TODAY, in_place=False, worktrees=worktrees)
    assert isinstance(result, knowledge.Promotion)
    assert result.branch == "learn/go" and result.worktree == worktrees / "go" and result.commit
    assert git(["rev-parse", "--abbrev-ref", "HEAD"], result.worktree) == "learn/go"
    assert (
        git(["log", "-1", "--format=%s"], result.worktree)
        == "docs(knowledge): lang-go learns 1 line(s) on go"
    )
    assert git(["status", "--porcelain"], result.worktree) == ""
    assert not (source / "plugins" / "cobot" / "skills" / "lang-go" / "references" / "learned.md").exists()
    text = "\n".join(result.lines())
    assert (
        "promote: lang-go, 1 new" in text
        and f"git -C {result.worktree} push -u origin learn/go" in text
        and "gh pr create --head learn/go" in text
    )
    second = knowledge.promote(
        source,
        "go",
        [{"claim": "another", "status": "verified", "source": "s", "scope": "general"}],
        {},
        TODAY,
        False,
        worktrees,
    )
    assert second.worktree == result.worktree and git(["rev-list", "--count", "HEAD"], second.worktree) == "3"
    nothing = knowledge.promote(source, "go", ENTRIES, {}, TODAY, False, worktrees)
    assert (
        nothing.written == []
        and nothing.commit is None
        and git(["rev-list", "--count", "HEAD"], nothing.worktree) == "3"
    )
    assert "no new commit" in "\n".join(nothing.lines())
    redate = knowledge.promote(
        source,
        "go",
        [{"claim": "known", "status": "verified", "source": "https://x", "checked": "2026-11-07"}],
        {},
        TODAY,
        False,
        worktrees,
    )
    assert redate.redated == 1 and git(["rev-list", "--count", "HEAD"], redate.worktree) == "4"


def test_promote_branchExistsWithoutWorktree_datesTheBranch(source, tmp_path):
    git(["branch", "learn/go"], source)
    result = knowledge.promote(source, "go", ENTRIES, {}, TODAY, False, tmp_path / "wt")
    assert result.branch == "learn/go-2026-11-07" and result.worktree == tmp_path / "wt" / "go-2026-11-07"


def test_promote_refusals(source, tmp_path):
    worktrees = tmp_path / "wt"
    (worktrees / "go").mkdir(parents=True)
    assert "is not on learn/go" in knowledge.promote(source, "go", ENTRIES, {}, TODAY, False, worktrees)
    assert "not an cobot checkout" in knowledge.promote(
        tmp_path / "nowhere", "go", ENTRIES, {}, TODAY, False, worktrees
    )
    assert knowledge.promote(source, "nope", ENTRIES, {}, TODAY, False, tmp_path / "wt2").startswith(
        "promote: no skill matches 'nope'"
    )
    plain = tmp_path / "plain"
    make_plugin(plain, {"lang-go": {}})
    assert "use --in-place" in knowledge.promote(plain, "go", ENTRIES, {}, TODAY, False, worktrees)
    in_place = knowledge.promote(plain, "go", ENTRIES, {}, TODAY, True, worktrees)
    assert (
        in_place.worktree is None
        and (plain / "plugins" / "cobot" / "skills" / "lang-go" / "references" / "learned.md").is_file()
    )


def test_promote_baseRefFollowsOriginHead(source, tmp_path):
    git(["branch", "feature"], source)
    git(["checkout", "-q", "feature"], source)
    (source / "x").write_text("x")
    git(["add", "x"], source)
    git(["commit", "-qm", "feature work"], source)
    assert knowledge.base_ref(source) == "HEAD"
    git(["update-ref", "refs/remotes/origin/main", "main"], source)
    git(["symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main"], source)
    assert knowledge.base_ref(source) == "refs/remotes/origin/main"
    result = knowledge.promote(source, "go", ENTRIES, {}, TODAY, False, tmp_path / "wt")
    assert not (result.worktree / "x").exists()


def test_sourceCheckout_resolutionOrder(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(cfg))
    monkeypatch.delenv("COBOT_SOURCE", raising=False)
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path / "cache" / "cobot"))
    assert knowledge.source_checkout(None) is None
    recorded = tmp_path / "recorded"
    make_plugin(recorded, {"lang-go": {}})
    (cfg / "plugins").mkdir(parents=True)
    record = cfg / "plugins" / "known_marketplaces.json"
    record.write_text(json.dumps({"cobot": {"source": {"source": "github", "repo": "YpNo/cobot"}}}))
    assert knowledge.source_checkout(None) is None
    record.write_text(json.dumps({"cobot": {"source": {"source": "directory", "path": str(recorded)}}}))
    assert knowledge.source_checkout(None) == recorded.resolve()
    dev = tmp_path / "dev"
    make_plugin(dev, {"lang-go": {}})
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(dev / "plugins" / "cobot"))
    assert knowledge.source_checkout(None) == dev.resolve()
    env = tmp_path / "env"
    make_plugin(env, {"lang-go": {}})
    monkeypatch.setenv("COBOT_SOURCE", str(env))
    assert knowledge.source_checkout(None) == env.resolve()
    explicit = tmp_path / "explicit"
    make_plugin(explicit, {"lang-go": {}})
    assert knowledge.source_checkout(str(explicit)) == explicit.resolve()
    assert knowledge.source_checkout(str(tmp_path / "missing")) is None
    record.write_text("{not json")
    assert knowledge.marketplace_path() is None


# ---------------------------------------------------------------- the memory CLI


@pytest.fixture
def repo(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(home / ".claude"))
    monkeypatch.setenv("XDG_DATA_HOME", str(home / ".local" / "share"))
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(PLUGIN))
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    monkeypatch.delenv("COBOT_SOURCE", raising=False)
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    monkeypatch.chdir(root)
    return root


def trust(repo):
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "origin", "git@github.com:YpNo/x.git"], check=True
    )
    cfg = Path(os.environ["CLAUDE_CONFIG_DIR"]) / "cobot"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "identities").write_text("github.com/ypno\n")


def test_learn_promote_splitsProjectAndGeneral(memory, repo, source, tmp_path, monkeypatch):
    mem = memory.Memory()
    raw = json.dumps(
        {
            "topic": "go",
            "entries": [
                {
                    "claim": "repo uses go 1.27",
                    "status": "verified",
                    "source": "exp: go version",
                    "scope": "project",
                },
                {
                    "claim": "generic go fact 1.27",
                    "status": "verified",
                    "source": "https://go.dev",
                    "scope": "plugin",
                },
            ],
        }
    )
    dry = memory.cmd_learn(mem, raw, dry_run=True, keep_assumed=False, promoting=True, source=str(source))
    assert (
        "1 new line(s), 0 skipped, 1 general to promote" in dry
        and "dry run, 1 general entry(ies) would be promoted" in dry
    )
    out = memory.cmd_learn(mem, raw, dry_run=False, keep_assumed=False, promoting=True, source=str(source))
    local = (repo / ".agent" / "knowledge" / "go.md").read_text()
    assert "repo uses go 1.27" in local and "generic go fact" not in local
    assert "promote: lang-go, 1 new" in out and "worktree:" in out
    worktree = Path(os.environ["XDG_DATA_HOME"]) / "cobot" / "promote" / "go"
    assert (worktree / "plugins" / "cobot" / "skills" / "lang-go" / "references" / "learned.md").is_file()
    none = memory.cmd_learn(
        mem, json.dumps({"topic": "go", "entries": []}), False, False, promoting=True, source=str(source)
    )
    assert "promote: no general entry" in none
    assert "no cobot checkout known" in memory.cmd_learn(
        mem, raw, False, False, promoting=True, source=str(tmp_path / "nope")
    )
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path / "nowhere" / "plugins" / "cobot"))
    assert "no cobot checkout known" in memory.cmd_learn(mem, raw, False, False, promoting=True)


def test_learn_promote_pendingGeneralLinesByTopic(memory, repo, source):
    mem = memory.Memory()
    raw = json.dumps(
        {
            "topic": "go",
            "entries": [
                {
                    "claim": "pending general 2.0",
                    "status": "verified",
                    "source": "https://s",
                    "scope": "general",
                }
            ],
        }
    )
    assert "(general)" in memory.cmd_learn(mem, raw, False, False)  # written locally, tagged
    out = memory.cmd_learn(mem, "go", False, False, promoting=True, source=str(source))
    assert "1 pending general line(s)" in out and "promote: lang-go, 1 new" in out
    assert f"+ - [verified {date.today().isoformat()} · src: https://s] pending general 2.0" in out
    assert "not JSON" in memory.cmd_learn(mem, "{", False, False, promoting=True)
    assert "must be a JSON object" in memory.cmd_learn(mem, "[1]", False, False)


def test_learn_local_redatesAndSupersedes(memory, repo):
    mem = memory.Memory()
    first = json.dumps(
        {
            "topic": "radio",
            "entries": [
                {
                    "claim": "freq 868.3 MHz",
                    "status": "reported",
                    "source": "exp: scan",
                    "checked": "2026-01-01",
                }
            ],
        }
    )
    assert "1 new line(s)" in memory.cmd_learn(mem, first, False, False)
    again = json.dumps(
        {
            "topic": "radio",
            "entries": [
                {
                    "claim": "Freq 868.3 MHz",
                    "status": "verified",
                    "source": "exp: capture",
                    "checked": "2026-11-07",
                },
                {"claim": "channel 11", "status": "verified", "source": "exp: x", "supersedes": "nothing"},
            ],
        }
    )
    out = memory.cmd_learn(mem, again, True, False)
    assert (
        "1 new line(s), 0 skipped, 1 re-dated or superseded" in out
        and "~ redated:" in out
        and "written" not in out
    )
    path = repo / ".agent" / "knowledge" / "radio.md"
    assert dated_lines(path) == ["- [reported 2026-01-01 · src: exp: scan] freq 868.3 MHz"]
    out = memory.cmd_learn(mem, again, False, False)
    assert "written" in out
    assert dated_lines(path) == [
        "- [verified 2026-11-07 · src: exp: capture] freq 868.3 MHz",  # the entry's own checked date
        f"- [verified {date.today().isoformat()} · src: exp: x] channel 11",  # no checked date: today
    ]
    sup = json.dumps(
        {
            "topic": "radio",
            "entries": [
                {"claim": "channel 15", "status": "verified", "source": "exp: y", "supersedes": "channel 11"}
            ],
        }
    )
    assert "~ superseded:" in memory.cmd_learn(mem, sup, False, False)
    assert dated_lines(path)[1] == f"- [verified {date.today().isoformat()} · src: exp: y] channel 15"


def test_cli_knowledge(memory, repo, capsys):
    (repo / ".agent" / "knowledge").mkdir(parents=True)
    (repo / ".agent" / "knowledge" / "radio.md").write_text(
        "# k\n" + dated(400, status="reported", claim="freq 868 MHz") + "\n"
    )
    assert memory.main(["knowledge", "--brief"]) == 0
    brief = capsys.readouterr().out
    assert brief.startswith("knowledge: ") and "knowledge/radio" not in brief  # untrusted: memory not scanned
    trust(repo)
    memory.main(["knowledge", "--stale"])
    assert "knowledge/radio: 1 line(s), 1 stale (1 idiom), 1 reported, 1 due" in capsys.readouterr().out
    memory.main(["knowledge", "radio", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert [d["skill"] for d in data] == ["knowledge/radio"]
    memory.main(["knowledge", "lang-go"])
    assert capsys.readouterr().out.startswith("lang-go: ")
    memory.main(["learn", "--promote", "--source", str(repo), "radio"])
    assert "no general entry" in capsys.readouterr().out
    (repo / ".agent" / "knowledge" / "radio.md").write_text(
        "# k\n" + dated(1, claim="shared (general)") + "\n"
    )
    memory.main(["learn", "--promote", "--source", str(repo), "radio"])
    assert "no cobot checkout known" in capsys.readouterr().out
