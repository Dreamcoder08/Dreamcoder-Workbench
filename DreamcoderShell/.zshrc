# Dreamcoder interactive Zsh ergonomics.
set -euo pipefail
[[ -o interactive ]] || return

export EDITOR="nvim" VISUAL="nvim" COLORTERM="${COLORTERM:-truecolor}"
typeset -U path PATH
path=("${HOME}/.local/bin" "${HOME}/.opencode/bin" "${HOME}/.cargo/bin" "${HOME}/.volta/bin" "${HOME}/.bun/bin" "${HOME}/.nix-profile/bin" "${path[@]}")
BUN_INSTALL="${HOME}/.bun"
[[ -s "${BUN_INSTALL}/_bun" ]] && source "${BUN_INSTALL}/_bun"
[[ -d "${BUN_INSTALL}/bin" ]] && path=("${BUN_INSTALL}/bin" "${path[@]}")
export BUN_INSTALL

# ── Dreamcoder Theme Hooks ─────────────────────────────────────
# Source shell-level theme snippets based on current mode.
_dc_mode="${DREAMCODER_THEME_MODE:-light}"
_dc_theme_dir="${DREAMCODER_DOTS_DIR:-${HOME}/Documents/PROYECTOS/dreamcoder-dots}/themes/dreamcoder"

[[ -f "${_dc_theme_dir}/ls-colors-dreamcoder-${_dc_mode}.sh" ]] && source "${_dc_theme_dir}/ls-colors-dreamcoder-${_dc_mode}.sh"
[[ -f "${_dc_theme_dir}/bat-dreamcoder-${_dc_mode}.sh" ]]    && source "${_dc_theme_dir}/bat-dreamcoder-${_dc_mode}.sh"
[[ -f "${_dc_theme_dir}/fzf-dreamcoder-${_dc_mode}.sh" ]]    && source "${_dc_theme_dir}/fzf-dreamcoder-${_dc_mode}.sh"
# zsh-syntax-highlighting is sourced AFTER the plugin loads (below)

ZSH="${ZSH:-${HOME}/.oh-my-zsh}"
plugins=(git sudo web-search)
for plugin in zsh-autosuggestions zsh-syntax-highlighting archlinux; do
  [[ -d "${ZSH_CUSTOM:-${ZSH}/custom}/plugins/${plugin}" || -d "${ZSH}/plugins/${plugin}" ]] && plugins+=("${plugin}")
done
[[ -f "${ZSH}/oh-my-zsh.sh" ]] && source "${ZSH}/oh-my-zsh.sh"

# Source zsh-syntax-highlighting theme (must be AFTER plugin loads)
[[ -f "${_dc_theme_dir}/zsh-syntax-highlighting-dreamcoder-${_dc_mode}.zsh" ]] && source "${_dc_theme_dir}/zsh-syntax-highlighting-dreamcoder-${_dc_mode}.zsh"

HISTSIZE=50000; SAVEHIST=50000; setopt HIST_IGNORE_DUPS SHARE_HISTORY AUTO_CD
shell_dir="${XDG_CONFIG_HOME:-${HOME}/.config}/shell"
for group in core aliases functions; do for file in "${shell_dir}/${group}"/*.sh(N); do [[ -f "${file}" ]] && source "${file}"; done; done
command -v fzf >/dev/null 2>&1 && eval "$(fzf --zsh)"
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init zsh)"
command -v starship >/dev/null 2>&1 && eval "$(starship init zsh)" && functions -q enable_transience && enable_transience
command -v starship >/dev/null 2>&1 || { [[ -f "${HOME}/.p10k.zsh" ]] && source "${HOME}/.p10k.zsh"; }
[[ -f "${HOME}/.cargo/env" ]] && source "${HOME}/.cargo/env"
[[ "${DREAMCODER_FASTFETCH_ON_START:-0}" == "1" ]] && command -v fastfetch >/dev/null 2>&1 && fastfetch
unset _dc_mode _dc_theme_dir shell_dir group file plugin
