"""cobot-deps: ecosystem adapters against fake tools, the cache, the brief line and the CLI."""

from __future__ import annotations

import json
import re
import stat
import subprocess
from datetime import date, timedelta
from pathlib import Path

import _cobot_deps as deps
import pytest
from conftest import load_script

TODAY = date(2026, 11, 7)

GO_LIST = (
    '{"Path": "example.com/app", "Main": true, "Version": ""}\n'
    '{"Path": "github.com/a/b", "Version": "v1.0.0", "Update": {"Version": "v1.2.0"}}\n'
    '{"Path": "github.com/c/d", "Version": "v2.0.0"}\n'
    '{"Path": "github.com/e/f", "Version": "v0.1.0", "Indirect": true, "Update": {"Version": "v0.2.0"}}\n'
)
CARGO_UPDATE_ERR = (
    "    Updating crates.io index\n"
    "    Updating serde v1.0.1 -> v1.0.9\n"
    "   Unchanged log v0.4.34 (available: v0.5.0)\n"
    "   Unchanged cc v1.10.0\n"
    "warning: not updating lockfile due to dry run\n"
)
CARGO_DENY = (
    '{"type":"diagnostic","fields":{"code":"vulnerability","message":"x"}}\n'
    '{"type":"summary","fields":{"advisories":{"errors":1,"warnings":0}}}\n'
)
NPM_OUTDATED = json.dumps(
    {
        "left-pad": {"current": "1.0.0", "wanted": "1.0.0", "latest": "1.3.0"},
        "ok": {"current": "2.0.0", "latest": "2.0.0"},
    }
)
NPM_AUDIT = json.dumps(
    {
        "metadata": {
            "vulnerabilities": {"info": 0, "low": 1, "moderate": 0, "high": 2, "critical": 0, "total": 3}
        }
    }
)
UV_TREE = "app v0.1.0\n├── requests v2.31.0 (latest: v2.32.3)\n├── rich v13.0.0\n└── click v8.1.7 (latest: v8.2.0)\n"  # noqa: E501
TF_LOCK = 'provider "registry.terraform.io/hashicorp/google" {\n  version     = "6.0.0"\n  constraints = "~> 6.0"\n}\nprovider "registry.terraform.io/hashicorp/random" {\n  version = "3.6.0"\n}\n'  # noqa: E501


def fake_tool(folder: Path, name: str, cases: list[tuple[str, str, int, str]] | str) -> None:
    """A fake CLI: ``cases`` are ``(glob on "$*", output, exit code, "out"|"err")`` tried in order,
    the output stored in a data file so no quoting is needed; a plain string is the raw script."""
    path = folder / name
    if isinstance(cases, str):
        script = cases
    else:
        script = 'case "$*" in\n'
        for index, (pattern, output, code, stream) in enumerate(cases):
            data = folder / f"{name}.{index}.out"
            data.write_text(output)
            redirect = " >&2" if stream == "err" else ""
            quoted = re.sub(r"([^*?\[\]]+)", r'"\1"', pattern)  # literals quoted, globs bare: "list -m"*
            script += f'  {quoted}) cat "{data}"{redirect}; exit {code} ;;\n'
        script += "esac\nexit 0\n"
    path.write_text("#!/bin/sh\n" + script)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


@pytest.fixture
def tools(tmp_path, monkeypatch):
    folder = tmp_path / "tools"
    folder.mkdir()
    monkeypatch.setenv("PATH", f"{folder}:/usr/bin:/bin")  # no real cargo, go, npm or uv can leak in
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    return folder


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    monkeypatch.chdir(root)
    return root


def write_fakes(folder: Path) -> None:
    fake_tool(folder, "cargo", [("update*", CARGO_UPDATE_ERR, 0, "err")])
    fake_tool(folder, "cargo-deny", [("*", CARGO_DENY, 1, "err")])
    fake_tool(folder, "go", [("list -m*", GO_LIST, 0, "out")])
    fake_tool(
        folder,
        "govulncheck",
        [("*", "Vulnerability #1: GO-2026-0001\nVulnerability #2: GO-2026-0002\n", 3, "out")],
    )
    fake_tool(folder, "npm", [("outdated*", NPM_OUTDATED, 1, "out"), ("audit*", NPM_AUDIT, 1, "out")])
    fake_tool(folder, "uv", [("tree*", UV_TREE, 0, "out")])
    fake_tool(folder, "terraform", [("*", '{"terraform_version": "1.17.0"}', 0, "out")])


