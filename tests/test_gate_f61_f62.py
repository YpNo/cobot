"""The other writers, and taking the config dir away (spec gate-f56-f60, stories 7 and 8).

F-61: writers whose output folder the gate did not read (aria2c, gh downloads, ditto, pax, sftp,
dpkg-deb, jar, ar, unar, the bsd tools, in-place decompression). F-62: removing, covering or
locking the config dir, and reaching it through a symlink. Each row reached no decision on
``6022fa6``.
"""

from __future__ import annotations

import json
import time

import pytest


def decide(rules, command, agent=None, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent, cwd)[0].decision


# ---------------------------------------------------------------- story 7, T07: other downloaders

DOWNLOADER_REFUSED = [
    "aria2c -d ~/.claude https://h/x",
    "aria2c --dir=~/.claude https://h/cobot.rules",
    "aria2c --dir ~/.claude https://h/x",
    "aria2c -d~/.claude https://h/cobot.rules",
    "aria2c -d ~/.claude -o cobot.rules https://h/x",
    "gh release download v1 -D ~/.claude",
    "gh release download v1 --dir ~/.claude",
    "gh release download v1 --dir=~/.claude/cobot",
    "gh run download 1 -D ~/.claude",
    "gh run download 1 --dir=~/.claude",
    "gh release download v1 -O ~/.claude/cobot.rules",
    "gh -R o/r release download v1 -D ~/.claude",
    "cd ~/.claude && gh release download v1 -p cobot.rules -O cobot.rules",
]
DOWNLOADER_ASKED = [
    "gh release download v1 -D ~",
    "cd ~ && gh run download 1",
    "cd ~ && gh release download v1 -p '*'",
    "aria2c -d ~ https://h/x",
    "aria2c -d ~ -i urls.txt",
    "cd ~ && aria2c https://h/x",
    "aria2c -d ~ -o .claude.json https://h/x",
    "aria2c --conf-path=e/conf https://h/x",
    "aria2c --conf-path e/conf https://h/x",
    # challenger: an input list's dir= and out= lines move the landing, as curl -K
    "aria2c -d dl -i list.txt",
    "aria2c --input-file=list.txt",
]
DOWNLOADER_SILENT = [
    "gh release download v1 -D dist/",
    "gh release download v1",
    "gh run download 1 -D artifacts",
    "gh run download 1 -n logs",
    "gh release list",
    "gh pr view 1",
    "aria2c -d dl https://h/x",
    "aria2c https://h/x",
    "aria2c -o out.bin https://h/x",
]


# ---------------------------------------------------------------- story 7, T08: copiers and extractors

