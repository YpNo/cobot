"""How a ``claude`` argv starts a session the gate may not govern (spec gate-f58, story 2): read by
a table of Claude Code's options, never by running it.

The table is the binary's own option list (Claude Code 2.1.311: the commander specs in
``/usr/bin/claude``, read 2026-11-24; hidden options included, each checked through ``claude
<opt> auth status``), so ``--help``'s omissions (``--max-turns``) are known. Each option has a
value shape as commander reads it: none; required (the next word, even one starting with a
dash); optional (the next word only when it is not an option); variadic (words up to the next
option). An option the table lacks asks (Q1): a new release may add one that switches hooks off.
"""

from __future__ import annotations

import os

NONE, REQUIRED, OPTIONAL, VARIADIC = "none", "required", "optional", "variadic"
_LONG_BY_SHAPE = {
    NONE: (
        "--all --allow-dangerously-skip-permissions --allow-other-models --allow-real-servers "
        "--available --await-claim --await-initialize --ax-screen-reader --bare --brief --chrome "
        "--claudeai --client-secret --console --continue --cowork --dangerously-skip-permissions "
        "--deep-link-origin --desktop --disable-slash-commands --dry-run --enable-auth-status "
        "--enable-auto-mode --exclude-dynamic-system-prompt-sections --force --fork-session "
        "--forward-subagent-text --from-link --host-auth-is-org-sign-in --ide --include-hook-events "
        "--include-partial-messages --include-unsupported-models --init --init-only --interactive "
        "--interview --keep-data --keep-temp --maintenance --no-browser --no-chrome --no-post "
        "--no-publish --no-scaffold --no-session-persistence --plan-mode-required --post --print "
        "--prune --publish-report --push --replace --replay-user-messages --reply-on-resume "
        "--resolve-only --restricted --safe-mode --scaffold --session-mirror --session-tunnel --sso "
        "--status --strict-mcp-config --strict --text --tmux --trust-plugin --trust-workspace "
        "--values-stdin --verbose --xaa --yes --bg --background --help --version"
    ),
    REQUIRED: (
        "--ablation --accept-command --advisor --agent-color --agent-id --agent-name --agent --agents "
        "--agent-type --append-subagent-system-prompt-file --append-subagent-system-prompt "
        "--append-system-prompt-file --append-system-prompt --attach-serve --author-email --author "
        "--autocompact --callback-port --case --client-data-url --client-id --concurrency --config "
        "--correlation-id --cwd --debug-file --deep-link-cwd-b64 --deep-link-last-fetch "
        "--deep-link-repo --description --effort --email --environment --eval-dir --fallback-model "
        "--fast-mode --forward-home-settings --id-token --inherit-permission-mode --input-format "
        "--issuer --json-schema --judge-model --label --managed-settings --marketplace "
        "--max-budget-usd --max-cost-usd --max-thinking-tokens --max-turns --message "
        "--messaging-socket-path --mocks --model --name --on-branch --output-dir --output-format "
        "--parent-session-id --permission-mode --permission-prompts --permission-prompt-tool "
        "--plan-mode-instructions --plugin-dir-no-mcp --plugin-dir --plugin-url --pool --port "
        "--prefill-b64 --prefill --proactivity --profile --project-config-root --ref --registry "
        "--remote-control-session-name-prefix --report --result-format --resume-drops-turn "
        "--resume-session-at --rewind-files --runner-declares --runs --scope --sdk-url --session-id "
        "--setting-sources --settings --system-prompt-file --system-prompt --system-prompt-snapshot "
        "--task-budget --teammate-mode --team-name --thinking-display --thinking --threshold "
        "--timeout --transport --watch-artifact-no-autoreact --watch-artifact --workload"
    ),
    OPTIONAL: (
        "--cloud --data-size --debug --from-pr --json --prompt-suggestions --rc --remote-control "
        "--remote --resume --teleport --worktree"
    ),
    VARIADIC: (
        "--add-dir --allow-tools --betas --channels --dangerously-load-development-channels "
        "--disallow-tools --env --file --header --mcp-config --sparse --tag --tools --with "
        "--allowedTools --allowed-tools --disallowedTools --disallowed-tools"
    ),
}
LONG_SHAPES = {name: shape for shape, names in _LONG_BY_SHAPE.items() for name in names.split()}
SHORT_OPTIONS = {
    "a": ("--all", NONE),
    "c": ("--continue", NONE),
    "d": ("--debug", OPTIONAL),
    "e": ("--env", VARIADIC),
    "f": ("--force", NONE),
    "h": ("--help", NONE),
    "H": ("--header", VARIADIC),
    "i": ("--interactive", NONE),
    "j": ("--concurrency", REQUIRED),
    "m": ("--message", REQUIRED),
    "n": ("--name", REQUIRED),
    "p": ("--print", NONE),
    "r": ("--resume", OPTIONAL),
    "s": ("--scope", REQUIRED),
    "t": ("--transport", REQUIRED),
    "v": ("--version", NONE),
    "w": ("--worktree", OPTIONAL),
    "y": ("--yes", NONE),
}
# Claude Code's subcommands; ``agents`` dispatches sessions with its own options, read the same way
SUBCOMMANDS = frozenset(
    "agents attach auth auto-mode doctor gateway import install logs mcp plugin plugins purge "
    "respawn rm setup-token stop kill ultrareview update upgrade help".split()
)
SESSION_SUBCOMMANDS = frozenset({"agents"})
# the subcommands that change Claude Code itself (spec gate-f58, story 7, Q7)
SELF_CHANGING = {
    "install": "replaces the binary every later session and hook runs under",
    "update": "replaces the binary every later session and hook runs under",
    "upgrade": "replaces the binary every later session and hook runs under",
    "purge": "edits ~/.claude.json, a protected file",
    "import": "writes Claude Code's configuration from another agent's",
    # T06 review: a long-lived token printed to stdout lands in the transcript
    "setup-token": "prints a long-lived subscription token into the transcript",
}
GATE_OFF = frozenset({"--bare", "--safe-mode", "--setting-sources", "--restricted"})
# read by Claude Code in process.argv before commander, so a value slot does not hide them
RAW_SCANNED = frozenset({"--bare", "--safe-mode", "--restricted"})
FOREIGN = frozenset(
    {
        "--project-config-root",  # project settings, .mcp.json and .claude trees from elsewhere
        "--managed-settings",
        "--permission-prompt-tool",
        "--sdk-url",
        "--dangerously-load-development-channels",
        "--channels",
        "--plugin-url",
    }
)
WIDENING = frozenset(
    {"--dangerously-skip-permissions", "--allow-dangerously-skip-permissions", "--enable-auto-mode"}
)
WIDE_MODES = frozenset({"bypassPermissions", "auto", "dontAsk"})
MODE_OPTIONS = frozenset({"--permission-mode", "--inherit-permission-mode"})
ELSEWHERE = frozenset(
    {"--cloud", "--environment", "--remote-control", "--rc", "--remote", "--teleport", "--desktop"}
)
NAMES = frozenset({"claude", "claude-code"})
Folders = list[str] | tuple[str, ...] | None  # where a segment may run; None when unknown


