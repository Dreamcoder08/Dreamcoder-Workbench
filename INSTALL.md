# Dreamcoder Workbench — Installation Guide

> Complete installation in 3 steps: Gentleman.Dots → ML4W → Dreamcoder Workbench.

## Prerequisites

- **Arch Linux** (or a derivative)
- `git`, `stow`, `python3` installed
- Internet connection

---

## Step 1: Gentleman.Dots

Gentleman.Dots provides the base for Neovim, shells, terminals, and multiplexers.

### Option A: Homebrew (recommended)

```bash
brew install Gentleman-Programming/tap/gentleman-dots
gentleman-dots
```

### Option B: Direct download

```bash
curl -fsSL https://github.com/Gentleman-Programming/Gentleman.Dots/releases/latest/download/gentleman-installer-linux-amd64 -o gentleman.dots
chmod +x gentleman.dots
./gentleman.dots
```

### Option C: Manual

```bash
git clone https://github.com/Gentleman-Programming/Gentleman.Dots.git
cd Gentleman.Dots
./install.sh
```

Follow the installer TUI to select:

- Shell: Fish (recommended), Zsh, or Nushell
- Terminal: Ghostty (recommended) or Kitty
- Multiplexer: Tmux or Zellij
- Editor: Neovim

> More info: [Gentleman.Dots](https://github.com/Gentleman-Programming/Gentleman.Dots)

---

## Step 2: ML4W OS

ML4W provides the full Hyprland desktop base.

```bash
bash <(curl -s https://ml4w.com/os/stable)
```

This installs:

- **Hyprland**: animations, keybinds, monitors, layouts, windows, workspaces
- **Waybar**: status bar with modules
- **Rofi**: app launcher
- **Dunst**: notifications
- **GTK 3.0/4.0**: theme and config
- **Btop**: system monitor
- **Matugen**: dynamic color generation

> More info: [ML4W OS](https://ml4w.com/os/)

---

## Step 3: Dreamcoder Workbench

Dreamcoder Workbench applies its visual layer over Gentleman + ML4W.

### Clone

```bash
git clone git@github.com:Dreamcoder08/Dreamcoder-Workbench.git ~/Documents/PROYECTOS/Dreamcoder-Workbench
cd ~/Documents/PROYECTOS/Dreamcoder-Workbench
```

### Install the Python package (theme engine)

```bash
pip install -e .
# or, with uv:
uv sync
```

### Install

```bash
./scripts/dreamcoder install
```

This:

1. Creates backups of existing configs
2. Stows the modules (DreamcoderShell, DreamcoderKitty, DreamcoderGhostty, DreamcoderFastfetch, DreamcoderWarp, DreamcoderBat, DreamcoderSystemd)
3. Installs the theme hooks for each app
4. Activates the systemd timer for auto-theme switching
5. Runs the first theme sync

### Verify

```bash
./scripts/dreamcoder doctor     # Full health check
./scripts/dreamcoder status      # System status
```

---

## Post-Installation

### Tmux

If you use Tmux with TPM:

```bash
tmux
prefix + I   # Install plugins
```

### Neovim

Open Neovim. LazyVim installs the plugins automatically:

```bash
nvim
:Lazy sync
```

### Auto Theme Switching

The systemd timer activates automatically. To verify:

```bash
systemctl --user status dreamcoder-theme-auto.timer
```

The timer switches modes by schedule:

- **07:00-18:00** → Light
- **18:00-07:00** → Dark

---

## Troubleshooting

### "Theme files not found"

Make sure you installed Gentleman.Dots and ML4W first. Dreamcoder Workbench is an overlay, not a replacement.

### "Error: stow not found"

```bash
sudo pacman -S stow
```

### "Colors not updating"

```bash
dreamcoder dark    # Force dark mode
dreamcoder light   # Force light mode
```

### "Neovim colorscheme not loading"

Add this to `~/.config/nvim/init.lua`:

```lua
vim.cmd.colorscheme("dreamcoder")
```

---

## References

- [Gentleman.Dots](https://github.com/Gentleman-Programming/Gentleman.Dots)
- [ML4W OS](https://ml4w.com/os/)
- [Dreamcoder Workbench docs index](docs/README.md)
- [Architecture Docs](docs/architecture/)
