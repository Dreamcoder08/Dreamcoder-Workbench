function hwt --description 'Create or reuse <repo>/.worktrees/<branch> and open the Herdr squad there'
    argparse h/help n/no-squad -- $argv; or return 1
    if set -q _flag_help; or test (count $argv) -lt 1
        echo "usage: hwt [-n|--no-squad] <branch> [base]" >&2
        echo "  Creates <repo>/.worktrees/<branch> (new branch from base, default HEAD)" >&2
        echo "  and opens two Gentle Shell panes and Claude Code there with hsquad." >&2
        set -q _flag_help; and return 0; or return 1
    end
    set -l branch $argv[1]
    set -l base HEAD
    test (count $argv) -gt 1; and set base $argv[2]
    set -l common (git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
    if test -z "$common"
        echo "hwt: not inside a git repository" >&2
        return 1
    end
    # From any worktree, new checkouts go under the main repository.
    set -l root (path dirname -- $common)
    set -l dir $root/.worktrees/(string replace -a / - -- $branch)
    if not test -d $dir
        # Keep checkouts out of git status without touching the shared .gitignore.
        mkdir -p $common/info
        grep -qxF /.worktrees/ $common/info/exclude 2>/dev/null; or echo /.worktrees/ >>$common/info/exclude
        if git -C $root show-ref --verify --quiet refs/heads/$branch
            git -C $root worktree add $dir $branch; or return 1
        else
            git -C $root worktree add -b $branch $dir $base; or return 1
        end
    end
    set -q _flag_no_squad; and begin
        echo $dir
        return 0
    end
    hsquad $dir
end
