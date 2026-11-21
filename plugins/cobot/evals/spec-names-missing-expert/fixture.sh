#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A small Python tool that reads a solar
# inverter over Modbus TCP: a domain no cobot expert covers (expert-iot-protocols comes later).
set -euo pipefail
mkdir -p src/inverter tests
cat > pyproject.toml <<'TOML'
[project]
name = "inverter"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pymodbus>=3"]
TOML
cat > README.md <<'MD'
# inverter

Reads a solar inverter's power registers over Modbus TCP and prints them.
MD
cat > src/inverter/__init__.py <<'PY'
"""Read a solar inverter over Modbus TCP."""

HOST = "192.0.2.10"  # documentation address (RFC 5737)
PORT = 502
PY
cat > tests/test_inverter.py <<'PY'
from inverter import PORT


def test_port_isModbusDefault():
    assert PORT == 502
PY
