# Python — minimal CI job

One job: `uv sync --locked`, ruff format and check, the type checker, pytest with the 85 %
coverage gate, `uv audit`.

- [verified 2026-11-07 · src: https://api.github.com/repos/actions/setup-python/git/ref/tags/v7.1.0] actions/setup-python v7.1.0 = `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`
- [verified 2026-11-07 · src: https://api.github.com/repos/astral-sh/setup-uv/git/ref/tags/v10.3.3] astral-sh/setup-uv v10.3.3 = `68559e99cc807c1eb7e9238fd43a15bba460eec2`; no floating `v10` tag exists, pin the SHA.
- [verified 2026-11-07 · src: https://github.com/astral-sh/setup-uv/blob/main/README.md] setup-uv has `enable-cache` (`true`, `false`, `auto`; default `auto`).
- [verified 2026-11-06 · src: https://github.com/actions/checkout/releases/tag/v7.0.1] actions/checkout v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`

SHAs resolved with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` (annotated tags dereferenced).

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  python:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with:
          enable-cache: true
          # reads .python-version or requires-python; add `python-version:` to pin a line
      - run: uv sync --locked
      - run: uv run ruff format --check .
      - run: uv run ruff check .
      - run: uv run mypy .
      - run: uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=85
      - run: uv audit
```

Notes

- PRs run the full pytest: no dependency-aware selector is verified for Python, and a path
  filter is not a test selector; the suite is small enough in the owner's repositories.
- `setup-uv` installs the interpreter uv needs; `actions/setup-python` is only for workflows
  that call `python` without uv.
- A matrix over Python lines is worth it only for a published library; an application tests the
  line it deploys.
- Home Assistant components: a second job with `home-assistant/actions/hassfest@<sha>` and
  `hacs/action@<sha>` with `category: integration`; both upstreams publish branch refs, so pin
  the commit and let Dependabot (`github-actions`) move it.
