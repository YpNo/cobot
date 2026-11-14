"""Shared fixtures: load the extension-less gate script as a module."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "cobot"
GATE_SCRIPT = PLUGIN / "bin" / "cobot-rules"
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
    return load_script("cobot-memory", "cobot_memory")


@pytest.fixture(scope="session")
def session():
    return load_script("cobot-session", "cobot_session")


@pytest.fixture(autouse=True)
def isolated_owner_layer(tmp_path_factory, monkeypatch):
    """No test reads the owner's real rules layer (F-15): an empty one, unless a test sets its own."""
    owner = tmp_path_factory.mktemp("owner") / "cobot.rules"
    owner.write_text("")
    monkeypatch.setenv("COBOT_RULES_OWNER", str(owner))


@pytest.fixture(scope="session")
def rules():
    loader = importlib.machinery.SourceFileLoader("cobot_rules", str(GATE_SCRIPT))
    spec = importlib.util.spec_from_loader("cobot_rules", loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cobot_rules"] = module  # dataclasses resolve annotations through sys.modules
    loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def stub_repository_config(request, monkeypatch):
    """The gate's repository-configuration check reads the checkout the tests run in; a test sees
    it only through ``repository_trust`` (gate-repo-config), every other test gets a neutral one."""
    if "repository_trust" in request.fixturenames:
        return
    module = sys.modules.get("cobot_rules")
    if module is not None:
        monkeypatch.setattr(module, "repository_config", lambda *_: None)


@pytest.fixture
def repository_trust(tmp_path, monkeypatch):
    """A config directory naming the identity ``github.com/ypno``, no global or system git config,
    and a home and cargo home of their own; returns the config directory."""
    config = tmp_path / "config"
    (config / "cobot").mkdir(parents=True)
    (config / "cobot" / "identities").write_text("github.com/ypno\n")
    home = tmp_path / "home"
    home.mkdir()
    for name, value in {
        "CLAUDE_CONFIG_DIR": config,
        "XDG_DATA_HOME": tmp_path / "data",
        "HOME": home,
        "CARGO_HOME": home / ".cargo",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
    }.items():
        monkeypatch.setenv(name, str(value))
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    return config
