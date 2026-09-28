# ML4W Keybindings & Waybar Integration Specification

## Purpose

This change completes the Dreamcoder Workbench ML4W integration on two surfaces.
It adds the standard ML4W application, window-management, workspace, focus and
system-control keybindings to both machine profiles
(`DreamcoderProfiles/dreamcoder/default.json` and
`DreamcoderProfiles/dreamcoder/asus-vivobook15.json`), so a fresh Hyprland
session behaves like a documented ML4W desktop instead of an unbound one. It
also adds the Waybar configuration and layout stylesheet that present the
workspace taskbar and the standard status modules.

The Waybar deliverables are **dormant templates**: `DreamcoderWaybar/` is
versioned in this repository, but no repository script installs it, so nothing
in this change makes Waybar run with it. The active-workspace accent highlight
is also not reachable in the shipped chain — `style.css` imports only
`colors.css`, which declares variables and no accent rule, while the
`#workspaces button.active` accent rule lives in the engine-generated
`DreamcoderThemes/dreamcoder/waybar-{dark,light}.css`, which `style.css`
does not import. The delivered Waybar behavior is therefore the taskbar module
plus `window-rewrite` icon mappings only. Both limitations, plus two further
ones, are recorded non-normatively in `## Known Gaps` and MUST NOT be read as
delivered behavior.

## Requirements

### Requirement: FR1.1 Standard ML4W app launchers

Both profiles MUST bind the five standard ML4W application launchers on the
SUPER modifier: SUPER+RETURN MUST launch Kitty, SUPER+B MUST launch Firefox,
SUPER+E MUST launch Thunar, SUPER+SPACE MUST launch the Rofi drun launcher
(`rofi -show drun`), and SUPER+V MUST launch the clipboard history pipeline
(`cliphist list | rofi -dmenu | cliphist decode | wl-copy`). These bindings MUST
use only existing profile schema fields and MUST be present in `default.json`
and `asus-vivobook15.json` alike.

#### Scenario: the five app launchers resolve to their commands in both profiles

- GIVEN `DreamcoderProfiles/dreamcoder/default.json` and
  `DreamcoderProfiles/dreamcoder/asus-vivobook15.json`
- WHEN the binding whose `mods` is `["SUPER"]` is read for each of the keys
  `RETURN`, `B`, `E`, `SPACE` and `V`
- THEN SUPER+RETURN resolves to `kitty`, SUPER+B to `firefox`, SUPER+E to
  `thunar`, SUPER+SPACE to `rofi -show drun` and SUPER+V to the
  `cliphist`→`rofi`→`cliphist decode`→`wl-copy` pipeline, in both profiles

### Requirement: FR1.2 Ctrl+Win secondary app shortcuts

The secondary application shortcuts MUST keep the Ctrl+Win modifier family:
SUPER+CTRL+M MUST launch Kitty with btop (`kitty btop`), SUPER+CTRL+S MUST
launch the ML4W Settings app (`flatpak run com.ml4w.settings`), and
SUPER+CTRL+C MUST launch the ML4W calculator
(`~/.config/ml4w/settings/calculator.sh`); those three chords MUST express the
Ctrl+Win combination through the modifier array (`["SUPER","CTRL"]` as
shipped; the schema also admits `["CTRL","SUPER"]`, because `mods` is an
order-insensitive unique-item array). The Kitty-with-Neovim shortcut MUST use the
shipped chord SUPER+CTRL+SHIFT+K (`kitty nvim`) with the modifier array
`["SUPER","CTRL","SHIFT"]`. The previously written `CTRL+SUPER+K` chord was
reconciled to this shipped chord on 2026-09-11.

#### Scenario: Ctrl+Win shortcuts resolve to the shipped chords

- GIVEN both machine profiles
- WHEN the bindings that carry a Ctrl+Win modifier array are read
- THEN `M` resolves to `kitty btop`, `S` to `flatpak run com.ml4w.settings` and
  `C` to `~/.config/ml4w/settings/calculator.sh`
- AND the Neovim shortcut is present as SUPER+CTRL+SHIFT+K with the command
  `kitty nvim`, not as `CTRL+SUPER+K`

### Requirement: FR1.3 Window management bindings

