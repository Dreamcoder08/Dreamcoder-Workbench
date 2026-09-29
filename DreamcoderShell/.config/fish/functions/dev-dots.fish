# Launch Dreamcoder-dots dev workspace with Herdr
function dev-dots
    set -l project_dir "$HOME/Documents/PROYECTOS/dreamcoder-dots"
    set -l herdr_lib "$project_dir/scripts/herdr-lib.sh"

    if not test -d "$project_dir"
        echo "❌ Project not found: $project_dir"
        return 1
    end

    # Herdr control commands only work from inside a Herdr pane; the fish
    # autostart in config.fish launches or attaches the session.
    if not set -q HERDR_ENV
        echo "❌ Run dev-dots from a Herdr pane (start one with: herdr)"
        return 1
    end

    cd "$project_dir"
    echo "🚀 Dreamcoder-dots workspace ready at $project_dir"

    # Herdr 0.9 has no `tab open`: create each tab, wait for its shell, then run.
    for tool in lazygit nvim
        set -l pane_id (herdr tab create --cwd "$project_dir" --label $tool --no-focus | jq -r '.result.root_pane.pane_id')
        if test -z "$pane_id"; or test "$pane_id" = null
            echo "❌ herdr tab create failed for $tool"
            return 1
        end
        bash -c 'source "$1"; herdr_wait_shell "$2"' _ "$herdr_lib" "$pane_id"
        and herdr pane run "$pane_id" $tool >/dev/null
    end

    # Status line
    echo "  📂 $(pwd)"
    echo "  🌿 $(git branch --show-current 2>/dev/null || echo 'no repo')"
    echo "  🎨 $DREAMCODER_THEME_MODE mode"
end
