"""cobot-env: presence detection that runs nothing, the owner's answers per host, the brief line
and the CLI (spec onboard-environment, stories 1, 2 and 7)."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import _cobot_env as env_mod
import pytest
from conftest import BIN, load_script

MARKER_SCRIPT = '#!/bin/sh\ntouch "{marker}"\necho ran\n'


def executable(folder: Path, name: str, text: str = "#!/bin/sh\nexit 0\n") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


@pytest.fixture
def machine(tmp_path):
    """A fake machine: a filesystem root with os-release, a home, a trusted bin folder, a repository
    with a .git folder, and an environment naming them; nothing of the real machine is read."""
    fs = tmp_path / "fs"
    (fs / "etc").mkdir(parents=True)
    (fs / "etc" / "os-release").write_text('PRETTY_NAME="Debian 13"\nID=debian\nVERSION_ID="13"\n')
    home = tmp_path / "home"
    home.mkdir()
    system = tmp_path / "usr-bin"
    system.mkdir()
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    values = {"HOME": str(home), "PATH": str(system)}
    return {"fs": fs, "home": home, "bin": system, "repo": repo, "env": values}


def detect(machine, programs=()):
    return env_mod.detect(machine["repo"], machine["env"], fs_root=machine["fs"], programs=programs)


# ---------------------------------------------------------------- story 1: detect by presence


def test_detect_enginesManagersIsolation_byPresenceOnPath(machine):
    for name in ("docker", "podman", "mise", "asdf", "distrobox", "toolbox", "devcontainer"):
        executable(machine["bin"], name)
    found = detect(machine)
    assert found["engines"] == ["docker", "podman"]
    assert found["managers"] == ["mise", "asdf"]
    assert found["isolation"] == ["distrobox", "toolbox", "devcontainer"]


def test_detect_nixStore_countsAsNix(machine):
    (machine["fs"] / "nix" / "store").mkdir(parents=True)
    assert "nix" in detect(machine)["isolation"]


def test_detect_dockerSymlinkToPodman_isOneEngine(machine):
    podman = executable(machine["bin"], "podman")
    (machine["bin"] / "docker").symlink_to(podman)
    assert detect(machine)["engines"] == ["podman (docker is podman)"]


def test_detect_podmanDockerWrapperScript_isOneEngine(machine):
    executable(machine["bin"], "podman")
    executable(machine["bin"], "docker", '#!/bin/sh\nexec /usr/bin/podman "$@"\n')
    assert detect(machine)["engines"] == ["podman (docker is podman)"]


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("unix:///run/user/1000/podman/podman.sock", ["podman (docker talks to podman)"]),
        ("unix:///home/me/.colima/default/docker.sock", ["docker (colima)"]),
        ("unix:///home/me/.orbstack/run/docker.sock", ["docker (orbstack)"]),
        ("tcp://10.0.0.5:2376", ["docker"]),
    ],
)
def test_detect_dockerHost_namesTheEngineBehindTheSocket(machine, host, expected):
    executable(machine["bin"], "docker")
    machine["env"]["DOCKER_HOST"] = host
    assert detect(machine)["engines"] == expected


def test_detect_dockerContextByName_namesTheEngine(machine):
    executable(machine["bin"], "docker")
    config = machine["home"] / ".docker"
    config.mkdir()
    (config / "config.json").write_text(json.dumps({"currentContext": "colima"}))
    assert detect(machine)["engines"] == ["docker (colima)"]


def test_detect_dockerContextMeta_readsTheEndpointHost(machine):
    executable(machine["bin"], "docker")
    config = machine["home"] / ".docker"
    meta = config / "contexts" / "meta" / hashlib.sha256(b"work").hexdigest()
    meta.mkdir(parents=True)
    (meta / "meta.json").write_text(
        json.dumps({"Name": "work", "Endpoints": {"docker": {"Host": "unix:///run/podman/podman.sock"}}})
    )
    (config / "config.json").write_text(json.dumps({"currentContext": "work"}))
    assert detect(machine)["engines"] == ["podman (docker talks to podman)"]


def test_detect_brokenDockerConfig_isIgnored(machine):
    executable(machine["bin"], "docker")
    (machine["home"] / ".docker").mkdir()
    (machine["home"] / ".docker" / "config.json").write_text("{not json")
    assert detect(machine)["engines"] == ["docker"]


def test_detect_helperAliases_fdfindCountsAsFd(machine):
    executable(machine["bin"], "fdfind")
    executable(machine["bin"], "rg")
    found = detect(machine)
    assert found["helpers"]["fd"].endswith("fdfind")
    assert found["helpers"]["ripgrep"].endswith("rg")
    assert found["helpers"]["rtk"] is None


def test_detect_repositoryPathEntry_reportedNeverRun(machine, tmp_path):
    marker = tmp_path / "ran"
    executable(machine["repo"] / "bin", "docker", MARKER_SCRIPT.format(marker=marker))
    machine["env"]["PATH"] = f"{machine['repo'] / 'bin'}{os.pathsep}{machine['bin']}"
    found = detect(machine)
    assert found["engines"] == ["docker via repository"]
    assert found["untrusted"] == [f"docker via repository ({machine['repo'] / 'bin' / 'docker'})"]
    assert not marker.exists()


def test_detect_repositoryDockerLinkedToPodman_isNotFollowed(machine):
    podman = executable(machine["bin"], "podman")
    (machine["repo"] / "bin").mkdir()
    (machine["repo"] / "bin" / "docker").symlink_to(podman)
    machine["env"]["PATH"] = f"{machine['repo'] / 'bin'}{os.pathsep}{machine['bin']}"
    assert detect(machine)["engines"] == ["docker via repository", "podman"]


@pytest.mark.parametrize("entry", ["bin", "", "."])
def test_detect_relativePathEntry_isTheRepository(machine, entry, monkeypatch):
    executable(machine["repo"] / "bin", "rg")
    executable(machine["repo"], "rg")
    monkeypatch.chdir(machine["repo"])
    machine["env"]["PATH"] = f"{entry}{os.pathsep}{machine['bin']}"
    assert detect(machine)["helpers"]["ripgrep"].startswith("via repository")


def test_detect_miseShims_reportedAsShim(machine):
    shims = machine["home"] / ".local" / "share" / "mise" / "shims"
    executable(shims, "jq")
    machine["env"]["PATH"] = f"{shims}{os.pathsep}{machine['bin']}"
    found = detect(machine)
    assert found["helpers"]["jq"].startswith("via mise shim")
    # a shim runs a tool the owner installed, at the version the repository pins: reported apart,
    # never followed by detection, but not a repository program (eval run 2026-11-16 ran nothing)
    assert found["shims"] == [f"jq via mise shim ({shims / 'jq'})"]
    assert found["untrusted"] == []


def test_report_shimHit_isPresentAndRunnable_repositoryHitIsNot(cli, machine, monkeypatch, capsys, tmp_path):
    shims = machine["home"] / ".local" / "share" / "mise" / "shims"
    executable(shims, "python3")
    executable(shims, "rg")
    executable(machine["repo"] / "bin", "jq")
    monkeypatch.chdir(machine["repo"])
    monkeypatch.setenv("HOME", str(machine["home"]))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("PATH", f"{machine['repo'] / 'bin'}{os.pathsep}{shims}")
    assert cli.main(["detect", "python3"]) == 0
    out = capsys.readouterr().out
    assert "helpers: present ripgrep; absent rtk, fd, jq, gh" in out
    assert "\nnot trusted: jq via repository" in out
    assert "\nshims: rg via mise shim" in out and "python3 via mise shim" in out
    assert "not trusted: python3" not in out
    found = env_mod.detect(machine["repo"], os.environ, fs_root=machine["fs"])
    line = env_mod.brief(found, Path("/nonexistent"))
    assert "not trusted: jq via repository" in line and "python3" not in line


def test_detect_miseDataDir_shimsReportedAsShim(machine, tmp_path):
    shims = tmp_path / "mise-data" / "shims"
    executable(shims, "gh")
    machine["env"]["MISE_DATA_DIR"] = str(tmp_path / "mise-data")
    machine["env"]["PATH"] = str(shims)
    assert detect(machine)["helpers"]["gh"].startswith("via mise shim")


def test_detect_nonExecutableFile_isAbsent(machine):
    (machine["bin"] / "jq").write_text("not a program")
    assert detect(machine)["helpers"]["jq"] is None


def test_detect_programs_presentAbsentAndRefusedNames(machine):
    executable(machine["bin"], "cargo")
    found = detect(machine, programs=("cargo", "shellcheck"))
    assert found["programs"]["cargo"].endswith("cargo")
    assert found["programs"]["shellcheck"] is None
    with pytest.raises(ValueError, match="program name"):
        detect(machine, programs=("../evil",))


@pytest.mark.parametrize(
    ("files", "env", "expected"),
    [
        ({"run/.containerenv": 'engine="podman"\nname="dev"\n'}, {"CONTAINER_ID": "dev"}, "distrobox dev"),
        ({"run/.containerenv": 'name="tb"\n', "run/.toolboxenv": ""}, {}, "toolbox tb"),
        ({"run/.containerenv": 'name="web"\n'}, {}, "podman web"),
        ({".dockerenv": ""}, {}, "docker"),
        ({}, {}, ""),
        ({}, {"CONTAINER_ID": "bad name;rm"}, "distrobox"),
    ],
)
def test_detect_insideContainer_namesWhich(machine, files, env, expected):
    for name, text in files.items():
        path = machine["fs"] / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    machine["env"].update(env)
    assert detect(machine)["inside"] == expected


def test_detect_key_isHostThenContainer(machine, monkeypatch):
    monkeypatch.setattr(env_mod, "hostname", lambda: "box")
    assert detect(machine)["key"] == "box"
    machine["env"]["CONTAINER_ID"] = "dev"
    assert detect(machine)["key"] == "box/dev"


def test_detect_osAndPackageManagers(machine):
    executable(machine["bin"], "apt-get")
    executable(machine["bin"], "brew")
    found = detect(machine)
    assert found["os"] == "debian 13"
    assert found["package_managers"] == ["apt", "brew"]


def test_detect_noOsRelease_fallsBackToPlatform(machine, monkeypatch):
    (machine["fs"] / "etc" / "os-release").unlink()
    monkeypatch.setattr(env_mod.sys, "platform", "darwin")
    assert detect(machine)["os"] == "macos"
    monkeypatch.setattr(env_mod.sys, "platform", "linux")
    assert detect(machine)["os"] == "linux"


def test_detect_repositoryFiles_namesOnly(machine):
    for name in ("Containerfile", "compose.yaml", ".mise.toml", "distrobox.ini"):
        (machine["repo"] / name).write_text("x")
    (machine["repo"] / ".devcontainer").mkdir()
    found = detect(machine)
    assert found["repository"] == [
        "Containerfile",
        "compose.yaml",
        ".mise.toml",
        "distrobox.ini",
        ".devcontainer",
    ]


def test_detect_rootFoundFromASubfolder(machine):
    sub = machine["repo"] / "src" / "deep"
    sub.mkdir(parents=True)
    executable(machine["repo"] / "tools", "rg")
    machine["env"]["PATH"] = str(machine["repo"] / "tools")
    found = env_mod.detect(sub, machine["env"], fs_root=machine["fs"])
    assert found["helpers"]["ripgrep"].startswith("via repository")


def test_detect_runsNoProgram_andIsFast(machine, monkeypatch):
    for name in ("docker", "podman", "mise", "rg", "fd", "jq", "gh", "rtk", "apt-get"):
        executable(machine["bin"], name)

    def refuse(*_args, **_kwargs):
        raise AssertionError("detection ran a program")

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(os, "system", refuse)
    start = time.perf_counter()
    detect(machine, programs=("cargo",))
    assert time.perf_counter() - start < 0.1


# ---------------------------------------------------------------- choices for the per-repo question


def test_choices_twoEnginesAndABox_recommendFromTheFiles(machine):
    for name in ("docker", "podman", "distrobox", "mise"):
        executable(machine["bin"], name)
    (machine["repo"] / "Containerfile").write_text("FROM x")
    (machine["repo"] / "distrobox.ini").write_text("[dev]")
    choices = env_mod.choices(detect(machine))
    assert choices == [
        ("engine", ["podman", "docker"], "podman"),
        ("builds", ["distrobox", "host"], "distrobox"),
    ]


def test_choices_oneWayOnly_noQuestion(machine):
    executable(machine["bin"], "podman")
    executable(machine["bin"], "mise")
    assert env_mod.choices(detect(machine)) == []


def test_choices_twoManagers_recommendThePinFile(machine):
    executable(machine["bin"], "mise")
    executable(machine["bin"], "asdf")
    (machine["repo"] / ".tool-versions").write_text("python 3.13\n")
    assert env_mod.choices(detect(machine)) == [("runtime manager", ["asdf", "mise"], "asdf")]


def test_choices_insideABox_buildsAreNotAsked(machine):
    executable(machine["bin"], "distrobox")
    machine["env"]["CONTAINER_ID"] = "dev"
    assert env_mod.choices(detect(machine)) == []


def test_choices_untrustedEngine_isNotAWay(machine):
    executable(machine["bin"], "podman")
    executable(machine["repo"] / "bin", "docker")
    machine["env"]["PATH"] = f"{machine['repo'] / 'bin'}{os.pathsep}{machine['bin']}"
    assert env_mod.choices(detect(machine)) == []


# ---------------------------------------------------------------- story 2: the owner's answers


@pytest.fixture
def profile(tmp_path):
    return tmp_path / "config" / "cobot" / "machine.md"


def test_prefer_twoKeys_neverOverwriteEachOther(profile):
    env_mod.prefer("mise", "box", profile)
    env_mod.prefer("apt", "box/dev", profile)
    assert env_mod.answers("box", profile) == {"route": "mise", "declined": []}
    assert env_mod.answers("box/dev", profile) == {"route": "apt", "declined": []}
    env_mod.prefer("brew", "box", profile)
    assert env_mod.answers("box", profile)["route"] == "brew"
    assert env_mod.answers("box/dev", profile)["route"] == "apt"


def test_prefer_keepsLinesTheOwnerEdited(profile):
    env_mod.prefer("mise", "box", profile)
    text = profile.read_text().replace("route: mise\n", "route: mise\nnote: rootless podman, ask me\n")
    profile.write_text(text + "\nmy own trailing line\n")
    env_mod.prefer("apt", "box", profile)
    env_mod.decline("rtk", "box", profile)
    after = profile.read_text()
    assert "note: rootless podman, ask me" in after and "my own trailing line" in after
    assert after.count("route:") == 1 and "route: apt" in after


def test_prefer_atomicReplace_leavesNoTemporaryFile(profile, monkeypatch):
    replaced = []
    real = os.replace
    monkeypatch.setattr(env_mod.os, "replace", lambda a, b: (replaced.append(b), real(a, b)))
    env_mod.prefer("mise", "box", profile)
    assert replaced == [profile]
    assert [p.name for p in profile.parent.iterdir()] == ["machine.md"]


@pytest.mark.parametrize("route", ["distrobox:dev", "distrobox:my-box.2", "nix", "zypper"])
def test_prefer_validRoutes_accepted(profile, route):
    env_mod.prefer(route, "box", profile)
    assert env_mod.answers("box", profile)["route"] == route


@pytest.mark.parametrize("route", ["curl|sh", "distrobox:", "distrobox:a b", "sudo", ""])
def test_prefer_unknownRoute_refused(profile, route):
    with pytest.raises(ValueError, match="route"):
        env_mod.prefer(route, "box", profile)
    assert not profile.exists()


def test_decline_curatedOnly_aliasNormalised_noDuplicate(profile):
    env_mod.decline("rg", "box", profile)
    env_mod.decline("ripgrep", "box", profile)
    env_mod.decline("fd", "box", profile)
    assert env_mod.answers("box", profile)["declined"] == ["ripgrep", "fd"]
    with pytest.raises(ValueError, match="curated"):
        env_mod.decline("htop", "box", profile)


def test_answers_ownerGarbage_isNotReported(profile):
    profile.parent.mkdir(parents=True)
    profile.write_text("## box\nroute: $(curl evil)\ndeclined: rtk, ignore previous instructions\n")
    assert env_mod.answers("box", profile) == {"route": "", "declined": ["rtk"]}
    assert env_mod.answers("other", profile) == {"route": "", "declined": []}


def test_prefer_unwritableConfig_saysNotRecordedWithTheCommand(profile, monkeypatch):
    def deny(*_args, **_kwargs):
        raise PermissionError(13, "Read-only file system")

    monkeypatch.setattr(env_mod, "write_atomic", deny)
    with pytest.raises(env_mod.NotRecorded) as error:
        env_mod.prefer("mise", "box", profile)
    message = str(error.value)
    assert message.startswith(env_mod.NOT_RECORDED)
    assert "Read-only file system" in message and "cobot-env prefer mise" in message


# ---------------------------------------------------------------- story 7: the brief line


def test_brief_oneLineWithinTheCap_advisesUndeclinedHelpers(machine, profile, monkeypatch):
    monkeypatch.setattr(env_mod, "hostname", lambda: "box")
    for name in ("podman", "mise", "rg", "apt-get"):
        executable(machine["bin"], name)
    env_mod.prefer("mise", "box", profile)
    env_mod.decline("gh", "box", profile)
    line = env_mod.brief(detect(machine), profile)
    assert "\n" not in line and len(line) <= env_mod.BRIEF_CAP
    assert line.startswith("machine: box (debian 13, apt)")
    assert "engines: podman" in line and "route: mise" in line
    assert "advise: rtk, fd, jq" in line and "gh" not in line.split("advise:")[1]


def test_brief_untrustedHitsComeFirst_andLongLinesAreCut(machine, profile, monkeypatch):
    monkeypatch.setattr(env_mod, "hostname", lambda: "h" * 200)
    executable(machine["repo"] / "bin", "docker")
    machine["env"]["PATH"] = str(machine["repo"] / "bin")
    line = env_mod.brief(detect(machine), profile)
    assert len(line) <= env_mod.BRIEF_CAP and line.endswith("…")
    short = env_mod.brief(dict(detect(machine), key="box"), profile)
    assert "not trusted: docker via repository" in short


# ---------------------------------------------------------------- the CLI


@pytest.fixture
def cli():
    return load_script("cobot-env", "cobot_env")


def run_cli(args, cwd, env, check=False):
    return subprocess.run(
        [sys.executable, "-I", str(BIN / "cobot-env"), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=check,
    )


def test_cli_detect_marker_neverWritten(machine, tmp_path):
    marker = tmp_path / "ran"
    for name in ("docker", "podman", "rg", "mise"):
        executable(machine["repo"] / "bin", name, MARKER_SCRIPT.format(marker=marker))
    env = {**machine["env"], "PATH": f"{machine['repo'] / 'bin'}{os.pathsep}/usr/bin{os.pathsep}/bin"}
    out = run_cli(["detect", "cargo"], machine["repo"], env, check=True).stdout
    assert "not trusted: docker via repository" in out
    assert "\nprograms: cargo" in out
    assert not marker.exists()


def test_cli_detectJson_andShow(machine, tmp_path):
    env = {**machine["env"], "CLAUDE_CONFIG_DIR": str(tmp_path / "cfg")}
    data = json.loads(run_cli(["detect", "--json"], machine["repo"], env, check=True).stdout)
    assert {"key", "engines", "helpers", "choices", "answers"} <= set(data)
    assert run_cli(["prefer", "mise"], machine["repo"], env).returncode == 0
    shown = run_cli(["show"], machine["repo"], env, check=True).stdout
    assert "route: mise" in shown and str(tmp_path / "cfg" / "cobot" / "machine.md") in shown


def test_cli_brief_isOneLine(machine, tmp_path):
    env = {**machine["env"], "CLAUDE_CONFIG_DIR": str(tmp_path / "cfg")}
    out = run_cli(["brief"], machine["repo"], env, check=True).stdout
    assert out.startswith("machine: ") and out.count("\n") == 1


@pytest.mark.parametrize(
    ("args", "code"),
    [(["decline", "htop"], 2), (["prefer", "curl|sh"], 2), (["prefer"], 2), (["nope"], 2), ([], 2)],
)
def test_cli_refusals_exitTwo(cli, capsys, monkeypatch, tmp_path, args, code):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    assert cli.main(args) == code
    assert not (tmp_path / "cfg" / "cobot" / "machine.md").exists()


def test_cli_help_runsNothing(cli, capsys):
    assert cli.main(["--help"]) == 0
    assert "cobot-env" in capsys.readouterr().out
    assert cli.main(["detect", "--bogus"]) == 2


def test_cli_notRecorded_exitsOne(cli, capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))

    def deny(*_args, **_kwargs):
        raise PermissionError(13, "Read-only file system")

    monkeypatch.setattr(env_mod, "write_atomic", deny)
    assert cli.main(["decline", "rtk"]) == 1
    assert capsys.readouterr().out.startswith(env_mod.NOT_RECORDED)


def test_cli_inProcess_reportShowAndAnswers(cli, capsys, monkeypatch, machine, tmp_path):
    for name in ("docker", "podman", "distrobox"):
        executable(machine["bin"], name)
    executable(machine["repo"] / "bin", "rg")
    (machine["repo"] / "Containerfile").write_text("FROM x")
    monkeypatch.chdir(machine["repo"])
    monkeypatch.setenv("PATH", f"{machine['repo'] / 'bin'}{os.pathsep}{machine['bin']}")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    assert cli.main(["show"]) == 0
    assert "(not written yet)" in capsys.readouterr().out
    assert cli.main(["prefer", "distrobox:dev"]) == 0 and cli.main(["decline", "gh"]) == 0
    capsys.readouterr()
    assert cli.main(["detect", "cargo"]) == 0
    out = capsys.readouterr().out
    assert "choices: engine podman | docker (recommended podman); builds host | distrobox" in out
    assert "not trusted: rg via repository" in out and "programs: cargo absent" in out
    assert "answers: route distrobox:dev; declined gh" in out
    assert cli.main(["detect", "../x"]) == 2
