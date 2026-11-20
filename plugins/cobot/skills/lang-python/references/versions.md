# Python — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale lang-python`).

## Interpreter

- [verified 2026-11-07 · src: https://endoflife.date/api/python.json] Latest patches: 3.15.2, 3.14.10, 3.13.18, 3.12.16, 3.11.18 (all 2026-10-25); 3.10.22 is the final 3.10 release (end of life 2026-10-01).
- [verified 2026-11-07 · src: https://devguide.python.org/versions/] Supported branches: 3.15 and 3.14 bugfix; 3.13, 3.12 and 3.11 security-only (3.13 moved to security-only on 2026-10-01).
- [verified 2026-11-07 · src: https://endoflife.date/api/python.json] 3.15 was first released on 2026-10-09.
- [verified 2026-11-07 · src: https://docs.python.org/3/whatsnew/3.14.html] 3.14 (2025-10-07): free-threaded Python officially supported (PEP 779); `-X importtime=2` prints `cached` for already-loaded modules.
- [verified 2026-11-07 · src: https://docs.python.org/3/whatsnew/3.13.html] 3.13: free-threaded mode is experimental and not enabled by default.
- [verified 2026-11-07 · src: https://docs.python.org/3/whatsnew/3.12.html] 3.12: PEP 695 type parameter syntax (`def max[T](...)`, `type` statement); `distutils` removed (PEP 632).
- [verified 2026-11-07 · src: https://docs.python.org/3/whatsnew/3.11.html] 3.11: `tomllib` (PEP 680) and exception groups with `except*` (PEP 654).
- [verified 2026-11-07 · src: https://docs.python.org/3/whatsnew/3.10.html] 3.10: structural pattern matching (PEP 634) and the `slots` parameter of `@dataclass`.
- [verified 2026-11-07 · src: https://docs.python.org/3/whatsnew/3.4.html] `pathlib` has been in the standard library since 3.4 (PEP 428).

## Tools

- [verified 2026-11-20 · src: https://api.github.com/repos/astral-sh/uv/releases/latest] uv 0.13.9 (2026-11-17).
- [verified 2026-11-07 · src: https://docs.astral.sh/uv/reference/cli/] `uv lock`, `uv sync --locked` (exits non-zero when `uv.lock` would change), `uv run`, `uv tree --outdated` and a top-level `uv audit` exist; the `uv audit` option list was not read.
- [verified 2026-11-07 · src: https://docs.astral.sh/uv/concepts/projects/init/] `uv init` defaults to `build-backend = "uv_build"`; `--build-backend hatchling` is the alternative.
- [verified 2026-11-07 · src: https://docs.astral.sh/uv/concepts/projects/dependencies/] uv uses the `[dependency-groups]` table (PEP 735) and includes the `dev` group by default in `uv run` and `uv sync`.
- [verified 2026-11-20 · src: https://api.github.com/repos/astral-sh/ruff/releases/latest] ruff 0.17.6 (2026-11-19).
- [verified 2026-11-07 · src: https://docs.astral.sh/ruff/rules/] ruff ships pyupgrade (UP), flake8-bugbear (B) and flake8-bandit (S); `lint.select` takes rule codes or prefixes.
- [verified 2026-11-07 · src: https://pypi.org/pypi/pytest/json] pytest 9.2.0 (changelog 2026-10-27, requires Python >= 3.10); pytest-cov 7.1.0 (its PyPI page).
- [verified 2026-11-07 · src: https://pytest-cov.readthedocs.io/en/latest/config.html] `--cov-fail-under=MIN` fails the run when total coverage is below MIN.
- [verified 2026-11-07 · src: https://pypi.org/pypi/mypy/json] mypy 2.4.1 (requires Python >= 3.10); pyright 1.1.414 on PyPI (GitHub release not cross-checked).
- [verified 2026-11-07 · src: https://api.github.com/repos/astral-sh/ty/releases] ty 0.0.99 (2026-11-06) is still beta per its README; no stable release.
- [verified 2026-11-07 · src: https://api.github.com/repos/pypa/pip-audit/releases/latest] pip-audit v2.10.1 (2026-06-10).

## Packaging

- [verified 2026-11-07 · src: https://packaging.python.org/en/latest/specifications/pyproject-toml/] `pyproject.toml` defines four tables: `[build-system]`, `[project]` (PEP 621), `[dependency-groups]`, `[tool]`.
- [verified 2026-11-07 · src: https://packaging.python.org/en/latest/specifications/dependency-groups/] `[dependency-groups]` (PEP 735, 2024-10) must not be included in built distributions.

## Home Assistant

- [verified 2026-11-07 · src: https://raw.githubusercontent.com/home-assistant/core/master/pyproject.toml] Home Assistant Core 2026.11.0 requires Python >= 3.14.2.
- [verified 2026-11-07 · src: https://api.github.com/repos/home-assistant/actions/git/refs/heads] hassfest runs as `home-assistant/actions/hassfest@master`; `master` is 86d4564712fa02543c808e3a693dd04f9d3f8361 today (pin it in your own workflow and let Dependabot move it).
- [verified 2026-11-07 · src: https://www.hacs.xyz/docs/publish/action/] HACS validation runs as `hacs/action@main` with a `category` input (integration, plugin, theme, …); the last tagged release is 22.5.0 (2022-05-28), so `main` is the de-facto ref.