WRITER_REFUSED = [
    "ditto e/cobot.rules ~/.claude/",
    "ditto e/ ~/.claude",
    "ditto -x -k e.zip ~/.claude",
    "ditto --arch x86_64 e/cobot.rules ~/.claude/",
    "pax -rw src ~/.claude",
    "pax -r -w -p e src ~/.claude/",
    "sftp h:/x/cobot.rules ~/.claude/",
    "sftp -P 22 h:/x/cobot.rules ~/.claude",
    "cd ~/.claude && sftp h:/x/cobot.rules",
    "dpkg-deb -x e.deb ~/.claude",
    "dpkg-deb --extract e.deb ~/.claude",
    "dpkg-deb -R e.deb ~/.claude",
    "dpkg-deb --vextract e.deb ~/.claude/cobot",
    "dpkg -x e.deb ~/.claude",
    "bsdunzip -d ~/.claude e.zip",
    "bsdcpio -i -D ~/.claude < e.cpio",
    "unar -o ~/.claude e.rar",
    "unar e.rar -o ~/.claude",
    "unar -output-directory ~/.claude e.rar",
    "ar x --output=~/.claude e.a",
    "ar x --output ~/.claude e.a",
    "jar xf e.jar -C ~/.claude",
    "jar --extract --file e.jar --dir ~/.claude",
    # challenger: ditto copies a folder's contents, and -x extracts into its last operand
    "ditto e ~",
    "ditto -x -k e.zip ~",
    "dpkg-deb -e e.deb ~/.claude/cobot",
    # T07 bypass review: pax keeps each operand's path; aria2c's --index-out
    "pax -rw .claude/cobot.rules ~",
    "pax -rw ./.claude/cobot.rules ~",
    "pax -rw .claude/cobot ~",
    "pax -rw ../cobot.rules ~/.claude/x",
    "aria2c --index-out=1=$HOME/.claude/cobot.rules a.torrent",
    "aria2c -O 1=$HOME/.claude/cobot.rules a.torrent",
]
WRITER_ASKED = [
    "cd ~/.claude && jar xf e.jar",
    "cd ~/.claude && jar -xf e.jar",
    "cd ~/.claude && ar x e.a",
    "cd ~/.claude && unar e.rar",
    "cd ~/.claude && bsdunzip e.zip",
    "cd ~ && unar e.rar",
    "cd ~ && jar xf e.jar",
    # member names the gate cannot place
    "pax -r -f e.pax",
    "pax -r < e.pax",
    "pax -r -s ,^,/x/, -f e.pax",
    "jar xPf e.jar",
    "ar xP e.a",
    "bsdcpio -i --insecure < e.cpio",
    # T07 bypass review: ar's separate dashed key words and --plugin; pax -rw -s
    "cd ~/.claude && ar -v -x a.a",
    "cd ~/.claude && ar --plugin p x a.a",
    "ar -v -xP a.a",
    "ar --plugin p xP a.a",
    "pax -rw -s ',^a$,../cobot.rules,' a ~/.claude/x",
    "aria2c -d ~ -O 1=.claude.json a.torrent",
]
WRITER_SILENT = [
    "ditto src dst",
    "ditto -c -k src out.zip",
    "ditto -c -k ~/.claude out.zip",
    "jar cf a.jar -C ~/.claude .",
    "pax -w -f out.pax src",
    "pax -rw src dst",
    "sftp h:/x/report.txt .",
    "sftp h",
    "dpkg-deb -x e.deb out",
    "dpkg-deb -c e.deb",
    "dpkg -i e.deb",
    "jar xf e.jar",
    "jar cf out.jar -C build .",
    "jar tf e.jar",
    "ar x e.a",
    "ar rcs lib.a a.o",
    "unar e.rar",
    "unar -o out e.rar",
    "bsdunzip e.zip",
    "bsdcpio -i < e.cpio",
    "pax -rw sub/.bashrc ~",
    "pax -rw cfg/.claude.json ~",
    "ar -v -x a.a",
    "ar t a.a",
]


@pytest.mark.parametrize("command", WRITER_REFUSED)
def test_story7_writerIntoASealedFolder_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", WRITER_ASKED)
def test_story7_writerInAProtectedCwdOrUnplaced_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", WRITER_SILENT)
def test_story7_writerElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- story 7, T08: in-place decompression

