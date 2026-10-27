# Configure your shell

Choose the shell you use, then review its configuration before installing it. The [installation guide](../../INSTALL.md) covers the desktop overlay; individual integrations and platforms have different prerequisites.

## Fish and Zsh

- Fish uses `DreamcoderShell/.config/fish/config.fish` and its `conf.d` fragments. Its theme fragment reads generated LS_COLORS and fzf values through Bash and selects a Bat theme. Set `DREAMCODER_DOTS_DIR` to your clone: its fallback is a machine-specific path and may not exist on your system. Interactive Fish can start Herdr when it is installed and no multiplexer is already active.
- Interactive Zsh uses `DreamcoderShell/.zshrc`, optionally loads Oh My Zsh and available plugins, and sources existing generated snippets from `themes/dreamcoder` in the clone. It initializes optional fzf, zoxide and Starship when available. It resolves the clone from `DREAMCODER_DOTS_DIR` or the installed `.zshrc` link.

Both configurations prefer a cached live mode over an inherited `DREAMCODER_THEME_MODE`, defaulting to dark when no mode is set. Fish and Zsh have different cache lookup details; inspect their fragments if using a custom cache location. Restart the shell to pick up installed configuration. The [theme system guide](theme-system.md) explains generation and mode changes; generating snippets does not install shell configuration.

## NetworkManager TUI colors

Run `nmtui` in Fish or Zsh to use the `dreamcoder-nmtui` launcher when it is
available on `PATH`; otherwise the shell runs the original command. The repository
Waybar default also launches `kitty dreamcoder-nmtui` for its network action.
Existing personal Waybar configurations are not changed automatically.

By default, the launcher sets process-local `NEWT_MONO=1` to inherit the terminal's
foreground and background and use native inverse-video selection. The intentionally
neutral appearance prioritizes a clearly visible selected row over accent hues;
it does not promise brown titles or borders. Other Newt programs and the terminal's
ANSI palette are unchanged.

Newt treats any present `NEWT_MONO` value as monochrome, including `0` and an
empty value. Setting it to `0` does not restore color. To use custom colors,
remove `NEWT_MONO` from the child environment and supply one of the explicit
color-family overrides described below.

When color mode is active, the launcher's defaults use terminal-default panels
and shadow, brown focus in light mode, blue focus in dark mode, red errors, and
gray disabled controls. These are terminal palette names, not an exact-RGB guarantee.

Mode comes from recognized `export DREAMCODER_THEME_MODE=light` or `dark` lines in
`${XDG_CACHE_HOME:-$HOME/.cache}/dreamcoder/cursor-cli.env` (single or double quotes
are also accepted). The cache is read as data, never sourced. Its last valid mode
wins over the inherited `DREAMCODER_THEME_MODE`; without one, a valid inherited
mode is used, otherwise dark.

Any explicit `NEWT_MONO`, `NEWT_COLORS`, `NEWT_COLORS_FILE`, `NMT_NEWT_COLORS`, or
`NMT_NEWT_COLORS_FILE` prevents the launcher from setting `NEWT_MONO` automatically,
even if its value is empty. An already present `NEWT_MONO` still activates Newt's
monochrome mode.
Explicit `NEWT_COLORS` or `NEWT_COLORS_FILE` also preserves your general-widget
color family. Explicit `NMT_NEWT_COLORS` or `NMT_NEWT_COLORS_FILE` preserves your
NetworkManager-specific family independently. Even an empty value opts that family
out of the launcher's defaults. Overrides apply only to the launched process.
All arguments, including `--help`, are forwarded to the original `nmtui`.

Restart the shell after installing its integration and relaunch `nmtui` after a
mode change; an already open TUI does not update in place.

## Customize shortcuts

Shell-specific aliases and functions live under `DreamcoderShell/.config/fish/` and `DreamcoderShell/.config/shell/`. Review the relevant file and optional tool requirements before relying on a shortcut; aliases are not guaranteed to match across shells. Continue with [terminal configuration](terminal-config.md) or the [documentation hub](../README.md).
