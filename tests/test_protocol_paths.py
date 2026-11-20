"""The protocol routes a diagnosis (spec debug-path, story 7): the Paths paragraph names
`unknown cause → /cobot:debug`, and the protocol stays within its cap."""

from __future__ import annotations

import importlib.util

from conftest import PLUGIN, REPO

PROTOCOL = PLUGIN / "protocol.md"


def paragraph(text: str, name: str) -> str:
    return next(p for p in text.split("\n\n") if p.startswith(f"{name}. "))


def test_protocol_paths_routeAnUnknownCauseToDebug():
    assert "unknown cause → /cobot:debug" in paragraph(PROTOCOL.read_text(encoding="utf-8"), "Paths")


def test_protocol_staysWithinItsCap():
    spec = importlib.util.spec_from_file_location("check_plugin", REPO / "scripts" / "check-plugin.py")
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    assert len(PROTOCOL.read_text(encoding="utf-8")) <= contract.PROTOCOL_MAX_CHARS