DECOMPRESSED_REFUSED = [
    "gunzip ~/.claude/cobot.rules.gz",
    "gunzip -f ~/.claude/cobot.rules.gz",
    "gzip -d ~/.claude/cobot.rules.gz",
    "gzip -dk ~/.claude/cobot.rules.gz",
    "gzip --decompress ~/.claude/cobot.rules.gz",
    "gzip --decomp ~/.claude/cobot.rules.gz",
    "gunzip -S .x ~/.claude/cobot.rules.x",
    "gunzip --suffix=.x ~/.claude/cobot.rules.x",
    "gunzip ~/.claude/cobot.rules-gz",
    "gunzip ~/.claude/cobot.rules_z",
    "xz -d ~/.claude/cobot.rules.xz",
    "unxz ~/.claude/cobot.rules.xz",
    "lzma -d ~/.claude/cobot.rules.lzma",
    "unlzma ~/.claude/cobot.rules.lzma",
    "zstd -d ~/.claude/cobot.rules.zst",
    "unzstd ~/.claude/cobot.rules.zst",
    "zstd -d --output-dir-flat ~/.claude e/cobot.rules.zst",
    "zstd -d e/cobot.rules.zst --output-dir-mirror ~/.claude",
    "zstd -d --output-dir-flat ~/.claude x.zst",
    "bunzip2 ~/.claude/cobot.rules.bz2",
    "bzip2 -d ~/.claude/cobot.rules.bz2",
    "lz4 -d ~/.claude/cobot.rules.lz4",
    "unlz4 ~/.claude/cobot.rules.lz4",
    "brotli -d ~/.claude/cobot.rules.br",
    "p7zip -d ~/.claude/cobot.rules.7z",
    "pigz -d ~/.claude/cobot.rules.gz",
    "unpigz ~/.claude/cobot.rules.gz",
    "lzip -d ~/.claude/cobot.rules.lz",
    "lzop -d ~/.claude/cobot.rules.lzo",
    "uncompress ~/.claude/cobot.rules.Z",
    "cd ~/.claude && gunzip cobot.rules.gz",
    "gunzip -N ~/.claude/x.gz",
    "gunzip x.gz ~/.claude/cobot.rules.gz",
    "gunzip -- ~/.claude/cobot.rules.gz",
    # T08 bypass review: clusters with digits and values, operands after --, lz4 --multiple,
    # lbzip2, lrzip, lzop -x and -p, getopt prefixes
    "zstd -dT0 ~/.claude/cobot.rules.zst",
    "xz -dT0 ~/.claude/cobot.rules.xz",
    "pigz -dp4 ~/.claude/cobot.rules.gz",
    "gzip -d1 ~/.claude/cobot.rules.gz",
    "zstd -d19 ~/.claude/cobot.rules.zst",
    "gzip -dS.x ~/.claude/cobot.rules.x",
    "xz -dS.r ~/.claude/cobot.rules.r",
    "zstd -d -Dlocal ~/.claude/cobot.rules.zst",
    "gzip -dSc ~/.claude/cobot.rulesc",
    "gzip -d -- -t ~/.claude/cobot.rules.gz",
    "gzip -d ~/.claude/cobot.rules.gz -- -c",
    "lz4 -d --multiple ~/.claude/cobot.rules.lz4 b.lz4",
    "lbzip2 -d ~/.claude/cobot.rules.bz2",
    "lrunzip ~/.claude/cobot.rules.lrz",
    "lzop -x ~/.claude/cobot.rules.lzo",
    "lzop -d -p ~/.claude ./cobot.rules.lzo",
    "lzop -d --path=~/.claude ./cobot.rules.lzo",
]
DECOMPRESSED_ASKED = [
    "gunzip ~/.claude.json.gz",
    "cd ~ && gunzip .claude.json.gz",
    "gunzip ~/.bashrc.gz",
    "gunzip -N ~/x.gz",
    "zstd -d --filelist l",
    "zstd --rm --filelist l",
    "sudo gunzip ~/.claude/cobot.rules.gz",  # sudo is opaque and asks, as ``sudo cp`` does
    "gzip -dS.x ~/.bashrc.x",
    "xz -d --files=list",
    "xz -d --files0=list",
    "xz -d --files list",
]
DECOMPRESSED_SILENT = [
    "gunzip f.gz",
    "cd work && gunzip f.gz",
    "xz -d build/x.xz",
    "zstd -d x.zst -o x",
    "gunzip -c e.gz",
    "gzip -dc ~/.claude/cobot.rules.gz",
    "gzip -t ~/.claude/cobot.rules.gz",
    "gzip -l ~/.claude/cobot.rules.gz",
    "xz -l x.xz",
    "gzip f",
    "bzip2 -k f",
    "zstd x",
    "zstd --filelist l",
    "zstd -d --output-dir-flat out x.zst",
    "gzip --std -d ~/.claude/cobot.rules.gz",
    "brotli -d --out=out ~/.claude/cobot.rules.br",
    "gzip -qd f.gz",
    "zstd -dT0 x.zst",
    "xz --files=list",
]