HERE: tuple[str, ...] = ()  # no folders given: the process's working directory


def nested_reason(argv: list[str], folders: Folders = HERE) -> str | None:
    """Why a ``claude`` argv may run a session outside the gate, or past the owner's prompts, or
    elsewhere; None for any other command and for a session the gate still governs. ``folders``
    are where the segment may run, where a relative ``--add-dir`` resolves (None: unknown)."""
    if not argv or os.path.basename(argv[0]).lower() not in NAMES:
        return None
    raw = argv[1 : argv.index("--")] if "--" in argv else argv[1:]
    scanned = next((word for word in raw if word in RAW_SCANNED), None)
    if scanned:  # Claude Code reads these in process.argv itself, wherever they sit (T02 review)
        return f"claude {scanned} starts a session without cobot's gate (its hooks do not load)"
    words, index, subcommand = argv[1:], 0, None
    while index < len(words) and words[index] != "--":
        word = words[index]
        if word.startswith("-") and len(word) > 1:
            options, taken = read_option(words, index)
            reason = next(
                filter(None, (option_reason(name, values, folders) for name, values in options)), None
            )
            if reason:
                return reason
            index += taken
            continue
        if subcommand is None:  # the first word that is not an option or an option's value
            subcommand = word if word in SUBCOMMANDS else ""
            if subcommand and subcommand not in SESSION_SUBCOMMANDS:
                return subcommand_reason(subcommand, words[index + 1 :])
        index += 1
    after = words[index + 1 : index + 2] if index < len(words) else []
    if subcommand is None and after and after[0] in SUBCOMMANDS:  # ``claude -- update`` (T06 review)
        if after[0] in SESSION_SUBCOMMANDS:
            return nested_reason([argv[0], *words[index + 1 :]], folders)
        return subcommand_reason(after[0], words[index + 2 :])
    return None


