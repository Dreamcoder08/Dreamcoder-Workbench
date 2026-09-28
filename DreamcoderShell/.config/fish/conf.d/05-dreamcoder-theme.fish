# Dreamcoder visual theme contract for Fish shells.
# Sources generated theme files from themes/dreamcoder/ (synced from tokens.json).
# No hardcoded colors — the .sh files are the single source of truth.

# The persisted live mode wins over an inherited value: a long-lived parent
# (e.g. a Herdr server started before the last mode switch) exports a stale one.
set -l mode_cache "$HOME/.cache/dreamcoder/cursor-cli.env"
if test -f "$mode_cache"
    set -l persisted (string match -rg '^(?:export )?DREAMCODER_THEME_MODE="?(light|dark)"?$' <"$mode_cache")
    test -n "$persisted"; and set -gx DREAMCODER_THEME_MODE $persisted[1]
end
set -q DREAMCODER_THEME_MODE; or set -gx DREAMCODER_THEME_MODE dark
set -q COLORTERM; or set -gx COLORTERM truecolor
set -gx FORCE_COLOR 3
set -gx CLICOLOR_FORCE 1
set -e NO_COLOR

set -q DREAMCODER_DOTS_DIR; or set -gx DREAMCODER_DOTS_DIR "$HOME/Documents/PROYECTOS/dreamcoder-dots"
set -l theme_dir "$DREAMCODER_DOTS_DIR/themes/dreamcoder"

# BAT — simple mode toggle
switch "$DREAMCODER_THEME_MODE"
    case dark
        set -gx BAT_THEME Dreamcoder-Dark
    case '*'
        set -gx BAT_THEME Dreamcoder-Light
end
set -q BAT_STYLE; or set -gx BAT_STYLE "auto,changes,header,grid"
set -q BAT_TABS; or set -gx BAT_TABS 4

# LS_COLORS / EZA_COLORS — source from generated theme file
set -l ls_file "$theme_dir/ls-colors-dreamcoder-$DREAMCODER_THEME_MODE.sh"
if test -f "$ls_file"
    set -l ls_val (bash -c "source '$ls_file' 2>/dev/null && echo \$LS_COLORS")
    test -n "$ls_val"; and set -gx LS_COLORS "$ls_val"
    set -l eza_val (bash -c "source '$ls_file' 2>/dev/null && echo \$EZA_COLORS")
    test -n "$eza_val"; and set -gx EZA_COLORS "$eza_val"
end

# FZF — source from generated theme file
set -l fzf_file "$theme_dir/fzf-dreamcoder-$DREAMCODER_THEME_MODE.sh"
if test -f "$fzf_file"
    set -l fzf_val (bash -c "source '$fzf_file' 2>/dev/null && echo \$FZF_DEFAULT_OPTS")
    test -n "$fzf_val"; and set -gx FZF_DEFAULT_OPTS "$fzf_val"
end