def test_story7_manyDecompressedOperands_askWithinTheHookTimeout(rules):
    """T08 review: 5000 operands took 10.9 s, past the hook's 10 s; past LANDING_WORDS_MAX they ask
    (5000 now take about 7 s, of which the plain word loop, as for ``cat``, is about 6)."""
    command = "gunzip " + " ".join(f"~/x/f{i}.gz" for i in range(300))
    started = time.monotonic()
    verdict = decide(rules, command)
    assert time.monotonic() - started < 5
    assert verdict == "ask"


@pytest.mark.parametrize("command", DECOMPRESSED_REFUSED)
def test_story7_decompressionOntoAnOwnerFile_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", DECOMPRESSED_ASKED)
def test_story7_decompressionOntoAnAskRowOrUnknownName_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", DECOMPRESSED_SILENT)
def test_story7_decompressionElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None


@pytest.mark.parametrize("command", DOWNLOADER_REFUSED)
def test_story7_downloaderIntoASealedFolder_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", DOWNLOADER_ASKED)
def test_story7_downloaderWithServerNamesInAHolder_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", DOWNLOADER_SILENT)
def test_story7_downloaderElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- story 8, T09: remove, cover, link, lock

TAKEN_REFUSED = [
    # the sources are removed, as rm -r
    "tar --remove-files -cf a.tar ~/.claude",
    "tar --remove-files -cf a.tar ~",
    "tar -cf a.tar --remove-files /home",
    "tar --rem -cf a.tar ~/.claude",
    "tar -czf a.tgz --remove-files ~",
    "zip -rm a.zip ~/.claude",
    "zip -r -m a.zip ~",
    "zip -mr a.zip ~/.claude",
    "zip --move -r a.zip ~/.claude",
    "7z a -sdel a.7z ~/.claude",
    "7z a -SDEL a.7z ~",
    "rclone purge ~/.claude",
    "rclone delete ~/.claude",
    "rclone rmdirs ~",
    "rclone -v deletefile ~/.claude/cobot.rules",
    # every file under it is replaced
    "gzip -r ~/.claude",
    "gunzip -r ~",
    "zstd -r --rm ~/.claude",
    "gzip --recursive ~",
    # covered for every process
    "mount --bind /tmp ~/.claude",
    "mount -o bind /tmp/x ~/.claude",
    "mount -t tmpfs t ~",
    "mount -B /tmp ~/.claude",
    "mount --target=~/.claude /tmp",
    "mount --target ~/.claude /tmp",
    "sshfs h:/x ~/.claude",
    "sshfs -o allow_other h:/x ~",
    "sshfs h:/x ~/.claude -o reconnect",
    "mount -t tmpfs -o size=1m t ~/.claude",
    "bindfs /tmp/x ~/.claude",
    "rclone mount r: ~/.claude",
    "rclone mount r: ~/.claude --daemon",
    "fuse-overlayfs -o lowerdir=/a,upperdir=/b,workdir=/c ~/.claude",
    "archivemount a.tar ~/.claude",
    "squashfuse a.sqfs ~",
    # a link to a folder holding the config dir reaches it
    "ln -s ~ /tmp/h; cp e/cobot.rules /tmp/h/.claude/cobot.rules",
    "ln -s /home /tmp/h && rm -r /tmp/h/u/.claude",
    "ln -s ~ /tmp/h",
    "ln -sT ~/ /tmp/h",
    "cp -rs ~ /tmp/h",
    "cp --symbolic-link -r ~ /tmp/h",
    # T09 bypass review: rclone flags with values, hard-link trees, long prefixes, other mounters
    "rclone --config /dev/null purge ~/.claude",
    "rclone --log-level DEBUG purge ~",
    "rclone -q --log-file /tmp/l purge ~",
    "rclone --config x mount r: ~/.claude",
    "rclone nfsmount r: ~/.claude",
    "cp -rl ~ /tmp/h",
    "cp -l -r ~ /tmp/h",
    "cp --sym -r ~ /tmp/h",
    "cp --link -r ~ /tmp/h",
    "mount.cifs //h/s ~/.claude",
    "s3fs b ~/.claude",
    "gocryptfs c ~",
    "mergerfs /a:/b ~/.claude",
]
LOCK_ASKED = [
    "chmod -R 000 ~/.claude",
    "chmod 000 ~/.claude",
    "chmod -R a-r ~",
    "chmod 700 ~",
    "chown -R nobody ~/.claude",
    "chown nobody: ~/.claude",
    "chgrp -R x ~/.claude",
    "setfacl -R -m u:x:0 ~/.claude",
    "chattr -R +i ~/.claude",
    "chmod --reference=x ~/.claude",
    "chmod -R 000 /home",
    # only the child sees a bwrap cover
    "bwrap --bind /tmp ~/.claude sh",
    "bwrap --tmpfs ~/.claude sh",
    "bwrap --ro-bind /tmp/x /home sh",
    "bwrap --ro-bind / / --tmpfs ~ sh",
    "bwrap --symlink /tmp/x ~/.claude sh",
    "bwrap --overlay a b ~/.claude sh",
    "bwrap --setenv A b --tmpfs ~ sh",
    # names from stdin, removed
    "zip -m -@ a.zip",
    # T09 bypass review: bwrap flags with no value, chmod's -w modes, globs, @ in a cluster
    "bwrap --unshare-all --tmpfs ~/.claude sh",
    "bwrap --die-with-parent --ro-bind / / --tmpfs /home sh",
    "bwrap --new-session --bind /tmp ~ sh",
    "bwrap --ro-bind / / --unshare-net --tmpfs ~/.claude sh",
    "bwrap --frobnicate --tmpfs ~/.claude sh",
    "chmod -w ~/.claude",
    "chmod -rwx ~/.claude",
    "chmod -R -w ~",
    "chmod -- -w ~/.claude",
    "chmod 000 /home/*",
    "chmod 000 ~/.cl*",
    "zip -m@ /tmp/a.zip",
    "zip -rm@ /tmp/a.zip",
    "find ~ -name x | zip -m@ /tmp/a.zip",
]
TAKEN_SILENT = [
    "chmod -R u+w build/",
    "chmod +x script.sh",
    "chmod 600 ~/.ssh/id_x",
    "chmod -R u+w ~/.claude/projects",
    "chown -R me build",
    "tar --remove-files -cf a.tar logs/",
    "tar -cf a.tar ~/.claude",
    "zip -rm a.zip old/",
    "zip -r a.zip ~/.claude",
    "7z a a.7z ~/.claude",
    "gzip -r logs/",
    "gzip f",
    "mount --bind /tmp/a /tmp/b",
    "sshfs h:/x mnt -o reconnect",
    "mount --bind /srv/a /mnt/b",
    "mount -o remount,ro /mnt/b",
    "mount",
    "sshfs h:/x mnt",
    "rclone mount r: mnt",
    "rclone delete r:old",
    "ln -s ~/proj/x ~/bin/x",
    "ln -s ../lib lib",
    "cp -s a b",
    "zip -@ a.zip",
    "chmod 700 ~/.ssh",
    "chmod -w build/x",
    "chmod 644 src/*.py",
    "rclone --config x copy a r:b",
    "cp -l a b",
    "lz4 -d -c x.lz4",
]
TAKEN_REFUSED += [
    # wrap reviews: a joined -o value, unzstd's list, lz4's and lrzip's -l, bindfs values after the
    # operands, a bind mount's source (a second name, as a link is)
    "mount -oremount,ro ~/.claude",
    "lz4 -d -l ~/.claude/cobot.rules.lz4",
    "lrzip -d -l ~/.claude/cobot.rules.lrz",
    "bindfs src ~/.claude -u me",
    "mount --bind ~ /mnt/home",
    "mount --bind ~/.claude /tmp/y",
    "mount -o bind ~/.claude /tmp/y",
    "mount -obind ~/.claude /tmp/y",
    "mount --rbind /home /tmp/y",
    "bindfs ~/.claude /mnt/c",
    # wrap security review: a customization-root landing elsewhere does not soften a literal deny
    "aria2c -d ~/.agents http://x/y; cp x ~/.claude/cobot.rules",
    "gh release download v1 -D ~/.agents; cp x ~/.claude/cobot.rules",
    "ditto /tmp/x ~/.agents; rm -rf ~/.claude",
    "sftp h:x ~/.agents; cp x ~/.claude/cobot.rules",
    "cp x ~/.agents/; cp x ~/.claude/cobot.rules",
]


