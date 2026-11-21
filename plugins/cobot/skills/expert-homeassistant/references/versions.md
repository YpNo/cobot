# Home Assistant — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale expert-homeassistant`).

## Releases and validators

- [verified 2026-11-21 · src: exp: gh api 'repos/home-assistant/core/contents/pyproject.toml?ref=2026.11.0' (requires-python = ">=3.14.2")] Home Assistant Core 2026.11.0 requires Python >= 3.14.2.
- [verified 2026-11-21 · src: exp: gh api repos/home-assistant/core/releases/latest; gh api 'repos/home-assistant/core/contents/pyproject.toml?ref=2026.11.2'] The latest stable Home Assistant Core is 2026.11.2 (published 2026-11-16); its pyproject.toml has requires-python >=3.14.2 and homeassistant/const.py has REQUIRED_PYTHON_VER (3, 14, 2).
- [verified 2026-11-21 · src: https://github.com/home-assistant-ecosystem/home-assistant-cli/releases/tag/1.0.0] hass-cli 1.0.0 (2026-04-12) is the latest release; the repository is not archived and was last pushed 2026-11-17 (exp: gh api repos/home-assistant-ecosystem/home-assistant-cli).
- [verified 2026-11-21 · src: exp: gh api repos/home-assistant/actions/commits/master; gh api repos/home-assistant/actions/releases; https://github.com/home-assistant/actions/blob/master/README.md] hassfest runs as `home-assistant/actions/hassfest@master` (the README ref); `master` is 07f46fd2e19967768b5fd3000f91f857452b767c today, which is also tag 2026.11.0 (released 2026-11-19), so pin that SHA in your own workflow and let Dependabot move it.
- [verified 2026-11-21 · src: exp: gh api repos/hacs/action/releases/latest; https://hacs.xyz/docs/publish/action/] HACS validation runs as `hacs/action@main` with a `category` input (integration, plugin, theme, …); the last tagged release is 22.5.0 (2022-05-28), so `main` is the de-facto ref.
- [verified 2026-11-21 · src: exp: gh api repos/hacs/action/commits/main; gh api repos/hacs/action/contents/action.yml; https://hacs.xyz/docs/publish/action/] hacs/action `main` is 1ebf01c408f29afcb6406bd431bc98fd8cbb15aa today (last commit 2026-06-08); `category` is required and takes appdaemon, integration, plugin, python_script, template or theme; HACS docs say to pin the ref after `@` and let Dependabot update it.
