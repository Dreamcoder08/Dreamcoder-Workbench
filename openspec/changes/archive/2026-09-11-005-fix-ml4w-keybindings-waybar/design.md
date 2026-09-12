# Design: ML4W Keybindings & Waybar

## Architecture

### Component Map

```
DreamcoderProfiles/dreamcoder/
├── default.json          ← [MODIFY] Add 30+ bindings
├── asus-vivobook15.json  ← [MODIFY] Add 30+ bindings
└── profile.schema.json   ← [NO CHANGE] Already compatible

DreamcoderWaybar/.config/waybar/
└── config.jsonc          ← [CREATE] New Waybar config

scripts/
├── generate-custom-lua.sh      ← [NO CHANGE] Generates Lua from profiles
├── apply-theme-mode.sh         ← [NO CHANGE] Handles Waybar CSS symlink
├── sync-dreamcoder-theme.py    ← [NO CHANGE] Generates Waybar CSS
└── validate-ml4w-profiles.py   ← [NO CHANGE] Validates profiles

DreamcoderThemes/dreamcoder/
├── waybar-light.css       ← [NO CHANGE] Already correct
└── waybar-dark.css        ← [NO CHANGE] Already correct
```

### Data Flow

```
profile.json → validate-ml4w-profiles.py → ✓ valid
profile.json → generate-custom-lua.sh → custom.lua → Hyprland loads
Dreamcoder tokens.json → sync-dreamcoder-theme.py → waybar-light.css → Waybar @import
config.jsonc + waybar-light.css → Waybar renders taskbar + modules
```

## Design Decisions

### D1: Binding Organization

Bindings grouped by category with section comments in the JSON (using `description` field grouping):

```json
{
  "keybindings": {
    "bindings": [
      // ── App Launchers (SUPER)
      {
        "key": "RETURN",
        "mods": ["SUPER"],
        "command": "kitty",
        "description": "Terminal"
      },
      // ── Secondary Apps (CTRL + SUPER)
      {
        "key": "K",
        "mods": ["CTRL", "SUPER"],
        "command": "kitty nvim",
        "description": "Code Editor"
      },
      // ── Window Management
      {
        "key": "Q",
        "mods": ["SUPER"],
        "command": "hyprctl dispatch killactive",
        "description": "Close Window"
      },
      // ── Workspaces
      {
        "key": "1",
        "mods": ["SUPER"],
        "command": "hyprctl dispatch workspace 1",
        "description": "Workspace 1"
      }
      // ...
    ]
  }
}
```

**Rationale**: JSON doesn't support comments, but our `generate-custom-lua.sh` preserves binding order and emits the `description` as Lua comments. Section grouping in the array is sufficient for readability.

### D2: Hyprland Dispatchers

Use `hyprctl dispatch` commands (Hyprland 0.55+ compatible):

| Action            | Command                               |
| ----------------- | ------------------------------------- |
| Close window      | `hyprctl dispatch killactive`         |
| Fullscreen        | `hyprctl dispatch fullscreen 1`       |
| Toggle float      | `hyprctl dispatch togglefloating`     |
| Toggle split      | `hyprctl dispatch togglesplit`        |
| Switch workspace  | `hyprctl dispatch workspace N`        |
| Move to workspace | `hyprctl dispatch movetoworkspace N`  |
| Move focus        | `hyprctl dispatch movefocus l/r/u/d`  |
| Move window       | `hyprctl dispatch movewindow l/r/u/d` |

**Rationale**: `hyprctl dispatch` is the canonical Lua-equivalent dispatcher for Hyprland 0.55+. The `generate-custom-lua.sh` script wraps commands in `hl.dsp.exec_cmd()`.

### D3: Waybar Config Structure

```jsonc
{
  "layer": "top",
  "position": "top",
  "height": 32,
  "spacing": 4,
  "modules-left": ["hyprland/workspaces"],
  "modules-center": ["clock"],
  "modules-right": [
    "network",
    "pulseaudio",
    "cpu",
    "memory",
    "battery",
    "tray",
  ],

  "hyprland/workspaces": {
    "format": "{icon}",
    "window-rewrite": {
      "class<firefox>": "󰈹",
      "class<kitty>": "",
      "class<thunar>": "",
      // ...
    },
    "sort-by-number": true,
  },

  "clock": {
    "format": "{:%H:%M}",
    "tooltip-format": "{:%A, %d %B %Y}",
  },
  // ... other modules
}
```

**Rationale**: ML4W uses `hyprland/workspaces` (not `sway/workspaces` which is for Sway WM). The `window-rewrite` maps X11 class names to Nerd Font icons. Using JSONC (JSON with comments) for human readability.

### D4: Theme CSS Import Strategy

Waybar style will be in a separate file that imports the Dreamcoder CSS:

```css
/* DreamcoderWaybar/.config/waybar/style.css */
@import url('colors-light.css');
/* or via symlink: colors.css → colors-light.css */

/* Layout-only rules (no color values) */
#waybar {
  padding: 0 8px;
}
#workspaces button {
  padding: 0 6px;
  margin: 4px 2px;
}
/* ... */
```

**Rationale**: Separation of concerns — Dreamcoder owns colors, user owns layout. The `apply-theme-mode.sh` script already manages the `colors.css` symlink. The waybar config stays in `config.jsonc`, CSS separately.

### D5: File Locations

| File         | Path                                           | Purpose                            |
| ------------ | ---------------------------------------------- | ---------------------------------- |
| Config JSONC | `DreamcoderWaybar/.config/waybar/config.jsonc` | Module config                      |
| Style CSS    | `DreamcoderWaybar/.config/waybar/style.css`    | Layout (colors via @import)        |
| Colors CSS   | `DreamcoderThemes/dreamcoder/waybar-light.css` | Dreamcoder colors (auto-generated) |

**Rationale**: Matches ML4W convention: `~/.config/waybar/config.jsonc` + `~/.config/waybar/style.css`. The Dreamcoder colors CSS stays in `DreamcoderThemes/` and is symlinked into place by `apply-theme-mode.sh`.
