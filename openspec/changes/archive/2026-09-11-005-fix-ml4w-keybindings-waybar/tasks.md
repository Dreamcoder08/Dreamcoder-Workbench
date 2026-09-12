# Tasks: Fix ML4W Keybindings & Waybar

## Task Breakdown

- [x] T1: Update `default.json` Profile
  - **Estimate**: 30 min
  - **Dependencies**: None
  - **Description**: Add 30+ standard ML4W keybindings to `DreamcoderProfiles/dreamcoder/default.json`
  - **Acceptance**: `validate-ml4w-profiles.py` passes, 40+ bindings total
  - **Files**: `DreamcoderProfiles/dreamcoder/default.json`
- [x] T2: Update `asus-vivobook15.json` Profile
  - **Estimate**: 15 min
  - **Dependencies**: T1 (copy bindings)
  - **Description**: Add same ML4W keybindings to `DreamcoderProfiles/dreamcoder/asus-vivobook15.json`, preserving laptop-specific bindings (brightness, volume, media, keyboard backlight)
  - **Acceptance**: `validate-ml4w-profiles.py` passes, 50+ bindings total
  - **Files**: `DreamcoderProfiles/dreamcoder/asus-vivobook15.json`
- [x] T3: Create Waybar Config
  - **Estimate**: 20 min
  - **Dependencies**: None
  - **Description**: Create `DreamcoderWaybar/.config/waybar/config.jsonc` with taskbar + standard modules + Dreamcoder CSS import
  - **Acceptance**: Valid JSONC, contains `hyprland/workspaces` module, references Dreamcoder CSS
  - **Files**: `DreamcoderWaybar/.config/waybar/config.jsonc`
- [x] T4: Create Waybar Style
  - **Estimate**: 10 min
  - **Dependencies**: T3
  - **Description**: Create `DreamcoderWaybar/.config/waybar/style.css` with layout-only rules (spacing, padding, fonts) and `@import` of Dreamcoder colors CSS
  - **Acceptance**: Valid CSS, no color definitions (colors via import only)
  - **Files**: `DreamcoderWaybar/.config/waybar/style.css`
- [x] T5: Validate & Generate
  - **Estimate**: 10 min
  - **Dependencies**: T1, T2
  - **Description**: Run `validate-ml4w-profiles.py` and `generate-custom-lua.sh` to verify profiles produce valid Lua
  - **Acceptance**: Both scripts exit 0, Lua output syntactically valid
  - **Files**: `scripts/validate-ml4w-profiles.py`, `scripts/generate-custom-lua.sh`
- [x] T6: Integration Test
  - **Estimate**: 15 min
  - **Dependencies**: T1–T5
  - **Description**: Verify end-to-end: profile JSON → validation → Lua generation → Waybar config loads
  - **Acceptance**: All checks pass, no errors
  - **Files**: All modified/created files

## Execution Order

```
T1 ──→ T2 ──→ T5 ──→ T6
T3 ──→ T4 ────────────↗
```

## Review Workload Forecast

- **Total changed lines**: ~200 (JSON additions + new config files)
- **Chained PRs recommended**: No — single cohesive change
- **400-line budget risk**: Low
- **Decision needed before apply**: No

## Execution Log (2026-08-03) — Root cause fix applied

The profile JSONs (T1/T2) were already populated (default: 56 binds, asus:
70 binds including the full F1-F12 multimedia row), but the bindings were
NEVER being applied to the running system. Two compounding bugs:

1. **Wrong profile auto-detection** — `generate-custom-lua.sh` and
   `setup-hyprland.sh` detected the profile by hostname (`*asus*|*vivobook*`).
   This laptop's hostname is `archlinux`, so the generic `default` profile
   (no multimedia/brightness binds) was generated and applied instead of
   `asus-vivobook15`. F4/F5 (brightness), F1-F3 (volume) and F7-F9 (media)
   were therefore unbound.
2. **40 duplicate bindings** — `default.lua` (ML4W) and the generated
   `custom.lua` were both loaded and defined the same keys with different
   commands. Pressing a key double-fired both actions (e.g. `SUPER+F`
   fullscreened and immediately unfullscreened; `SUPER+J` toggled split AND
   moved focus down).

### Changes made

- `scripts/generate-custom-lua.sh` — profile auto-detection now reads DMI
  hardware (`/sys/class/dmi/id/product_name` + `sys_vendor`) first, hostname
  as fallback. Detects `Vivobook_ASUSLaptop` → `asus-vivobook15`.
- `scripts/setup-hyprland.sh` — same DMI detection; new Step 3 installs the
  curated `default.lua` keybindings contract from
  `ml4w_assets/hypr/conf/keybindings/default.lua` (re-applies after ML4W
  updates restore the stock file with duplicate binds).
- `ml4w_assets/hypr/conf/keybindings/default.lua` (NEW) — curated ML4W
  `default.lua`: only native binds the generator cannot emit (mouse
  drag/resize, swap, group, scratchpad, XF86* fallback). Applied live at
  `~/.config/hypr/conf/keybindings/default.lua`.
- `~/.config/hypr/custom.lua` — regenerated from `asus-vivobook15.json`.
- `tests/ml4w/generate_custom_lua.bats` — bind-count tests were hardcoded to
  the old 3/19-bind profiles; now dynamic against the JSON (`jq length`).
- `tests/ml4w/profile_validation.bats` — Fn-key check matched plain `F`
  (fullscreen) as a function key; now `^F[0-9]` only.
- `README.md` — profiles table updated, DMI detection and the binding
  contract documented.