@pytest.mark.parametrize(
    "command",
    [
        "unzstd --filelist l",
        "ar --output d xP lib.a",
        "bwrap --bind / / rm -rf ~/.claude",
        "bwrap --bind / / sh",
        "bwrap --ro-bind ~ ~ sh",
        "bwrap --unshare-all --ro-bind / / make",
    ],
)
def test_wrap_reviewForms_ask(rules, command):
    """Wrap reviews: unzstd's list; ar's --output value; bwrap runs a command the gate does not
    read, so it asks as unshare and firejail do (it was silent, and ran ``rm -rf ~/.claude``)."""
    assert decide(rules, command) == "ask"


def test_wrap_dpkgRecursive_isNoExtraction(rules):
    """Wrap code review: for dpkg itself, -R is --recursive, not dpkg-deb's --raw-extract."""
    assert decide(rules, "dpkg -i -R pkgs out") is None


# ---------------------------------------------------------------- story 8, T10: the config dir's real path

LINKED_REFUSED = [
    "mv {real} /tmp/y",
    "rm -r {real}",
    "cp e/cobot.rules {real}/",
    "cp e/x {real}/cobot.rules",
    "tar -C {real} -xf e.tar",
    "mv {root} /tmp/y",
    "rm -r {root}",
    "ln -sfn /tmp/other {link}",
    "cp e/cobot.rules {link}/",
]
LINKED_SILENT = ["ls {real}", "cp report {root}/x/", "cat {real}/projects/a.json"]