def seed_repo(root: Path, *names: str) -> None:
    for name in names:
        content = {
            "Cargo.lock": '[[package]]\nname = "a"\n\n[[package]]\nname = "b"\n',
            ".terraform.lock.hcl": TF_LOCK,
        }.get(name, f"{name}\n")
        (root / name).write_text(content)
    if "package-lock.json" in names:
        (root / "package.json").write_text(
            json.dumps({"dependencies": {"left-pad": "1", "ok": "2"}, "devDependencies": {"ts": "5"}})
        )


def registry(url: str) -> dict | None:
    if "hashicorp/google" in url:
        return {"version": "6.4.0"}
    if "hashicorp/random" in url:
        return {"version": "3.6.0"}
    if "checkpoint" in url:
        return {"current_version": "1.17.1"}
    return None


# ---------------------------------------------------------------- adapters


def test_rust_adapter_countsCompatibleAndAvailable(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "Cargo.lock")
    result = deps.rust(repo, deps.run)
    assert (result.total, result.behind, result.advisories, result.advisory_tool) == (
        2,
        2,
        1,
        "cargo-deny check advisories",
    )
    assert result.items == ["serde v1.0.1 -> v1.0.9", "log v0.4.34 -> v0.5.0 (outside the requirement)"]


def test_rust_adapter_wholeGraph_compatibleUpdatesNotOutsideRequirement(tools, repo):
    # cargo 1.99 on arlo-camera-streamer-rs: `--workspace` holds every dependency back, so
    # each compatible update came back as "Unchanged … (available: …)"
    write_fakes(tools)
    fake_tool(
        tools,
        "cargo",
        [
            ("*--workspace*", "   Unchanged arlo-rs v0.4.0 (available: v0.4.1)\n", 0, "err"),
            (
                "update*",
                "     Locking 3 packages to highest compatible versions\n"
                "    Updating arlo-rs v0.4.0 -> v0.4.1 (requires Rust 1.99.1)\n"
                "   Unchanged matchit v0.8.4 (available: v0.8.6)\n"
                "   Unchanged foo v1.0.0 (available: v2.0.0, requires Rust 1.200)\n",
                0,
                "err",
            ),
        ],
    )
    seed_repo(repo, "Cargo.lock")
    result = deps.rust(repo, deps.run)
    assert result.items == [
        "arlo-rs v0.4.0 -> v0.4.1",
        "matchit v0.8.4 -> v0.8.6 (outside the requirement)",
        "foo v1.0.0 -> v2.0.0 (outside the requirement)",
    ]


def test_rust_adapter_cargoAuditFallback_andMissingTools(tools, repo):
    seed_repo(repo, "Cargo.lock")
    fake_tool(tools, "cargo", [("*", "error: failed to load manifest\n", 101, "err")])
    fake_tool(tools, "cargo-audit", [("*", '{"vulnerabilities": {"count": 4}}', 0, "out")])
    result = deps.rust(repo, deps.run)
    assert result.behind == 0 and result.advisories == 4 and result.advisory_tool == "cargo-audit"
    assert any("cargo update failed: error: failed to load manifest" in n for n in result.notes)
    (tools / "cargo").unlink()
    (tools / "cargo-audit").unlink()
    result = deps.rust(repo, deps.run)
    assert (
        result.notes == ["cargo not installed", "no advisory tool (cargo-deny or cargo-audit)"]
        and result.advisories is None
    )


def test_go_adapter_directModulesOnly(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "go.mod")
    result = deps.go(repo, deps.run)
    assert (result.total, result.behind, result.advisories) == (2, 1, 2)
    assert result.items == ["github.com/a/b v1.0.0 -> v1.2.0"]
    fake_tool(
        tools,
        "go",
        [("*", "go: go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)\n", 1, "err")],
    )
    result = deps.go(repo, deps.run)
    assert result.behind == 0 and result.notes[0].startswith(
        "go list failed: go: go.mod requires go >= 1.27.3"
    )


def test_node_adapter_npmExitOneIsSuccess_andMissingTree(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "package-lock.json")
    result = deps.node(repo, deps.run, "npm", "package-lock.json")
    assert (result.total, result.behind, result.advisories) == (3, 1, 3)
    assert result.items == ["left-pad 1.0.0 -> 1.3.0"] and result.notes == []
    missing = json.dumps({"left-pad": {"wanted": "1.0.0", "latest": "1.3.0"}})
    fake_tool(tools, "npm", [("outdated*", missing, 1, "out"), ("audit*", "nope\n", 1, "out")])
    result = deps.node(repo, deps.run, "npm", "package-lock.json")
    assert result.behind == 0 and "no installed tree: run `npm install` first" in result.notes
    assert result.advisories is None and "npm audit gave no JSON (exit 1)" in result.notes
    (tools / "npm").unlink()
    result = deps.node(repo, deps.run, "npm", "package-lock.json")
    assert result.as_dict()["notes"] == ["npm not installed"]