Both profiles MUST bind the four ML4W window-management actions on the SUPER
modifier: SUPER+Q MUST close the active window (`killactive`), SUPER+F MUST
toggle fullscreen, SUPER+T MUST toggle the floating state, and SUPER+Y MUST
toggle the split direction. These bindings MUST NOT be duplicated by any other
loaded keybinding source (see NFR4).

#### Scenario: window management keys are bound once in both profiles

- GIVEN `default.json` and `asus-vivobook15.json`
- WHEN the `["SUPER"]` bindings for `Q`, `F`, `T` and `Y` are read
- THEN they resolve to close, fullscreen, floating-toggle and split-toggle
  respectively, in both profiles

### Requirement: FR1.4 Workspace navigation bindings

Both profiles MUST bind workspace switching and window movement for workspaces
1-10: SUPER+1…5 and SUPER+6…0 MUST switch to workspaces 1-10, and
SUPER+SHIFT+1…5 and SUPER+SHIFT+6…0 MUST move the active window to workspaces
1-10. The ten switch bindings and the ten move bindings MUST all be present in
each profile.

#### Scenario: all twenty workspace bindings exist in both profiles

- GIVEN `default.json` and `asus-vivobook15.json`
- WHEN the `["SUPER"]` and `["SUPER","SHIFT"]` binding sets are read
- THEN keys `1`-`0` switch to workspaces 1-10 and the same keys with SHIFT move
  the active window to workspaces 1-10, in both profiles

### Requirement: FR1.5 Window focus and move bindings

Both profiles MUST bind directional focus and directional window movement on
two key families: SUPER+H/J/K/L MUST move focus left/down/up/right and
SUPER+SHIFT+H/J/K/L MUST move the window in the same four directions; the arrow
keys MUST provide the same actions as SUPER+Left/Right/Up/Down (focus) and
SUPER+SHIFT+Left/Right/Up/Down (move). The previously written `SUPER+L`
lock-screen chord is not part of this requirement; it was reconciled on
2026-09-11 to the shipped SUPER+ALT+L chord recorded under FR1.6.

#### Scenario: focus and move chords cover letters and arrows in both profiles

- GIVEN `default.json` and `asus-vivobook15.json`
- WHEN the `["SUPER"]` and `["SUPER","SHIFT"]` bindings for `H`, `J`, `K`, `L`
  and the four arrow keys are read
- THEN focus moves in the four directions without SHIFT and the active window
  moves in the four directions with SHIFT, in both profiles

### Requirement: FR1.6 System control bindings

`default.json` MUST bind SUPER+ALT+L to the screen locker (`hyprlock`) and the
bare `PRINT` key to area screenshots (`grimblast save area`). Both profiles MUST
bind SUPER+SHIFT+S to full-screen screenshots (`grimblast save screen`). The
lock-screen chord is the shipped SUPER+ALT+L, reconciled on 2026-09-11 from the
earlier `SUPER+L` text.

#### Scenario: system control chords are bound in the profile that owns them

- GIVEN `default.json` and `asus-vivobook15.json`
- WHEN the system-control bindings are read
- THEN `default.json` binds SUPER+ALT+L to `hyprlock` and bare `PRINT` to
  `grimblast save area`, and both profiles bind SUPER+SHIFT+S to
  `grimblast save screen`

### Requirement: FR1.7 Binding coverage across both profiles

Both profiles MUST carry the shared core binding set defined by FR1.1, FR1.3,
FR1.4, FR1.5 and the SUPER+SHIFT+S screenshot chord of FR1.6. `default.json`
MUST carry 56 bindings and `asus-vivobook15.json` MUST carry 70 bindings, so both
MUST exceed the 40-binding floor. `default.json` MUST carry the modifier sets
SUPER (27), SUPER+SHIFT (22), SUPER+CTRL (4), SUPER+CTRL+SHIFT (1), SUPER+ALT (1)
and one bare key; `asus-vivobook15.json` MUST carry SUPER (29), SUPER+SHIFT (22),
SUPER+CTRL (4), SUPER+CTRL+SHIFT (1) and 14 bare keys. `asus-vivobook15.json`
MUST intentionally omit the SUPER+ALT+L lock chord and the bare `PRINT`
screenshot chord that `default.json` carries, because its bare-key row is the
XF86 multimedia row; that omission MUST NOT be reported as a coverage failure.
Existing bindings MUST be preserved in both profiles: the theme toggle
(SUPER+SHIFT+D), the blue-light bindings (SUPER+SHIFT+U / SUPER+SHIFT+I),
brightness, volume and media keys. `scripts/validate-ml4w-profiles.py --ci` MUST
exit 0 for both profiles.