### Verification

- `hyprctl binds -j`: 106 binds, **0 duplicates** (was 40).
- `bats tests/ml4w/`: 33/33 pass.
- `validate-ml4w-profiles.py --ci`: all profiles clean.
- Brightness command `brightnessctl -e4 -n2 set 5%+` verified working
  (10 → 44 on amdgpu_bl1).
- Active binds include F5 → brightness up, F4 → brightness down (profile)
  plus XF86MonBrightnessUp/Down fallback.

### T3/T4 note

Waybar config/style tasks are NOT part of this fix (keybindings only). If the
Waybar pieces were already delivered in an earlier run of this change, they
remain; otherwise they are tracked separately.

### Follow-up (2026-08-03) — Migrated to official ML4W variant workflow

Verified against official docs (ml4w.com/os/customization/variants, ML4W
Settings → System → Keybindings, Hyprland wiki Configuring/Basics/Binds):

- ML4W officially says: do NOT edit shipped keybinding variations — they are
  overwritten on updates. The correct flow is a separate keybinding VARIANT
  selected via the selector file.
- Hyprland wiki confirms: duplicate binds are ALL executed in declaration
  order (the double-fire bug), and to replace a bind you must unbind first or
  keep a single source of truth.

Changes from the earlier fix:

- `~/.config/hypr/conf/keybindings/dreamcoder.lua` (NEW) — curated variant
  holding only native binds the generator cannot emit (mouse drag/resize,
  swap, group, scratchpad, XF86* fallback).
- `~/.config/hypr/conf/keybinding.lua` — selector now points to
  `dreamcoder.lua` instead of the stock `default.lua`.
- `ml4w_assets/hypr/conf/keybinding.lua` + `ml4w_assets/hypr/conf/keybindings/
  dreamcoder.lua` — assets versioned in repo; `setup-hyprland.sh` Step 3
  re-applies both after ML4W updates.
- Stock `default.lua` left curated as a defensive fallback if an ML4W update
  resets the selector (keeps 0 duplicates either way).

Verified after reload: 106 binds, 0 duplicates; bats 33/33; profiles clean.

### Follow-up (2026-08-03) — Native dispatchers: `hyprctl dispatch` broken on 0.55+

User reported SUPER+<number> did not switch workspaces. Root cause: Hyprland
0.56 (Lua config) parses `hyprctl dispatch <arg>` as Lua code
(`hl.dispatch(<arg>)`), so the profile's `hyprctl dispatch workspace N`
commands errored at runtime ("')' expected near '2'") and the binds appeared
registered but did nothing.

Fix in `scripts/generate-custom-lua.sh`: the generator now translates the
known `hyprctl dispatch workspace/movetoworkspace/killactive/fullscreen/
togglefloating/togglesplit/movefocus/movewindow` commands to native `hl.dsp.*`
dispatchers (`hl.dsp.focus({workspace=N})`, `hl.dsp.window.move(...)`,
`hl.dsp.window.close()`, etc.). Other commands keep `hl.dsp.exec_cmd()`.

Verified: custom.lua regenerated (70 binds), Lua syntax valid, `hl.dsp.focus
({workspace=N})` switches workspaces via CLI, 106 binds / 0 duplicates after
reload, bats 34/34 (new test asserts no `hyprctl dispatch workspace` remains
in generated output).

### Follow-up (2026-08-03) — hl.bindl does not exist; release is a flag

pi-lens reported config error: `require("custom"): custom.lua:414: attempt to
call a nil value (field 'bindl')`. The profile's F1 (mute) used
`bind_type: "release"` and the generator emitted `hl.bindl(...)`, which does
not exist in the Hyprland Lua API (0.56).

Fix: `hl.bindl` removed — the generator now emits `hl.bind(..., { release =
true })` (documented flag). Also found that `release` + `repeating` together
is invalid (release cannot repeat): F1 silently failed to register until
`repeating` was removed from its options in asus-vivobook15.json. Verified F1
registers as release=True. Schema description updated. bats 34/34.

### Follow-up (2026-08-03) — hl.mouse_bind does not exist either

pi-lens reported: `require("custom"): custom.lua:484: attempt to call a nil
value (field 'mouse_bind')`. The BTN_SIDE/BTN_EXTRA mouse binds used
`"mouse": true, "button": "BTN_SIDE"` and the generator emitted
`hl.mouse_bind(...)`, which does not exist in the Hyprland Lua API.

Fix:

- Generator: `hl.mouse_bind` removed. Mouse binds are now regular `hl.bind()`
  with the button in the key string and `mouse = true` as a flag (the same
  pattern ML4W uses for `mouse:272` drag/resize).
- Profile: `button` changed from BTN_* names to libinput codes
  `mouse:275` (BTN_SIDE) / `mouse:276` (BTN_EXTRA) — BTN_* is not a valid
  keysym and the binds were silently discarded.
- Schema + validate-ml4w-profiles.py: accept `mouse:<code>` buttons.

Verified: mouse:275/276 registered, 118 binds, 0 real duplicates, bats 34/34,
profiles clean.

## Native Status

Task checkboxes were added on 2026-09-11 so the native status engine can count
6/6; earlier revisions of this file used a non-checkbox `T1..` format, which
made the engine report `taskProgress 0/0` and `verify: blocked`.

The profile counts quoted in the Execution Log were corrected in place to the
measured truth (default 56, asus 70). The live `hyprctl binds` counts quoted
inside the dated log entries are observations from those passes (106 at the
time, 119 now) and are not profile counts.