def test_uv_adapter_parsesTree_andPipAuditOptional(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "uv.lock")
    result = deps.uv_tree(repo, deps.run)
    assert (result.total, result.behind) == (3, 2) and result.items == [
        "requests 2.31.0 -> 2.32.3",
        "click 8.1.7 -> 8.2.0",
    ]
    assert result.advisories is None and "pip-audit not installed" in result.notes
    fake_tool(tools, "uv", [("tree*", UV_TREE, 0, "out"), ("export*", "requests==2.31.0\n", 0, "out")])
    fake_tool(
        tools,
        "pip-audit",
        [
            (
                "*",
                '{"dependencies": [{"name": "requests", "vulns": [{"id": "X"}, {"id": "Y"}]}, {"name": "rich", "vulns": []}]}',  # noqa: E501
                0,
                "out",
            )
        ],
    )
    result = deps.uv_tree(repo, deps.run)
    assert result.advisories == 2 and result.advisory_tool == "pip-audit"
    assert not (repo / ".agent" / ".deps-requirements.txt").exists()
    fake_tool(tools, "uv", [("tree*", "error: no lock\n", 2, "err"), ("export*", "", 1, "out")])
    result = deps.uv_tree(repo, deps.run)
    assert (
        result.notes[0] == "uv tree failed: error: no lock"
        and "uv export failed; pip-audit skipped" in result.notes
    )


def test_poetry_adapter(tools, repo):
    seed_repo(repo, "poetry.lock")
    fake_tool(
        tools,
        "poetry",
        [
            ("*--outdated*", "requests (!) 2.31.0 2.32.3 HTTP\nclick 8.1.7 8.2.0 CLI\n", 0, "out"),
            ("show --top-level*", "requests 2.31.0 HTTP\nclick 8.1.7 CLI\nrich 13.0.0 Text\n", 0, "out"),
        ],
    )
    result = deps.poetry(repo, deps.run)
    assert (result.total, result.behind) == (3, 2) and result.items == [
        "requests 2.31.0 -> 2.32.3",
        "click 8.1.7 -> 8.2.0",
    ]
    (tools / "poetry").unlink()
    assert deps.poetry(repo, deps.run).notes == ["poetry not installed"]


def test_terraform_adapter_registryAndCheckpoint(tools, repo):
    write_fakes(tools)
    seed_repo(repo, ".terraform.lock.hcl")
    result = deps.terraform(repo, deps.run, fetch=registry)
    assert (result.total, result.behind) == (3, 2)
    assert result.items == ["hashicorp/google 6.0.0 -> 6.4.0", "terraform 1.17.0 -> 1.17.1"]
    result = deps.terraform(repo, deps.run, fetch=lambda _url: None)
    assert (
        result.behind == 0
        and "registry unreachable for hashicorp/google" in result.notes
        and "checkpoint unreachable for terraform core" in result.notes
    )
    assert deps.fetch_json("https://127.0.0.1:9/nothing") is None


def test_jsonObjects_streamsAndNoise():
    assert deps.json_objects('{"a": 1}\ngarbage line\n{"b": [1, 2]} {"c": null}') == [
        {"a": 1},
        {"b": [1, 2]},
        {"c": None},
    ]
    assert deps.first_json("") is None and deps.json_objects("   ") == []


def test_run_missingAndTimeout(tools, repo, monkeypatch):
    assert deps.run(["definitely-not-a-tool-xyz"], repo)[0] is None
    monkeypatch.setattr(deps, "TOOL_TIMEOUT", 0.2)
    fake_tool(tools, "slowtool", "sleep 2\n")
    code, _out, err = deps.run(["slowtool"], repo)
    assert code is None and err.startswith("slowtool timed out")


# ---------------------------------------------------------------- cache, check, brief


def test_cacheKey_originThenRootCommitThenPath(repo):
    assert deps.cache_key(repo).startswith("path/")
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=t@x",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "init",
        ],
        check=True,
    )
    assert deps.cache_key(repo).startswith("local/")
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "origin", "git@github.com:YpNo/x.git"], check=True
    )
    assert deps.cache_key(repo) == "github.com/ypno/x"
    assert deps.cache_path(repo).name == "github.com__ypno__x.json"


