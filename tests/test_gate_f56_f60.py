"""Where a copy, a download or an extraction lands (spec gate-f56-f60, F-56 and F-60).

The gate checked the words a copy names, not the place it lands: an option value joined to its
option, a source copied into a folder, a download into a folder, an extraction into the working
directory and a config dir outside HOME reached no decision.
"""

from __future__ import annotations

import json
import os

import pytest


def decide(rules, command, agent=None, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent, cwd)[0].decision


# ---------------------------------------------------------------- story 1: option values (F-60)

LANDING_OPTION_REFUSED = [
    "cp --target-directory=$HOME/.claude cobot.rules",
    "cp --target-directory=~/.claude cobot.rules",
    "cp -t$HOME/.claude cobot.rules",
    "cp -rt$HOME/.claude cobot.rules",
    "cp --target=$HOME/.claude cobot.rules",
    "cp --t=$HOME/.claude cobot.rules",
    "mv --target-directory=$HOME/.claude cobot.rules",
    "ln --target-directory=$HOME/.claude cobot.rules",
    "install --target-directory=$HOME/.claude cobot.rules",
    "curl -o~/.claude/cobot.rules https://h/x",
    "curl -sSLo~/.claude/cobot.rules https://h/x",
    "curl --output=~/.claude/cobot.rules https://h/x",
    "wget -O~/.claude/cobot.rules https://h/x",
    "wget --output-document=~/.claude/cobot.rules https://h/x",
    "curl --output-dir=~/.claude -O https://h/x",
    "wget -P~/.claude https://h/x",
    "wget --directory-prefix=~/.claude https://h/x",
    "7z x -o$HOME/.claude e.7z",
    "cpio -i -D ~/.claude < e.cpio",
    # T01 bypass review: a joined path on any short option, current 7-Zip binaries
    "wget -o~/.claude/cobot.rules https://h/x",
    "wget -qa~/.claude/cobot.rules https://h/x",
    "curl -sD~/.claude/cobot.rules https://h/x",
    "curl -c~/.claude/cobot.rules https://h/x",
    "sort -o~/.claude/cobot.rules x",
    "gcc -o~/.claude/cobot.rules x.c",
    "7zz x -o~/.claude/cobot a.7z",
    "7zr x -o$HOME/.claude a.7z",
]
LANDING_OPTION_SILENT = [
    "cp -t dist a.js",
    "cp --target-directory=dist a.js",
    "curl -oout.json https://h/x",
    "curl -o out.json https://h/x",
    "wget -O- https://h/x",
    "wget -Pdl https://h/x",
    "7z x -odist e.7z",
    "gcc -I/usr/include -o build/x x.c",
    "curl -fsSLo /tmp/x https://h/x",
    "install -t ~/.local/bin x",
    "cp -t ~/.claude/projects x",
]


