# ML4W Integration — Profile-Driven Keybinding System

← Back to [docs/README.md](../README.md)

Dreamcoder Workbench integrates with [ML4W](https://ml4w.com) through a modular, profile-driven system.
All machine-specific keybindings live in JSON profiles, avoiding manual editing of ML4W-managed files.
Profiles are compiled into `~/.config/hypr/custom.lua` by the generator and validated in CI.

## Architecture

```mermaid
flowchart LR
    P["DreamcoderProfiles/dreamcoder/<br/>&lt;machine&gt;.json"]
    S["profile.schema.json"]
    GEN["scripts/generate-custom-lua.sh"]
    ORCH["scripts/setup-hyprland.sh"]
    VER["scripts/verify-ml4w-setup.sh"]
    VAL["scripts/validate-ml4w-profiles.py"]
    CUSTOM["~/.config/hypr/custom.lua"]
    TST["tests/ml4w/*.bats"]

    P -->|jq + tmpl| GEN
    S -->|schema| VAL
    S -->|schema| GEN
    GEN -->|validate| VAL
    GEN --> CUSTOM
    ORCH -->|symlinks + generation| CUSTOM
    VER -->|post-reboot| CUSTOM
    TST -->|bats| GEN
    TST -->|bats| ORCH
```

## Workflow

1. **Edit profile**: `DreamcoderProfiles/dreamcoder/<machine>.json`
2. **Generate**: `./scripts/generate-custom-lua.sh --profile <machine>`
3. **Setup**: `./scripts/setup-hyprland.sh --profile <machine>`
4. **Verify (post-reboot)**: `./scripts/verify-ml4w-setup.sh`
5. **Validate (CI)**: `python3 scripts/validate-ml4w-profiles.py --ci`

## Profiles

| Profile           | Machine          | Keybindings                                     |
| ----------------- | ---------------- | ----------------------------------------------- |
| `default`         | Any generic      | Apps, workspaces, focus, theme, blue light      |
| `asus-vivobook15` | ASUS VivoBook 15 | Multimedia F row, brightness, backlight + all of the above |

Profile auto-detection reads **DMI hardware** (`/sys/class/dmi/id/product_name`,
`sys_vendor`) first, then falls back to the hostname. Hostname-only detection
was a bug: hosts named `archlinux` never matched `*asus*`, so the wrong profile
(with no multimedia or brightness binds) was generated silently.

## Binding contract (avoid duplicate binds)

`~/.config/hypr/conf/keybindings/dreamcoder.lua` (the curated ML4W variant) and
the generated `custom.lua` are BOTH loaded by `hyprland.lua`. They must not
define the same key — Hyprland executes ALL matching duplicate binds in
declaration order (e.g. `SUPER + F` fullscreens and immediately unfullscreens).

Per the official ML4W docs, shipped keybinding variations are overwritten on
updates, so custom bindings live in a separate **variant**. `conf/keybinding.lua`
(the selector) points at `dreamcoder.lua` instead of the stock `default.lua`.

- The **profile JSON owns** everything the generator can emit: apps, workspaces,
  focus/move, fullscreen/floating/split, screenshots, theme, hyprsunset, the
  multimedia F row and the keyboard backlight.
- The **`dreamcoder.lua` variant** is restricted to binds the generator
  **cannot** emit: native mouse drag/resize, workspace scroll, window swap,
  group toggle, scratchpad, ML4W actions (wallpaper, power, launcher,
  statusbar) and the XF86* multimedia keys as a hardware fallback.
- The stock `default.lua` stays untouched (defensive fallback if an ML4W
  update resets the selector; it is also curated to avoid duplicate binds).
- `setup-hyprland.sh` re-applies the selector + variant after ML4W updates.

If you add a keybinding, add it to the profile JSON and re-run the generator —
never to `dreamcoder.lua` unless it is a native-only bind.

### Tracking upstream `default.lua` (ML4W 2.16)

`dreamcoder.lua` follows upstream `default.lua` minus the profile-owned binds.
The ML4W 2.16 delta is ported as follows:

| Upstream 2.16 change | In `dreamcoder.lua` |
| --- | --- |
| Overview moved to `~/.local/share/quickshell-overview` | `SUPER + Tab` runs `qs -p ~/.local/share/quickshell-overview ipc call overview toggle` |
| `SUPER + ALT + B` statusbar autohide | Ported |
| `SUPER + ALT + D` dock autohide | Ported |
| Reload Dock moved to `SUPER + SHIFT + D` | Not bound — the profile owns that combo (theme toggle) |
| Rewritten AZERTY detection (`fr`, `be`) | Ported; binds the AZERTY keysyms only on AZERTY layouts, since the profile owns the digit workspace binds |

`tests/ml4w/keybindings_variant.bats` fails on any new collision between the
variant and the profile; there are no exceptions. The profile owns
`SUPER + SHIFT + arrows` (move window), so the variant's keyboard resize sits on
`SUPER + CTRL + arrows` instead of ML4W's upstream `SUPER + SHIFT + arrows`.

## hyprctl dispatch is broken on Hyprland 0.55+ — native dispatchers used

Hyprland's Lua config parses `hyprctl dispatch <arg>` as Lua
(`hl.dispatch(<arg>)`), so legacy shell commands like
`hyprctl dispatch workspace 2` fail at runtime with a syntax error — the bind
appears registered but does nothing. `generate-custom-lua.sh` therefore
translates the following `hyprctl dispatch` commands in profiles to native
`hl.dsp.*` dispatchers:

| Shell command           | Native Lua dispatcher                                |
| ----------------------- | ---------------------------------------------------- |
| `hyprctl dispatch workspace N`     | `hl.dsp.focus({ workspace = N })`          |
| `hyprctl dispatch movetoworkspace N` | `hl.dsp.window.move({ workspace = N })`  |
| `hyprctl dispatch killactive`      | `hl.dsp.window.close()`                    |
| `hyprctl dispatch fullscreen 1`    | `hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" })` |
| `hyprctl dispatch togglefloating`  | `hl.dsp.window.float({ action = "toggle" })` |
| `hyprctl dispatch togglesplit`     | `hl.dsp.layout("togglesplit")`             |
| `hyprctl dispatch movefocus <dir>` | `hl.dsp.focus({ direction = "<dir>" })`    |
| `hyprctl dispatch movewindow <dir>`| `hl.dsp.window.move({ direction = "<dir>" })` |

Any other command still falls back to `hl.dsp.exec_cmd(...)`.

## Upgrade-proof hooks: Dreamcoder hooks live in Dreamcoder-owned files

ML4W upgrades overwrite every file ML4W ships (`hyprland.lua`, the
`ml4w-wallpaper` runner, shipped keybinding variants). A line injected into
one of those files silently disappears on the next upgrade. The rule:

- **Put hooks in files ML4W never ships.** `custom.lua` (generated from the
  profile) loads `dreamcoder-colors`; `hyprland.lua` already requires
  `custom.lua` when it exists, so nothing is injected into `hyprland.lua`.
  `dreamcoder doctor` accepts the loader from `custom.lua` (a legacy require in
  `hyprland.lua` is still recognised).
- **When a hook must live in an ML4W file, make it re-appliable.**
  `scripts/apply-ml4w-hooks.sh` appends the wallpaper hook to
  `~/.config/ml4w/scripts/ml4w-wallpaper` (the runner ML4W 2.16's Quickshell
  wallpaper app calls with `$IMAGE_PATH`) between
  `# >>> Dreamcoder wallpaper hook >>>` markers. Each run replaces the block, so
  re-running it after an ML4W upgrade restores the hook without duplicates.
- **The GTK theme listener is hooked the same way.** ML4W 2.16 runs
  `~/.config/ml4w/listeners/gtk-theme-switcher.sh`, which watches
  `~/.config/gtk-3.0/settings.ini`. Dreamcoder's own light/dark switch writes
  that file, so the listener then runs Matugen over the wallpaper and
  overwrites Dreamcoder's colour files (`waybar/colors.css`, `hypr/colors.lua`,
  `hypr/colors.conf`, rofi colours) before reloading Quickshell, Waybar, GTK and
  swaync. `scripts/apply-ml4w-hooks.sh` inserts a block between
  `# >>> Dreamcoder listener hook >>>` markers right after each Matugen call.
  The block runs `scripts/dreamcoder sync` synchronously
  (`DREAMCODER_THEME_MODE` taken from the branch's `matugen -m dark|light`, or
  read from `settings.ini` when the call has no `-m`; `DREAMCODER_WRITE_REPO=0`;
  streams to
  `~/.cache/dreamcoder/ml4w-listener-sync.log`, 120 s timeout), so the reloads
  that follow pick up Dreamcoder colours. The sync never writes `settings.ini`,
  so the listener cannot loop. When the file changes, the running listener is
  restarted with `~/.config/ml4w/listeners.sh --restart gtk-theme-switcher`
  (it keeps the body it parsed at start). A listener without a Matugen call is
  left untouched with a warning; a missing listener is skipped. Override the
  paths with `ML4W_GTK_LISTENER` and `ML4W_LISTENERS_SCRIPT`.
