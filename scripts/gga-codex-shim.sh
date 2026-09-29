#!/usr/bin/env bash
# GGA-only model pin for the Codex CLI, installed as ~/.config/gga/bin/codex.
#
# Gentleman Guardian Angel (gga) runs `codex exec "<prompt>"` with no model
# options, so reviews would follow whatever ~/.codex/config.toml selects for
# interactive work. This shim sits first on PATH and, only for `codex exec`
# calls made by a gga process, injects the pinned model and reasoning effort.
# Every other invocation (interactive codex, other tools) passes through
# untouched, and an explicit -m/--model always wins.
#
# The pin lives in ~/.config/gga/pin.env (GGA_PIN_MODEL, GGA_PIN_EFFORT) and
# never in ~/.config/gga/config, which `gentle-ai sync` rewrites wholesale.
# Installed by scripts/install-gga-pin.sh; see docs/configuration/gga.md.
set -euo pipefail

readonly DEFAULT_MODEL="gpt-6.1-sol"
readonly DEFAULT_EFFORT="medium"
readonly MAX_ANCESTORS=10
# Linux procfs; without it the shim never pins and passes every call through.
readonly PROC_ROOT="${GGA_SHIM_PROC_ROOT:-/proc}"

self_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

find_real_codex() {
  local candidate
  while IFS= read -r candidate; do
    [[ "$(cd "$(dirname "${candidate}")" && pwd -P)" == "${self_dir}" ]] && continue
    printf '%s\n' "${candidate}"
    return 0
  done < <(type -ap codex)
  return 1
}

# True when one of the first MAX_ANCESTORS ancestors is a gga process: its
# comm is `gga` (the kernel names a script after its file) or it runs an
# interpreter whose script argument is named gga.
has_gga_ancestor() {
  local pid="${PPID}" depth comm ppid arg
  local -a argv
  [[ -d "${PROC_ROOT}/self" ]] || return 1
  for ((depth = 0; depth < MAX_ANCESTORS; depth++)); do
    [[ "${pid}" =~ ^[0-9]+$ && "${pid}" -gt 1 && -r "${PROC_ROOT}/${pid}/status" ]] || return 1
    comm="$(cat "${PROC_ROOT}/${pid}/comm" 2>/dev/null)" || return 1
    [[ "${comm}" == "gga" ]] && return 0
    argv=()
    while IFS= read -r -d '' arg; do argv+=("${arg}"); done <"${PROC_ROOT}/${pid}/cmdline" 2>/dev/null || true
    for arg in "${argv[@]:0:2}"; do
      [[ "${arg##*/}" == "gga" ]] && return 0
    done
    ppid="$(sed -n 's/^PPid:[[:space:]]*//p' "${PROC_ROOT}/${pid}/status" 2>/dev/null)" || return 1
    pid="${ppid}"
  done
  return 1
}

has_explicit_model() {
  local arg
  for arg in "$@"; do
    case "${arg}" in -m | --model | --model=* | -m?*) return 0 ;; esac
  done
  return 1
}

# Read GGA_PIN_MODEL / GGA_PIN_EFFORT from pin.env without executing it.
read_pin() {
  local key="$1" fallback="$2" file line value=""
  file="${XDG_CONFIG_HOME:-${HOME}/.config}/gga/pin.env"
  if [[ -r "${file}" ]]; then
    while IFS= read -r line || [[ -n "${line}" ]]; do
      line="${line#export }"
      [[ "${line}" == "${key}="* ]] || continue
      value="${line#"${key}"=}"
      value="${value#[\"\']}"
      value="${value%[\"\']}"
    done <"${file}"
  fi
  printf '%s\n' "${value:-${fallback}}"
}

real="$(find_real_codex)" || {
  echo "gga codex shim: the real codex CLI was not found on PATH" >&2
  exit 127
}

if [[ "${1:-}" == "exec" ]] && ! has_explicit_model "$@" && has_gga_ancestor; then
  shift
  model="$(read_pin GGA_PIN_MODEL "${DEFAULT_MODEL}")"
  effort="$(read_pin GGA_PIN_EFFORT "${DEFAULT_EFFORT}")"
  exec "${real}" exec -m "${model}" -c "model_reasoning_effort=${effort}" "$@"
fi
exec "${real}" "$@"
