# Web UI — verified facts and versions

Format: `- [verified|reported YYYY-MM-DD · src: <url>] claim`. Version lines are flagged after 30
days, idiom after 90 (`cobot-memory knowledge --stale expert-ui`).

## Accessibility (WCAG 2.2, Recommendation 12 December 2024)

- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.3 Contrast (Minimum), AA: text 4.5:1; large text (18 pt, or 14 pt bold) 3:1.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.11 Non-text Contrast, AA: UI components and graphical objects 3:1 against adjacent colours.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 2.5.8 Target Size (Minimum), AA, new in 2.2: 24×24 CSS px, with spacing, equivalent-control, inline, user-agent and essential exceptions.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html] 2.4.11 Focus Not Obscured (Minimum), AA, new in 2.2; 2.4.12 is AAA.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 2.4.7 Focus Visible, AA; 2.4.13 Focus Appearance (2 CSS px perimeter, 3:1 change) is AAA.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.10 Reflow, AA: no two-dimensional scrolling at 320 CSS px wide or 256 CSS px high.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 1.4.12 Text Spacing, AA: line height 1.5, paragraph 2, letter 0.12, word 0.16 without loss.
- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] 2.1.1 Keyboard, A; 3.3.7 Redundant Entry, A, and 3.3.8 Accessible Authentication (Minimum), AA, are new in 2.2; 4.1.1 Parsing was removed.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html] WCAG sets no minimum font size; 1.4.4 Resize Text (AA) requires 200 % zoom without loss.
- [verified 2026-11-08 · src: https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html] 1.4.8 (AAA) caps line width at 80 characters (40 CJK).
- [verified 2026-11-08 · src: https://www.w3.org/TR/wcag-3.0/] WCAG 3.0 is a Working Draft (10 September 2026); do not cite it as a requirement.

## Design tokens

- [verified 2026-11-08 · src: https://www.designtokens.org/tr/2025.10/format/] Design Tokens Format Module 2025.10 is the first stable version (Final Community Group Report, 28 October 2025); files `.tokens` or `.tokens.json`; a token is an object with `$value`; `$type` inherits from the group; `$description`, `$extensions`, `$deprecated`, `$root`, `$extends`, `$ref` reserved.
- [verified 2026-11-08 · src: https://registry.npmjs.org/style-dictionary/latest] Style Dictionary 5.8.0 is latest (2026-11-03); DTCG support since v4, full 2025.10 support still in progress in v5 (<https://styledictionary.com/info/dtcg/>).

## Component systems and CSS

- [verified 2026-11-08 · src: https://android-developers.googleblog.com/2025/05/the-android-show-io-edition.html] Material 3 Expressive (13 May 2025) is an expansion of Material 3: components, motion physics, type styles, colours, shapes.
- [verified 2026-11-08 · src: https://registry.npmjs.org/shadcn/latest] shadcn CLI 4.23.0 is latest (2026-10-27); Base UI became the default in July 2026, the unified `radix-ui` package in February 2026 (<https://ui.shadcn.com/docs/changelog>).
- [verified 2026-11-08 · src: https://ui.shadcn.com/docs/tailwind-v4] shadcn/ui on Tailwind v4 and React 19: `data-slot` on every primitive, `forwardRef` removed, `new-york` style; Tailwind v3 / React 18 still work.
- [verified 2026-11-08 · src: https://registry.npmjs.org/radix-ui] `radix-ui` 1.8.1 (2026-10-12); per-primitive subpath imports since the 20 July 2026 release notes.
- [verified 2026-11-08 · src: https://registry.npmjs.org/tailwindcss/latest] Tailwind CSS 4.3.5 is latest (2026-11-06); v4 (22 January 2025) is CSS-first: `@import "tailwindcss"` and `@theme`; requires Chrome 111, Safari 16.4, Firefox 128.
- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion] `prefers-reduced-motion` and `prefers-color-scheme` Baseline Widely available since January 2020; `color-scheme` since January 2022.
- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark] `light-dark()` is Baseline 2024 Newly available (May 2024) and needs `color-scheme: light dark`.

## Type, targets, grid

- [verified 2026-11-08 · src: https://developer.mozilla.org/en-US/docs/Web/CSS/font-size] Browser default `font-size` is usually 16 px (1 rem); use relative units because it is user-adjustable.
- [verified 2026-11-08 · src: https://practicaltypography.com/line-length.html] Butterick: 45–90 characters per line; body text 15–25 px on the web.
- [verified 2026-11-08 · src: https://developer.apple.com/design/human-interface-guidelines/accessibility] Apple HIG: default control 44×44 pt (iOS, iPadOS, watchOS), platform minimum 28×28 pt; default type 17 pt, minimum 11 pt.
- [verified 2026-11-08 · src: https://developer.android.com/guide/topics/ui/accessibility/apps] Android: touch targets ≥ 48×48 dp (8 dp apart per Google accessibility help); 8 dp layout grid, 4 dp for icons and type.
