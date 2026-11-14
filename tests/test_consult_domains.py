"""Consult procedures: the commands they hand a consultant run as written and stay on its read list."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

DOMAINS = Path(__file__).resolve().parents[1] / "plugins" / "cobot" / "skills" / "consult" / "domains"


def bash_block(path: Path) -> str:
    """The first ```bash block of a procedure, dedented."""
    block = re.search(r"```bash\n(.*?)\n\s*```", path.read_text(encoding="utf-8"), re.S).group(1)
    return "\n".join(line[3:] if line.startswith("   ") else line for line in block.splitlines())


@pytest.mark.skipif(shutil.which("jq") is None, reason="jq not installed")
def test_uiContrast_oneCallFormula_givesTheReferenceRatios():
    command = bash_block(DOMAINS / "ui.md")
    out = subprocess.run(["bash", "-c", command], capture_output=True, text=True, check=True).stdout
    assert out.splitlines() == ["777777 on ffffff: 4.48", "00aa00 on ffffff: 3.11"]


def test_uiContrast_oneCallFormula_isSilentForTheConsultant(rules):
    command = bash_block(DOMAINS / "ui.md")
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": os.getcwd(),
        "agent_type": "cobot:consultant",
    }
    assert rules.gate(json.dumps(payload)) is None
