set -gx EDITOR nvim
set -gx VISUAL nvim
set -q COLORTERM; or set -gx COLORTERM truecolor
set -q STARSHIP_CONFIG; or set -gx STARSHIP_CONFIG "$HOME/.config/starship.toml"
set -q DREAMCODER_THEME_MODE; or set -gx DREAMCODER_THEME_MODE dark
set -g fish_greeting ""

# Pre-set TMUX_PLUGIN_MANAGER_PATH for plugins (Kanagawa, etc.) that need it
set -q TMUX_PLUGIN_MANAGER_PATH; or set -gx TMUX_PLUGIN_MANAGER_PATH "$HOME/.tmux/plugins/"
set -q DREAMCODER_FASTFETCH_ON_START; or set -gx DREAMCODER_FASTFETCH_ON_START 1

fish_add_path -g "$HOME/.local/bin" "$HOME/.cargo/bin"
fish_add_path -g "$HOME/.volta/bin" "$HOME/.bun/bin"
fish_add_path -g "$HOME/.nix-profile/bin" /nix/var/nix/profiles/default/bin
fish_add_path -g /usr/local/bin
fish_add_path -g "$HOME/go/bin"

if test -d "$HOME/.bun/bin"
    set -gx BUN_INSTALL "$HOME/.bun"
    fish_add_path -g "$BUN_INSTALL/bin"
end

# gga model pin: the shim must come before ~/.local/bin (the real codex). fish keeps
# fish_user_paths ahead of the rest of PATH, so the shim has to join that list (no --path) and
# move to its front. Keep this after the block above: each fish_add_path puts its entries first.
set -l _dc_gga_config_home $HOME/.config
set -q XDG_CONFIG_HOME[1]; and test -n "$XDG_CONFIG_HOME"; and set _dc_gga_config_home $XDG_CONFIG_HOME
test -d $_dc_gga_config_home/gga/bin; and fish_add_path --global --move $_dc_gga_config_home/gga/bin

if status is-interactive
    command -q zoxide; and zoxide init fish | source
end

# Clean PATH: remove stale entries and duplicates
set -gx PATH (string match -v "$HOME/.config" $PATH)
set -gx PATH (string match -v "$HOME/.opencode/bin" $PATH)

# Dedup PATH resolving symlinks (Arch: /bin → /usr/bin, etc.)
set -l seen
set -l clean_path
for dir in $PATH
    # Resolve real path to catch symlinked dirs (e.g. /bin -> /usr/bin)
    set -l real_dir (realpath $dir 2>/dev/null; or echo $dir)
    if not contains -- $real_dir $seen
        set -a clean_path $dir
        set -a seen $real_dir
    end
end
set -gx PATH $clean_path

# Zen Browser - Profile aliases
alias zp="zen-browser -P Personal"
alias zd="zen-browser -P Dev"
alias zf="zen-browser -P Founder"
# Default browser = Zen Personal (for pi login OAuth, git, etc.)
set -gx BROWSER "zen-browser -P Personal"
# Start selected terminal multiplexer (Herdr)
if status is-interactive; and command -q herdr; and not set -q HERDR_ENV; and not set -q TMUX; and not set -q ZELLIJ; and not set -q ORCA_PANE_KEY
    # Herdr spawns panes with $SHELL; pin it to this fish so panes never inherit
    # a foreign login shell (e.g. zsh from the session environment).
    env SHELL=(status fish-path) herdr; or echo "⚠️  Herdr failed to start; continuing in Fish."
end

# ── SDD Profile Aliases ───────────────────────────────────────────
alias sdd-gpt='~/.pi/gentle-ai/sdd-swap chatgpt'
alias sdd-deepseek='~/.pi/gentle-ai/sdd-swap deepseek'
alias sdd-status='~/.pi/gentle-ai/sdd-swap status'

# Redirección de directorios temporales para evitar saturar tmpfs
set -gx TMPDIR "$HOME/.tmp"
set -gx BUN_TMPDIR "$HOME/.tmp"
set -gx ENGRAM_URL http://127.0.0.1:7437

# Enable OpenCode background subagents for new sessions.
set -gx OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS true

# pnpm
set -gx PNPM_HOME "/home/dreamcoder08/.local/share/pnpm"
if not string match -q -- "$PNPM_HOME/bin" $PATH
  set -gx PATH "$PNPM_HOME/bin" $PATH
end
# pnpm end