#### Scenario: both profiles meet the binding contract and stay valid

- GIVEN profiles validated by `scripts/validate-ml4w-profiles.py --ci`, with
  `asus-vivobook15.json` carrying 14 bare keys on the XF86 multimedia row
- WHEN the binding array of each profile is counted, grouped by modifier set,
  and compared profile to profile
- THEN `default.json` reports 56 bindings and `asus-vivobook15.json` reports 70,
  each exceeding 40, with the required modifier sets present
- AND the validator prints `All profiles clean!` and exits 0
- AND the missing SUPER+ALT+L and bare `PRINT` bindings are accepted as the
  intended laptop difference, while the preserved brightness, volume and media
  bindings are present in both profiles

### Requirement: FR2.1 Waybar configuration template exists

`DreamcoderWaybar/.config/waybar/config.jsonc` MUST exist and MUST declare the
three ML4W-compatible module anchors `modules-left`, `modules-center` and
`modules-right`. The file MUST be a dormant repository template: it MUST NOT be
described as installed or running, because no repository script installs
`DreamcoderWaybar/` (see `## Known Gaps`).

#### Scenario: the Waybar config template declares the three module anchors

- GIVEN `DreamcoderWaybar/.config/waybar/config.jsonc`
- WHEN the file is parsed as JSONC and its top-level keys are read
- THEN `modules-left`, `modules-center` and `modules-right` are all present

### Requirement: FR2.2 Waybar taskbar module renders workspace buttons with app icons

The Waybar config MUST declare a `hyprland/workspaces` taskbar module and that
module MUST carry a `window-rewrite` mapping from window class or title patterns
to icon glyphs, so workspace buttons can show per-application icons. The
delivered scope of this requirement is the module declaration plus
`window-rewrite`; it MUST NOT be read as delivering the Dreamcoder accent
highlight on the active workspace, because the shipped `style.css` only sets
`font-weight` on `#workspaces button.active` and the accent rule is not
reachable through the shipped import chain (see `## Known Gaps`).

#### Scenario: the taskbar module declares window-rewrite icon mappings

- GIVEN the `hyprland/workspaces` entry in the Waybar config and
  `DreamcoderWaybar/.config/waybar/style.css`
- WHEN its `window-rewrite` object and the `#workspaces button.active` rule are
  read
- THEN `window-rewrite` maps application class or title patterns to icon
  glyphs, and the `format-icons` workspace glyph set is present
- AND the `#workspaces button.active` rule declares only `font-weight`, so no
  accent color is claimed as delivered by this requirement

### Requirement: FR2.3 Waybar standard modules

The Waybar config MUST place the taskbar in `modules-left`, the clock in
`modules-center`, and the six standard status modules `network`, `pulseaudio`,
`cpu`, `memory`, `battery` and `tray` in `modules-right`, and each of those
modules MUST carry its own configuration block.

#### Scenario: standard modules occupy the documented anchors

- GIVEN the parsed Waybar config
- WHEN the three module anchor arrays are read
- THEN `modules-left` is `["hyprland/workspaces"]`, `modules-center` is
  `["clock"]` and `modules-right` lists `network`, `pulseaudio`, `cpu`,
  `memory`, `battery` and `tray` in that set
- AND each listed module has a matching configuration block

### Requirement: FR2.4 Waybar theme integration import

`DreamcoderWaybar/.config/waybar/style.css` MUST import exactly one stylesheet,
`colors.css`, which is the Dreamcoder color bridge that selects the active
light/dark variable set written by the theme sync. The shipped import is
`colors.css`; the `waybar-light.css` / `waybar-dark.css` files named by an
earlier revision of this requirement were reconciled to the shipped import on
2026-09-11. The layout stylesheet MUST NOT define colors itself (no
`@define-color`, no color variable declaration), and the CSS import MUST stay
separate from the layout configuration, which MUST declare no stylesheet import.
The Waybar CSS files are already generated by the Dreamcoder theme sync
(`scripts/sync-dreamcoder-theme.py`), and this change MUST add no changes to
them: those generated files remain the source of the module color rules and of
the CSS variables defined by Dreamcoder tokens, which the color rules reference
(see FR4.1).

#### Scenario: the layout stylesheet imports only the color bridge

