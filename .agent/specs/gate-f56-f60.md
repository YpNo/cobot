# Spec — where a copy, a download or an extraction lands (F-56, F-60, F-61, F-62)

size: medium · profile: library · owner: YpNo · date: 2026-11-23 · revision 3 (stories 7 and 8
added for F-61 and F-62, owner: "Work on the nit + F-61 and F-62 on the same branch/PR") · base
`main` `a5db3f8` (PR 82, F-55, merged); stories 7 and 8 measured on `6022fa6`

## Goal

Close F-56 (HIGH) and F-60 (HIGH): the gate checks the words a copy names, not the place the copy
lands. These all reach no decision today:

- a copy into a folder (`cp e/.claude.json ~/`);
- an option value joined to its option (`cp --target-directory=~/.claude …`, `curl -o~/.claude/…`);
- a download into a folder;
- an extraction into the working directory;
- a config dir moved outside HOME.

The owner asked for both findings in one spec ("Spec F-56 and F-60"). F-57 (inline code) and F-58
(nested Claude Code) are out: they are about what runs, not where a file lands.

Measured with `plugins/cobot/bin/cobot-rules check "<cmd>"` on `a5db3f8`, with the owner and project
layers empty:

| # | command | today | after |
|---|---|---|---|
| F-60 | `cp --target-directory=/home/u/.claude cobot.rules` · `cp -t$HOME/.claude …` · `cp --t=~/.claude …` · `mv`, `ln`, `install` with `--target-directory=` · `curl -o~/.claude/cobot.rules u` · `wget -O~/.claude/cobot.rules u` · `curl --output-dir=~/.claude -O u/x` · `7z x -o$HOME/.claude e.7z` | none | deny, as each separate form is |
| F-56 | `cp e/.claude.json ~/` · `cp e/.claude.json ~` · `cp -t ~ e/.claude.json` · `mv`, `ln -s`, `install` and `rsync` of it into `~` · `rsync -rt e/.claude.json ~/` · `scp h:/x/.claude.json ~/` · `cp e/.bashrc ~/` | none | ask (the landing file is an ask row) |
| F-56 | `scp h:/x/cobot.rules ~/.claude` · `docker cp c:/x/cobot.rules ~/.claude/` · `rclone copy r:x/cobot.rules ~/.claude/ --transfers 4` · `cp --parents .claude/cobot.rules ~` · `rsync -R .claude/cobot.rules ~/` | none | deny |
| F-56 | `cd ~/.claude && tar -xf e.tar` · `cd ~/.claude && unzip e.zip` · `cd ~/.claude && curl -OJ u` | none | ask, as `cd ~/.claude && tar -C . -xf e.tar` did before this spec (build note, T03: the customization-root check reads the relative `.`; deny stays for a literal `~/.claude`) |
| F-56 | `cd ~ && tar -xf e.tar` · `cd ~ && unzip x.zip` | none | ask (the working directory holds the config dir) |
| F-56 | `tar -xPf e.tar` · `cpio -i < e.cpio` · `unzip -: e.zip` · `curl -K e/cfg` · `wget -e dir_prefix=~ u` · `wget -x -nH -P ~ https://h/.claude/cobot.rules` | none | ask (the landing place is unknown) |
| F-56 | `curl --output-dir ~ -O https://h/.claude.json` · `wget -P ~ https://h/.claude.json` · `cd ~ && curl -O https://h/.claude.json` | none | ask |
| F-56 | `curl --output-dir ~/.claude -O https://h/cobot.rules` · `wget -P ~/.claude https://h/cobot.rules` | none | deny |
| F-56 | `mv /home x` · `mv ~ /tmp/h` (a folder holding the config dir, moved) | none | deny |
| F-56 | with `CLAUDE_CONFIG_DIR=/tmp/cc`: `cp e/cobot.rules /tmp/cc/` · `tar -C /tmp/cc -xf e.tar` · `unzip -d /tmp/cc e.zip` · `ln -sfn e /tmp/cc` · `mv /tmp/cc /tmp/y` · `rm -r /tmp/cc` · `mv /tmp /x` · `cd /tmp/cc && tar -xf e.tar` | none | deny |

