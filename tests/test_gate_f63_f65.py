"""Editors and debuggers, newlines, loader variables and dotglob (spec gate-f63-f65: F-63, F-64,
F-65, F-70).

Each Goal row is measured on ``3e83cc6`` with the owner and project layers empty; the friction
rows stay silent. Fixtures hold no secret-shaped literal: ``x`` stands for any value. ``\\n``
inside a quoted row is a newline the shell passes in the word.
"""

from __future__ import annotations

import json

import pytest


def verdict(rules, command, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, None, cwd)[0]


def decide(rules, command, cwd=None):
    return verdict(rules, command, cwd).decision


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project folder as the working directory, with a HOME outside it and no owner layer."""
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    work = tmp_path / "proj"
    work.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("CDPATH", raising=False)
    monkeypatch.chdir(work)
    return work


def assert_all(rules, commands, expected, cwd=None):
    wrong = {command: decide(rules, command, cwd) for command in commands}
    wrong = {command: got for command, got in wrong.items() if got != expected}
    assert not wrong, wrong


# ---------------------------------------------------------------- story 3: newlines (F-64)

NEWLINE_DENY = [
    # row 1: an escaped backslash, then a newline, is a separator; the next line is a command
    "echo a\\\\\nrm -rf /",
    "bash -c 'echo a\\\\\nrm -rf /'",
    "echo a\\\\\ngit push --force origin main",
]
NEWLINE_ASK = [
    # row 2: a quoted newline stays a newline, so an awk comment ends at it
    "awk '#x\nBEGIN{system(\"x\")}'",
    "gawk '#x\n@load \"x\"'",
]
NEWLINE_UNCHANGED_DENY = [
    "bash -c 'echo a\nrm -rf /'",
    "r\\\nm -rf /",
    "# it's\nrm -rf /",
]
NEWLINE_UNCHANGED_ASK = [
    "sed 's/a/b/\\\ne' f",
    "git commit -m 'a\nb'",
    "gh pr create --body 'a\nb'",
    "python3 -c 'x=1\ny'",
]
NEWLINE_FRICTION = [
    'echo "a\nb"',
    "sed -n 'p\nw out' f",
    "cat <<'EOF'\nrm -rf /\nEOF",
    'bash -c "echo a\\\nrm -rf /"',  # bash joins it into ``echo arm -rf /``
]


def test_story3_escapedBackslashThenNewline_isASeparator(rules, project):
    assert_all(rules, NEWLINE_DENY, "deny")


def test_story3_quotedNewline_reachesTheReader(rules, project):
    assert_all(rules, NEWLINE_ASK, "ask")


def test_story3_unchangedDenies_stayDenied(rules, project):
    assert_all(rules, NEWLINE_UNCHANGED_DENY, "deny")


def test_story3_unchangedAsks_stayAsks(rules, project):
    assert_all(rules, NEWLINE_UNCHANGED_ASK, "ask")


def test_story3_friction_staysSilent(rules, project):
    assert_all(rules, NEWLINE_FRICTION, None)


@pytest.mark.parametrize(
    ("text", "words"),
    [
        ("echo 'a\nb'", ["echo", "a\nb"]),  # single quotes keep the newline
        ('echo "a\nb"', ["echo", "a\nb"]),  # double quotes too
        ("echo 'a\\\nb'", ["echo", "a\\\nb"]),  # single quotes keep both characters
        ('echo "a\\\nb"', ["echo", "ab"]),  # double quotes drop a backslash-newline
        ("ec\\\nho x", ["echo", "x"]),  # outside quotes it joins the words
    ],
)
def test_story3_shellItems_readsNewlinesAsBash(rules, text, words):
    assert rules.shell_items(text) == [words]


def test_story3_unquotedNewline_separates(rules):
    assert rules.shell_items("a\nb") == [["a"], ";", ["b"]]
    assert rules.shell_items("a\\\\\nb") == [["a\\"], ";", ["b"]]


# T01 review: forms the gate read differently from bash, each a never row hidden
REVIEW_DENY = [
    "sh -c 'echo a\\\\\nrm -rf /'",
    'bash -c "echo a\\\\\\\\\nrm -rf /"',  # the inner string is ``a\\``, then a new line
    'bash -c "# it\'s\nrm -rf /"',
]
# in double quotes \$ is $ to bash: the inner string holds an ANSI-C quote, then a command. A body
# holding an ANSI-C quote is opaque (command_parts takes expansion holes only), so it asks
REVIEW_ASK = [
    "bash -c \"echo \\$'it\\\\'s'; git push --force origin main #'\"",
    "bash -c \"echo \\$'it\\\\'s'\ngit push --force origin main #'\"",
]


# wrap security review: a substitution in a -c body is read as at the top level, so its never row
# denies (the body is otherwise opaque, an ask)
BODY_SUBSTITUTION_DENY = [
    'bash -c "echo \\$(rm -rf /)"',
    'bash -c "\\$(rm -rf /)"',
    'bash -c "echo hi; \\$(rm -rf /)"',
    'sh -c "x=\\$(git push --force origin main)"',
    "bash -c 'echo $(rm -rf /)'",
    'bash -c "echo \\`rm -rf /\\`"',
    "bash -c 'bash -c \"echo \\$(rm -rf /)\"'",
]


def test_story3_wrap_substitutionInABody_denies(rules, project):
    assert_all(rules, BODY_SUBSTITUTION_DENY, "deny")


def test_story3_wrap_substitutionInABody_staysOpaque(rules, project):
    assert decide(rules, "bash -c 'echo $(date)'") == "ask"


def test_story3_review_innerStringsReadAsBash(rules, project):
    assert_all(rules, REVIEW_DENY, "deny")


def test_story3_review_ansiQuoteInAnInnerString_asks(rules, project):
    assert_all(rules, REVIEW_ASK, "ask")


def test_story3_review_doubleQuotedEscapedDollar_isADollar(rules):
    assert rules.shell_items("echo \"\\$x\" '\\$y'") == [["echo", "$x", "\\$y"]]


def test_story3_review_backtickInDoubleQuotes_isNotSilent(rules, project):
    command = "bash -c \"echo \\`echo '\\`\ngit push --force origin main\n#'\""
    assert decide(rules, command) in ("ask", "deny")


def test_story3_review_makefileEvenBackslashes_endTheLine(rules, project):
    (project / "Makefile").write_text("b:\n\techo a\\\\\n\tgit push --force origin main\n")
    assert decide(rules, "make b") == "deny"


def test_story3_review_makefileContinuation_staysOneLine(rules, project):
    (project / "Makefile").write_text("b:\n\techo a \\\n\t  b\n")
    assert decide(rules, "make b") is None


# ---------------------------------------------------------------- stories 1, 2, 8: editors, debuggers

EDITOR_ASK = [
    # row 3
    "vim -c '!x' f",
    "vim +'!x' f",
    "vim --cmd x f",
    "vim -S s.vim f",
    "vim -u x.vim f",
    "vi -c x f",
    "ex -c x f",
    "view -c x f",
    "vimdiff -c x a b",
    "rvim -c x f",
    "vim -Z -c x f",
    "busybox vi -c x f",
    "printf ':!x\\n' | vim f",
    # row 4: names installed on Debian hosts
    "vim.basic -c x f",
    "vim.tiny -c x f",
    "/usr/bin/vim.basic -c x f",
    "editor -c x f",
    "sensible-editor f",
    "vipe",
    # row 5
    "nvim -c x f",
    "nvim --cmd x",
    "nvim --headless -c x",
    "emacs --batch --eval '(x)'",
    "emacs -l x.el",
    "emacs --script x.el",
    "emacs -x x.el",
    "emacsclient --eval '(x)'",
    "emacs-29.4 --eval '(x)'",
    "ed f",
    "kak -e x",
]
DEBUGGER_ASK = [
    # row 6
    "gdb -ex 'shell x'",
    "gdb -batch -ex run ./a",
    "gdb -x cmds ./a",
    "gdb ./a",
    "gdb -p 1",
    "lldb -o 'platform shell x'",
    "lldb-18 -o x",
    "lldb ./a",
    "rust-gdb ./a",
    "cgdb ./a",
    "dlv exec ./a",
    "jdb x",
    # row 7
    "valgrind rm -rf /",
    "ltrace rm -rf /",
    "perf stat rm -rf /",
    "perf_6.12 stat rm -rf /",
    "perf record -- rm -rf /",
    "gdb --args rm -rf /",
    "lldb -- rm -rf /",
    "rr record rm -rf /",
    "catchsegv rm -rf /",
    "heaptrack rm -rf /",
    "uftrace rm -rf /",
    "gdbserver :1 rm -rf /",
    "sotruss rm -rf /",
    "xtrace rm -rf /",
    "memusage rm -rf /",
    # row 8: the read-only subcommands run a program through these options
    "perf report --objdump=/tmp/x",
    "perf annotate --objdump=/tmp/x",
    "perf --exec-path=/tmp report",
    # the sole-argument rule
    "gdb --version -ex 'shell x'",
    # T02 review: a perf config can name the program perf report runs
    "PERF_CONFIG=./x perf annotate --stdio",
    # T02 review: debuggers and disassemblers that run commands
    "r2 -c '!x' f",
    "radare2 -c x f",
    "rizin -c '!x' f",
    "frida -f ./a",
    "edb --run ./a",
    "ddd ./a",
    "kdbg ./a",
    "gdbtui ./a",
]
LAUNCHER_ASK = [
    # row 9 (Q6)
    "fakeroot rm -rf /",
    "eatmydata rm -rf /",
    "nsenter -t 1 rm -rf /",
    "setpriv rm -rf /",
    "prlimit rm -rf /",
    "xvfb-run rm -rf /",
    "ssh-agent rm -rf /",
    # T02 review: launchers outside Q6's first list, and the dynamic loader by path
    "torsocks git push --force origin main",
    "proxychains4 rm -rf /",
    "proxychains rm -rf /",
    "faketime 2020-01-01 rm -rf /",
    "numactl -i all rm -rf /",
    "ifne rm -rf /",
    "trickle -d 1 rm -rf /",
    "cpulimit -l 5 -- rm -rf /",
    "cgexec -g cpu:x rm -rf /",
    "systemd-inhibit rm -rf /",
    "runuser -u x -- rm -rf /",
    "sg grp -c 'rm -rf /'",
    "capsh -- -c 'rm -rf /'",
    "/lib64/ld-linux-x86-64.so.2 /bin/rm -rf /",
    "ld.so ./a",
]
TOOLS_UNCHANGED_ASK = [
    "strace ls",
    "strace -o out ls",
    "strace -o ~/.claude/settings.json ls",
    "vim -c 'w! ~/.claude/settings.json' f",
]
TOOLS_UNCHANGED_DENY = [
    "ex -s f <<'EOF'\n%s/a/b/\nwq\nEOF",
    "ed -s f <<< '!x'",
]
TOOLS_FRICTION = [
    "vim --version",
    "emacs --version",
    "gdb --version",
    "vim --help",
    "perf list",
    "perf version",
    "perf report",
    "perf annotate",
    "less f",
    "man ls",
    "more f",
    # T02 review: the family pattern leaves these alone
    "perf_analyzer -m x",
    "viewer f",
    "vimtutor",
    "gdbus call x",
    "vitest run",
    "gdb-12 --version",
]


def test_story1_editors_ask(rules, project):
    assert_all(rules, EDITOR_ASK, "ask")


def test_story2_debuggersAndProfilers_ask(rules, project):
    assert_all(rules, DEBUGGER_ASK, "ask")


def test_story8_launchers_ask(rules, project):
    assert_all(rules, LAUNCHER_ASK, "ask")


def test_story1_unchangedAsks_stayAsks(rules, project):
    assert_all(rules, TOOLS_UNCHANGED_ASK, "ask")


def test_story1_unchangedDenies_stayDenied(rules, project):
    assert_all(rules, TOOLS_UNCHANGED_DENY, "deny")


def test_story1_friction_staysSilent(rules, project):
    assert_all(rules, TOOLS_FRICTION, None)


def test_story1_projectScriptNamedEditor_asks_knownCost(rules, project):
    # the name is Debian's editor alternative; a project script under it asks (T02 review)
    assert decide(rules, "./editor") == "ask"


# ---------------------------------------------------------------- story 4: loader variables (F-65)

LOADER_ASK = [
    # row 10
    "LD_PRELOAD=/tmp/x.so ls",
    "LD_AUDIT=/tmp/x.so ls",
    "DYLD_INSERT_LIBRARIES=/tmp/x.dylib ls",
    "export LD_PRELOAD=/tmp/x.so; ls",
    "env LD_PRELOAD=/tmp/x.so ls",
    "GCONV_PATH=/tmp ls",
    "OPENSSL_CONF=/tmp/x.cnf curl https://x",
    "PERL5DB='system(1)' perl -d x.pl",
    # row 11
    "JAVA_TOOL_OPTIONS=-javaagent:x.jar java -version",
    "_JAVA_OPTIONS=x java",
    "JDK_JAVA_OPTIONS=x java",
    "DOTNET_STARTUP_HOOKS=/tmp/x.dll dotnet run",
    "CORECLR_PROFILER_PATH=/tmp/x.so dotnet run",
    "LUA_INIT=x lua s.lua",
    "ERL_AFLAGS='-eval x' erl",
    "LD_BIND_NOW=1 ls",  # the prefix
    # T03 review: module folders every program of a kind loads from
    "GIO_EXTRA_MODULES=/tmp x",
    "GIO_MODULE_DIR=/tmp x",
    "GTK_MODULES=x x",
    "GTK_PATH=/tmp x",
    "QT_PLUGIN_PATH=/tmp x",
    "GST_PLUGIN_PATH=/tmp x",
    "GST_PLUGIN_SYSTEM_PATH=/tmp x",
    "VK_LAYER_PATH=/tmp x",
    "VK_ICD_FILENAMES=/tmp/x.json x",
    "LIBGL_DRIVERS_PATH=/tmp x",
    "GDK_PIXBUF_MODULE_FILE=/tmp/x x",
    "OPENSSL_MODULES=/tmp curl https://x",
    "OPENSSL_ENGINES=/tmp curl https://x",
    "DOTNET_ADDITIONAL_DEPS=/tmp dotnet run",
]
SEARCH_PATH_ASK = [
    # row 12: a search path outside the project, or one the gate cannot place
    "LD_LIBRARY_PATH=/tmp ls",
    "DYLD_LIBRARY_PATH=/tmp ls",
    "PYTHONPATH=/tmp python3 x.py",
    "PYTHONUSERBASE=/tmp/u python3 x.py",
    "PERL5LIB=/tmp perl x.pl",
    "RUBYLIB=/tmp ruby x.rb",
    "NODE_PATH=/tmp node x.js",
    "cd /tmp && PYTHONPATH=. python3 x.py",
    "PYTHONPATH=src:/tmp python3 x.py",
    "PYTHONPATH=~/lib python3 x.py",
    "PYTHONPATH=$X python3 x.py",
    "PYTHONPATH=$(x) python3 x.py",
    "export PYTHONPATH=/tmp; python3 x.py",
    "env PYTHONPATH=/tmp python3 x.py",
    "declare -x NODE_PATH=/tmp",
    "read PYTHONPATH",
    "PYTHONPATH+=:/tmp python3 x.py",
    # T03 review: a reserved word, a compound or a wrapper before the assignment
    "time LD_LIBRARY_PATH=/tmp ./t",
    "! LD_LIBRARY_PATH=/tmp ./t",
    "if LD_LIBRARY_PATH=/tmp ./t; then :; fi",
    "while LD_LIBRARY_PATH=/tmp ./t; do :; done",
    "{ LD_LIBRARY_PATH=/tmp ./t; }",
    "f() { LD_LIBRARY_PATH=/tmp ./t; }; f",
    "nice env PYTHONPATH=/tmp python3 x.py",
    "timeout 5 env PYTHONPATH=/tmp python3 x.py",
    "stdbuf -o0 env PYTHONPATH=/tmp python3 x.py",
    "command env PYTHONPATH=/tmp python3 x.py",
    "exec env PYTHONPATH=/tmp python3 x.py",
    "nohup env PYTHONPATH=/tmp python3 x.py",
    # T03 review: a nameref, a loop or getopts variable
    "declare -n r=PYTHONPATH; r=/tmp python3 x.py",
    "export PYTHONPATH; for PYTHONPATH in /tmp; do python3 x.py; done",
    "export PYTHONPATH; select PYTHONPATH in /tmp; do python3 x.py; done",
    "getopts a: PYTHONPATH",
    # T03 review: folder forms the gate cannot place
    "PYTHONPATH=~+/.. python3 x.py",
    "LD_LIBRARY_PATH=~-/lib ./t",
    "PWD=/tmp; PYTHONPATH=$PWD python3 x.py",
    "PWD=/tmp PYTHONPATH=$PWD python3 x.py",
    # T03 review: versioned Lua paths and Erlang's library path
    "LUA_PATH_5_4=/tmp/?.lua lua s.lua",
    "LUA_CPATH_5_4=/tmp/?.so lua s.lua",
    "ERL_LIBS=/tmp erl",
    # wrap code review: a reader behind an assignment, a reserved word or a wrapper
    "IFS= read -r PYTHONPATH; export PYTHONPATH; python3 x.py",
    "while read PYTHONPATH; do python3 x.py; done",
    "if read PYTHONPATH; then python3 x.py; fi",
    "{ read PYTHONPATH; }",
    "command read PYTHONPATH",
    "builtin read LD_LIBRARY_PATH",
]
LOADER_FRICTION = [
    "PYTHONPATH=. pytest",
    "PYTHONPATH=src python3 -m pytest",
    "PYTHONPATH=$PWD/src pytest",
    "PYTHONPATH=${PWD}/src pytest",
    "PYTHONPATH=src:$PYTHONPATH pytest",
    "LD_LIBRARY_PATH=./build ./a.out",
    "rg 'LD_LIBRARY_PATH=' .",
    "grep -n 'PYTHONPATH=' Makefile",
    "LDFLAGS=-L. ls",
    # T03 review: Java's own wildcard, and other daily forms
    "CLASSPATH=build/classes:lib/* java Main",
    "CLASSPATH='build/classes:lib/*' java Main",
    "PYTHONPATH=tests:src pytest",
    "GEM_HOME=vendor/bundle bundle exec x",
    "LD_LIBRARY_PATH=$PWD/lib ./t",
    "NODE_PATH=node_modules node x.js",
    "cd tests && PYTHONPATH=../src pytest",
    "PYTHONPATH=~+/src pytest",
    "printenv LD_LIBRARY_PATH",
    "env grep PYTHONPATH=/etc f",  # wrap code review: the words after env's program are its data
]


def test_story6_editorReason_showsTheSubstitution(rules, project):
    assert "$(id)" in verdict(rules, "EDITOR=$(id) crontab -e").note


def test_story5_longUnsetoptText_isLinear(rules, project):
    import time

    started = time.monotonic()
    rules.dotglob_on([], "unsetopt " * 6000)
    assert time.monotonic() - started < 1.0


def test_story4_loaderVariables_ask(rules, project):
    assert_all(rules, LOADER_ASK, "ask")


def test_story4_searchPathOutside_asks(rules, project):
    assert_all(rules, SEARCH_PATH_ASK, "ask")


def test_story4_friction_staysSilent(rules, project):
    (project / "tests").mkdir()
    assert_all(rules, LOADER_FRICTION, None)


def test_story4_unchanged_namedVariableInText_asks_knownCost(rules, project):
    assert decide(rules, "grep -rn 'NODE_OPTIONS=' .") == "ask"
    assert decide(rules, "PATH=/tmp:$PATH ls") == "ask"


# ---------------------------------------------------------------- story 6: git -c, command variables (F-70)

GIT_COMMAND_ASK = [
    # row 14
    "git -c core.fsmonitor=x status",
    "git -c core.sshCommand=x fetch",
    "git --config-env=core.fsmonitor=V status",
    "git --config-env core.fsmonitor=V status",
    "git --exec-path=/tmp status",
    "git -C . -c core.hooksPath=/tmp/h status",
    "git -c core.editor=x commit --amend",
    # T04 review: --attr-source takes a value
    "git --attr-source HEAD -c core.fsmonitor=x status",
]
COMMAND_VARIABLE_ASK = [
    # row 15
    "GIT_SSH_COMMAND=x git fetch",
    "GIT_SSH=x git fetch",
    "GIT_PROXY_COMMAND=x git fetch",
    "GIT_EXEC_PATH=/tmp git status",
    "GIT_ASKPASS=x git fetch",
    "SSH_ASKPASS=x git fetch",
    "GIT_EXTERNAL_DIFF=x git diff",
    "GIT_TEMPLATE_DIR=/tmp git init",
    "GIT_CONFIG_GLOBAL=/tmp/x git status",
    "GIT_CONFIG_SYSTEM=/tmp/x git status",
    "GIT_CONFIG_PARAMETERS=x git status",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=x git status",
    "LESSOPEN='|x %s' less f",
    "LESSCLOSE=x less f",
    "EDITOR=x crontab -e",
    "VISUAL=x crontab -e",
    "export EDITOR=x; crontab -e",
]
COMMAND_FRICTION = [
    "GIT_PAGER=cat git log",
    "PAGER=cat man ls",
    "git --no-pager log",
    "git -c color.ui=always log",
    "git -c core.pager=less log",  # a pager never runs without a terminal (Q5)
    "git --exec-path",
    "git --exec-path /tmp",  # without =, git prints its own folder and exits (T04 review)
    "git -c core.editor=cat status",
    "git -c core.autocrlf=false status",
    "GIT_TERMINAL_PROMPT=0 git status",
    "EDITOR=true crontab -e",
    "EDITOR= crontab -l",
    "grep -rn 'GIT_EDITOR=' .",
]


def test_story6_gitCommandLineConfig_asks(rules, project):
    assert_all(rules, GIT_COMMAND_ASK, "ask")


def test_story6_commandVariables_ask(rules, project):
    assert_all(rules, COMMAND_VARIABLE_ASK, "ask")


def test_story6_friction_staysSilent(rules, project):
    assert_all(rules, COMMAND_FRICTION, None)


def test_story6_unchanged_gitConfigEditor_asks(rules, project):
    assert decide(rules, "git config core.editor x") == "ask"


# ---------------------------------------------------------------- story 5: dotglob

DOTGLOB_ASK = [
    # row 13
    "shopt -s dotglob; cat *",
    "shopt -s dotglob; tee *.json",
    "shopt -s nullglob dotglob; cp x *.json",
    "shopt -s dotglob; cat ~/*",
    "shopt -s dot''glob; cat *",
    "GLOBIGNORE=x; cat *",
    "export GLOBIGNORE=x; cat *",
    "bash -O dotglob -c 'cat *'",
    "bash -c 'shopt -s dotglob; cat *'",
    "o=dotglob; shopt -s $o; cat *",
    "setopt globdots; cat *",
    "setopt GLOB_DOTS; cat *",
    "set -o globdots; cat *",
    # T05 review: a shell's flag one level down, and zsh's inversions and short flag
    "bash -c 'bash -O dotglob -c \"cat *\"'",
    "sh -c 'bash -O dotglob -c \"cat *\"'",
    "bash -c 'zsh -o globdots -c \"cat *\"'",
    "cat <(bash -O dotglob -c 'cat *')",
    "find . -maxdepth 0 -exec bash -O dotglob -c 'cat *' \\;",
    "zsh -c 'unsetopt noglobdots; cat *'",
    "zsh +o noglobdots -c 'cat *'",
    "setopt -4; cat *",
    "zsh -c 'options[globdots]=on; cat *'",
]
DOTGLOB_UNCHANGED_ASK = [
    "cat {.,}*.json",
    "cat .mc?.json",
    "shopt -s dotglob && rm -f *",
]
DOTGLOB_FRICTION = [
    "ls *",
    "cat *.json",
    "shopt -s nullglob; cat *.json",
    "shopt -s dotglob; ls *.md",
    "shopt -u dotglob; cat *",
    "shopt -s extglob; ls *.json",
    "shopt dotglob",
    "shopt -p",
    "echo shopt -s dotglob",
    "unset GLOBIGNORE",
    "ping -4 -c 1 h; ls *",  # -4 is zsh's globdots letter for zsh, set and setopt only
]


def test_story5_textNamingGlobignore_asks_knownCost(rules, with_server_lists):
    # quotes are stripped before the setter scan, so a mention reads as a set (T05 review)
    assert decide(rules, "grep 'GLOBIGNORE=x' f; cat *") == "ask"


@pytest.fixture
def with_server_lists(project):
    (project / ".mcp.json").write_text("{}")
    (project / "a.json").write_text("{}")
    (project / "r.md").write_text("")
    (project.parent / "home" / ".claude.json").write_text("{}")
    return project


def test_story5_dotglobOn_globReachesProtectedFile_asks(rules, with_server_lists):
    assert_all(rules, DOTGLOB_ASK, "ask")


def test_story5_unchangedAsks_stayAsks(rules, with_server_lists):
    assert_all(rules, DOTGLOB_UNCHANGED_ASK, "ask")


def test_story5_friction_staysSilent(rules, with_server_lists):
    assert_all(rules, DOTGLOB_FRICTION, None)


def test_story6_unchanged_gitConfigAndAliases_ask(rules, project):
    assert decide(rules, "git -c alias.st='!x' st") == "ask"
    assert decide(rules, "git config core.pager cat") == "ask"
    assert decide(rules, "GIT_EDITOR=x git commit") == "ask"


# ---------------------------------------------------------------- story 7: the 2.1.331 options (Q7)

NESTED_REASONS = {
    # row 16: read from the raw argv, so a value slot does not hide them
    "claude --model --managed-settings-in-initialize -p x": "brings settings",
    "claude --model --initialize-fields -p x": "brings settings",
    # row 17: each with its class's reason
    "claude -p x --managed-settings-in-initialize": "brings settings",
    "claude -p x --initialize-fields x": "brings settings",
    "claude -p x --trusted-folder /tmp/x": "brings settings",
    "claude -p x --organization-gateway": "gateway",
    "claude -p x --gateway-json": "gateway",
    "claude -p x --web": "outside this machine",
    "claude -p x --routine r": "outside this machine",
    "claude -p x --discard": "drop",
    # the fleet check reads --routine from the raw argv too (ci-claude-pin, both binaries)
    "claude --model --routine -p x": "outside this machine",
    "claude --model --routine=r -p x": "outside this machine",
    # T06 review: the = form in a value slot
    "claude --model --initialize-fields=x -p x": "brings settings",
}
NESTED_UNKNOWN = [
    # the ten whose meaning checkpoint 5 could not read keep the unknown-option ask
    "claude -p x --event x",
    "claude -p x --list x",
    "claude -p x --metadata x",
    "claude -p x --output x",
    "claude -p x --path x",
    "claude -p x --review-md x",
    "claude -p x --lead-verify-key x",
    "claude -p x --session-began-as-copy x",
    "claude -p x --agents-view-if-allowed",
    "claude -p x --hold-repository-while-parked",
]
NESTED_FRICTION = [
    "claude -p x --max-cost 1",
    "claude -p x --max-cost-usd 1",
    "claude -p x --registry https://h",  # dropped by 2.1.331, kept for older installs
    # T06 review, a canary: --max-cost takes a value (the relayed diff, not read in a binary here);
    # if a later pin shows no value, this row must ask
    "claude --max-cost --dangerously-skip-permissions -p x",
]


@pytest.mark.parametrize(("command", "reason"), NESTED_REASONS.items())
def test_story7_newOptions_askWithTheirClass(rules, project, command, reason):
    found = verdict(rules, command)
    assert found.decision == "ask" and reason in found.note, (command, found.note)


def test_story7_unreadOptions_keepTheUnknownAsk(rules, project):
    for command in NESTED_UNKNOWN:
        assert "does not know" in verdict(rules, command).note, command


def test_story7_friction_staysSilent(rules, project):
    assert_all(rules, NESTED_FRICTION, None)


# ---------------------------------------------------------------- story 9: both runtimes

AGY_ROWS = [
    ("echo a\\\\\nrm -rf /", "deny"),  # story 3
    ("vim -c '!x' f", "force_ask"),  # story 1
    ("valgrind rm -rf /", "force_ask"),  # story 2
    ("fakeroot rm -rf /", "force_ask"),  # story 8
    ("LD_PRELOAD=/tmp/x.so ls", "force_ask"),  # story 4
    ("PYTHONPATH=/tmp python3 x.py", "force_ask"),
    ("git -c core.fsmonitor=x status", "force_ask"),  # story 6
    ("GIT_SSH_COMMAND=x git fetch", "force_ask"),
    ("claude --model --managed-settings-in-initialize -p x", "force_ask"),  # story 7
    ("PYTHONPATH=. pytest", "allow"),
    ("vim --version", "allow"),
]


@pytest.mark.parametrize(("command", "expected"), AGY_ROWS)
def test_story9_agy_sameJudgement(rules, project, monkeypatch, command, expected):
    """ADR-0007: under agy, run_command reaches the same judgement; ``allow`` there is no opinion."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    (project / ".agent").mkdir()
    (project / ".agent" / "cobot.rules").write_text("")
    call = {"id": "t1", "name": "run_command", "args": {"CommandLine": command, "Cwd": str(project)}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(project)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == expected


def test_story9_agy_dotglob_sameJudgement(rules, with_server_lists, monkeypatch):  # story 5
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    (with_server_lists / ".agent").mkdir()
    (with_server_lists / ".agent" / "cobot.rules").write_text("")
    args = {"CommandLine": "shopt -s dotglob; cat *", "Cwd": str(with_server_lists)}
    call = {"id": "t1", "name": "run_command", "args": args}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(with_server_lists)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == "force_ask"
