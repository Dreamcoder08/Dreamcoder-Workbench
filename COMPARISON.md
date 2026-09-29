# Dreamcoder Workbench — Comparison

> Why do you need Dreamcoder Workbench if you already have Gentleman.Dots + ML4W?
> Because Dreamcoder Workbench is the layer neither of them has: **visual health, identity, and AI integration**.

## Feature Comparison

| Feature               | Gentleman.Dots         | ML4W                | **Dreamcoder Workbench**       |
| --------------------- | ---------------------- | ------------------- | ------------------------------ |
| **Theme Engine**      | — Catppuccin static    | ✓ Matugen dynamic   | ✓ **Token-based + WCAG/APCA**  |
| **Dark/Light**        | — Dark only            | ✓ Light/Dark        | ✓ **+ scheduled switching**    |
| **Accessibility**     | —                      | —                   | ✓ **WCAG 4.5:1 + APCA 75**     |
| **AI Session Prompt** | —                      | —                   | ✓ **Live AI session state**    |
| **Neovim Plugins**    | ✓ 29 (LazyVim)         | —                   | ◐ Dreamcoder colorscheme       |
| **Hyprland Config**   | —                      | ✓ Full              | ◐ Color overlay                |
| **Shell Configs**     | ✓ Fish/Zsh/Nushell     | ✓ Fish/Bash         | ◐ Aliases + 19 functions       |
| **Ghostty Shaders**   | ✓ 53 GLSL              | —                   | ◐ Uses Gentleman's shaders     |
| **Go TUI Installer**  | ✓ Bubbletea            | ✓ bash              | ✓ Bubbletea + Vim Trainer      |
| **Starship Prompt**   | — Basic                | — Basic             | ✓ **17 modules + AI state**    |
| **Python Theme Lib**  | —                      | —                   | ✓ **Published on PyPI**        |
| **Vim Trainer**       | ✓ RPG-style            | —                   | ✓ RPG-style                    |
| **Auto Theme Switch** | —                      | ✓ Manual            | ✓ **Systemd timer**            |
| **CI/CD**             | —                      | —                   | ✓ GitHub Actions               |

> ✓ = full support · ◐ = Dreamcoder Workbench overlay · — = not provided

---

## What stays from Gentleman.Dots

After installing Dreamcoder Workbench, everything Gentleman provides keeps working exactly the same:

| Component           | What stays                    | How Dreamcoder Workbench uses it                       |
| ------------------- | ----------------------------- | ------------------------------------------------------ |
| **Neovim**          | init.lua + 29 plugins         | Adds `colorscheme dreamcoder` to init.lua              |
| **Ghostty shaders** | 53 GLSL                       | Uses `dreamcoder-cursor-pulse.glsl` by default         |
| **Tmux**            | `~/.tmux.conf` with TPM + kanagawa | `apply-theme-mode.sh` overwrites kanagawa colors  |
| **Zellij**          | `config.kdl` with plugins     | Switches `theme "dreamcoder-{mode}"`                   |
| **Fish/Zsh/Nushell**| Base configs                  | Adds `conf.d/dreamcoder-*.fish`                        |
| **Vim Trainer**     | Full RPG                      | No changes                                            |
| **Starship**        | Base config (if any)          | Replaces it with 17 modules                            |

## What stays from ML4W

| Component      | What stays                           | How Dreamcoder Workbench uses it                 |
| -------------- | ------------------------------------ | ------------------------------------------------ |
| **Hyprland**   | hyprland.conf + animations + keybinds| Adds `colors.{conf,lua}` with color variables    |
| **Waybar**     | `config.jsonc` + `style.css`         | Generates `colors.css` with `@import`            |
| **Rofi**       | `config.rasi`                        | Generates `colors.rasi` with `@import`           |
| **Dunst**      | `dunstrc`                            | Generates `dreamcoder-dunst.conf` with `[include]` |
| **GTK 3.0/4.0**| `settings.ini`                       | Switches `prefer-dark-theme` at runtime          |
| **Btop**       | `btop.conf`                          | Adds `dreamcoder.theme`                          |
| **Matugen**    | Color pipeline                       | Dreamcoder Workbench runs matugen on each mode switch |

---

## What Dreamcoder Workbench ADDS

### Token Engine with WCAG/APCA

```json
{
  "guardrails": {
    "minimum_text_contrast": 4.5,
    "minimum_apca_body": 75,
    "avoid_pure_black_white": true
  }
}
```

No other dotfiles setup does this. Every color is validated against WCAG 4.5:1 and APCA.

### 2 Color Modes

| Mode    | Name              | Schedule       |
| ------- | ----------------- | -------------- |
| 🌙 Dark | Anthracite Steel  | 18:00-07:00    |
| ☀️ Light| Cocoa/Lúcuma      | 07:00-18:00    |

### AI Session State in the Prompt

When Claude Code or OpenCode are active, the prompt shows:

```
⎔ claude-4 42K
```

(only visible when a session is active)

### 19 Shell Functions

| Function      | Purpose                                      |
| ------------- | -------------------------------------------- |
| `extract`     | Extract any archive format                   |
| `sysupdate`   | Update pacman + brew + flatpak               |
| `ports`       | Show listening ports                         |
| `killport`    | Kill a process on a port                     |
| `dots`        | cd to the repo                               |
| `cheat`       | Quick cheat sheet (tldr wrapper)             |
| `http`        | HTTP request with pretty output (HTTPie wrapper) |
| `logs`        | Tail system logs with filters                |
| `tm-session`  | Tmux session picker                          |
| `tm`          | Smart tmux attach (create or attach)         |
| `tmux-kill-all` | Kill all tmux sessions (careful)          |
| `identity`    | Switch to an identity workspace (personal, founder, dev, research) |
| `id-dev`      | Switch to Dev identity                       |
| `id-founder`  | Switch to Founder identity                   |
| `id-personal` | Switch to Personal identity                  |
| `id-research` | Switch to Research identity                  |
| `dev-dots`    | Launch the dev workspace with Herdr          |
| `sdd-swap`    | Switch SDD profile between chatgpt and deepseek |
| `tl`          | List tmux sessions                           |

### Modern CLI Aliases

```bash
alias ll='eza -la --icons'     # better ls
alias cat='bat --paging=never' # better cat
alias find='fd'                # better find
alias grep='rg'                # better grep
alias cd='z'                   # zoxide smart cd
alias ps='procs'               # better ps
alias top='btm'                # better htop
alias du='dua'                 # better du
alias df='duf'                 # better df
alias sed='sd'                 # better sed
alias help='tldr'              # better man
```

All with graceful fallback if the tool is not installed.

---

## Visual Summary

```
Without Dreamcoder Workbench:
┌─────────────────────────────────────────────┐
│  Gentleman.Dots: Catppuccin                │
│  ML4W: Matugen colors                      │
│  No WCAG, no AI prompt, no auto switching  │
└─────────────────────────────────────────────┘

With Dreamcoder Workbench:
┌─────────────────────────────────────────────┐
│  Gentleman.Dots: Neovim, shaders, tmux     │
│  ML4W: Hyprland, waybar, rofi, dunst       │
│  Dreamcoder Workbench: WCAG/APCA tokens    │
│  + AI prompt                               │
└─────────────────────────────────────────────┘
```
