# Home Assistant — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale expert-homeassistant`).

## Releases and validators

- [verified 2026-11-07 · src: https://raw.githubusercontent.com/home-assistant/core/master/pyproject.toml] Home Assistant Core 2026.11.0 requires Python >= 3.14.2.
- [verified 2026-11-07 · src: https://api.github.com/repos/home-assistant/actions/git/refs/heads] hassfest runs as `home-assistant/actions/hassfest@master`; `master` is 86d4564712fa02543c808e3a693dd04f9d3f8361 today (pin it in your own workflow and let Dependabot move it).
- [verified 2026-11-07 · src: https://www.hacs.xyz/docs/publish/action/] HACS validation runs as `hacs/action@main` with a `category` input (integration, plugin, theme, …); the last tagged release is 22.5.0 (2022-05-28), so `main` is the de-facto ref.
