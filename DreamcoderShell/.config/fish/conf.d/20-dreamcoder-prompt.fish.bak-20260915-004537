if status is-interactive
    functions -e fish_prompt 2>/dev/null
    command -q starship; and starship init fish | source
    functions -q enable_transience; and enable_transience

    # Auto-detect theme mode changes from systemd timer on every prompt.
    functions -c fish_prompt _dreamcoder_starship_prompt
    function fish_prompt
        set -l cache "$HOME/.cache/dreamcoder/cursor-cli.env"
        if test -f "$cache"
            set -l cached (grep DREAMCODER_THEME_MODE "$cache" | cut -d= -f2 | tr -d \")
            if test -n "$cached" -a "$cached" != "$DREAMCODER_THEME_MODE"
                set -gx DREAMCODER_THEME_MODE "$cached"
                set -l td "$DREAMCODER_DOTS_DIR/themes/dreamcoder"
                switch "$cached"
                    case dark
                        set -gx BAT_THEME Dreamcoder-Dark
                    case '*'
                        set -gx BAT_THEME Dreamcoder-Light
                end
                set -l lf "$td/ls-colors-dreamcoder-$cached.sh"
                if test -f "$lf"
                    set -l v (bash -c "source '$lf' 2>/dev/null && echo \$LS_COLORS")
                    test -n "$v"; and set -gx LS_COLORS "$v"
                    set v (bash -c "source '$lf' 2>/dev/null && echo \$EZA_COLORS")
                    test -n "$v"; and set -gx EZA_COLORS "$v"
                end
                set -l ff "$td/fzf-dreamcoder-$cached.sh"
                if test -f "$ff"
                    set -l v (bash -c "source '$ff' 2>/dev/null && echo \$FZF_DEFAULT_OPTS")
                    test -n "$v"; and set -gx FZF_DEFAULT_OPTS "$v"
                end
            end
        end
        _dreamcoder_starship_prompt
    end
end
