# Terminal Configuration

## Supported Terminals

| Terminal | Theme Format | Notes |
|----------|-------------|-------|
| Kitty | `.conf` | GPU-accelerated, primary terminal |
| Ghostty | Custom | Custom shaders, blur effects |
| WezTerm | `.lua` | Cross-platform, Lua config |
| Alacritty | `.toml` | Minimal, fast |

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
