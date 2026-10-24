# Terminal Configuration

## Supported Terminals

| Terminal | Theme Format | Notes |
|----------|-------------|-------|
| Kitty | `.conf` | GPU-accelerated, primary terminal |
| Ghostty | Custom | Custom shaders, blur effects |
| WezTerm | `.lua` | Cross-platform, Lua config |
| Alacritty | `.toml` | Minimal, fast |
| Orca | Live settings JSON | Written into Orca's own profile, not a repo file |

### Orca

Orca keeps its themes in its own per-profile settings file
(`~/.config/orca/profiles/local-default/orca-data.json`, overridable with
`ORCA_DATA_PATH`). `dreamcoder sync` writes both `Dreamcoder Dark` and
`Dreamcoder Light` into `terminalCustomThemes`, points
`terminalThemeDark`/`terminalThemeLight` at them, enables
`terminalUseSeparateLightTheme`, sets the per-appearance divider colors from
the palette `border_ui` token, and sets the app chrome `theme` to the active
Dreamcoder mode.

Orca holds its settings in memory while its main window is open and flushes
that copy over external edits, so the sync skips the file and reports
`skipped-running` instead of writing something that would be discarded.
Close Orca, then re-run `dreamcoder dark` or `dreamcoder light` to apply.

## Theme Switching

Terminals auto-detect `DREAMCODER_THEME_MODE` env var:

```bash
export DREAMCODER_THEME_MODE="dark"  # or "light"
```

## Font Configuration

All terminals use JetBrainsMono Nerd Font:

```
Font: JetBrainsMono Nerd Font
Size: 14pt
Ligatures: Enabled
```

## Key Bindings

Common key bindings across terminals:

| Action | Kitty | Ghostty | WezTerm | Alacritty |
|--------|-------|---------|---------|-----------|
| New tab | Ctrl+Shift+T | Ctrl+Shift+T | Ctrl+Shift+T | Ctrl+Shift+T |
| Close tab | Ctrl+Shift+W | Ctrl+Shift+W | Ctrl+Shift+W | Ctrl+Shift+W |
| Split horizontal | Ctrl+Shift+5 | Ctrl+Shift+5 | Ctrl+Shift+5 | Ctrl+Shift+5 |
| Split vertical | Ctrl+Shift+6 | Ctrl+Shift+6 | Ctrl+Shift+6 | Ctrl+Shift+6 |