@pytest.fixture
def linked_config(tmp_path, monkeypatch):
    """CLAUDE_CONFIG_DIR set to a symlink ``{link}`` whose target is ``{real}``, outside HOME."""
    root = tmp_path / "outside"
    (root / "real").mkdir(parents=True)
    (root / "x").mkdir()
    (tmp_path / "link").symlink_to(root / "real")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "link"))
    return {"link": str(tmp_path / "link"), "real": str(root / "real"), "root": str(root)}


@pytest.mark.parametrize("command", LINKED_REFUSED)
def test_story8_configDirThroughASymlink_keepsItsRealPathProtected(rules, linked_config, command):
    assert decide(rules, command.format(**linked_config)) == "deny"


@pytest.mark.parametrize("command", LINKED_SILENT)
def test_story8_configDirThroughASymlink_friction_staysSilent(rules, linked_config, command):
    assert decide(rules, command.format(**linked_config)) is None


@pytest.fixture
def dotfiles_home(tmp_path, monkeypatch):
    """``~/.claude`` a symlink to ``~/dotfiles/claude``, a dotfile manager's layout."""
    home = tmp_path / "home"
    (home / "dotfiles" / "claude").mkdir(parents=True)
    (home / ".claude").symlink_to(home / "dotfiles" / "claude")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    return home


