# Dreamcoder modern CLI aliases (shared for bash & zsh)
# Gracefully degrades when modern tools aren't installed.

## ─── Git shortcuts ────────────────────────────────────
alias g='git'
alias gs='git status'
alias gp='git push'
alias gl='git log --oneline --graph --all'
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
alias groot='cd "$(git rev-parse --show-toplevel 2>/dev/null)"'

## ─── Modern CLI replacements ──────────────────────────
# eza (better ls)
if command -v eza &>/dev/null; then
  alias ll='eza -la --icons --group-directories-first'
  alias la='eza -a --icons --group-directories-first'
  alias lt='eza -T --icons --group-directories-first'
  alias l1='eza -1 --icons'
else
  alias ll='ls -lahF'
  alias la='ls -A'
fi

# bat (better cat)
command -v bat &>/dev/null && alias cat='bat --paging=never'

# fd (better find)
command -v fd &>/dev/null && alias find='fd'

# rg (better grep)
command -v rg &>/dev/null && alias grep='rg'

# zoxide (better cd)
command -v zoxide &>/dev/null && alias cd='z' && alias cdi='zi'

# Modern replacements (graceful fallback)
command -v procs &>/dev/null && alias ps='procs'
command -v btm &>/dev/null && alias top='btm'
command -v dua &>/dev/null && alias du='dua'
command -v duf &>/dev/null && alias df='duf'
command -v sd &>/dev/null && alias sed='sd'
command -v tldr &>/dev/null && alias help='tldr'

## ─── Quick navigation ─────────────────────────────────
alias home='cd ~'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias docs='cd "${DREAMCODER_DOTS_DIR:-$HOME/Documents/PROYECTOS/dreamcoder-dots}/docs"'

## ─── Extract function ─────────────────────────────────
extract() {
  if [ $# -eq 0 ]; then
    echo "Usage: extract <archive> [output_dir]"
    return 1
  fi
  # Two statements: in bash a single `local` expands every value before any is
  # assigned, so dir would not see file (ShellCheck SC2318).
  local file="$1"
  local dir="${2:-${file%.*}}"
  case "$file" in
  *.tar.gz | *.tgz) tar -xzf "$file" -C "$(dirname "$file")" 2>/dev/null || tar -xzf "$file" ;;
  *.tar.bz2 | *.tbz2) tar -xjf "$file" ;;
  *.tar.xz | *.txz) tar -xJf "$file" ;;
  *.tar.zst) tar --zstd -xf "$file" ;;
  *.tar) tar -xf "$file" ;;
  *.gz) gunzip -k "$file" ;;
  *.bz2) bunzip2 -k "$file" ;;
  *.xz) unxz -k "$file" ;;
  *.zip) unzip "$file" -d "$dir" ;;
  *.rar) unrar x "$file" "$dir" ;;
  *.7z) 7z x "$file" "-o$dir" ;;
  *)
    echo "extract: unknown archive: $file" >&2
    return 1
    ;;
  esac
}
