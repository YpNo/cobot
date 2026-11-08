# ui — knowledge (project scope: research delta for expert-ui, gathered 2026-11-08)

Format: `- [status date · src: url] claim`. Status `verified` = primary source read that day; `reported` = secondary; `derived` = computed from verified figures.

## WCAG 2.2 and 3.0

- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] WCAG 2.2 is a W3C Recommendation dated 12 December 2024 (current edition of the TR page).
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.3 Contrast (Minimum), AA: text and images of text 4.5:1; large text (18 pt, or 14 pt bold) 3:1.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.11 Non-text Contrast, AA: UI components and graphical objects needed to understand content 3:1 against adjacent colours.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 2.5.8 Target Size (Minimum), AA, new in 2.2: pointer targets at least 24×24 CSS px, with exceptions for spacing (a 24 px circle centred on each target must not intersect another target), equivalent control, inline text targets, user-agent sizing, essential presentation.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html] 2.4.11 Focus Not Obscured (Minimum), AA, new in 2.2: a focused component is not entirely hidden by author-created content; 2.4.12 (Enhanced) is AAA.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 2.4.7 Focus Visible, AA: any keyboard-operable UI has a mode where the focus indicator is visible.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html] 2.4.13 Focus Appearance is AAA: indicator area at least a 2 CSS px perimeter of the component, 3:1 change between focused and unfocused pixels.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.10 Reflow, AA: no two-dimensional scrolling at 320 CSS px width (vertical scroll) or 256 CSS px height (horizontal scroll).
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.12 Text Spacing, AA: no loss of content with line height 1.5× font size, paragraph spacing 2×, letter spacing 0.12×, word spacing 0.16×.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 2.1.1 Keyboard, A: all functionality operable through a keyboard interface without specific timings, except path-dependent input.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 3.3.7 Redundant Entry, A, new in 2.2: information entered earlier in the same process is auto-populated or selectable, except when essential, required for security, or no longer valid.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 3.3.8 Accessible Authentication (Minimum), AA, new in 2.2: no cognitive function test in authentication unless an alternative, an assist mechanism (password manager, paste), object recognition or personal-content identification is provided.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] WCAG 2.2 removed 4.1.1 Parsing (obsolete).
- [verified 2026-11-08 · src: https://www.w3.org/TR/wcag-3.0/] WCAG 3.0 is a W3C Working Draft; current draft dated 10 September 2026.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html] WCAG sets no minimum font size; 1.4.4 Resize Text (AA) requires text resizable to 200 % without loss of content or function.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html] 1.4.8 Visual Presentation (AAA) caps line width at 80 characters (40 CJK).

## Design tokens

- [verified 2026-11-08 · src: https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/] The Design Tokens Community Group published the first stable Design Tokens specification, 2025.10, on 28 October 2025; reference implementations named: Style Dictionary, Tokens Studio, Terrazzo.
- [verified 2026-11-08 · src: https://www.designtokens.org/tr/2025.10/format/] "Design Tokens Format Module 2025.10" is a Final Community Group Report dated 28 October 2025; recommended extensions `.tokens` and `.tokens.json`; MIME `application/design-tokens+json`.
- [verified 2026-11-08 · src: https://www.designtokens.org/tr/2025.10/format/] An object with a `$value` property is a token; `$type` is optional on a token and inherited from a group; `$description` and `$extensions` optional; `$deprecated`, `$root`, `$extends`, `$ref` reserved.
- [verified 2026-11-08 · src: https://registry.npmjs.org/style-dictionary/latest] Style Dictionary 5.8.0 is latest on npm (GitHub release 2026-11-03).
- [verified 2026-11-08 · src: https://styledictionary.com/info/dtcg/] Style Dictionary has first-class DTCG support since v4; full support for the 2025.10 format is still a work in progress in v5.

## Component systems and CSS features

- [verified 2026-11-08 · src: https://android-developers.googleblog.com/2025/05/the-android-show-io-edition.html] Material 3 Expressive was announced 13 May 2025 as an expansion of Material 3 (components, motion-physics system, type styles, colours, shapes), shipping to Android 16 and Wear OS 6.
- [reported 2026-11-08 · src: https://android-developers.googleblog.com/2025/05/the-android-show-io-edition.html] Google frames M3 Expressive as an update to Material 3, not a Material 4 (the m3.material.io blog is JS-rendered and unreadable for a fetch).
- [verified 2026-11-08 · src: https://registry.npmjs.org/shadcn/latest] shadcn CLI 4.23.0 is latest on npm (GitHub release 2026-10-27).
- [verified 2026-11-08 · src: https://ui.shadcn.com/docs/tailwind-v4] shadcn/ui supports Tailwind v4 and React 19; every primitive has a `data-slot` attribute; `forwardRef` removed; `default` style deprecated for `new-york`; Tailwind v3 / React 18 apps still work.
- [verified 2026-11-08 · src: https://ui.shadcn.com/docs/changelog] shadcn milestones: React 19 (Oct 2024), Tailwind v4 (Feb 2025), CLI 3.0 + MCP server (Aug 2025), unified Radix UI package (Feb 2026), CLI v4 (Mar 2026), Base UI as the default (Jul 2026), `cn` extracted (Sep 2026).
- [verified 2026-11-08 · src: https://registry.npmjs.org/radix-ui] Unified `radix-ui` package 1.8.1 (published 2026-10-12).
- [verified 2026-11-08 · src: https://www.radix-ui.com/primitives/docs/overview/releases] Radix Primitives release notes dated 20 July 2026: per-primitive subpath imports (`radix-ui/accordion`), tree-shaking improvements, React 19.2 fixes.
- [verified 2026-11-08 · src: https://registry.npmjs.org/tailwindcss/latest] Tailwind CSS 4.3.5 is latest on npm (GitHub release 2026-11-06).
- [verified 2026-11-08 · src: https://tailwindcss.com/blog/tailwindcss-v4] Tailwind CSS v4.0 shipped 22 January 2025 with CSS-first configuration (`@import "tailwindcss"` + `@theme` emitting CSS custom properties).
- [verified 2026-11-08 · src: https://tailwindcss.com/docs/compatibility] Tailwind v4 core requires Chrome 111, Safari 16.4, Firefox 128.
- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion] `prefers-reduced-motion` is Baseline Widely available (since January 2020); values `no-preference`, `reduce`.
- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme] `prefers-color-scheme` is Baseline Widely available (since January 2020).
- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme] `color-scheme` is Baseline Widely available (since January 2022); values `normal`, `light`, `dark`, `only`.
- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark] `light-dark()` is Baseline 2024 Newly available (since May 2024); requires `color-scheme: light dark`.

## Typography and layout

- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/font-size] The browser default `font-size` is usually 16 px (1rem = 16px by default); MDN advises relative units because the default is user-adjustable.
- [verified 2026-11-08 · src: https://practicaltypography.com/point-size.html] Butterick's Practical Typography: body text 15–25 px on the web, 10–12 pt in print.
- [verified 2026-11-08 · src: https://practicaltypography.com/line-length.html] Butterick: 45–90 characters per line including spaces.
- [verified 2026-11-08 · src: https://developer.apple.com/design/human-interface-guidelines/accessibility] Apple HIG: default control size iOS/iPadOS/watchOS 44×44 pt, platform minimum 28×28 pt; macOS 28/20; tvOS 66/56; visionOS 60/28; default type 17 pt (iOS), minimum 11 pt; support text at 200 %.
- [verified 2026-11-08 · src: https://developer.android.com/guide/topics/ui/accessibility/apps] Android/Material: interactive elements at least 48×48 dp; text under 18 sp (or bold under 14 sp) 4.5:1, other text 3:1.
- [verified 2026-11-08 · src: https://support.google.com/accessibility/android/answer/7101858] Touch targets at least 48×48 dp separated by 8 dp or more.
- [verified 2026-11-08 · src: https://developer.android.com/design/ui/mobile/guides/layout-and-content/grids-and-units] Android UI uses an 8 dp grid for layout, components and spacing; icons, type and small elements align to a 4 dp grid; 1 dp = 1 px at 160 dpi.

## Miyoo Mini Plus and OnionOS

- [reported 2026-11-08 · src: https://www.ifixit.com/Device/RetroMini_Miyoo_Mini_Plus] Miyoo Mini Plus: 3.5-inch IPS 640×480, dual-core Cortex-A7 1.2 GHz, 128 MB DDR3, 3000 mAh; 15 buttons: D-pad, A/B/X/Y, SELECT, START, L/L2/R/R2 (iFixit page; spec sheets disagree on SoC and RAM).
- [verified 2026-11-08 · src: https://onionui.github.io/docs/4.1/shortcuts] OnionOS buttons: MENU, POWER, SELECT, START, L/R, L2/R2, D-pad, A/B/X/Y; MENU+POWER takes a screenshot; SELECT+L2/R2 brightness; START+L2/R2 volume.
- [verified 2026-11-08 · src: https://onionui.github.io/] Onion is an OS overhaul for Miyoo Mini and Mini+; no touch input is documented anywhere (all interaction is button-driven).
- [verified 2026-11-08 · src: https://api.github.com/repos/OnionUI/Onion/releases?per_page=5] Latest stable OnionOS is v4.3.1-1 (2024-06-24); prerelease v4.4.0-beta-20260120 (2026-01-21).
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/OnionUI/Themes/main/CONTRIBUTING.md] Theme preview is 480×360, made from a 640×480 screenshot (MENU+POWER) resized; background music must be 48 kHz mp3; zip named `[NAME] by [AUTHOR].zip` with one same-named folder or `config.json` at the root; `name` and `author` are separate keys.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/OnionUI/Themes/main/themes/Silky%20by%20DiMo/config.json] Default theme "Silky by DiMo" `config.json` keys: `name`, `author`, `description`, `batteryPercentage` {visible, color, size, offsetX, fixed}, `title`/`hint`/`list` {font, size, color}, `currentpage`/`total` {color}, `grid` {font, grid1x4, grid3x4, color, selectedcolor}; fonts under `/mnt/SDCARD/miyoo/app/`; title/hint/list size 25, grid 25 (1×4) / 18 (3×4), battery 18.
- [verified 2026-11-08 · src: https://api.github.com/repos/OnionUI/Themes/contents/themes/Silky%20by%20DiMo] A theme is `config.json`, `preview.png`, a credits text and `skin/` with 84 PNG assets (`background.png`, `bg-title.png`, `bg-list-*.png`, `bg-pop-menu-*.png`, `ic-*-f/-n.png` icon pairs, `icon-*-48.png`, `icon-*-24.png`, `power-*-icon.png`, `mask-*.png`) plus `extra/`.
- [verified 2026-11-08 · src: https://onionui.github.io/docs/theme-design] Since Onion v4 `skin/extra` holds `bootScreen.png`, `Screen_Off.png`, `Screen_Off_Save.png`, `chargingState0..23.png` (80 ms per frame by default via `chargingState.json`), `lum0..10.png`, toggle images; `Saves/CurrentProfile/theme/skin/extra` overrides any theme; bundled fonts are no longer needed, point `config.json` font paths at `/mnt/SDCARD/miyoo/app/[FONT]`; the Blueprint theme is the layout template.
- [derived 2026-11-08 · from 640×480 at 3.5 in] ≈ 228.6 ppi, 1 px ≈ 0.111 mm: a 16 px glyph ≈ 1.8 mm, 12 px ≈ 1.3 mm, 18 px ≈ 2.0 mm, Silky's 25 px ≈ 2.8 mm; the 480×360 preview is a 0.75× downscale.

## Google Stitch

- [verified 2026-11-08 · src: https://raw.githubusercontent.com/gemini-cli-extensions/stitch/main/gemini-extension.json] Google's Gemini CLI Stitch extension configures an MCP server `stitch` with `httpUrl` `https://stitch.googleapis.com/mcp`, header `X-Goog-Api-Key: YOUR_API_KEY`, timeout 300000 ms; extension 0.1.4.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/gemini-cli-extensions/stitch/main/README.md] Two auth templates: API key, or Application Default Credentials after `gcloud beta services mcp enable stitch.googleapis.com` and `gcloud auth application-default set-quota-project`; the README says the Stitch MCP is free of charge; capabilities: list projects, project details, retrieve screens, download assets (images, HTML), generate screen from text; tool names discoverable with `/mcp list`.
- [verified 2026-11-08 · src: https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch] API key: profile picture → Stitch settings → API key → Create key; the agent extracts palette and typography from a project into a DESIGN.md.
- [reported 2026-11-08 · src: https://discuss.ai.google.dev/t/mcp-generate-screen-from-text-rejects-all-credentials-api-key-and-oauth-both-fail-management-tools-work/174160] Tool names seen in use: `list_projects`, `create_project`, `list_screens`, `get_screen`, `generate_screen_from_text`; OAuth path uses `Authorization: Bearer` + `X-Goog-User-Project`.
- [reported 2026-11-08 · src: https://sotaaz.com/post/stitch-mcp-api-en] `generate_screen_from_text` takes `project_id`, `prompt`, `model_id` (GEMINI_3_PRO or GEMINI_3_FLASH); Claude Code registration: `claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: YOUR-API-KEY" -s user`; quota reported as 350 standard and 50 experimental generations per month, undocumented by Google.
- [reported 2026-11-08 · src: https://justinmckelvey.com/blog/google-stitch-mcp] On 2026-09-25 the server listed 15 tools: four for projects, two reading screens, three generating or editing screens, six for design systems; no export-to-React or Flutter tool; generate and edit calls take minutes.
- [reported 2026-11-08 · src: https://mcpservers.org/en/servers/kargatharaakash/stitch-mcp] `get_screen` takes `projects/{project}/screens/{screen}` and returns HTML, a screenshot and a Figma export (third-party listing).

## unverified

- Material 3 touch-target and 8-dp grid pages on m3.material.io (JS-rendered); Apple HIG "minimum 44 pt" wording (the table says default 44, minimum 28); line length 45–75 (Bringhurst, not fetched); a Miyoo official spec sheet; explicit "no touch" statement; `bgm.mp3` location in a theme; Stitch's official tool list, export targets and quota from Google-owned pages (docs are JS-rendered).