def test_check_runsCachesAndReportsStaleness(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "Cargo.lock", "go.mod", "yarn.lock")
    assert deps.brief(repo, TODAY) == "deps: not checked; run cobot-deps check"
    data = deps.check(repo, TODAY)
    assert (
        data["cached"] is False
        and [e["ecosystem"] for e in data["ecosystems"]] == ["rust", "go"]
        and data["unsupported"] == ["yarn"]
    )
    text = deps.report(data, TODAY)
    assert text.startswith("deps: 3 of 4 behind, 3 advisories (checked today)")
    assert (
        "  rust (Cargo.lock): 2 of 2 behind · cargo update --dry-run --verbose · 1 advisories (cargo-deny check advisories)"  # noqa: E501
        in text
    )
    assert (
        "    github.com/a/b v1.0.0 -> v1.2.0" in text
        and "unsupported here, check by hand: yarn" in text
        and "/cobot:consult gha" not in text  # no workflow here: no Actions hint (F-48)
    )
    again = deps.check(repo, TODAY)
    assert again["cached"] is True and deps.report(again, TODAY).startswith(
        "deps: 3 of 4 behind, 3 advisories (checked today) [cached]"
    )
    assert deps.brief(repo, TODAY) == "deps: 3 of 4 behind, 3 advisories (checked today)"
    assert (
        deps.brief(repo, TODAY + timedelta(days=3))
        == "deps: 3 of 4 behind, 3 advisories (checked 3 day(s) ago)"
    )
    assert deps.brief(repo, TODAY + timedelta(days=8)).endswith("; stale, run cobot-deps check")
    (repo / "go.mod").write_text("changed\n")
    assert deps.brief(repo, TODAY).endswith("; a lockfile changed since, run cobot-deps check")
    assert deps.check(repo, TODAY)["cached"] is False
    forced = deps.check(repo, TODAY, force=True)
    assert forced["cached"] is False
    cache = json.loads(deps.cache_path(repo).read_text())
    assert "cached" not in cache and cache["lockfiles"].keys() == {"Cargo.lock", "go.mod", "yarn.lock"}


def test_check_scrubsSecretsAndSurvivesABrokenAdapter(tools, repo, monkeypatch):
    seed_repo(repo, "Cargo.lock", "go.mod")
    fake_tool(
        tools,
        "cargo",
        [("*", "error: token = ghp_abcdefghijklmnopqrstuvwxyz0123456789 rejected\n", 1, "err")],
    )

    def boom(_root, _runner):
        raise RuntimeError("kaput")

    monkeypatch.setattr(deps, "ADAPTERS", [("Cargo.lock", deps.rust), ("go.mod", boom)])
    data = deps.check(repo, TODAY)
    text = json.dumps(data)
    assert "ghp_" not in text and "[redacted]" in text
    assert data["ecosystems"][1]["notes"] == ["adapter failed: RuntimeError: kaput"]


def test_check_noLockfile_andCorruptCache(repo, tools):
    assert deps.brief(repo, TODAY) == "deps: no lockfile"
    data = deps.check(repo, TODAY)
    assert (
        data["ecosystems"] == []
        and deps.headline(data, TODAY) == "deps: no supported lockfile (checked today)"
    )
    deps.cache_path(repo).write_text("{broken")
    assert deps.read_cache(repo) is None and deps.cache_state(repo, {"checked": "nonsense"}, TODAY) == "none"
    assert deps.totals({"ecosystems": [{"behind": 1, "total": 2, "advisories": None}]}) == (1, 2, None)
    assert (
        deps.headline(
            {"checked": TODAY.isoformat(), "ecosystems": [{"behind": 0, "total": 1, "advisories": 1}]}, TODAY
        )
        == "deps: 0 of 1 behind, 1 advisory (checked today)"
    )


def test_cli(tools, repo, capsys, monkeypatch):
    write_fakes(tools)
    seed_repo(repo, "uv.lock")
    script = load_script("cobot-deps", "cobot_deps_cli")
    assert script.main(["check"]) == 0
    assert capsys.readouterr().out.startswith("deps: 2 of 3 behind")
    assert script.main(["check", "--json", "--fresh"]) == 0
    assert json.loads(capsys.readouterr().out)["ecosystems"][0]["ecosystem"] == "python"
    assert script.main(["brief"]) == 0 and capsys.readouterr().out.startswith("deps: 2 of 3 behind")
    assert script.main(["path"]) == 0 and capsys.readouterr().out.strip().endswith(".json")
    assert script.main(["bogus"]) == 2


