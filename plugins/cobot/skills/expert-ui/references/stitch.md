# Google Stitch through MCP (decision 27, ADR-0005)

Every line here is `reported` until the owner's first live call turns it `verified`: Google's
documentation pages are JavaScript-rendered and return only a title to a fetch.

## What is established

- [verified 2026-11-08 · src: https://raw.githubusercontent.com/gemini-cli-extensions/stitch/main/gemini-extension.json] Google's own Gemini CLI extension registers an MCP server `stitch` at `https://stitch.googleapis.com/mcp` (HTTP transport) with the header `X-Goog-Api-Key`, timeout 300 s.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/gemini-cli-extensions/stitch/main/README.md] Auth: an API key, or Application Default Credentials after `gcloud beta services mcp enable stitch.googleapis.com`; the README says the MCP is free of charge; capabilities: list projects, project details, retrieve screens, download assets (images, HTML), generate a screen from text.
- [verified 2026-11-08 · src: https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch] The API key is created from the profile picture → Stitch settings → API key → Create key.

## Reported (third-party write-ups and forum posts)

- [reported 2026-11-08 · src: https://discuss.ai.google.dev/t/mcp-generate-screen-from-text-rejects-all-credentials-api-key-and-oauth-both-fail-management-tools-work/174160] Tool names seen in use: `list_projects`, `create_project`, `list_screens`, `get_screen`, `generate_screen_from_text`.
- [reported 2026-11-08 · src: https://sotaaz.com/post/stitch-mcp-api-en] `generate_screen_from_text` takes `project_id`, `prompt`, `model_id` (`GEMINI_3_PRO` or `GEMINI_3_FLASH`); quota reported as 350 standard and 50 experimental generations per month.
- [reported 2026-11-08 · src: https://justinmckelvey.com/blog/google-stitch-mcp] On 2026-09-25 the server listed 15 tools (projects, screens, design systems); generate and edit calls take minutes; no export-to-React or Flutter tool.
- [reported 2026-11-08 · src: https://mcpservers.org/en/servers/kargatharaakash/stitch-mcp] `get_screen` returns HTML, a screenshot and a Figma export.

## How the cobot uses it

The owner registers the server at user scope; the plugin never ships it (the key and the quota
are the owner's):

```bash
claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: YOUR-API-KEY" -s user
```

The gate's default layer asks on `mcp__*__generate*` and `mcp__*__edit*` whatever the server is
named; list and get tools are silent. Sequence: `list_projects` → pick or `create_project`
(asks) → `generate_screen_from_text` with the brief (asks, minutes) → `get_screen` → adapt the
HTML into the repository's component system with the tokens; the generated markup is a sketch,
not code to ship. When the first live call succeeds, re-date these lines to `verified` through
`/cobot:learn ui` with `exp:` sources.