- GIVEN `DreamcoderWaybar/.config/waybar/style.css` and
  `DreamcoderWaybar/.config/waybar/config.jsonc`
- WHEN all `@import` statements and all color definitions in the stylesheet are
  read together with the layout config's keys
- THEN exactly one import exists and it is `@import url("colors.css");`, and no
  `@define-color` or accent variable is defined in that file
- AND the layout config declares layout and module configuration only, with no
  CSS import of its own

### Requirement: FR3.1 Profile schema compatibility

Every new binding MUST use only pre-existing schema fields — `key`, `mods`,
`command`, `description`, `bind_type` and `options` — and MUST NOT require any
schema extension for the chords this change delivers. The `mods` field MUST
remain a unique-item array of the enumerated modifiers (`SUPER`, `SHIFT`,
`CTRL`, `ALT`, `CTRL_SHIFT`, `SUPER_SHIFT`), so a Ctrl+Win combination is
expressible as a modifier array — the shipped Ctrl+Win chords use
`["SUPER","CTRL"]` and the Neovim chord uses `["SUPER","CTRL","SHIFT"]`,
while bare keys use an empty `mods` array. The schema MUST continue to accept
letter keys, digits, arrow keys and `F`-numbered function keys.

#### Scenario: schema fields and modifier arrays cover every delivered binding

- GIVEN `DreamcoderProfiles/dreamcoder/profile.schema.json`
- WHEN the binding item schema is read
- THEN `key`, `mods`, `command`, `description`, `bind_type` and `options` exist,
  `mods` is an array of the enumerated modifiers, and `key`, `command` and
  `description` are required
- AND every binding in both profiles validates against that schema

### Requirement: FR3.2 Profile validation and Lua generation

`scripts/validate-ml4w-profiles.py --ci` MUST exit 0 and print
`All profiles clean!` for both profiles. `scripts/generate-custom-lua.sh` MUST
pass `bash -n`, MUST detect the machine profile from DMI hardware identifying
this laptop as `Vivobook_ASUSLaptop M1502IA_M1502IA` / `ASUSTeK COMPUTER INC.`,
and MUST therefore generate its 70 bindings from `asus-vivobook15.json`. Its
generated Lua MUST pass `luac -p`.

#### Scenario: validation passes and generation selects the DMI-detected profile

- GIVEN `scripts/validate-ml4w-profiles.py` and the DMI hardware strings
  `Vivobook_ASUSLaptop M1502IA_M1502IA` and `ASUSTeK COMPUTER INC.`
- WHEN the validator is run with `--ci` and `scripts/generate-custom-lua.sh`
  runs on this machine
- THEN the validator exits 0 after reporting both profiles as passing and
  printing `All profiles clean!`
- AND the generator selects `asus-vivobook15.json`, reports 70 bindings, and its
  output passes `luac -p`

### Requirement: FR4.1 No theme engine changes

This change MUST NOT modify any theme engine source file, and the delivered
theme-integration behavior MUST stay owned by the existing engine path. The
change's file set MUST NOT extend beyond the ML4W surface: the two machine
profiles, the profile schema, the Waybar template files, the ML4W shell scripts
and assets, the tests, the README, and this change's own OpenSpec artifacts.
`scripts/apply-theme-mode.sh` MUST keep handling the
Waybar color bridge by repointing the `colors.css` link to the active mode
variant and restarting Waybar, and the Waybar CSS import MUST stay separate from
the layout config (see FR2.4).

#### Scenario: no theme engine source file is touched

- GIVEN the change's delivered file set together with
  `scripts/apply-theme-mode.sh`
- WHEN the changed paths and the Waybar section of that script are inspected
- THEN no file under the theme engine package is present, and
  `DreamcoderThemes/dreamcoder/waybar-{dark,light}.css` remain
  engine-generated and unedited
- AND the mode switch still repoints `~/.config/waybar/colors.css` to the active
  mode variant before the sync and restarts Waybar

### Requirement: NFR1 Binding commands are valid dispatchers or shell commands

Every binding command MUST be either a Hyprland dispatcher call the generator can
emit natively or a valid shell command. The generator MUST translate the known
`hyprctl dispatch workspace | movetoworkspace | killactive | fullscreen |
togglefloating | togglesplit | movefocus | movewindow` forms into native
`hl.dsp.*` dispatchers, because `hyprctl dispatch` is parsed as Lua by Hyprland
0.55 and later and fails at runtime. The generated Lua MUST contain zero
occurrences of `hyprctl dispatch`.

