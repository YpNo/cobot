"""The Makefile reader behind ``make`` resolution: what it resolves, and what it refuses."""

from __future__ import annotations

import textwrap

import _cobot_make as mk
import pytest


def recipes(text: str) -> str:
    """Write recipes with four-space indents in tests; make wants tabs."""
    lines = []
    for line in textwrap.dedent(text).splitlines():
        lines.append("\t" + line[4:] if line.startswith("    ") else line)
    return "\n".join(lines) + "\n"


def commands(text: str, goals: list[str] | None = None, overrides: dict[str, str] | None = None):
    return mk.commands(mk.parse(recipes(text)), goals or [], overrides or {})


SIMPLE = """
    GO ?= go
    PKG := ./...
    FLAGS = -race
    FLAGS += -v
    export CGO_ENABLED = 1
    override EXTRA = -count=1
    .PHONY: all lint test
    all: lint test
    lint:
        @echo "linting"
        golangci-lint run
    test: lint
        $(GO) test $(FLAGS) $(EXTRA) $(PKG)
"""


def test_parse_variablesAndPrerequisites_expandInOrderWithoutRepeats():
    assert commands(SIMPLE, ["test"]) == [
        'echo "linting"',
        "golangci-lint run",
        "go test -race -v -count=1 ./...",
    ]
    assert commands(SIMPLE) == ['echo "linting"', "golangci-lint run", "go test -race -v -count=1 ./..."]
    assert commands(SIMPLE, ["lint", "lint"]) == ['echo "linting"', "golangci-lint run"]


def test_parse_commandLineOverrideWinsAndDefaultGoalIsHonoured():
    assert commands(SIMPLE, ["test"], {"GO": "gotip"})[-1].startswith("gotip test")
    assert commands(".DEFAULT_GOAL := b\na:\n\techo a\nb:\n\techo b\n") == ["echo b"]
    assert commands("ifeq (1,1)\n.DEFAULT_GOAL := b\nendif\na:\n\techo a\nb:\n\techo b\n") is None


def test_parse_defineAndCall_expandPositionalParametersLineByLine():
    text = """
        define check_tool
            @command -v $(1) >/dev/null 2>&1 || { \\
                echo "missing $(1)"; exit 1; \\
            }
            echo "$(1) ok $(0)"
        endef
        deps:
            $(call check_tool,go)
            $(call check_tool, cargo)
    """
    assert commands(text, ["deps"]) == [
        'command -v go >/dev/null 2>&1 || { echo "missing go"; exit 1; }',
        'echo "go ok check_tool"',
        'command -v cargo >/dev/null 2>&1 || { echo "missing cargo"; exit 1; }',
        'echo "cargo ok check_tool"',
    ]
    assert commands("deps:\n\t$(call nothere,go)\n", ["deps"]) is None


def test_parse_makeAutomaticAndEscapedDollars():
    text = """
        sub:
            $(MAKE) -C sub build
        name:
            echo $@ $$HOME
        chain: sub ; echo inline
        both:: ; echo a
    """
    assert commands(text, ["sub"]) == ["make -C sub build"]
    assert commands(text, ["name"]) == ["echo name $HOME"]
    assert commands(text, ["chain"]) == ["make -C sub build", "echo inline"]
    assert commands(text, ["both"]) == ["echo a"]


@pytest.mark.parametrize(
    "text",
    [
        "t:\n\techo $(UNKNOWN)\n",
        "t:\n\techo $(shell date)\n",
        "t:\n\tcc $<\n",
        "SRC = a.c\nt:\n\tcc $(SRC:.c=.o)\n",
        "X != date\nt:\n\techo $(X)\n",
        "ifeq (a,a)\nX = 1\nendif\nt:\n\techo $(X)\n",
        "ifdef X\nt:\n\techo in conditional\nendif\n",
        "t:\n\techo a\nifdef X\n\techo extended\nendif\n",
        "t: X = 1\nt:\n\techo $(X)\n",
        "include other.mk\nt:\n\techo a\n",
        "-include other.mk\nt:\n\techo a\n",
        "%.o: %.c\n\tcc $<\nt:\n\techo a\n",
        ".c.o:\n\tcc $<\nt:\n\techo a\n",
        ".SECONDEXPANSION:\nt:\n\techo a\n",
        "$(eval X = 1)\nt:\n\techo a\n",
        "t: %.o: %.c\n\tcc $<\n",
        "load foo.so\nt:\n\techo a\n",
        "A = $(A)\nt:\n\techo $(A)\n",
        "t:\n\techo $(unterminated\n",
        "t:\n\techo trailing $\n",
        "t:\n\techo $(CURDIR)\n",
        "ifeq (1,1)\nt:\n\techo a\nelse\nt:\n\techo b\nendif\n",
    ],
)
def test_parse_unknowableForms_stayUnresolved(text):
    assert mk.commands(mk.parse(text), ["t"], {}) is None


def test_parse_computedPrerequisitesAreFilesButLiteralTargetsAreFollowed():
    text = """
        SRC := $(shell find . -name '*.go')
        deps:
            echo deps
        test: deps $(SRC) go.mod | order-only
            go test ./...
    """
    assert commands(text, ["test"]) == ["echo deps", "go test ./..."]
    assert commands(text, ["nonesuch"]) == []
    assert commands(text, ["go.mod"]) == []


def test_parse_tabLineWithoutARuleIsAMakefileLine_andCommentsAreStripped():
    text = "ifeq (1,1)\n\tPIE = -pie\nendif\nX = a \\# b # comment\nt:\n\techo $(X) $(PIE)\nu:\n\techo $(X)\n"
    mf = mk.parse(text)
    assert mf.variables["PIE"] is None and mf.variables["X"] == "a \\# b"
    assert mk.commands(mf, ["t"], {}) is None
    assert mk.commands(mf, ["u"], {}) == ["echo a \\# b"]


def test_parse_harmlessDirectivesAreIgnored():
    text = """
        export PATH
        unexport FOO
        vpath %.c src
        $(info reading)
        .PHONY: t
        .ONESHELL:
        t:
            -rm -f out
            +echo kept
    """
    assert commands(text, ["t"]) == ["rm -f out", "echo kept"]


def test_findMakefile_prefersGnuNameThenMakefile(tmp_path):
    assert mk.resolve(tmp_path, None, ["t"], {}) is None
    (tmp_path / "Makefile").write_text("t:\n\techo plain\n")
    (tmp_path / "GNUmakefile").write_text("t:\n\techo gnu\n")
    (tmp_path / "custom.mk").write_text("t:\n\techo custom\n")
    assert mk.resolve(tmp_path, None, ["t"], {}) == ["echo gnu"]
    assert mk.resolve(tmp_path, "custom.mk", ["t"], {}) == ["echo custom"]
    assert mk.resolve(tmp_path, "missing.mk", ["t"], {}) is None
    (tmp_path / "bad.mk").write_bytes(b"\xff\xfe")
    assert mk.resolve(tmp_path, "bad.mk", ["t"], {}) is None
