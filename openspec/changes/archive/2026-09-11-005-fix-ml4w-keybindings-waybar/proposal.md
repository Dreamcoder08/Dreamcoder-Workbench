# Proposal: Fix ML4W Keybindings & Waybar Integration

## Problem

The Dreamcoder-dots ML4W profiles (`default.json`, `asus-vivobook15.json`) contain only 3–19 keybindings. A standard ML4W Hyprland setup has 50+ bindings covering window management, workspace switching, app launching, and system controls. Additionally, there is no Waybar configuration in the repository — only CSS theme files — so the Waybar taskbar/app display is broken.

### Specific Issues

1. **Zero `CTRL+SUPER` bindings**: User cannot use Ctrl+Win+K or any Ctrl+Win+letter shortcut for app launching.
2. **Zero app launchers**: No `SUPER+B` (browser), `SUPER+T` (terminal), `SUPER+E` (file manager), etc.
3. **Missing window management**: No workspace switching (`SUPER+1–5`), no window focus/move/resize, no close (`SUPER+Q`), no fullscreen (`SUPER+F`).
4. **No Waybar config**: The repo has `waybar-light.css` / `waybar-dark.css` (Dreamcoder-themed) but no `config.jsonc` with module definitions. Taskbar is missing.
5. **ML4W 2.14+ compatibility**: Hyprland 0.55+ deprecated `hyprlang` in favor of Lua. Our `generate-custom-lua.sh` already generates Lua — needs to be verified against current ML4W Lua conventions.

## Proposed Solution

### 1. Extended ML4W Keybinding Profiles

Add standard ML4W bindings to both `default.json` and `asus-vivobook15.json`:

| Category                      | Key     | Mods         | Action                                  |
| ----------------------------- | ------- | ------------ | --------------------------------------- |
| **App Launchers**             |         |              |                                         |
| Terminal                      | RETURN  | SUPER        | `kitty`                                 |
| Browser                       | B       | SUPER        | `firefox` (or `xdg-open https://`)      |
| File Manager                  | E       | SUPER        | `thunar`                                |
| App Launcher (Rofi)           | SPACE   | SUPER        | `rofi -show drun`                       |
| Clipboard                     | V       | SUPER        | `cliphist list \| rofi`                 |
| **Secondary Apps (Ctrl+Win)** |         |              |                                         |
| Code Editor                   | K       | CTRL, SUPER  | `kitty nvim`                            |
| System Monitor                | M       | CTRL, SUPER  | `kitty btop`                            |
| Settings                      | S       | CTRL, SUPER  | `flatpak run com.ml4w.settings`         |
| Calculator                    | C       | CTRL, SUPER  | `~/.config/ml4w/settings/calculator.sh` |
| **Window Management**         |         |              |                                         |
| Close Window                  | Q       | SUPER        | `killactive`                            |
| Fullscreen                    | F       | SUPER        | `fullscreen`                            |
| Toggle Float                  | T       | SUPER        | `togglefloating`                        |
| Toggle Split                  | Y       | SUPER        | `togglesplit`                           |
| **Workspaces**                |         |              |                                         |
| Switch 1–5                    | 1–5     | SUPER        | `workspace, 1–5`                        |
| Move to 1–5                   | 1–5     | SUPER, SHIFT | `movetoworkspace, 1–5`                  |
| Switch 6–10                   | 6–0     | SUPER        | `workspace, 6–10`                       |
| Move to 6–10                  | 6–0     | SUPER, SHIFT | `movetoworkspace, 6–10`                 |
| **Focus**                     |         |              |                                         |
| Left/Right/Up/Down            | h/l/k/j | SUPER        | `movefocus, l/r/u/d`                    |
| Move Window                   | h/l/k/j | SUPER, SHIFT | `movewindow, l/r/u/d`                   |
| **System**                    |         |              |                                         |
| Lock Screen                   | L       | SUPER        | `hyprlock`                              |
| Screenshot                    | PRINT   | (none)       | `grimblast save area`                   |

### 2. Waybar Configuration

Create `DreamcoderWaybar/.config/waybar/config.jsonc` with:

- `hyprland/workspaces` module with taskbar support (`window-rewrite`, app icons)
- `wlr/taskbar` for open app display
- Standard modules: clock, battery, network, pulseaudio, cpu, memory, tray
- `@import` of Dreamcoder `waybar-light.css` / `waybar-dark.css` for colors
- ML4W-compatible structure (modules-left/center/right layout)

### 3. Theme Integration

- `scripts/apply-theme-mode.sh` already handles Waybar CSS symlink and restart
- `scripts/sync-dreamcoder-theme.py` already renders Waybar CSS through the Python theme engine
- No changes needed to the theme engine — it correctly generates `waybar-{mode}.css`

### 4. Verification

- `scripts/validate-ml4w-profiles.py` validates profile JSON against schema
- `scripts/generate-custom-lua.sh` generates Hyprland Lua from profiles
- `scripts/verify-theme-health.py` checks theme integrity
- New: validate Waybar config JSON syntax and module references

## Scope

**In scope:**

- ML4W standard keybindings for both profiles
- Ctrl+Win+letter secondary app shortcuts
- Waybar config with taskbar + Dreamcoder Light theme import
- Profile schema validation (no schema changes needed)

**Out of scope:**

- Waybar CSS changes (already correct)
- Hyprland core config (managed by ML4W directly)
- Kitty/Ghostty/other terminal config changes
- Rofi config (separate concern)

## Risks

- **Low**: Schema validation already covers all new binding fields
- **Low**: Waybar config is additive — won't break existing setup
- **Medium**: Binding conflicts with ML4W defaults need verification (SUPER+Q, SUPER+F are standard ML4W)
