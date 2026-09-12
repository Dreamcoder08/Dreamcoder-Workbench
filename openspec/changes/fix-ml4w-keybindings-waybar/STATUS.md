# Status: fix-ml4w-keybindings-waybar (verified PASS)

Status: **verified pass** (2026-09-11). Archive-ready after reconciling four
partial requirements. `verify-report.md` holds the full evidence and hashes.

## Delivered and verified

- **Keybindings.** `DreamcoderProfiles/dreamcoder/default.json` carries **56**
  bindings and `asus-vivobook15.json` carries **70**. Modifier sets:
  - default — `SUPER`, `SUPER+SHIFT`, `SUPER+CTRL`, `SUPER+CTRL+SHIFT`,
    `SUPER+ALT`, and a bare `PRINT`.
  - asus — `SUPER`, `SUPER+SHIFT`, `SUPER+CTRL`, `SUPER+CTRL+SHIFT` (no `SUPER+ALT`,
    no bare binding).
- **Waybar configuration.** `DreamcoderWaybar/.config/waybar/config.jsonc` exists
  and parses as JSONC with the expected `modules-left/center/right` layout.
- **`scripts/generate-custom-lua.sh`.** `bash -n` passes; its output passes
  `luac -p` (70 `hl.bind`, 0 `hyprctl dispatch`) and leaves `hyprctl configerrors`
  empty on Hyprland 0.56.2.

## Commands executed this pass

`pytest` 680 passed · `bats tests/ml4w/` 34/34 · `validate-ml4w-profiles.py --ci`
exit 0 · `bash -n` + `luac -p` exit 0 · `ruff` / `mypy` / `shellcheck` /
`verify-theme-health.py` exit 0.

## Partial — reconcile before archiving

- **FR1.5 / FR1.2:** the spec claims `SUPER+L` for hyprlock and `CTRL+SUPER+K`, but
  the shipped chords are `SUPER+ALT+L` and `SUPER+CTRL+SHIFT+K`. The capabilities
  exist; the normative chords were never reconciled.
- **FR2.x:** `style.css` imports `colors.css`, not the `waybar-light.css` /
  `waybar-dark.css` the spec names.
- **NFR3 / NFR5:** unprovable as shipped — no repository script installs
  `DreamcoderWaybar/`, so the Waybar deliverables are dormant templates.

## Corrections to earlier revisions of this note

- The keybinding *count* was first misread from the two keys of the `keybindings`
  object (`super_mod`, `bindings`) instead of the `bindings` array.
- `SUPER+ALT` was claimed for **both** profiles; it exists only in `default`.
- The live `hyprctl binds` count (119) is not the profile count and is not used here.
- `tasks.md` uses a non-checkbox `T1..` format, so the native status engine reports
  `verify: blocked` regardless of content; that is a format artifact, not missing work.