@pytest.mark.parametrize("command", LANDING_OPTION_REFUSED)
def test_story1_joinedLandingOption_isRefusedAsTheSeparateForm(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", LANDING_OPTION_SILENT)
def test_story1_landingOptionOutsideAProtectedFolder_staysSilent(rules, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- story 2: landing words per copier

LANDING_ASKED = [
    "cp e/.claude.json ~/",
    "cp e/.claude.json ~",
    "cp -t ~ e/.claude.json",
    "mv e/.claude.json ~",
    "ln -s e/.claude.json ~",
    "install e/.claude.json ~",
    "rsync e/.claude.json ~/",
    "rsync -rt e/.claude.json ~/",
    "scp h:/x/.claude.json ~/",
    "scp -P 22 h:/x/.claude.json ~",
    "cp e/.bashrc ~/",
    "cp -t ~ .bashrc",
    "cp x/.zshenv y/.profile ~/",
]
LANDING_REFUSED = [
    "scp h:/x/cobot.rules ~/.claude",
    "scp -r h:/x/cobot ~/.claude/",
    "docker cp c:/x/cobot.rules ~/.claude/",
    "podman cp c:/x/cobot.rules ~/.claude",
    "kubectl cp ns/pod:/x/cobot.rules ~/.claude/",
    "rclone copy r:x/cobot.rules ~/.claude/",
    "rclone copy r:x/cobot.rules ~/.claude/ --transfers 4",
    "cp --parents .claude/cobot.rules ~",
    "rsync -R .claude/cobot.rules ~/",
    "rsync --relative .claude/cobot.rules ~/",
    "cp e/cobot.rules ~/.claude/shell-snapshots/",
]
LANDING_SILENT = [
    "cp a ~",
    "cp README.md ~/",
    "cp report /tmp/",
    "cp a.txt ~/notes/",
    "mv build dist/",
    "cp -t dist a.js",
    "rsync -rt src/ dist/",
    "rsync -a src/ dist/",
    "scp h:/x/report.txt .",
    "docker cp c:/app/log.txt .",
    "rclone copy r:photos ~/Pictures",
    'cp "$f" dist/',
    "cp -T a.txt ~/b.txt",
]


LANDING_ASKED += [
    # T02 bypass review: verbs behind global options, git mv, rsync -R's /./ marker
    "docker --log-level debug --context x cp c:/.bashrc ~",
    "podman --remote --url x cp c:/.bashrc ~",
    "git mv e/.bashrc ~",
    "git mv -k e/.bashrc ~",
    "rsync -R e/./.bashrc ~/",
]
LANDING_REFUSED += [
    "rclone -v copy r:cobot.rules ~/.claude/",
    "rclone copy r:dir ~",
    "rsync -a --files-from=l h: ~/",
]
LANDING_SILENT += ["rclone copy . r:backup", "git mv a b", "docker cp ./x c:/root/", "scp file h:~/"]


@pytest.mark.parametrize("command", ["cp e/.bashrc x:/../..", "cp -t x:/../.. e/.bashrc", "cp e/.bashrc ../"])
def test_story2_colonIsALocalFolderForCp_landingIsJudged(rules, command):
    """For cp, ``x:`` is a folder: from ``~/proj`` the file lands at ``~/.bashrc`` (T02 review)."""
    assert decide(rules, command, cwd=os.path.expanduser("~/proj")) == "ask"


# ---------------------------------------------------------------- story 3: downloads

DOWNLOAD_ASKED = [
    "curl --output-dir ~ -O https://h/.claude.json",
    "curl -O --output-dir ~ https://h/.claude.json",
    "curl --output-dir ~ -o .claude.json https://h/x",
    "curl -fsSLO --output-dir ~ https://h/.bashrc",
    "wget -P ~ https://h/.claude.json",
    "wget -P ~ 'https://h/.bashrc?x=1'",
    "wget -P ~ -i urls.txt",
    "wget -r -P ~ https://h/",
    "curl -OJ --output-dir ~ https://h/x",
    "curl -K e/cfg",
    "curl --config=e/cfg https://h/x",
    "wget -e dir_prefix=~ https://h/x",
    "wget --execute=output_document=~/.claude/cobot.rules https://h/x",
    "wget -x -nH -P ~ https://h/.claude/cobot.rules",
]
DOWNLOAD_ASKED += [
    # T03 bypass review: every --next folder, wget prefixes, --config, globbing, decoded names
    "curl --output-dir ~ -O https://h/.bashrc --next --output-dir /tmp -O https://h/x",
    "cd ~ && wget --input-file=x",
    "cd ~ && wget --mirr https://h/",
    "cd ~ && wget --trust https://h/x",
    "cd ~ && wget --config=e/rc https://h/x",
    "cd ~ && curl -O 'https://h/{.bashrc}'",
    "cd ~ && curl -O 'https://h/.bash[r]c'",
    "cd ~ && curl -o '#1' 'https://h/{.bashrc,x}'",
    "cd ~ && wget https://h/%2Ebashrc",
    "cd ~ && wget 'https://h/a/.bashrc;x'",
    "wget --default-page=.bashrc -P ~ https://h/",
]
DOWNLOAD_ASKED += [
    # through the working directory a sealed folder asks, as ``cd ~/.claude && tar -C . -xf`` did
    # before this spec: the customization-root check reads the relative ``.`` (build note, T03)
    "cd ~/.claude && curl -OJ https://h/x",
]
DOWNLOAD_REFUSED = [
    "curl --output-dir ~/.claude -O https://h/cobot.rules",
    "wget -P ~/.claude https://h/cobot.rules",
    "wget -P ~/.claude -i urls.txt",
]
DOWNLOAD_SILENT = [
    "curl -O https://h/x.tar.gz",
    "curl -sSL https://h/x",
    "curl -oout.json https://h/x",
    "wget https://h/x.tar.gz",
    "curl --output-dir dl -O https://h/x",
    "wget -P dl -i urls.txt",
    "wget -qO- https://h/x",
    "wget -e robots=off -r -P mirror https://h/",
    "curl -g -O 'https://h/x[1]'",
    "wget -O x.json -P ~ https://h/x",
]


# ---------------------------------------------------------------- story 4: extraction into the cwd

EXTRACTION_ASKED = [
    # Q1 (owner, 2026-11-23): a working directory that only holds the config dir asks
    "cd ~ && tar -xf e.tar",
    "cd ~ && tar xf e.tar",
    "cd ~ && bsdtar -xf e.tar",
    "cd ~ && unzip x.zip",
    "cd ~ && cpio -idv < e.cpio",
    "cd ~ && 7z x e.7z",
    "cd ~/.claude && tar -xf e.tar",
    "cd ~/.claude && unzip e.zip",
    # landings the gate cannot place
    "tar -xPf e.tar",
    "tar --absolute-names -xf e.tar",
    "tar xPf e.tar",
    "cpio -i < e.cpio",
    "unzip -: e.zip",
]
EXTRACTION_ASKED += [
    # T04 bypass review: long prefixes, --one-top-level, option variables, 7-Zip forms, unknown cd
    "cd ~ && tar --ext -f e.tar",
    "cd ~ && cpio --extr < e.cpio",
    "cd ~ && tar --one-top-level -xf .claude.tar",
    "TAR_OPTIONS=-C$HOME/.claude tar -xf e.tar",
    "export TAR_OPTIONS=-C$HOME/.claude; tar -xf e.tar",
    "UNZIP=-d$HOME/.claude unzip x.zip",
    "7z x -spf x.7z",
    "cd ~ && 7z -y x x.7z",
    "cd ~ && 7z X x.7z",
    "cd $D && tar -xf e.tar",
]
EXTRACTION_REFUSED = ["cpio -p ~/.claude < list", "cpio -pd ~ < list"]
EXTRACTION_SILENT = [
    "tar -xf x.tar.gz",
    "cd /tmp && tar -xf x.tar",
    "unzip x.zip",
    "unzip -l x.zip",
    "tar -tf x.tar",
    "tar -czf out.tgz src",
    "cpio -i --no-absolute-filenames < e.cpio",
    "7z l e.7z",
    "cd plugins && tar -xf ../x.tar",  # an existing folder: a cd into a missing one is unknown, so asks
]


@pytest.mark.parametrize("command", EXTRACTION_ASKED)
def test_story4_extractionInAHolderOrUnplaced_asks(rules, command):
    assert decide(rules, command) == "ask"


# ---------------------------------------------------------------- story 5: moved config dir, moved holders

MOVED_REFUSED = [
    "cp e/cobot.rules {cc}/",
    "tar -C {cc} -xf e.tar",
    "unzip -d {cc} e.zip",
    "ln -sfn e {cc}",
    "mv {cc} {root}/y",
    "rm -r {cc}",
    "rm -r {root}",
    "mv {root} /x",
]
MOVED_SILENT = ["cp report {root}/", "cp a ~", "ls {cc}", "mkdir -p {root}/other"]


@pytest.fixture
def moved_config(tmp_path, monkeypatch, rules):
    """CLAUDE_CONFIG_DIR outside HOME: ``{root}/cc``."""
    root = tmp_path / "outside"
    (root / "cc").mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(root / "cc"))
    return {"cc": str(root / "cc"), "root": str(root)}


@pytest.mark.parametrize("command", MOVED_REFUSED)
def test_story5_movedConfigDir_keepsItsFolderProtection(rules, moved_config, command):
    assert decide(rules, command.format(**moved_config)) == "deny"


@pytest.mark.parametrize("command", MOVED_SILENT)
def test_story5_movedConfigDir_friction_staysSilent(rules, moved_config, command):
    assert decide(rules, command.format(**moved_config)) is None


@pytest.mark.parametrize("command", ["mv /home x", "mv ~ /tmp/h", "mv /home/ /x", "rename /home x"])
def test_story5_movingAFolderThatHoldsTheConfigDir_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", ["mv /ho* x", "mv {root}* y"])
def test_story5_movingAGlobThatCouldNameTheHolder_asks(rules, moved_config, command):
    """T05 review: a glob source is judged as ``rm -rf /ho*`` is."""
    assert decide(rules, command.format(**moved_config)) in ("ask", "deny")


@pytest.mark.parametrize(
    "command",
    ["mv build dist/", "mv a.txt ~/notes/", "mv ~/Downloads/x.zip .", "mv src/*.py lib/", 'mv "$f" dist/'],
)
def test_story5_ordinaryMoves_staySilent(rules, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- story 6: both runtimes


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("cp --target-directory=~/.gemini/config x", "force_ask"),
        ("cp e/settings.json ~/.gemini/config/", "force_ask"),
        ("curl --output-dir ~/.gemini/config -O https://h/settings.json", "force_ask"),
        ("cd ~/.gemini && tar -xf e.tar", "force_ask"),
        ("cp --target-directory=~/.claude cobot.rules", "deny"),
        ("cp a dist/", "allow"),
        ("tar -xf x.tar", "allow"),
    ],
)
def test_story6_agy_sameJudgement(rules, tmp_path, monkeypatch, command, expected):
    """ADR-0007: under agy, run_command reaches the same judgement; ``allow`` there is no opinion."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    home = tmp_path / "home"
    (home / ".gemini" / "config").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    workspace = tmp_path / "ws"
    (workspace / ".agent").mkdir(parents=True)
    (workspace / ".agent" / "cobot.rules").write_text("")
    call = {"id": "t1", "name": "run_command", "args": {"CommandLine": command}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(workspace)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == expected


def test_story6_sessionGrant_neverCoversALandingVerdict(rules):
    loaded, _, _ = rules.load_rules(None)
    verdict = rules.judge_bash("cp e/.claude.json ~/", loaded, None)[0]
    assert verdict.decision == "ask" and verdict.rule is None


@pytest.mark.parametrize("command", EXTRACTION_REFUSED)
def test_story4_copyPassIntoAProtectedFolder_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", EXTRACTION_SILENT)
def test_story4_extractionElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None


def test_story4_sessionStartedInHome_asksOnAnExtraction(rules):
    """Friction the owner accepted (Q1): in a session whose working directory is HOME, every
    extraction asks, since the archive could hold the config dir."""
    assert decide(rules, "tar -xf x.tar", cwd=os.path.expanduser("~")) == "ask"


@pytest.mark.parametrize("command", DOWNLOAD_ASKED)
def test_story3_downloadLandingOnAProtectedFileOrUnknown_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", DOWNLOAD_REFUSED)
def test_story3_downloadIntoASealedFolder_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", DOWNLOAD_SILENT)
def test_story3_downloadElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None


def test_story3_downloadWithNoFolder_landsInTheWorkingDirectory(rules):
    """Q2 (owner, 2026-11-23): a download with no output folder lands in the working directory."""
    assert decide(rules, "cd ~ && curl -O https://h/.claude.json") == "ask"
    assert decide(rules, "cd ~ && wget https://h/.bashrc") == "ask"
    assert decide(rules, "cd ~/.claude && curl -O https://h/cobot.rules") == "deny"


@pytest.mark.parametrize("command", LANDING_ASKED)
def test_story2_copyLandingOnAnAskRowFile_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", LANDING_REFUSED)
def test_story2_copyLandingOnASealedFile_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", LANDING_SILENT)
def test_story2_copyLandingElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None
