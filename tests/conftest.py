"""Shared fixtures: load the extension-less gate script as a module."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "partner"
GATE_SCRIPT = PLUGIN / "bin" / "partner-rules"
GATE_SHIM = PLUGIN / "hooks" / "gate.sh"
INSTALL = REPO / "install.sh"


BIN = PLUGIN / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))


def load_script(name: str, module_name: str):
    loader = importlib.machinery.SourceFileLoader(module_name, str(BIN / name))
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclasses resolve annotations through sys.modules
    loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def memory():
    return load_script("partner-memory", "partner_memory")


@pytest.fixture(scope="session")
def session():
    return load_script("partner-session", "partner_session")


@pytest.fixture(scope="session")
def rules():
    loader = importlib.machinery.SourceFileLoader("partner_rules", str(GATE_SCRIPT))
    spec = importlib.util.spec_from_loader("partner_rules", loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["partner_rules"] = module  # dataclasses resolve annotations through sys.modules
    loader.exec_module(module)
    return module
