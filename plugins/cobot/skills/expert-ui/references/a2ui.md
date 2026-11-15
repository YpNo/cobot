# A2UI — agent-driven UI as data

Format: `- [verified|reported YYYY-MM-DD · src: <url>] claim`. Version lines are flagged after 30
days, idiom after 90 (`cobot-memory knowledge --stale expert-ui`). Knowledge only: cobot ships no
A2UI code and adds no dependency.

## Project

- [verified 2026-11-15 · src: https://api.github.com/repos/a2ui-project/a2ui] The repository is `github.com/a2ui-project/a2ui` (`github.com/google/A2UI` redirects there), Apache-2.0, 17 425 stars, last commit on `main` 2026-11-14.
- [verified 2026-11-15 · src: https://api.github.com/repos/a2ui-project/a2ui/community/profile] No GOVERNANCE.md, SECURITY.md or CODE_OF_CONDUCT.md; CONTRIBUTING.md requires the Google CLA; private vulnerability reporting is on; 311 open issues and 172 open pull requests.
- [verified 2026-11-15 · src: https://api.github.com/repos/a2ui-project/a2ui/releases] GitHub's "latest release" is the CLI tag `cli-v0.3.0` (2026-11-11), not a protocol or package release: read package versions from the registries below.

## Protocol

- [verified 2026-11-15 · src: https://a2ui.org/specification/versions.json] v1.0 is `current`, v0.9.1 and v0.9 `previous`, v0.8 `deprecated`; the spec is at <https://a2ui.org/specification/v1.0-a2ui/>.
- [verified 2026-11-15 · src: https://github.com/a2ui-project/a2ui/pull/4044] v1.0 still moves: a breaking change on 2026-11-11 renamed the component envelope keys to `@catalogId`, `@metadata`, `@accessibility`, `@checks`, after the 2026-11-02 npm packages; the spec header's "Last Updated: Jun 8, 2026" is stale.
- [verified 2026-11-15 · src: https://github.com/a2ui-project/a2ui/blob/main/specification/v1_0/docs/a2ui_protocol.md] The agent streams JSON envelopes (`createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface`, `callRendererFunction`, `agentFunctionResponse`); the renderer answers with `action`, `callAgentFunction`, `rendererFunctionResponse`, `error`. Components are a flat list keyed by id with one `root`, bound to a JSON data model by path.
- [verified 2026-11-15 · src: https://github.com/a2ui-project/a2ui/blob/main/specification/v1_0/docs/a2ui_protocol.md] The renderer owns the catalog: it advertises `supportedCatalogIds` (and optional inline catalogs); "Defining your own catalog allows you to restrict the agent to using exactly the components and visual language that exist in your application."
- [verified 2026-11-15 · src: https://github.com/a2ui-project/a2ui/blob/main/specification/v1_0/docs/a2ui_protocol.md] Functions declare `allowedCallers` (`rendererOnly`, `agentOnly`, `rendererOrAgent`) and `requiresUserActivation`; a call to a renderer-only, gesture-gated or unregistered function "MUST" be rejected with `INVALID_FUNCTION_CALL`.
- [verified 2026-11-15 · src: https://github.com/a2ui-project/a2ui/blob/main/README.md] "A2UI expresses UI using _data_, not code" is the README's wording, not the spec's; the spec's security model is the catalog and the function boundary above.
- [verified 2026-11-15 · src: https://github.com/a2ui-project/a2ui/blob/main/specification/v1_0/docs/a2ui_protocol.md] Transport bindings: AG-UI (the standard binding), A2A (an extension), MCP (tool calls, tool outputs, resource subscriptions).

## Packages (pre-1.0: pin exactly)

- [verified 2026-11-15 · src: https://registry.npmjs.org/@a2ui/react] npm, 2026-11-02, Apache-2.0: `@a2ui/web_core` 0.15.0, `@a2ui/react` 0.15.0, `@a2ui/lit` 0.15.0, `@a2ui/angular` 0.14.0 (a minor behind), `@a2ui/agent` 0.1.0; also `@a2ui/markdown-it` 0.2.2 (2026-10-17), `@a2ui/catalog-mcp` 0.0.3 (2026-11-03). The React renderer's CHANGELOG lists unreleased breaking changes after 0.15.0.
- [verified 2026-11-15 · src: https://pypi.org/pypi/a2ui-agent-sdk/json] PyPI, 2026-11-10, Python ≥ 3.10: `a2ui-agent-sdk` 0.11.0, `a2ui-core` 0.6.0, `a2ui-a2a` 0.3.0, `a2ui-adk` 0.3.0.
- [verified 2026-11-15 · src: https://pub.dev/api/packages/a2ui_flutter] pub.dev, 2026-11-11: `a2ui_flutter` 0.3.0, `a2ui_core` 0.7.0, `a2ui_agent` 0.3.0; Swift through SwiftPM from the repository (tag `v0.10.0+swift`).

## Neighbours

- [verified 2026-11-15 · src: https://github.com/modelcontextprotocol/ext-apps] MCP Apps (SEP-1865, stable spec 2026-01-26; `@modelcontextprotocol/ext-apps` 2.0.4 on npm `latest`, 2.1.0 released on GitHub 2026-11-10): an MCP server ships HTML and script in a `ui://` resource that the host renders in a sandboxed iframe. Code, MCP only; A2UI is data the client renders with its own components.
- [verified 2026-11-15 · src: https://github.com/ag-ui-protocol/ag-ui] AG-UI (`@ag-ui/core` 1.0.4, 2026-11-05; MIT): an event protocol between an agent and its front end over SSE, WebSockets or webhooks. A transport, not a UI format; A2UI names it its standard binding.
- [verified 2026-11-15 · src: https://github.com/vercel/ai/blob/main/content/docs/04-ai-sdk-ui/04-generative-user-interfaces.mdx] Vercel AI SDK generative UI (`ai` 7.0.173, 2026-11-13): a tool result mapped to the app's own React components; AI SDK RSC is experimental and the docs recommend AI SDK UI for production. A framework, not a protocol.