- **waypaper is optional.** ML4W 2.16 no longer installs it; its
  `post_command` is hooked only when `~/.config/waypaper/config.ini` exists.
- **Colour files may be regular files.** ML4W 2.16 ships
  `~/.config/hypr/colors.lua` / `colors.conf` as regular files and the theme
  sync writes Dreamcoder colours through them (it only re-points files that are
  already symlinks). `doctor.sh` and `verify-ml4w-setup.sh` accept either a
  symlink into a Dreamcoder variant or a regular file whose bytes match a
  `DreamcoderThemes/dreamcoder/hypr-colors-*` variant.

After every ML4W upgrade:

```bash
./scripts/generate-custom-lua.sh      # custom.lua (keybinds + colour loader)
./scripts/apply-ml4w-hooks.sh         # re-hook the wallpaper runner + GTK listener
./scripts/dreamcoder sync             # rewrite colors.lua / colors.conf
./scripts/verify-ml4w-setup.sh
```

## What setup-hyprland.sh does

1. **Symlinks** wlogout + swaync `colors.css` → waybar (single theme toggle point)
2. **Generates** `custom.lua` from JSON profile via `generate-custom-lua.sh`
3. **Installs** toggle script (`dreamcoder-toggle-theme.sh`) to `~/.config/hypr/scripts/`
4. **Applies** ML4W hooks (wallpaper, theme regeneration)
5. **Reloads** Hyprland

