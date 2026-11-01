# Dreamcoder terminal shortcuts.
if status is-interactive
    alias c='clear'
    alias cls='clear'
    alias q='exit'

    set -q DREAMCODER_DOTS_DIR; or set -gx DREAMCODER_DOTS_DIR $HOME/Documents/PROYECTOS/dreamcoder08/dreamcoder-workbench

    # Dreamcoder theme switcher — updates shell env vars after sync
    function dreamcoder --description 'Switch Dreamcoder theme and reload shell colors'
        # Run the sync script
        $DREAMCODER_DOTS_DIR/scripts/dreamcoder $argv

        # Reload DREAMCODER_THEME_MODE from cache (updated by apply-theme-mode.sh)
        set -l cache_file "$HOME/.cache/dreamcoder/cursor-cli.env"
        if test -f "$cache_file"
            set -l cached_mode (grep DREAMCODER_THEME_MODE "$cache_file" | cut -d= -f2 | tr -d '"')
            test -n "$cached_mode"; and set -gx DREAMCODER_THEME_MODE "$cached_mode"
        end

        # Update BAT_THEME immediately
        switch "$DREAMCODER_THEME_MODE"
            case dark
                set -gx BAT_THEME Dreamcoder-Dark
            case '*'
                set -gx BAT_THEME Dreamcoder-Light
        end

        # Reload LS_COLORS + EZA_COLORS from generated theme file
        set -l theme_dir "$DREAMCODER_DOTS_DIR/themes/dreamcoder"
        set -l ls_file "$theme_dir/ls-colors-dreamcoder-$DREAMCODER_THEME_MODE.sh"
        if test -f "$ls_file"
            set -l ls_val (bash -c "source '$ls_file' 2>/dev/null && echo \$LS_COLORS")
            test -n "$ls_val"; and set -gx LS_COLORS "$ls_val"
            set -l eza_val (bash -c "source '$ls_file' 2>/dev/null && echo \$EZA_COLORS")
            test -n "$eza_val"; and set -gx EZA_COLORS "$eza_val"
        end

        # Reload FZF colors from generated theme file
        set -l fzf_file "$theme_dir/fzf-dreamcoder-$DREAMCODER_THEME_MODE.sh"
        if test -f "$fzf_file"
            set -l fzf_val (bash -c "source '$fzf_file' 2>/dev/null && echo \$FZF_DEFAULT_OPTS")
            test -n "$fzf_val"; and set -gx FZF_DEFAULT_OPTS "$fzf_val"
        end

        echo "🎨 Shell theme reloaded: $DREAMCODER_THEME_MODE mode"
    end

    ## ─── Git shortcuts ────────────────────────────────────
    alias g='git'
    alias gs='git status'
    alias gp='git push'
    # gl is defined as an abbreviation (git log --oneline -20) in
    # 60-abbreviations.fish; the full graph lives in glg below, so the
    # divergent alias was removed to avoid the abbr/alias shadow trap.
    alias gd='git diff'
    alias gc='git commit'
    alias gco='git checkout'
    alias gb='git branch'
    alias ga='git add'
    alias gpl='git pull'
    alias gst='git stash'
    alias glg='git log --oneline --graph --all --decorate'
    alias gundo='git reset --soft HEAD~1'
    alias gcleanup='git branch --merged | grep -v "\*\|main\|master" | xargs -r git branch -d'
    alias gconflicts='git diff --name-only --diff-filter=U'
    alias groot='git rev-parse --show-toplevel'

    ## ─── Modern CLI replacements ──────────────────────────
    # eza (better ls)
    if command -q eza
        alias ll='eza -la --icons --group-directories-first'
        alias la='eza -a --icons --group-directories-first'
        alias lt='eza -T --icons --group-directories-first'
        alias l1='eza -1 --icons'
    else
        alias ll='ls -lahF'
        alias la='ls -A'
        alias lt='tree -C 2>/dev/null; or ls -R'
    end

    # bat (better cat)
    if command -q bat
        alias cat='bat --paging=never'
    end

    # fd (better find)
    if command -q fd
        alias find='fd'
    end

    # rg (better grep)
    if command -q rg
        alias grep='rg'
    end

    # zoxide (better cd)
    if command -q zoxide
        alias cd='z'
        alias cdi='zi'
    end

    # Modern replacements (graceful fallback)
    if command -q procs
        alias ps='procs'
    end
    if command -q btm
        alias top='btm'
    end
    if command -q dua
        alias du='dua'
    end
    if command -q duf
        alias df='duf'
    end
    if command -q sd
        alias sed='sd'
    end

    ## ─── Quick navigation ─────────────────────────────────
    alias home='cd ~'
    alias ..='cd ..'
    alias ...='cd ../..'
    alias ....='cd ../../..'
    alias docs='cd $DREAMCODER_DOTS_DIR/docs'
end