Unchanged: `cp e/cobot.rules ~/.claude/`, `cp -t ~/.claude cobot.rules`, `tar -C ~ -xf e.tar`,
`unzip -d ~ e.zip`, `rsync e/ ~/`, `cp "$f" ~/` and `cp -r $X ~` (deny).

Silent and unchanged, the friction guard (each one a test row):

- copies: `cp a ~`, `cp README.md ~/`, `cp report /tmp/` (also with the config dir moved to
  `/tmp/cc`), `cp a.txt ~/notes/`, `mv build dist/`, `cp -t dist a.js`, `rsync -rt src/ dist/`,
  `scp h:/x/report.txt .`, `docker cp c:/app/log.txt .`;
- downloads: `curl -O https://h/x.tar.gz`, `curl -oout.json u`, `wget https://h/x.tar.gz`,
  `curl --output-dir dl -O https://h/x`;
- extractions: `tar -xf x.tar.gz`, `cd /tmp && tar -xf x.tar`, `unzip x.zip`.

## Principles check

- **Proportionality:** medium, one topic (where a file lands): `cobot-rules` and the tests only. No
  new rows: the existing file rows are what a landing word meets.
- **Rules before autonomy:** every change adds an ask or a deny; nothing is silenced.
- **Proof, not promises:** each Goal row is a row in a new `tests/test_gate_f56_f60.py`, failing on
  `a5db3f8`. A bypass-aimed review follows each build task.
- Governance (`docs/01-decisions.md`):
  - decision 18 (attribution) holds;
  - 20 (one spec, one PR, a task per commit) holds;
  - 22 holds: no dependency;
  - 28 (read-only agents) holds: the new asks apply to them too;
  - 31 (stamp) holds;
  - 33 (trust boundaries) holds: see below;
  - 34 (session grants) holds: a grant never covers a protected-file verdict (a test row);
  - ADR-0007 (both runtimes) holds: story 6;
  - the others are not relevant.
- Architecture: plain layering (`library`), inside `protected_file_touched` and its helpers.
- New dependencies: none.
- Experts: shell → `lang-shell`. Every option table is read from the tool's own `--help` or man
  page at build (`cp`, `mv`, `ln`, `install`, `rsync`, `scp`, `docker cp`, `rclone`, `curl --help
  all`, `wget`, `tar`, `unzip`, `7z`, `cpio`) and dated in a comment. CONTEXT.md has no `domains:`
  bullet, so an onboard refresh is proposed at hand-over.
- Delivery: one branch `security/gate-f56-f60`, one PR; tasks below are the commits.

## Stories and acceptance