def test_rust_adapter_denyGraphTargets_notesNarrowerScopeThanLockfile(tools, repo):
    # arlo-camera-streamer-rs: deny.toml lists four targets, so cargo-deny skips a wasm32-only
    # crate's advisory that cargo-audit, reading the whole Cargo.lock, reports
    write_fakes(tools)
    seed_repo(repo, "Cargo.lock")
    (repo / "deny.toml").write_text('[graph]\ntargets = [\n  { triple = "x86_64-unknown-linux-gnu" },\n]\n')
    result = deps.rust(repo, deps.run)
    assert (
        "cargo-deny checks only the deny.toml [graph] targets; cargo-audit reads all of Cargo.lock"
        in result.notes
    )


def test_rust_adapter_denyWithoutTargetsOrUnreadable_noScopeNote(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "Cargo.lock")
    (repo / "deny.toml").write_text("[advisories]\nignore = []\n")
    assert not any("deny.toml" in note for note in deps.rust(repo, deps.run).notes)
    (repo / "deny.toml").write_text("not = [valid toml\n")
    assert not any("deny.toml" in note for note in deps.rust(repo, deps.run).notes)


# ---------------------------------------------------------------- toolchains and the Actions hint (story 7)

FLOATING = [
    ("rust-toolchain.toml", '[toolchain]\nchannel = "stable"\n', "rust-toolchain.toml: stable"),
    ("rust-toolchain", "nightly\n", "rust-toolchain: nightly"),
    (".nvmrc", "lts/iron\n", ".nvmrc: lts/iron"),
    (".node-version", "20\n", ".node-version: 20"),
    (".python-version", "3\n", ".python-version: 3"),
    (".tool-versions", "rust stable\nnodejs 22.11.0\n", ".tool-versions: rust stable"),
    ("mise.toml", '[tools]\nnode = "latest"\n', "mise.toml: node latest"),
    (".mise.toml", '[tools]\npython = { version = "3" }\n', ".mise.toml: python 3"),
    (".config/mise.toml", '[tools]\ngo = ["lts"]\n', ".config/mise.toml: go lts"),
]
PINNED = [
    ("rust-toolchain.toml", '[toolchain]\nchannel = "1.99.1"\n'),
    ("rust-toolchain", "nightly-2026-11-01\n"),
    (".nvmrc", "v22.11.0\n"),
    (".python-version", "3.12\n"),
    (".tool-versions", "rust 1.99.1\n"),
    ("mise.toml", '[tools]\nnode = "22.11.0"\n'),
]


@pytest.mark.parametrize(("name", "text", "row"), FLOATING)
def test_toolchainRows_floatingChannel_named(repo, name, text, row):
    (repo / name).parent.mkdir(parents=True, exist_ok=True)
    (repo / name).write_text(text)
    rows = deps.toolchain_rows(repo)
    assert any(r.startswith(row) and "floats" in r for r in rows), rows


@pytest.mark.parametrize(("name", "text"), PINNED)
def test_toolchainRows_pinnedFile_nothing(repo, name, text):
    (repo / name).write_text(text)
    assert deps.toolchain_rows(repo) == []


def test_toolchainRows_goModWithoutToolchain_isANote(repo):
    (repo / "go.mod").write_text("module x\n\ngo 1.27\n")
    rows = deps.toolchain_rows(repo)
    assert rows and "go.mod" in rows[0] and "note" in rows[0] and "floats" not in rows[0]
    (repo / "go.mod").write_text("module x\n\ngo 1.27\n\ntoolchain go1.27.3\n")
    assert deps.toolchain_rows(repo) == []


def test_check_readOnlyCache_reportsAnyway(tools, repo, monkeypatch):
    # an eval sandbox mounts the data folder read-only: the report must still come out (T06)
    write_fakes(tools)
    seed_repo(repo, "go.mod")
    (repo / "rust-toolchain").write_text("stable\n")

    def refuse(*args, **kwargs):
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr(deps.Path, "write_text", refuse)
    data = deps.check(repo, TODAY)
    text = deps.report(data, TODAY)
    assert "cache: not written (Read-only file system)" in text and "rust-toolchain: stable floats" in text


def test_report_actionsHint_onlyWithAWorkflow_andToolchainsShown(tools, repo):
    write_fakes(tools)
    seed_repo(repo, "go.mod")
    (repo / "rust-toolchain").write_text("stable\n")
    text = deps.report(deps.check(repo, TODAY), TODAY)
    assert "GitHub Actions pins" not in text and "toolchain: rust-toolchain: stable floats" in text
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("on: push\n")
    cached = deps.check(repo, TODAY)  # cached result: the file facts are read again
    assert cached["cached"] is True and "GitHub Actions pins" in deps.report(cached, TODAY)
