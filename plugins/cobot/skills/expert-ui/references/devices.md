# Constrained devices — Miyoo Mini Plus and OnionOS themes

Profile `handheld-640x480-dpad`. Format as in `web.md`; `derived` lines are computed from the
verified figures beside them.

## Hardware and input

- [reported 2026-11-08 · src: https://www.ifixit.com/Device/RetroMini_Miyoo_Mini_Plus] Miyoo Mini Plus: 3.5-inch IPS 640×480, 15 buttons (D-pad, A/B/X/Y, SELECT, START, L/L2/R/R2, plus MENU and POWER), 3000 mAh; spec sheets disagree on SoC and RAM, so quote none.
- [verified 2026-11-08 · src: https://onionui.github.io/docs/4.1/shortcuts] OnionOS buttons: MENU, POWER, SELECT, START, L/R, L2/R2, D-pad, A/B/X/Y; MENU+POWER screenshot; SELECT+L2/R2 brightness; START+L2/R2 volume.
- [verified 2026-11-08 · src: https://onionui.github.io/] No touch input is documented anywhere in Onion: every interaction is a button press; the focused item is the pointer.
- [derived 2026-11-08 · from 640×480 at 3.5 in] ≈ 229 ppi, 1 px ≈ 0.11 mm: 12 px ≈ 1.3 mm, 16 px ≈ 1.8 mm, 18 px ≈ 2.0 mm, 25 px ≈ 2.8 mm.

## Rules for the profile

1. Fixed canvas 640×480, no reflow: design on the pixel grid, integer scales, no subpixel text.
2. Text ≥ 18 px for anything read at arm's length; ≥ 25 px for list items (Silky's default);
   high-contrast pairs (≥ 7:1) because panels are viewed outdoors.
3. Every action reachable with D-pad plus A (confirm) and B (back); X/Y and L/R only as
   accelerators with an on-screen hint.
4. A visible focus state is mandatory on every selectable item (`selectedcolor`, background pair
   `-f`/`-n` icons); never rely on a subtle tint.
5. 16 px safe margin on every edge; battery and page indicators keep their fixed offsets.
6. Assets by name and size from the theme format; previews are 480×360 (0.75× of a 640×480
   screenshot); background music 48 kHz mp3.

## OnionOS theme format

- [verified 2026-11-08 · src: https://api.github.com/repos/OnionUI/Onion/releases?per_page=5] Latest stable OnionOS is v4.3.1-1 (2024-06-24); v4.4.0-beta-20260120 is a prerelease.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/OnionUI/Themes/main/CONTRIBUTING.md] A theme zip is `[NAME] by [AUTHOR].zip` with one same-named folder or `config.json` at the root; `preview.png` is 480×360 from a MENU+POWER screenshot; background music 48 kHz mp3.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/OnionUI/Themes/main/themes/Silky%20by%20DiMo/config.json] `config.json`: `name`, `author`, `description`, `batteryPercentage` {visible, color, size, offsetX, fixed}, `title`/`hint`/`list` {font, size, color}, `currentpage`/`total` {color}, `grid` {font, grid1x4, grid3x4, color, selectedcolor}; Silky uses size 25 for title, hint and list, 25/18 for the grids, 18 for the battery; fonts live under `/mnt/SDCARD/miyoo/app/`.
- [verified 2026-11-08 · src: https://api.github.com/repos/OnionUI/Themes/contents/themes/Silky%20by%20DiMo/skin] `skin/` holds the PNG assets: `background.png`, `bg-title.png`, `bg-list-*.png`, `bg-pop-menu-*.png`, `ic-*-f.png`/`ic-*-n.png` focused/normal icon pairs, `icon-*-48.png`, `icon-*-24.png`, `power-*-icon.png`, `mask-*.png`, and `extra/`.
- [verified 2026-11-08 · src: https://onionui.github.io/docs/theme-design] Since v4, `skin/extra` holds `bootScreen.png`, `Screen_Off.png`, `Screen_Off_Save.png`, `chargingState0..23.png` (80 ms per frame via `chargingState.json`), `lum0..10.png`, toggle images; `Saves/CurrentProfile/theme/skin/extra` overrides any theme; point font paths at `/mnt/SDCARD/miyoo/app/[FONT]`; the Blueprint theme is the layout template.

## Not covered (ask `/cobot:learn ui <question>`)

Exact pixel sizes of each `skin/*.png` (read them from Blueprint or Silky with `file` or
`identify` before drawing), the `bgm.mp3` location, other handhelds (RG35XX, Trimui) and their
firmwares.