Every story's acceptance is `uv run --no-project --python 3.13 --with pytest==9.2.0 --with
pytest-cov==7.1.0 pytest tests/test_gate_f56_f60.py -k <story>`, plus its Goal rows through
`cobot-rules check`. Its negative rows are the hostile commands of its Goal rows; its friction
rows must stay silent.

1. **An option that says where a file lands is read in every form (F-60).** One table,
   `LANDING_OPTIONS`, names per program the options whose value is a target folder or an output
   file:
   - `cp`, `mv`, `ln`, `install` and `gio`: `-t` and `--target-directory` (a folder);
   - `curl`: `-o` and `--output` (a file), `--output-dir` (a folder);
   - `wget`: `-O` and `--output-document` (a file), `-P` and `--directory-prefix` (a folder);
   - `7z`: `-o` (a folder).

   Each is read in every form: separate (`-t DIR`), joined short (`-tDIR`, `-o~/x`), the end of a
   short cluster (`-rt DIR`), `--long=VALUE`, `--long VALUE`, and every prefix of three or more
   characters of the long name that names one option of that program (`--t=` is
   `--target-directory` for `cp`; `--no-t…` is `-T`).
   - A folder value is judged as the separate `-t DIR` is today: a relocating word.
   - A file value is judged as a path word.
   - Today a joined value skips both checks, and an `=` value gets only the plain word check.
   - The tables of `tar`, `unzip`, `git` and `patch` in `FOLDER_OPTIONS` stay as they are. `7z -o`
     and `cpio -D` join them.
2. **Each source lands at `<target>/<basename(source)>` (F-56).** The target may be a folder and
   the gate cannot know, so that landing word goes through `word_touches` like any path word.
   - It meets a file row and a sealed row the same way: a literal `~/.claude.json` asks, and a
     literal `~/.claude/cobot.rules` denies.
   - The copiers are `cp`, `mv`, `ln`, `install`, `rsync`, `gio copy|move`, `scp`,
     `docker|podman|kubectl cp` and `rclone copy|copyto|move|moveto|sync`.
   - Each copier has its own table of value options: rsync's `-t` keeps times, and rclone takes
     flags after its paths. The target is the last positional that table leaves. Where an option
     is not in the table, every positional is tried as the target, against every other one as a
     source.
   - A remote source (`h:/x/f`, `c:/x/f`, `r:x/f`) counts by its basename. A remote target has no
     local landing.
   - A copy that keeps the source's path (`cp --parents`, `rsync -R|--relative`) lands at
     `<target>/<source as written>`.
   - `scp`, `docker|podman|kubectl cp` and `rclone` join `relocates`, so a target inside
     `~/.claude` denies as it does for `cp`.
3. **A download lands where its options say (F-56).** `D` is the output folder from story 1, or the
   working directory as tracked.
   - `curl -O`, `--remote-name` or `--remote-name-all` lands at `D/<url basename>`, and `-o NAME`
     at `D/NAME`.
   - `wget` lands at `D/<url basename>`.
   - Landings the gate cannot place ask: `curl -J|--remote-header-name`, `wget -i`,
     `--content-disposition`, `--trust-server-names`, `-r`, `-m` and `-x|--force-directories`.
     So do `curl -K|--config` and `wget -e|--execute`, which read options the gate does not see.
4. **An extraction lands in the working directory (F-56).** `tar -x`, `bsdtar -x`, `unzip`,
   `cpio -i` and `7z x` with no folder option are read as if the tracked working directory were
   that folder.
   - A working directory that is a protected folder, or inside one, denies, as `tar -C ~/.claude`
     does.
   - A working directory that only holds one (HOME, `/`, `/home`) asks: the archive could hold the
     config dir, and the owner may approve.
   - Landings the gate cannot place ask: `tar -P|--absolute-names`, `cpio -i` without
     `--no-absolute-filenames`, and `unzip -:`.
   - The tests run with a tracked cd, and with the payload cwd set to HOME (friction: a session
     started in HOME asks on every extraction).
5. **A moved config dir keeps its folder protection, and so does a moved HOME (F-56).**
   - `protected_anchors` walks a moved row's folders up to and including `config_dir()`, as it
     walks a HOME row's up to HOME. Its parents are not added, so `cp report /tmp/` stays silent.
   - A move, rename or link of a folder that holds an anchor denies, as its removal does today
     (`holds_an_anchor`, applied to `mv`/`rename` sources): `mv /home x`, `mv /tmp /x` with the
     config dir in `/tmp/cc`.
   - The rows run with `CLAUDE_CONFIG_DIR` set in the test's environment to a folder outside HOME.
6. **Both runtimes (ADR-0007).** Under agy (`run_command`), stories 1 to 8 reach the same
   judgement on `~/.gemini/config` paths. Accept: rows in `tests/test_gate_f56_f60.py` through
   `gate_agy`.
7. **The other writers' landings are read (F-61).** Measured on `6022fa6`, owner and project layers
   empty. The T01–T05 machinery is reused; no new rows.

   | command | today | after |
   |---|---|---|
   | `aria2c -d ~/.claude https://h/x` · `aria2c --dir=~/.claude …` · `aria2c -d~/.claude …` · `gh release download v1 -D ~/.claude` · `gh run download 1 --dir=~/.claude` | none | deny (a folder landing option, as `curl --output-dir`) |
   | `gh release download v1 -D ~` · `cd ~ && gh run download 1` · `aria2c -d ~ https://h/x` | none | ask (the names come from the server, in a folder that holds the config dir) |
   | `ditto e/cobot.rules ~/.claude/` · `ditto -x -k e.zip ~/.claude` · `pax -rw src ~/.claude` · `sftp h:/x/cobot.rules ~/.claude/` | none | deny (copiers: the target is the last positional) |
   | `dpkg-deb -x e.deb ~/.claude` · `dpkg -x e.deb ~/.claude` · `bsdunzip -d ~/.claude e.zip` · `unar -o ~/.claude e.rar` · `unar e.rar -o ~/.claude` · `ar x --output=~/.claude e.a` · `jar xf e.jar -C ~/.claude` | none | deny (folder options and dpkg-deb's folder operand) |
   | `cd ~/.claude && jar xf e.jar` · `… && ar x e.a` · `… && unar e.rar` · `… && bsdunzip e.zip` | none | ask, as `cd ~/.claude && tar -xf` (story 4) |
   | `pax -r -f e.pax` · `pax -r < e.pax` · `jar xPf e.jar` · `ar xP e.a` · `bsdcpio -i --insecure < e.cpio` | none | ask (absolute or rewritten member names: the landing is unknown) |
   | `gunzip ~/.claude/cobot.rules.gz` · `gzip -d …` · `xz -d`, `unxz`, `zstd -d`, `unzstd`, `bunzip2`, `bzip2 -d`, `lzma -d`, `lz4 -d`, `brotli -d`, `p7zip -d` on `~/.claude/cobot.rules.<ext>` · `cd ~/.claude && gunzip cobot.rules.gz` | none | deny (in-place decompression lands at the name without its suffix) |
   | `gunzip ~/.claude.json.gz` · `cd ~ && gunzip .claude.json.gz` | none | ask (an ask row) |
   | `gunzip -N ~/.claude/x.gz` | none | deny (`-N` restores a stored name: unknown, in a protected folder) |

   Already closed, kept as rows: `curl --create-dirs -o ~/.claude/cobot/x u` (T01), `gh release
   download v1 -O ~/.claude/cobot.rules`, `zstd -d e.zst -o ~/.claude/cobot.rules` (path words).

   Friction guard, silent: `gunzip f.gz`, `cd work && gunzip f.gz`, `xz -d build/x.xz`, `zstd -d
   x.zst -o x`, `gunzip -c e.gz > out`, `gh release download v1 -D dist/`, `gh run download 1 -D
   artifacts`, `aria2c -d dl https://h/x`, `dpkg-deb -x e.deb out`, `jar xf e.jar`, `unar e.rar`,
   `ar x e.a`, `ditto src dst`, `pax -w -f out.pax ~/.claude` (an archive of it is a read).
   Friction accepted: `pax -r` asks everywhere, as `cpio -i` does (pax keeps absolute names).
8. **Taking the config dir away or locking it is refused or asked (F-62).**

   | command | today | after |
   |---|---|---|
   | `tar --remove-files -cf a.tar ~/.claude` (also `~`, `/home/u/.claude`, `--rem`) · `zip -rm a.zip ~/.claude` · `zip -r -m a.zip ~` · `7z a -sdel a.7z ~/.claude` | none | deny (the sources are removed, as `rm -r`) |
   | `gzip -r ~/.claude` · `gunzip -r ~` · `zstd -r --rm ~/.claude` | none | deny (every file under it is replaced) |
   | `rclone purge ~/.claude` · `rclone delete ~/.claude` · `rclone rmdirs ~` | none | deny (as `rm -r`) |
   | `mount --bind /tmp ~/.claude` · `mount -o bind /tmp/x ~/.claude` · `mount -t tmpfs t ~` · `mount --target=~/.claude …` · `sshfs h:/x ~/.claude` · `bindfs /tmp/x ~/.claude` · `rclone mount r: ~/.claude` | none (`sudo mount` asks) | deny (the config dir is covered for every process) |
   | `ln -s ~ /tmp/h; cp e/cobot.rules /tmp/h/.claude/` · `ln -s /home /tmp/h && rm -r /tmp/h/u/.claude` · `cp -rs ~ /tmp/h` | none | deny (a link to a holder, as a move of it) |
   | `bwrap --bind /tmp ~/.claude sh` · `bwrap --tmpfs ~/.claude sh` · `bwrap --ro-bind /tmp/x /home sh` · `bwrap --ro-bind / / --tmpfs ~ sh` | none | ask (only the child sees the cover) |
   | `chmod -R 000 ~/.claude` · `chmod 000 ~/.claude` · `chmod -R a-r ~` · `chown -R nobody ~/.claude` · `chgrp -R x ~/.claude` · `setfacl -R -m u:x:0 ~/.claude` · `chattr -R +i ~/.claude` | none | ask (a lock; the mode is not read, so the owner may approve a harmless one) |
   | `CLAUDE_CONFIG_DIR=/x/link`, a symlink to `/x/real`: `mv /x/real /y` · `rm -r /x/real` · `cp e/cobot.rules /x/real/` | none | deny (the config dir's real path is protected too) |
   | the same with `~/.claude` a symlink to `/data/claude` (a dotfile manager's layout) | none | deny |

   Already closed, kept as rows: `ln -sfn /tmp/other /x/link` (T05), `zip -m a.zip
   ~/.claude/cobot.rules`, `chmod 000 ~/.claude/cobot.rules` and `chown nobody
   ~/.claude/cobot.rules` (literal sealed words).

   Friction guard, silent: `chmod -R u+w build/`, `chmod +x script.sh`, `chmod 600 ~/.ssh/id_x`,
   `chmod -R u+w ~/.claude/projects`, `chown -R me build`, `tar --remove-files -cf a.tar logs/`,
   `zip -rm a.zip old/`, `gzip -r logs/`, `mount --bind /tmp/a /tmp/b`, `bwrap --bind / / sh`,
   `bwrap --ro-bind / / --tmpfs /tmp sh` (a bind of a folder on itself covers nothing).
   Friction accepted: `chmod 700 ~` asks; `ln -s ~ x` denies; `ditto x ~` denies (a contents
   copy, as `rclone copy r:x ~`); with `~/.claude` linked into `~/dotfiles`, `git -C ~/dotfiles …`
   and `tar -C ~/dotfiles …` deny, as `git -C ~` does today.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| an option value joined to its option, naming a protected folder or file | `LANDING_OPTIONS` in every form | 1 |
| a copy, move, link or remote copy that lands on a protected file | landing words through `word_touches`, a table per copier | 2 |
| a download that lands on a protected file or in a protected folder | landing words from curl's and wget's options, or an ask | 3 |
| an extraction into a protected working directory, or to absolute member paths | the cwd as a folder option, an ask on unplaceable landings | 4 |
| a config dir outside HOME, or a folder holding one moved away | anchors up to `config_dir()`, `holds_an_anchor` on moves | 5 |
| the same commands under Antigravity | the shared judge | 6 |
| a download, copy, extraction or decompression by another writer | the same landing checks, a table per writer | 7 |
| removing, covering or locking the config dir, or reaching it through a link | `deleted_words`, a lock check, the real path's twin rows | 8 |

## Clarify

For the owner at review. The stories carry the recommended defaults.

- Q1 In a working directory that only holds the config dir (a session started in HOME), should
  `tar -xf x.tar` and `unzip x.zip` ask, or deny as `tar -C ~` does today? → recommended: ask.
  The archive's members are unknown, and a deny cannot be approved or granted (decision 34) →
  **answer:** ask (owner, 2026-11-23: "Yes, then build")
- Q3 (stories 7 and 8, built on the recommended default; the owner may reverse it at review)
  Should `chmod`, `chown`, `chgrp`, `setfacl` and `chattr` on the config dir or a folder holding it
  deny, as `rm -r` does? → recommended: ask. The gate does not read modes, so `chmod 700 ~/.claude`
  would be refused with no way to approve it; a removal or a cover (`mount`, `bwrap`) denies.
- Q2 Should a download with no output folder land in the working directory
  (`cd ~ && curl -O https://h/.claude.json`)? → recommended: yes, as the cwd already counts for a
  relative path word; it costs a few lines → **answer:** yes (owner, 2026-11-23: "Yes, then build")

## Plan

1. **T01, landing options (F-60):** `LANDING_OPTIONS`, and a `landing_option_values(argv)` that
   reads every form. `protected_file_touched` checks a folder value as a relocating word and a file
   value as a path word. `7z -o` and `cpio -D` join `FOLDER_OPTIONS`.
2. **T02, landing words:** `landing_words(segment)`, with each copier's value-option table, the
   every-positional fallback, remote sources, and `--parents`/`-R`. `scp`,
   `docker|podman|kubectl cp` and `rclone` join `relocates`.
3. **T03, downloads:** `download_landings(argv, dirs)` for curl and wget, and the asks on unplaceable
   forms, `-K` and `-e`.
4. **T04, extraction into the cwd:** `folder_options` returns the tracked cwd for an extraction with
   no folder option. A cwd that only holds an anchor asks; the unplaceable forms ask.
5. **T05, moved anchors and moved holders:** `protected_anchors` stops at `config_dir()` for moved
   rows, and `holds_an_anchor` applies to `mv`/`rename` sources.
6. **T06, both runtimes and docs:**
   - the agy rows;
   - the CHANGELOG Security entry;
   - FINDINGS: F-56 and F-60 closed, F-61 for the residual extractors;
   - `docs/configuration.md` "Not covered".

7. **T07, other downloaders, copiers and extractors (F-61):** `aria2c` (`-d`, `--dir`, `-o`) and
   `gh release|run download` (`-D`, `--dir`, `-O`) join `LANDING_OPTIONS` and `download_landings`;
   their server-named files are unplaced, as `curl -J`; `aria2c -i` and `--conf-path` ask, as
   `curl -K`. `pax -rw`, `sftp` and `ditto` join the copiers (`ditto` also as a contents copier;
   `ditto -c` is a read, `ditto -x` extracts into its last operand). `pax -r`, `jar x`, `ar x`,
   `unar`, `bsdunzip`, `bsdcpio` and `dpkg-deb -x|-X|-R` join `extracts`, `FOLDER_OPTIONS` (ar's
   `--output`, jar's `-C`/`--dir` in extraction only) or their own folder reading (unar's
   single-dash longs, dpkg-deb's folder operand), and `extraction_unplaced`.
8. **T08, in-place decompression (F-61):** `decompress_landings(argv)` returns each input without
   its suffix (or `-S`), unplaced under `-N`; `download_hit`'s folder logic judges it. zstd's
   `--output-dir-flat` and `--output-dir-mirror` are folder landing options. `-c`, `-t`, `-l` and
   an `-o` file add none. `zstd --filelist` with `-d` or `--rm` asks.
9. **T09, removing, covering and locking (F-62):** `deleted_words` takes the sources of
   `tar --remove-files`, `zip -m`, `7z -sdel` (any case), a recursive compressor and `rclone
   purge|delete|deletefile|rmdir|rmdirs`; the target of `mount` and of the FUSE mounters (`sshfs`,
   `bindfs`, `rclone mount`, `fuse-overlayfs`, `archivemount`, `squashfuse`); and the sources of
   `ln` and `cp -s` (a link to a folder holding the config dir reaches it). `zip -m -@` asks. A lock
   check asks (an `<anchor>/*` form) for `chmod`, `chown`, `chgrp`, `setfacl` and `chattr` on an
   anchor or a holder, and for `bwrap`'s mount destinations (a bind of a folder on itself
   excepted): only the child sees a `bwrap` cover.
10. **T10, the config dir's real path (F-62):** twin rows and anchors for the resolved
    `config_dir()` when it is, or sits under, a symlink.
11. **T11, both runtimes and docs:** agy rows; CHANGELOG; FINDINGS F-61 and F-62 closed;
    `docs/configuration.md`.

Each task is test first (its rows fail on `a5db3f8`, or on `6022fa6` from T07), then the code,
then the focused tests, ruff and the gate dry run, with a bypass-aimed review before its commit.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 ✅ | `LANDING_OPTIONS` in every form; `7z -o`, `cpio -D` folder options | gate | auth | — |
| T02 ✅ | `landing_words` per copier, the positional fallback, `--parents`/`-R`, relocating copiers | gate | auth | T01 |
| T03 ✅ | curl and wget landings, the asks on unplaceable forms, `-K`, `-e` | gate | auth | T01 |
| T04 ✅ | extraction into the tracked cwd (deny inside, ask on a holder), the unplaceable forms | gate | auth | — |
| T05 ✅ | anchors up to a moved `config_dir()`; moving a folder that holds an anchor | gate | auth | — |
| T06 ✅ | agy rows, CHANGELOG, FINDINGS, configuration.md | gate | — | T01–T05 |
| T07 ✅ | aria2c, gh; ditto, pax, sftp; jar, ar, unar, bsd*, dpkg-deb | gate | auth | T02–T04 |
| T08 ✅ | in-place decompression | gate | auth | T03 |
| T09 ✅ | removal, cover, link and lock verbs | gate | auth | T05 |
| T10 ✅ | the config dir's real path | gate | auth | T05 |
| T11 ✅ | agy rows, CHANGELOG, FINDINGS, configuration.md | gate | — | T07–T10 |

Stories 7 and 8 are tested in `tests/test_gate_f61_f62.py`, so the story 1–6 file stays readable.

One lane: every task edits `protected_file_touched` or its helpers, so the tasks run in order.

## Trade-offs

- Landing words through the existing `word_touches`, over a new check per copier: every existing
  row (file, folder, sealed, ask) is met the same way, with no new rows.
- The working directory as an extraction's folder, over reading the archive: the gate never opens
  the files it judges.
- An ask, not a deny, for an extraction in a folder that only holds the config dir: a deny there
  would block every extraction in a session started in HOME, with no way to approve it.
- A moved config dir's anchors stop at the dir itself, as HOME's stop at HOME. Its parents as
  anchors would ask on every `cp x /tmp/`; a parent moved or removed is caught by
  `holds_an_anchor`.

## Residuals (kept out of this spec, and why)

- **A copy made by code** (`python3 -c 'shutil.copy(…)'`, `node -e …`): that is F-57, inline code.
- **Claude Code launched to write a file** (`claude -p`, a renamed binary): that is F-58.
- **A copy into a target the gate cannot read** (`cp e/.claude.json "$D"`, `$D` inherited): the
  whole-word residual F-59, closed with whole-word `$(…)`.
- **A remote-to-remote copy** (`scp h1:a h2:b`, `rclone copy r1: r2:`): nothing lands locally.
- **An archive's member list** (a member named `.claude.json` extracted in the repository): the
  gate does not open archives. It judges only where the extraction lands.
- **Other writers, recorded as F-61:** taken in by story 7.
- **A client's own command language** (`sftp -b batch`, `lftp -c`, `ftp`, `smbclient -c`): the
  commands are text in another language, like inline code (F-57). Story 7 reads `sftp`'s
  positional form only.
- **Other sandboxes** (`firejail --private`, `proot -b`, `unshare -m` with a script,
  `systemd-run -p BindPaths=`, `docker run -v …:…/.claude`): like `bwrap`, they change only the
  child's view; what the child runs is F-58's (nested Claude Code). Story 8 asks on `bwrap`, the
  one named in F-62, and denies the covers every process sees (`mount`, the FUSE mounters).
- **`dpkg --root DIR` / `--instdir DIR` with `-i`:** an install into any folder needs root, and
  a package's files are its own; `sudo` already asks (T07 review).
- **aria2c's hooks and RPC** (`--on-download-complete=CMD`, `--enable-rpc`) and its default
  `~/.aria2/aria2.conf`: a program run after the download is F-57's class, an RPC server takes
  commands the gate never sees, and the default config file is the owner's.
- **`rar m`, `rar a -df`:** not free software, rarely installed; the same `deleted_words` line when
  wanted.
- **Modes and owners:** story 8 does not read them, so a lock that loosens asks too (Q3).
- **A symlinked `~/.gemini` under agy:** agy has no config-dir variable; story 8 resolves Claude
  Code's config dir only.
- **A link swapped in between the check and the run:** an existing residual (configuration.md).
- **`git` writing a protected file** (`git -C ~ checkout`): git's folder options are read (F-33);
  a checkout's content is not.

## Challenger verdict

2026-11-23, revision 1: **SOUND WITH CHANGES** (5 MAJOR, 2 MINOR). I reproduced each shape on
`a5db3f8` and folded every point:

- joined short and `=` values of curl, wget and 7z (story 1);
- `--parents`, `-R` and `wget -x` keep the source's path (stories 2 and 3);
- rsync's `-t` and rclone's trailing flags, handled by a table per copier and the positional
  fallback (story 2);
- long-option prefixes of three or more characters (story 1);
- moving a folder that holds an anchor, which was not caught: `holds_an_anchor` now applies to moves
  (story 5);
- an extraction in a cwd that only holds an anchor asks, not denies (story 4, Q1);
- the `<target>/*` tier was misstated, and `cp "$f" ~/` already denies, so the old Q1 is gone;
- `7z -o` and `cpio -D` were added, and the other writers became F-61.

2026-11-23, revision 3 (stories 7 and 8): **SOUND WITH CHANGES** (1 CRITICAL, 6 MAJOR, 3 MINOR).
Every point was folded:

- CRITICAL: a link to a folder holding the config dir, made in the same command (`ln -s ~ /tmp/h;
  cp e/cobot.rules /tmp/h/.claude/`), reached the owner files; `ln` and `cp -s` sources now count
  as moved holders (T09);
- zstd's `--output-dir-flat|-mirror` (T08);
- `ditto` copies a folder's contents, `-x` extracts, `-c` reads (T07);
- `aria2c -i` and `--conf-path` ask (T07), and its hooks and RPC are a residual;
- the FUSE covers a user can mount without root (T09);
- a `bwrap` cover asks, since only the child sees it (T09; friction row `bwrap --ro-bind / /
  --tmpfs ~ sh` asks);
- `rclone purge|delete|rmdirs` (T09);
- MINOR: under the T10 dotfile layout, `git -C ~/dotfiles …` and `tar -C ~/dotfiles …` deny as
  `git -C ~` does today: listed as friction; the lock check returns an `<anchor>/*` form so it
  asks; the missing decompressors, gzip's `-gz` and `_z` suffixes, `-SDEL` in any case, `zip -m
  -@`, a `dpkg-deb -e` row, and `jar -C` read in extraction only.

## Converge

2026-11-23: Q1 ask and Q2 yes (owner: "Yes, then build"). T01 to T06 were built, each with a
bypass-aimed review folded before the next task. F-56 and F-60 are closed; F-61 and F-62 hold what
stays out. One build decision: a sealed folder reached through `cd` asks, as it did before this
spec. Wrap follows; nothing is pushed.

2026-11-23, stories 7 and 8 (owner: "Work on the nit + F-61 and F-62 on the same branch/PR"):
T07 to T11 were built, each gate task with a bypass-aimed review folded before the next. F-61
and F-62 are closed. Q3 was built on its recommended default (a lock asks); the owner may reverse
it at review. Two build decisions: a mount's source is not covered, only its mount point (T11,
found by an agy row: a bind of HOME elsewhere shows it, it does not hide it); the lock check reads
the folders of `never` rows only, so `chmod 700 ~/.ssh` stays silent (T09 review).
