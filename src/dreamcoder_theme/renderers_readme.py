"""Focused desktop shell theme renderers."""

from __future__ import annotations


def readme_content() -> str:
    return """# Dreamcoder Palette Layer

This directory contains the Dreamcoder visual contract and generated color-only snippets for ML4W/Gentleman Dots.

- `tokens.json`: canonical Dreamcoder Workbench design tokens and guardrails.
- `tokens.schema.json`: machine-readable token contract.
- `*-dark.*`: Dreamcoder Dark mode with near-black bg, cool steel-blue accents, and muted slate surfaces.
- `*-light.*`: paper-like daytime mode with flat surface ladder and distinct semantic tokens.
## Color-only Snippets (Hooks)

Hook these into your app configs after ML4W/Gentleman files:

| Target | Files | How to Use |
|--------|-------|------------|
| **Kitty** | `kitty-dreamcoder-{mode}.conf`, `dreamcoder-ui.conf` | `include` in kitty.conf |
| **Ghostty** | `ghostty-dreamcoder-{mode}` | `theme = dreamcoder-{mode}` in ghostty config |
| **Warp** | `Warp/.local/share/warp-terminal/themes/Dreamcoder-{Mode}.yaml` | Select in Warp theme picker |
| **Hyprland** | `hyprland-{mode}.conf` | `source` from hyprland.conf |
| **Waybar** | `waybar-{mode}.css` | `@import` in waybar style.css |
| **Rofi** | `rofi-{mode}.rasi` | `@import` or `-theme` in rofi launch |
| **Starship** | `starship-{mode}.toml` | `STARSHIP_CONFIG` env var |
| **Antigravity** | `DreamcoderAntigravity/Dreamcoder-{Mode}.json` | Antigravity theme selector |
| **opencode** | `opencode/dreamcoder.json` | `theme: "dreamcoder"` in opencode config |
| **Codex CLI** | `DreamcoderCodexCLI/Dreamcoder-{Mode}.tmTheme` | `theme = "Dreamcoder"` in codex config |
| **PI CLI** | `DreamcoderPi/.pi/agent/themes/dreamcoder-{mode}.json` | `theme: "dreamcoder"` in pi settings |
| **Neovim** | `nvim-dreamcoder-{mode}.lua` | `require('dreamcoder')` in neovim config |
| **Lazygit** | `DreamcoderLazygit/.config/lazygit/config.{mode}.yml` | `~/.config/lazygit/config.yml` symlink → `config.{mode}.yml` |
| **Zsh-syntax-highlighting** | `zsh-syntax-highlighting-dreamcoder-{mode}.zsh` | `source` after zsh-syntax-highlighting plugin |
| **LS_COLORS / eza** | `ls-colors-dreamcoder-{mode}.sh` | `source` in .zshrc or .bashrc |
| **Bat** | `bat-dreamcoder-{mode}.sh` | Sets `BAT_THEME` env var; pair with Codex CLI tmTheme |
| **Delta (git diff)** | `delta-dreamcoder-{mode}.gitconfig` | `[include]` in ~/.config/git/config |
| **Fzf** | `fzf-dreamcoder-{mode}.sh` | `source` in .zshrc or .bashrc |
| **Btop** | `btop-dreamcoder-{mode}.theme` | Place in ~/.config/btop/themes/ |
| **Dunst** | `dunst-dreamcoder-{mode}.conf` | `[include]` in dunstrc |
| **Firefox** | `firefox-dreamcoder-{mode}.css` | userChrome.css for Firefox customization |
| **Obsidian** | `obsidian-dreamcoder-{mode}.css` | CSS snippet in Obsidian vault |
| **Cava** | `cava-dreamcoder-{mode}.config` | `include` in ~/.config/cava/config |

## Word of Caution

Import these snippets after existing ML4W/Gentleman files so layouts, keybinds, wallpaper scripts, gaps, animations, and behavior remain owned by those systems.
"""
