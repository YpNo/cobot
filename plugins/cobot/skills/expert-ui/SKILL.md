---
name: expert-ui
description: >-
  UI/UX design knowledge for web interfaces and for constrained devices such as the Miyoo Mini
  Plus (640×480, D-pad, OnionOS themes), current as of 2026-11-08. Loads when stylesheets,
  components, Tailwind config, token files or theme folders are touched, and when a request asks
  for a screen, layout, theme, token sheet or accessibility fix. Gives WCAG 2.2 AA by criterion,
  the token discipline, the type scale, the component-system choice, device profiles, the brief →
  tokens → screens procedure (Google Stitch under the gate when the owner registered it) and
  pitfalls. Facts and versions live in references/.
paths:
  - "**/*.css"
  - "**/*.scss"
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/tailwind.config.*"
  - "**/*tokens*.json"
  - "**/Themes/**"
  - "**/themes/**"
user-invocable: false
---

# expert-ui

A screen is a contract with a person who cannot see your intent. Design from the person's task
inward: who, on what device, with which input, under which constraints. Quote the status of every
fact you rely on (`references/web.md`, `references/devices.md`, `references/stitch.md`); when a
line is older than its threshold (versions 30 days, idiom 90) or the question falls outside them,
say so and propose `/cobot:learn ui <question>` instead of guessing.

## Non-negotiables (WCAG 2.2 AA unless noted)

1. **Contrast** 1.4.3: text 4.5:1, large text (18 pt, or 14 pt bold) 3:1; 1.4.11: component
   edges, icons and focus rings 3:1 against what surrounds them. Compute, never eyeball: the
   formula is in `skills/consult/domains/ui.md` as one `jq` expression.
2. **Keyboard and focus** 2.1.1: everything works from the keyboard; 2.4.7: focus is visible;
   2.4.11: the focused element is never hidden under sticky bars or dialogs. Style
   `:focus-visible`; `outline: none` only with a replacement of equal visibility.
3. **Targets** 2.5.8: pointer targets ≥ 24×24 CSS px with spacing, 44 pt (Apple) / 48 dp
   (Material) for touch-first surfaces.
4. **Reflow and spacing** 1.4.10: no two-dimensional scrolling at 320 CSS px; 1.4.12: layouts
   survive line height 1.5, paragraph spacing 2, letter spacing 0.12, word spacing 0.16; 1.4.4:
   text zooms to 200 %. Use `rem`, not `px`, for type.
5. **Preferences** honour `prefers-reduced-motion` (no essential information in motion, no
   parallax or autoplay for `reduce`), `prefers-color-scheme` with `color-scheme: light dark`
   on `:root`; `light-dark()` only where Baseline 2024 is acceptable.
6. **Meaning** never carried by colour alone; text as text, not images; one `h1`, landmarks,
   labels bound to controls, `aria-*` only to fix what native semantics cannot express.
7. **Forms** 3.3.7: never ask twice in one process; 3.3.8: no puzzle in authentication, paste and
   password managers allowed.

## Token discipline

- One source of truth in the W3C Design Tokens format (`*.tokens.json`, `$value`, `$type`,
  `$description`), semantic names over raw (`color.text.primary`, not `grey-700`), light and
  dark as modes of the same token, spacing on a 4/8 px grid, a type scale with ≤ 7 steps.
- Build output (CSS custom properties, Tailwind `@theme`, platform constants) is generated
  (Style Dictionary 5 or the framework's own pipeline), never edited by hand.
- A raw colour or size beside a token in a component is a finding, not a style.

## Type and layout scale

Body 16 px (1 rem) by default on the web, 45–90 characters per line, line height 1.4–1.6;
headings from a modular scale (1.2–1.25 ratio); spacing 4, 8, 12, 16, 24, 32, 48, 64; breakpoints
from content, tested at 320, 768, 1024, 1440. Density is a token, not a per-screen decision.

## Component system by stack

The stack decides the framework (`lang-typescript`); the expert decides the system and keeps it
to one: Material 3 (Expressive is an update, not a new version) for Android-adjacent or
Google-flavoured products; shadcn/ui on Radix and Tailwind v4 for React 19 product UI; the
framework's own primitives for Vue or Svelte; plain CSS with tokens when there is no framework.
Versions: `references/web.md`. Never two systems in one surface.

## Device profiles

| profile | input | rules that change |
|---|---|---|
| `web-desktop` | pointer + keyboard | hover is a hint, never the only path; dense tables allowed; 24 px targets |
| `web-mobile` | touch | 44–48 px targets with 8 px gaps; thumb zones; no hover; sheets over dialogs |
| `handheld-640x480-dpad` | D-pad, A/B/X/Y, L/R, no touch, no pointer | `references/devices.md`: 640×480 fixed, 229 ppi, pixel-grid text ≥ 18 px (≈ 2 mm), 16 px safe margin, focus ring is the pointer, every action reachable with D-pad + A/B, OnionOS theme assets by name and size |

## Design procedure

1. **Read** the stack, the existing tokens and components, CONTEXT.md constraints, the device
   profile. A request without a profile gets `web-desktop` + `web-mobile` and says so.
2. **Brief** from `templates/design-brief.md`: users, tasks, device profile, states (empty,
   loading, error, success, offline), constraints, success measure. Five lines each at most.
3. **Tokens**: reuse or extend; `templates/tokens.json` is the skeleton for a new sheet.
4. **Screens**. With Stitch registered by the owner (`mcp__*stitch*` tools present): list the
   project, then `generate_screen_from_text` with the brief; the gate asks before every
   generate or edit call, generation takes minutes and spends the owner's quota; read the result
   back with the get tool and treat it as a sketch to adapt into the repository's component
   system, never pasted as is (`references/stitch.md`). Without Stitch: lay the screen out in
   text (regions in reading order, states, focus order) and build from the component system.
5. **Audit** every screen with the ui consult (`/cobot:consult ui`) before calling it done; findings carry
   the criterion number.

## Pitfalls

- A disabled control with 2:1 contrast is allowed by 1.4.3; a placeholder used as a label is not.
- `aria-label` on a `div` with a click handler is not a button; use `button`.
- `100vh` on mobile hides content behind the browser chrome; use `100dvh`.
- Dark mode by inverting colours breaks contrast; derive it from the same semantic tokens.
- On the handheld, 12–14 px type reads at 1.3–1.5 mm: unreadable at arm's length. Silky, the
  default OnionOS theme, uses 25 px list text and 18 px for the 3×4 grid.
- Hover-only disclosure, infinite scroll without a reachable end, and toasts that vanish before
  a screen reader finishes are the three most common keyboard failures.

- [verified 2026-11-08 · src: https://www.w3.org/TR/WCAG22/] WCAG 2.2 is a W3C Recommendation dated 12 December 2024; the criteria above are quoted from it.