def subcommand_reason(subcommand: str, rest: list[str]) -> str | None:
    """A subcommand that sends the branch away (Q3), or changes Claude Code itself (Q7: replaces
    the binary, edits ``~/.claude.json``, writes configuration, resets the classifier), asks."""
    if subcommand == "ultrareview":
        return "claude ultrareview sends the branch to a review in the cloud"
    if subcommand in SELF_CHANGING:
        return f"claude {subcommand} {SELF_CHANGING[subcommand]}"
    verb = next((word for word in rest if not word.startswith("-")), None)
    if subcommand == "auto-mode" and verb == "reset":
        return "claude auto-mode reset resets the auto mode classifier's configuration"
    return None


def read_option(words: list[str], index: int) -> tuple[list[tuple[str, list[str]]], int]:
    """The options a word holds, each with its values, and the words they take. An unknown long
    name, or a cluster letter the table lacks, comes back with the value ``None`` marker."""
    word = words[index]
    if word.startswith("--"):
        name, eq, value = word.partition("=")
        shape = LONG_SHAPES.get(name)
        if shape is None:
            return [(name, ["\0unknown"])], 1
        if eq:
            return [(name, [value])], 1
        values, taken = shaped_values(words, index + 1, shape)
        return [(name, values)], taken + 1
    options: list[tuple[str, list[str]]] = []
    for position, letter in enumerate(word[1:], start=1):
        if letter not in SHORT_OPTIONS:
            return [*options, (f"-{letter}", ["\0unknown"])], 1
        name, shape = SHORT_OPTIONS[letter]
        rest = word[position + 1 :]
        if shape != NONE:
            if rest:
                return [*options, (name, [rest])], 1
            values, taken = shaped_values(words, index + 1, shape)
            return [*options, (name, values)], taken + 1
        options.append((name, []))
    return options, 1


def shaped_values(words: list[str], start: int, shape: str) -> tuple[list[str], int]:
    """The values an option of this shape takes from ``words[start:]``, and how many."""
    following = words[start] if start < len(words) else None
    if shape == NONE or following is None:
        return [], 0
    if shape == REQUIRED:
        return [following], 1
    if shape == OPTIONAL:
        return ([], 0) if following.startswith("-") else ([following], 1)
    end = start
    while end < len(words) and not words[end].startswith("-"):
        end += 1
    return words[start:end], end - start


def option_reason(name: str, values: list[str], folders: Folders = HERE) -> str | None:
    """The ask an option carries, with its name in the reason."""
    if values == ["\0unknown"]:
        return f"claude {name}: an option the gate does not know may switch its hooks off"
    if name in GATE_OFF and not (name == "--setting-sources" and keeps_owner_settings(values)):
        return f"claude {name} starts a session without cobot's gate (its hooks do not load)"
    if name in FOREIGN:
        return f"claude {name} brings settings, a permission answerer or code from outside the session"
    if widens(name, values):
        return f"claude {name} runs a session past the owner's permission prompts"
    if name == "--add-dir" and any(protected_folder(value, folders) for value in values):
        return "claude --add-dir opens HOME, the config dir or a .claude folder to a nested session"
    if name in ELSEWHERE:
        return f"claude {name} runs or reaches a session outside this machine's gate"
    return None


def keeps_owner_settings(values: list[str]) -> bool:
    """``--setting-sources user,project[,local]`` still loads the settings cobot is enabled in."""
    sources = {part.strip() for value in values for part in value.split(",")}
    return {"user", "project"} <= sources


def widens(name: str, values: list[str]) -> bool:
    """A bypass flag, a wide permission mode, or agents defined with one (``--agents`` JSON)."""
    if name in WIDENING:
        return True
    if name in MODE_OPTIONS:
        return any(value in WIDE_MODES for value in values)
    return name == "--agents" and any(mode in value for value in values for mode in WIDE_MODES)


def protected_folder(value: str, folders: Folders = HERE) -> bool:
    """HOME or one of its ancestors, the config dir or a path inside it, or a ``.claude`` folder
    itself (a project's), resolved from each of ``folders``; a relative value where the folder is
    unknown counts (wrap code review: ``cd ~ && claude --add-dir .``). A folder below a project's
    ``.claude`` (a worktree in ``.claude/worktrees``) is not one: its files have their own rows."""
    text = os.path.expanduser(value.replace("${HOME}", "~").replace("$HOME", "~"))
    if "\0" in text or (folders is None and not os.path.isabs(text)):
        return True
    return any(
        protected_path(os.path.realpath(os.path.join(base, text))) for base in folders or [os.getcwd()]
    )


def protected_path(path: str) -> bool:
    home = os.path.realpath(os.path.expanduser("~"))
    config = os.path.realpath(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(home, ".claude"))
    inside_config = path == config or path.startswith(config + os.sep)
    return (
        home == path
        or home.startswith(path.rstrip(os.sep) + os.sep)
        or inside_config
        or (os.path.basename(path) == ".claude")
    )
