# Status: fix-ml4w-keybindings-waybar (delivered, one item unverified)

Status: **open — effectively delivered** (updated 2026-09-11).

The proposal's premise — "only 3–19 keybindings, zero CTRL+SUPER, no Waybar
config" — is stale. Both deliverables are in the repository.

## Delivered (verified 2026-09-11)

- **Keybindings expanded.** `DreamcoderProfiles/dreamcoder/default.json` carries
  **56** bindings and `asus-vivobook15.json` carries **70**, against the
  proposal's "50+ bindings / zero CTRL+SUPER" goal. Modifier sets present in both:
  `SUPER`, `SUPER+SHIFT`, `SUPER+CTRL`, `SUPER+CTRL+SHIFT`, `SUPER+ALT`, and a
  bare `PRINT`. `SUPER+CTRL` shortcuts number five per profile.
- **Waybar configuration.** `DreamcoderWaybar/.config/waybar/config.jsonc`
  exists; the proposal said the repository had CSS files only.

> Correction: an earlier revision of this note claimed the keybindings were not
> delivered because it counted the two keys of the `keybindings` object
> (`super_mod`, `bindings`) instead of the `bindings` array. The array holds 56
> and 70 entries.

## Remaining

- Confirm `scripts/generate-custom-lua.sh` still matches current ML4W Lua
  conventions (the proposal's item 5). Not independently verified here.
- `tasks.md` uses a non-checkbox `T1..` format, so it does not report a progress
  ratio; the evidence above comes from the repository.