@pytest.mark.parametrize(
    "command",
    [
        "rm -r ~/dotfiles/claude",
        "mv ~/dotfiles/claude /tmp/x",
        "mv ~/dotfiles /tmp/x",
        "cp e/cobot.rules ~/dotfiles/claude/",
        "cp e/x ~/dotfiles/claude/cobot/y",
        "rm -r ~/dotfiles",
    ],
)
def test_story8_symlinkedHomeConfig_keepsItsRealPathProtected(rules, dotfiles_home, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", ["ls ~/dotfiles/claude", "cp a ~/notes/", "cat ~/dotfiles/claude/x.json"])
def test_story8_symlinkedHomeConfig_friction_staysSilent(rules, dotfiles_home, command):
    assert decide(rules, command) is None


@pytest.mark.parametrize(
    "command",
    ["cp e/x {cc}/cobot.rules", "mv {cc}/cobot /tmp/y", "cp e/cobot.rules {cc}/"],
)
def test_story8_configDirWithDotDot_isReadInItsCleanForm(rules, tmp_path, monkeypatch, command):
    """T10 review: ``CLAUDE_CONFIG_DIR=/x/cc/../cc`` named no operand's form."""
    (tmp_path / "cc").mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cc" / ".." / "cc"))
    assert decide(rules, command.format(cc=tmp_path / "cc")) == "deny"


@pytest.fixture
def linked_home(tmp_path, monkeypatch):
    """HOME itself a symlink: ``{home}`` points at ``{real}``."""
    (tmp_path / "real" / ".claude").mkdir(parents=True)
    (tmp_path / "home").symlink_to(tmp_path / "real")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    return {"home": str(tmp_path / "home"), "real": str(tmp_path / "real")}


@pytest.mark.parametrize("command", ["ln -sfn /tmp/o ~", "ln -snf /tmp/o {home}", "ln -sfT /tmp/o {home}"])
def test_story8_repointingALinkAboveTheConfigDir_isRefused(rules, linked_home, command):
    """T10 review: ``ln -n`` replaces HOME's link, so ``~/.claude`` resolves into another folder."""
    assert decide(rules, command.format(**linked_home)) == "deny"


@pytest.mark.parametrize("command", ["ln -sf /tmp/o ~/x", "ln -sfn /tmp/o ~/bin/tool", "ln -s a b"])
def test_story8_linksBesideTheConfigDir_staySilent(rules, linked_home, command):
    assert decide(rules, command.format(**linked_home)) is None


# ---------------------------------------------------------------- story 6 extended: both runtimes


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("gh release download v1 -D ~/.gemini/config", "force_ask"),
        ("ditto e ~/.gemini/config", "force_ask"),
        ("gunzip ~/.gemini/config/settings.json.gz", "force_ask"),
        ("tar --remove-files -cf a.tar ~/.gemini", "force_ask"),
        ("chmod -R 000 ~/.gemini/config", "force_ask"),
        # a cover is judged as a folder option, as ``tar -C`` on the same folder is
        ("mount --bind /srv/x ~/.gemini/config", "force_ask"),  # HOME is under /tmp here
        ("tar -C ~/.gemini/config -xf e.tar", "force_ask"),
        ("gunzip ~/.claude/cobot.rules.gz", "deny"),
        ("gzip -r ~/.claude", "deny"),
        ("gunzip f.gz", "allow"),
        ("chmod -R u+w build/", "allow"),
    ],
)
def test_story6_agy_storiesSevenAndEight_sameJudgement(rules, tmp_path, monkeypatch, command, expected):
    """ADR-0007: under agy, run_command reaches the same judgement; ``allow`` there is no opinion."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    home = tmp_path / "home"
    (home / ".gemini" / "config").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    workspace = tmp_path / "ws"
    (workspace / ".agent").mkdir(parents=True)
    (workspace / ".agent" / "cobot.rules").write_text("")
    call = {"id": "t1", "name": "run_command", "args": {"CommandLine": command}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(workspace)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == expected


def test_story8_manyLockedPaths_askWithinTheHookTimeout(rules):
    """T09 review: 6000 operands took 10.2 s; past LOCK_WORDS_MAX the lock asks."""
    command = "chmod 000 " + " ".join(f"x{i}" for i in range(300))
    started = time.monotonic()
    verdict = decide(rules, command)
    assert time.monotonic() - started < 5
    assert verdict == "ask"


@pytest.mark.parametrize("command", TAKEN_REFUSED)
def test_story8_removingCoveringOrLinkingTheConfigDir_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", LOCK_ASKED)
def test_story8_lockingTheConfigDirOrAChildCover_asks(rules, command):
    """Q3: the gate does not read modes, so a lock asks; a bwrap cover is the child's only."""
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", TAKEN_SILENT)
def test_story8_everydayPermissionsArchivesAndMounts_staySilent(rules, command):
    assert decide(rules, command) is None
