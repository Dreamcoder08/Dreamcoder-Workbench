# shellcheck shell=bash disable=SC1090,SC1091
# Dreamcoder interactive Bash. No errexit/nounset/pipefail here: in an
# interactive shell they close the terminal on the first failing command.
[[ -z "${TERM:-}" || "${TERM}" == "dumb" ]] && export TERM="xterm-256color"
export COLORTERM="${COLORTERM:-truecolor}"
[[ "${-}" != *i* ]] && return
shopt -s histappend cmdhist autocd cdspell globstar
export HISTFILE="${HOME}/.bash_history"
HISTSIZE=50000
HISTFILESIZE=100000
export HISTCONTROL=ignoreboth:erasedups
PATH_DIRS=("${HOME}/.local/bin" "${HOME}/.opencode/bin" "${HOME}/.cargo/bin" "${HOME}/.volta/bin" "${HOME}/.nix-profile/bin" "${HOME}/.config")
for dir in "${PATH_DIRS[@]}"; do
    [[ -d "${dir}" && ":${PATH}:" != *":${dir}:"* ]] && export PATH="${dir}:${PATH}"
done
BUN_COMPLETION="${HOME}/.bun/_bun"
[[ -f "${BUN_COMPLETION}" ]] && source "${BUN_COMPLETION}"
export BUN_INSTALL="${HOME}/.bun"
[[ -d "${BUN_INSTALL}/bin" ]] && export PATH="${BUN_INSTALL}/bin:${PATH}"
# gga reviews: Codex provider with the pinned model shim first (docs/configuration/gga.md).
_dc_gga_bin="${XDG_CONFIG_HOME:-${HOME}/.config}/gga/bin"
if [[ -d "${_dc_gga_bin}" ]]; then
    export GGA_PROVIDER="codex"
    # Shared with the gga config block: the shim dir must come first, exactly once.
    # shellcheck source=../lib/gga-shim-path.sh
    [[ -f "${_dc_gga_bin%/bin}/shim-path.sh" && -r "${_dc_gga_bin%/bin}/shim-path.sh" ]] && source "${_dc_gga_bin%/bin}/shim-path.sh"
fi
unset _dc_gga_bin
SHELL_DIR="${XDG_CONFIG_HOME:-${HOME}/.config}/shell"
for group in core aliases functions; do
    for file in "${SHELL_DIR}/${group}"/*.sh; do [[ -f "${file}" ]] && source "${file}"; done
done
command -v fzf >/dev/null && eval "$(fzf --bash)"
if command -v starship >/dev/null; then
    eval "$(starship init bash)"
    declare -F enable_transience >/dev/null && enable_transience
fi
command -v zoxide >/dev/null && eval "$(zoxide init bash)"
[[ -f "${HOME}/.cargo/env" ]] && source "${HOME}/.cargo/env"
_dc_fnm_dir="${HOME}/.local/share/fnm"
[[ -d "${_dc_fnm_dir}" && ":${PATH}:" != *":${_dc_fnm_dir}:"* ]] && export PATH="${_dc_fnm_dir}:${PATH}"
command -v fnm >/dev/null && eval "$(fnm env --use-on-cd --shell bash)"
unset PATH_DIRS dir group file BUN_COMPLETION SHELL_DIR _dc_fnm_dir
