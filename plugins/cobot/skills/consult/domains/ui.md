# Consult: ui

Paths below start at the plugin root your prompt names.

Read-only. Change nothing, commit nothing, run no formatter or build. Read the sibling skill
`skills/expert-ui/SKILL.md` and its references first: they are the baseline and carry the status of
every fact. The argument narrows the audit to one path.

## Procedure

1. **Inventory.** Stylesheets (`*.css`, `*.scss`, Tailwind config and `@theme` blocks), token
   files (`*.tokens.json`, `tokens.json`), components (`*.tsx`, `*.jsx`, `*.vue`, `*.svelte`),
   pages and templates, theme folders (`config.json`, `skin/`). Name the device profile per
   surface (`web-desktop`, `web-mobile`, `handheld-640x480-dpad`); a theme folder is the
   handheld profile.
2. **Contrast, computed.** Collect text/background and component/background pairs from the
   stylesheet or the tokens (resolve custom properties to their hex values). Run the WCAG formula
   with `jq` (on the read list) once, every pair in `pairs`, never estimate; a `for` loop or a
   shell function around it is off the read list and asks:

   ```bash
   jq -rn --argjson pairs '[["777777","ffffff"],["00aa00","ffffff"]]' '
     def chan($h): ($h | ascii_downcase | explode
       | map(if . >= 97 then . - 87 else . - 48 end) | .[0] * 16 + .[1]) / 255;
     def lin: if . <= 0.04045 then . / 12.92 else pow((. + 0.055) / 1.055; 2.4) end;
     def lum($c): 0.2126 * (chan($c[0:2]) | lin) + 0.7152 * (chan($c[2:4]) | lin)
       + 0.0722 * (chan($c[4:6]) | lin);
     $pairs[] | . as [$fg, $bg]
     | "\($fg) on \($bg): \([lum($fg), lum($bg)] | (max + 0.05) / (min + 0.05) | . * 100 | round / 100)"'
   ```

   Reference values: `#777777` on `#ffffff` = 4.48 (fails 1.4.3 by 0.02; `#767676` passes at
   4.54), `#00aa00` on `#ffffff` = 3.11 (passes only as large text or a component edge). Report
   the ratio to two decimals with both colours and the selector.
3. **Focus and keyboard.** `outline: none` or `outline: 0` without a `:focus-visible` rule of
   equal visibility; click handlers on non-interactive elements; `tabindex` above 0; dialogs and
   sticky bars that can cover the focused element (2.4.11); menus and tooltips opened by hover
   only; custom controls without a keyboard path (2.1.1).
4. **Targets, reflow, spacing.** Interactive elements under 24×24 CSS px (2.5.8) or under 44–48
   px on the mobile profile; fixed widths or `overflow-x` that break at 320 px (1.4.10);
   `px` type sizes and `line-height` in `px` that break 1.4.12 and 1.4.4; `100vh` on mobile.
5. **Preferences and meaning.** No `prefers-reduced-motion` guard around animation; no
   `color-scheme` or `prefers-color-scheme` handling where a dark theme exists; `light-dark()`
   without `color-scheme: light dark`; status by colour alone; text rendered in images;
   placeholders used as labels; `aria-*` contradicting native semantics; more than one `h1`.
6. **Tokens.** Raw colours, sizes or durations in components beside a token system; the same
   value under two names; dark mode as inverted colours rather than mode values; generated
   output edited by hand (differs from what the token file would produce).
7. **Handheld profile** (theme folders): text below 18 px (list items below 25), missing or
   subtle `selectedcolor`, icon pairs with a missing `-f` or `-n` file, assets outside the 16 px
   safe margin, a preview that is not 480×360, background music not 48 kHz mp3, fonts bundled
   instead of referenced from `/mnt/SDCARD/miyoo/app/`. Sizes come from `file` or `identify`
   on the PNGs when available, else from the config.
8. **Rank.** HIGH: a 1.4.3 or 2.1.1 failure on a primary path, an unreadable handheld text size;
   MEDIUM: 2.5.8, 2.4.11, 1.4.10, missing preference handling; LOW: token drift, hygiene.
   Merge duplicates across files into one finding with every location.

## Report

```text
scope: <paths read, profiles, pairs computed, tools run or absent>

findings:
1. <HIGH|MEDIUM|LOW> · <criterion, e.g. 1.4.3> · <file>:<line> · <selector or component> · <what, with the computed ratio or size> · fix: <concrete change, with the passing value>
…

accepted / not applicable: <shape-based exclusions, e.g. no touch targets on a D-pad device>

not covered: <files not read, pairs not resolvable (runtime colours), tools absent>

knowledge_delta (optional, JSON, only facts verified during the audit and absent from the references):
{"topic": "ui", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

Never report a finding you did not anchor to a file and line; never report the absence of a
feature the profile does not call for; never fix anything. The orchestrator decides what becomes
a task.
