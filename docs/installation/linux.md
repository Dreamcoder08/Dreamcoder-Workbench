# Installing Dreamcoder Workbench on Linux

## Prerequisites

- **Arch Linux** (recommended), Fedora, or Ubuntu/Debian
- `git`, `python` 3.11+, `curl`
- `systemd --user` available (for auto-theme timer)
- ~10GB free disk space

## Step 1: Install Gentleman.Dots

Gentleman.Dots provides: Neovim (29 plugins LazyVim), Ghostty shaders (53), Tmux/Zellij, Fish/Zsh/Nushell.

```bash
# Option A: Homebrew (recommended)
brew install Gentleman-Programming/tap/gentleman-dots
gentleman-dots

# Option B: Direct download
curl -fsSL https://github.com/Gentleman-Programming/Gentleman.Dots/releases/latest/download/gentleman-installer-linux-amd64 -o gentleman.dots
chmod +x gentleman.dots
./gentleman.dots
```

The TUI will guide you through selecting your preferred tools.

> **Important:** After installation, open tmux and press `prefix + I` (capital I) to install TPM plugins.

## Step 2: Install ML4W OS

ML4W provides: Hyprland (animations, keybinds, monitors), Waybar, Rofi, Dunst, Btop, GTK.

```bash
bash <(curl -s https://ml4w.com/os/stable)
```

> **Important:** After installation, reboot or restart Hyprland for changes to take effect.

## Step 3: Install Dreamcoder Workbench

Dreamcoder Workbench provides: Token-based color engine, Starship prompt with AI session state, auto-theme switching, 19 shell functions.

```bash
# Clone
git clone https://github.com/Dreamcoder08/Dreamcoder-Workbench.git ~/Documents/PROYECTOS/Dreamcoder-Workbench
cd ~/Documents/PROYECTOS/Dreamcoder-Workbench

# Install Python package (required for theme engine)
pip install -e .

# Run installer
./scripts/dreamcoder install
```

## Step 4: Verify Installation

Run the comprehensive health check:

```bash
dreamcoder doctor
```

Expected output: all checks pass

### Quick verification checklist

```bash
# 1. Theme files exist
ls ~/.config/ghostty/themes/dreamcoder*
ls ~/.config/kitty/colors-dreamcoder.conf
ls ~/.config/hypr/dreamcoder-colors.lua
ls ~/.config/btop/themes/dreamcoder.theme

# 2. Symlinks are correct
readlink ~/.config/hypr/dreamcoder-colors.lua        # → hypr-colors-light.lua or hypr-colors-dark.lua
readlink ~/.config/btop/themes/dreamcoder.theme      # → dreamcoder-light.theme or dreamcoder-dark.theme
readlink ~/.config/waybar/colors.css                 # → colors-light.css or colors-dark.css
readlink ~/.config/rofi/colors.rasi                  # → colors-light.rasi or colors-dark.rasi

# 3. Hyprland loads dreamcoder colours (from the generated custom.lua)
grep "dreamcoder-colors" ~/.config/hypr/custom.lua    # → require("dreamcoder-colors")

# 4. Timer is active
systemctl --user is-active dreamcoder-theme-auto.timer  # → active

# 5. Mode switching works
dreamcoder dark
dreamcoder light
dreamcoder status
```

## Mode Switching

```bash
# Manual
dreamcoder dark     # → Dreamcoder Dark
dreamcoder light    # → Cocoa/Lúcuma
dreamcoder status   # → System overview

# Automatic (via systemd timer)
# Switches at 07:00 (light) and 18:00 (dark)
systemctl --user status dreamcoder-theme-auto.timer
```

## Rollback

```bash
# Option A: From backup manifest
ls ~/.local/share/dreamcoder/backups/
# Pick the latest backup id and restore it:
./scripts/dreamcoder backup restore <backup_id> --json

# Option B: Manual per component
rm ~/.config/hypr/dreamcoder-colors.lua
rm ~/.config/btop/themes/dreamcoder.theme
sed -i 's/color_theme = "dreamcoder"/color_theme = "matugen"/' ~/.config/btop/btop.conf

# The dreamcoder-colors loader lives in the generated ~/.config/hypr/custom.lua;
# with dreamcoder-colors.lua removed, its guard skips the require.

# Disable timer
systemctl --user disable --now dreamcoder-theme-auto.timer
```

## Troubleshooting

| Problem                         | Solution                                                    |
| ------------------------------- | ----------------------------------------------------------- |
| `dreamcoder: command not found` | Ensure `~/.local/bin` is in your PATH                       |
| Ghostty theme not loading       | Verify `~/.config/ghostty/config` has `theme = dreamcoder`  |
| Kitty colors not showing        | Check `include colors-dreamcoder.conf` in `kitty.conf`      |
| Hyprland colors look wrong      | Run `hyprctl reload` after mode switch                      |
| Btop theme not found            | Run `dreamcoder-theme sync` to regenerate                   |
| Auto-timer not switching        | Check `systemctl --user status dreamcoder-theme-auto.timer` |
| Doctor reports missing files    | Run `./scripts/dreamcoder repair`                           |

### Upstream upgrades that re-point Dreamcoder targets

An ML4W upgrade can re-point `~/.config/fish`, `~/.config/kitty`,
`~/.config/fastfetch`, `~/.bashrc`, or `~/.zshrc` to its own tree under
`~/.mydotfiles`. `./scripts/dreamcoder repair` (and `install`) relinks the
Dreamcoder stow modules (`DreamcoderShell`, `DreamcoderKitty`,
`DreamcoderGhostty`, `DreamcoderFastfetch`, `DreamcoderWarp`, `DreamcoderBat`,
`DreamcoderSystemd`) before applying hooks:

- a stow dry run lists every blocking target: regular files, and symlinks stow
  does not own (foreign trees or absolute links into the repo);
- each one is moved, never deleted, to
  `~/.local/share/dreamcoder/install-conflicts/<backup-id>/<path under $HOME>`;
  symlinks move as links, so the tree they point to stays untouched;
- stow then links the modules. Anything the upstream tree held that you still
  need (for example fish universal variables in its `fish_variables`) must be
  copied back by hand.