## Theme Toggle

| Shortcut            | Action                             |
| ------------------- | ---------------------------------- |
| `SUPER + SHIFT + D` | Toggle light/dark theme |
| `SUPER + SHIFT + U` | Activate blue light filter (4000K) |
| `SUPER + SHIFT + I` | Deactivate blue light filter       |

## Testing

```bash
# Run all ML4W integration tests
bats tests/ml4w/*.bats

# Validate all profiles against schema
python3 scripts/validate-ml4w-profiles.py --ci

# Dry-run without system changes
./scripts/setup-hyprland.sh --profile default --dry-run
./scripts/generate-custom-lua.sh --profile default --dry-run
```

## File Layout

```
scripts/
├── generate-custom-lua.sh    # JSON → custom.lua generator with --validate
├── setup-hyprland.sh         # Idempotent orchestrator (symlinks + generation + hooks)
├── verify-ml4w-setup.sh      # Post-reboot health verification
└── validate-ml4w-profiles.py  # Schema + convention validation with --ci flag

ml4w_assets/
└── hypr/
    ├── custom.lua.tmpl        # Lua template for keybinding generation
    └── scripts/
        └── dreamcoder-toggle-theme.sh  # Theme toggle script

DreamcoderProfiles/dreamcoder/
├── profile.schema.json        # JSON Schema for machine profiles
├── default.json               # Default profile (theme toggle + blue light)
└── asus-vivobook15.json       # ASUS VivoBook 15 profile (all Fn keys)

tests/ml4w/
├── apply_ml4w_hooks.bats      # wallpaper + GTK listener hooks (ML4W 2.16 fixtures)
├── args.bats                  # script argument handling
├── generate_custom_lua.bats   # generator, incl. the dreamcoder-colors loader
├── keybindings_variant.bats   # dreamcoder.lua vs ML4W 2.16 and the profile
├── ml4w_managed.bats          # ML4W ownership + colour-file predicates
├── setup_hyprland.bats        # orchestrator
├── profile_validation.bats    # JSON profiles
└── waybar_override.bats       # Waybar accent override

tests/fixtures/ml4w/
└── ml4w-wallpaper-2.16        # upstream runner at tag 2.16 (3960570)
```