#### Scenario: generated Lua contains no hyprctl dispatch calls

- GIVEN the generated Lua produced from the auto-detected profile and
  `tests/ml4w/generate_custom_lua.bats`
- WHEN `hyprctl dispatch` is searched for in that output and the Bats suite runs
- THEN zero occurrences are found, and the translated binds appear as native
  `hl.dsp.*` dispatcher calls
- AND the suite's dispatcher test asserts that neither
  `hyprctl dispatch workspace` nor `hyprctl dispatch movetoworkspace` appears in
  generated output

### Requirement: NFR2 Waybar config parses as valid JSONC

`DreamcoderWaybar/.config/waybar/config.jsonc` MUST parse as valid JSONC after
its `//` comment lines are removed, and MUST contain no trailing commas or other
constructs that break a strict JSON parse of the comment-stripped text.

#### Scenario: comment-stripped config parses as JSON

- GIVEN `DreamcoderWaybar/.config/waybar/config.jsonc`
- WHEN `//` comment lines are stripped and the remainder is parsed as JSON
- THEN parsing succeeds and the expected module keys are readable

### Requirement: NFR4 Bindings do not conflict with ML4W built-in defaults

The delivered bindings MUST NOT collide with ML4W's built-in defaults on a live
session. The curated keybinding variant selector shipped by this change MUST keep
the single-source-of-truth model, in which the profile JSON owns the keyboard
binds and the curated variant owns only the native binds the generator cannot
emit, so that ML4W's stock `default.lua` and the generated `custom.lua` cannot
both define the same chord. On the live session, `hyprctl binds -j` MUST report
119 binds, 118 distinct `(modmask, key)` pairs, and zero real duplicate
`(modmask, key)` collisions. The two keyless entries in that output are distinct
keyboard-backlight binds (`Brillo teclado +` with arg `167` and `Brillo teclado
-` with arg `169`, both `locked=true`, dispatcher `__lua`) and MUST NOT be
counted as a collision. The profile test suite MUST also assert that no profile
contains a duplicate key+mods combination.

#### Scenario: the live bind table has no real collisions

- GIVEN a live Hyprland session with the generated binds loaded and
  `ml4w_assets/hypr/conf/keybinding.lua` in the repository
- WHEN `hyprctl binds -j` and the selector asset are read
- THEN 119 binds and 118 distinct `(modmask, key)` pairs are reported, with zero
  real duplicate `(modmask, key)` collisions once the two distinct keyless
  keyboard-backlight entries are excluded
- AND the selector loads the curated `dreamcoder.lua` variant, so the
  profile-generated binds are not declared twice

## Known Gaps

The gaps below are non-normative. They record behavior that is **not** delivered
or **not** provable from this repository, and they MUST NOT be counted as
satisfied requirements.

### Gap: The active workspace accent is not reachable in the shipped Waybar chain

`DreamcoderWaybar/.config/waybar/style.css` imports only `colors.css`, which
declares variables and no accent rule; the `#workspaces button.active` accent
rule lives in the engine-generated
`DreamcoderThemes/dreamcoder/waybar-{dark,light}.css`, which `style.css`
does not import. Delivered behavior is the module plus `window-rewrite` only.
Follow-up: wire the mode CSS import so the accent rule reaches the live chain.

### Gap: The Waybar deliverables are dormant templates

No repository script installs `DreamcoderWaybar/`, so "Waybar starts without
errors using this config" (the original NFR3) and "Dreamcoder Light colors
visible in all Waybar modules" (the original NFR5) are **not provable** from the
repository. Follow-up: add an installer or wiring step, then re-verify both
statements.

### Gap: shellcheck reports 17 info-level findings

`shellcheck --shell=bash scripts/*.sh` exits 1. All 17 findings are SC1091
(info) for dynamic `source` paths shellcheck cannot follow; there are no warning
or error level findings. This is pre-existing and unrelated to this change.
Follow-up: add per-line `# shellcheck source=` directives or a scoped
`.shellcheckrc`.

### Gap: Earlier partial specs of this capability were superseded

Earlier partial specs of this capability were superseded by archived changes;
this delta is the single source of truth for the ML4W binding contract.
Follow-up: none — recorded so the superseded specifications are never treated as
current.
