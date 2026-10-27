# Configure a terminal multiplexer

Choose Tmux or Zellij and inspect the corresponding repository configuration before installing it. The canonical desktop installer does not list either as a Stow module; generating a theme is not the same as installing a multiplexer configuration. See [INSTALL.md](../../INSTALL.md) for the desktop path and platform-specific component guides.

## Tmux

`DreamcoderTmux/.tmux.conf` conditionally sources the Gentleman.Dots Tmux configuration from `$HOME/Gentleman.Dots/GentlemanTmux/tmux.conf`, then loads `~/.config/tmux/tmux-dreamcoder-base.conf`. Make both paths available if using this layer. The upstream configuration supplies the base and its prefix; the local config adds:

| Action | Binding |
|--------|---------|
| Horizontal / vertical split | prefix + `\|` / prefix + `-` |
| Navigate panes | Alt + h/j/k/l |
| Reload configuration | prefix + r |
| Detach | prefix + D or prefix + Ctrl+d |
| Session picker | prefix + f (requires fzf) |

The local config declares `tmux-continuum`; other plugin setup belongs to the upstream base. The generated active theme is `~/.config/tmux/tmux-dreamcoder.conf` by default. Ensure the installed configuration reads the relevant theme files, then reload it or restart the session as needed.

## Zellij

`DreamcoderZellij/.config/zellij/config.kdl` declares Alt+n for a new tab, Alt+j/k for previous/next tab, Alt+1–5 for tab selection and Ctrl+t for tab mode. The `dreamcoder` layout has a base pane and a top tab/time bar using `zjstatus`; it is a layout file, not a claim that it is selected by default.

The theme sync updates the Zellij selector and generates dark/light KDL themes. Make those themes available to the installed Zellij configuration and restart or reload as supported by your version; writing files alone does not ensure a running session changes.

For mode selection and synchronization, see the [theme system guide](theme-system.md); for terminal setup, see [terminal configuration](terminal-config.md).
