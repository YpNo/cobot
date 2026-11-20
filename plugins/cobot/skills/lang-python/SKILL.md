---
name: lang-python
description: >-
  Senior Python: verified interpreter and tools, the exact uv, ruff, pytest, type-check and audit
  commands, 3.12+ idiom, pyproject and uv.lock shape, test and security rules, Home Assistant custom
  components. Use on *.py, pyproject.toml, uv.lock, requirements*.txt, in python-builder, and before
  writing, reviewing or testing Python.
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/uv.lock"
  - "**/requirements*.txt"
user-invocable: false
---

# lang-python

CONTEXT.md and the governance file it names override this skill: the project's coverage tool and
threshold, error-handling rules and shape win over the defaults below.

Versions, dates and sources: `references/versions.md`. Re-verify a line the brief flags stale
(versions after 30 days, idiom after 90) before relying on it; never "upgrade" a repo as a side
effect — report the gap.

## Toolchain and commands

- [verified 2026-11-07 · src: https://endoflife.date/api/python.json] 3.15.2 and 3.14.10 are the bugfix lines; 3.13, 3.12 and 3.11 are security-only; 3.10 is end of life.
- [verified 2026-11-20 · src: https://api.github.com/repos/astral-sh/uv/releases/latest] uv 0.13.9 is current; ruff 0.17.6 (its own release page).
- Repo pins win: `requires-python` in `pyproject.toml` and `.python-version` decide the interpreter.

| step | command |
|---|---|
| environment | `uv sync --locked` (dev group included by default); `uv run <cmd>` for every tool |
| format | `uv run ruff format --check .` (fix: drop `--check`) |
| lint | `uv run ruff check .` with `[tool.ruff.lint] select = ["E", "F", "I", "UP", "B", "S", "SIM", "RUF"]` |
| type check | `uv run mypy .` (strict in `pyproject.toml`) or `uv run pyright`; one of them, not both |
| test (focused) | `uv run pytest tests/test_x.py -k name -q` |
| test (all) | `uv run pytest -q` |
| coverage | `uv run pytest --cov=<package> --cov-report=term-missing --cov-fail-under=85` |
| audit | `uv audit` or `uv run pip-audit` ; `cobot-deps check` reports what is behind |
| outdated | `uv tree --depth 1 --outdated` |
| build | `uv build` (backend from `[build-system]`) |
| lock check | `uv lock --check` (non-zero when `uv.lock` would change) |

- Lock rule: `uv.lock` committed; CI runs `uv sync --locked`; a `requirements.txt` is an export
  (`uv export --no-hashes`), never the source of truth.
- Tools as dependency groups (`[dependency-groups] dev = ["pytest", "ruff", ...]`, PEP 735), not
  a `requirements-dev.txt`. Project metadata in `[project]` (PEP 621).
- `uv init` chooses `uv_build` as the backend; `hatchling` is the alternative for plugins or
  dynamic metadata. No `setup.py` in new code.
- One-off tools: `uvx ruff@0.17.6 check .` pins the version; `uvx <tool>` without a pin floats.

## Idiom

- Target the oldest supported line the repo declares; new code assumes 3.12+: `type` aliases and
  `def f[T](...)` (PEP 695), `match` for structured dispatch, `tomllib` for TOML, `except*` for
  exception groups, `pathlib.Path` for every path, `dataclass(slots=True, frozen=True)` for
  value objects, `enum.StrEnum` for string constants.
- Errors: one exception hierarchy per package rooted in a `XError(Exception)`; raise with
  context (`raise ConfigError(f"load {path}") from error`); never bare `except:`; never
  `except Exception: pass`. Catch at the boundary that can act, let the rest propagate.
- Typing is part of the API: every public function annotated; `X | None` over `Optional`;
  `collections.abc` for `Iterable`, `Callable`, `Mapping`; `TypedDict` or a dataclass for
  structured dicts; `Protocol` for duck-typed ports. `Any` needs a comment.
- Constructor injection; module-level state only for constants. No `global`.
- Logging through `logging.getLogger(__name__)`, lazy formatting (`log.info("x %s", v)`), never
  secrets. `print` only in CLI output paths.
- Async: `asyncio.TaskGroup` over gather for structured concurrency; `asyncio.timeout()`; never
  block the loop (`time.sleep`, sync I/O) inside `async def`; `anyio` when the code must run on
  trio too.
- Free-threaded builds (3.14 officially supported) change nothing in idiom: keep shared state
  behind locks or queues, assume the GIL is not a lock.
- CLI: `argparse` for small tools, `typer` or `click` when subcommands and completion matter;
  exit codes 0/1/2 with meaning.

## Project shape

```text
pyproject.toml  uv.lock  README.md  CHANGELOG.md
src/<package>/__init__.py  py.typed      # src layout; tests import the installed package
tests/conftest.py  tests/test_<module>.py
```

- `src/` layout so tests never import the working directory by accident.
- One package per repository unless a workspace is declared (`[tool.uv.workspace]`).
- Home Assistant custom components: `custom_components/<domain>/` with `manifest.json`
  (`version`, `requirements`, `codeowners`), `hacs.json`, `strings.json` + `translations/`,
  `config_flow.py`; the interpreter floor is HA's (`requires-python >= 3.14.2` in 2026.11);
  validate with `hassfest` and the HACS action (both run from a branch ref upstream; pin the
  commit in your own workflow).

## Tests

- pytest only; no `unittest.TestCase` in new code. Fixtures in `conftest.py`, `tmp_path`,
  `monkeypatch`, `capsys`; `pytest.mark.parametrize` for tables of cases.
- Names: `test_<unit>_<scenario>_<expected>`; one behaviour per test; assert messages that name
  the value.
- Fakes over mocks: a `Protocol` with an in-memory implementation; `unittest.mock.patch` only at
  the process boundary (clock, network, subprocess).
- Property tests with `hypothesis` for parsers and arithmetic. Coverage floor 85 % on `src/`.
- Doctests only for pure helpers whose example is the documentation.

## Security

- Subprocess: argv lists, `shell=False`, `check=True`, timeouts; never f-string a command;
  `shlex.quote` when a shell is unavoidable.
- Deserialisation: `json`, `tomllib`, `yaml.safe_load`; never `pickle`, `marshal`, `eval`,
  `exec` on input; `defusedxml` for XML from outside.
- Paths: `Path(base, name).resolve()` must stay under `base.resolve()`; `tempfile` with
  `delete=False` only with a cleanup; `os.open(..., 0o600)` for secrets.
- Secrets from the environment or a secret manager, never in code or logs; `secrets` module
  for tokens, `hmac.compare_digest` for comparisons; `hashlib` with `usedforsecurity=False`
  only for checksums.
- HTTP: `httpx` or `requests` with explicit timeouts and `verify=True`; validate inputs with
  `pydantic` at the boundary when the shape is not trivial.
- Supply chain: `uv.lock` pinned, `uv audit` or `pip-audit` in CI, `--require-hashes` when a
  `requirements.txt` is installed by `pip`.

## CI

`references/ci.md`: one job with `astral-sh/setup-uv` (cache on), `uv sync --locked`, ruff,
type check, pytest with the coverage gate, `uv audit`; SHAs dated there.

## Pitfalls

1. Mutable default arguments (`def f(x=[])`): use `None` and build inside.
2. `from module import *` and circular imports from package `__init__` side effects.
3. Relying on dict order before 3.7 semantics, or on set order at all.
4. `datetime.now()` without a timezone; use `datetime.now(UTC)` and `zoneinfo`.
5. `requirements.txt` edited by hand while `uv.lock` exists: the lock wins, the file drifts.
6. Running tests from the repo root with a flat layout: the working-copy module shadows the
   installed one and hides packaging errors.
7. `python -m pip install` into the system interpreter: always `uv` or a virtualenv.

## Do not

- Do not add a dependency the spec does not name (decision 22); prefer the standard library.
- Do not change `requires-python` or the lock to "make it work" in a task; report the gap.
- Do not disable a ruff rule file-wide; `# noqa: <code>` with a reason on the line.
