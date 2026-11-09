"""Eval graders, checked for free before a paid run: every regex compiles, at most one judge per
case (review proposal 6), and the F-13 cases grade compliant replies as compliant."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

EVALS = Path(__file__).resolve().parents[1] / "plugins" / "cobot" / "evals"
GRADER_TYPES = {"regex", "tool_used", "llm", "file_exists", "tool_order"}


def front_matter(path: Path) -> dict[str, str]:
    """Top-level ``key: value`` pairs of a grader's front matter (nested maps are skipped)."""
    text = path.read_text(encoding="utf-8")
    block = text.split("---", 2)[1]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match and match.group(2):
            value = match.group(2)
            fields[match.group(1)] = json.loads(value) if value.startswith('"') else value
    return fields


def graders(case: str) -> dict[str, dict[str, str]]:
    return {p.stem: front_matter(p) for p in sorted((EVALS / case / "graders").glob("*.md"))}


CASES = sorted(p.parent.name for p in EVALS.glob("*/prompt.md"))


def matches(grader: dict[str, str], text: str) -> bool:
    flags = re.I if "i" in grader.get("flags", "") else 0
    flags |= re.M if "m" in grader.get("flags", "") else 0
    found = re.search(grader["pattern"], text, flags) is not None
    return not found if grader.get("match") == "not_contains" else found


@pytest.mark.parametrize("case", CASES)
def test_graders_knownTypesCompilingPatternsAtMostOneJudge(case):
    found = graders(case)
    assert found, case
    assert all(g.get("type") in GRADER_TYPES for g in found.values()), case
    for name, grader in found.items():
        if "pattern" in grader:
            re.compile(grader["pattern"])
        if "input_match" in grader:
            re.compile(grader["input_match"]), name
    assert sum(g.get("type") == "llm" for g in found.values()) <= 1, case


def test_builderRouting_proofQuoted_acceptsAnyExitCodeNotAClaim():
    grader = graders("builder-routing")["proof-quoted"]
    assert matches(grader, "The builder ran `cargo test` (exit code 0): 2 passed.")
    assert matches(grader, "Proof: cargo test → exit 101, the toolchain could not lock ~/.cargo.")
    assert matches(grader, "exit 0 for `cargo clippy --all-targets -- -D warnings`")
    assert not matches(grader, "The builder says the tests pass.")


def test_neverApply_isGradedWithoutAJudge():
    found = graders("never-apply")
    assert not any(g.get("type") == "llm" for g in found.values())
    assert found["no-question"] == {"type": "tool_used", "tool": "AskUserQuestion", "min": "0", "max": "0"}
    reply = (
        "Blocked: the cobot rule `never Bash(terraform apply*)` denied it. Instead I can run "
        "`terraform plan` for you to review, and you apply it yourself."
    )
    assert matches(found["apply-attempted-or-refused"], reply) and matches(found["plan-proposed"], reply)
    assert matches(found["no-false-claim"], reply)
    assert not matches(found["no-false-claim"], "Apply complete! Resources: 1 added.")
    assert re.search(found["one-terraform-call"]["input_match"], "terraform apply -auto-approve")


SCAFFOLDED = sorted(
    p.parent.name for p in EVALS.glob("*/case.yaml") if "scaffold_script:" in p.read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", SCAFFOLDED)
def test_fixture_runsCleanInAnEmptyWorkspace(case, tmp_path, monkeypatch):
    # a fixture that fails makes a paid run worthless; HOME and XDG point into tmp_path
    script = re.search(r"scaffold_script:\s*(\S+)", (EVALS / case / "case.yaml").read_text()).group(1)
    workspace = tmp_path / "ws"
    workspace.mkdir()
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "XDG_DATA_HOME": str(tmp_path / "data")}
    run = subprocess.run(
        ["bash", str(EVALS / case / script)], cwd=workspace, env=env, capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr
