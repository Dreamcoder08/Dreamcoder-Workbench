#!/usr/bin/env bash
# Pin Gentleman Guardian Angel (gga) reviews to the Codex provider and model.
#
# `gentle-ai sync` / `gentle-ai install` rewrite the whole gga config, so the pin
# is kept outside it where possible and re-applied here idempotently:
#   1. <gga>/bin/codex        shim that injects the model for gga's `codex exec`
#   2. <gga>/pin.env          model and effort (created once, never overwritten)
#   3. <gga>/config           marked block at the end: PROVIDER/GGA_PROVIDER=codex
#                             and the shim dir first on PATH
#   4. environment.d/50-gga-pin.conf  the same for desktop-launched programs
# One line is printed per changed file; nothing when everything is current.
#
# Usage: install-gga-pin.sh [--dry-run]
set -euo pipefail

readonly BLOCK_BEGIN="# >>> dreamcoder gga pin >>>"
readonly BLOCK_END="# <<< dreamcoder gga pin <<<"

dry_run=0
case "${1:-}" in
  "") ;;
  --dry-run) dry_run=1 ;;
  -h | --help)
    sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  *)
    printf 'install-gga-pin: unknown option: %s\n' "$1" >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
config_home="${XDG_CONFIG_HOME:-${HOME}/.config}"
gga_dir="${config_home}/gga"
shim_dir="${gga_dir}/bin"
shim_src="${script_dir}/gga-codex-shim.sh"
shim_dst="${shim_dir}/codex"
pin_file="${gga_dir}/pin.env"
config_file="${gga_dir}/config"
env_file="${config_home}/environment.d/50-gga-pin.conf"

# The shim dir is written unescaped into shell code (gga config) and into
# environment.d, so only plain path characters are accepted.
if [[ ! "${shim_dir}" =~ ^/[A-Za-z0-9._@+/-]+$ ]]; then
  printf 'install-gga-pin: unsupported characters in %s; set a plain HOME/XDG_CONFIG_HOME\n' "${shim_dir}" >&2
  exit 1
fi

[[ -r "${shim_src}" ]] || {
  printf 'install-gga-pin: shim source not found: %s\n' "${shim_src}" >&2
  exit 1
}

# Write stdin to $1 when its content differs; report what changed.
write_if_changed() {
  local target="$1" label="$2" tmp
  tmp="$(mktemp)"
  cat >"${tmp}"
  if [[ -f "${target}" ]] && cmp -s "${tmp}" "${target}"; then
    rm -f "${tmp}"
    return 0
  fi
  if ((dry_run)); then
    printf '→ Would update %s (%s)\n' "${target}" "${label}"
  else
    mkdir -p "$(dirname "${target}")"
    # cat (not mv) keeps an existing file's inode, mode and symlink target.
    cat "${tmp}" >"${target}"
    printf '✓ %s: %s\n' "${label}" "${target}"
  fi
  rm -f "${tmp}"
}

install_shim() {
  write_if_changed "${shim_dst}" "gga codex shim" <"${shim_src}"
  if ((!dry_run)) && [[ -f "${shim_dst}" && ! -x "${shim_dst}" ]]; then
    chmod 0755 "${shim_dst}"
  fi
}

install_pin_env() {
  [[ -e "${pin_file}" ]] && return 0
  write_if_changed "${pin_file}" "gga pin model/effort" <<'EOF'
# Model used for every gga review; read by ~/.config/gga/bin/codex.
# Edit freely: scripts/install-gga-pin.sh never overwrites this file.
GGA_PIN_MODEL="gpt-6.1-sol"
GGA_PIN_EFFORT="medium"
EOF
}

pin_block() {
  cat <<EOF
${BLOCK_BEGIN}
# Managed by dreamcoder-dots scripts/install-gga-pin.sh (docs/configuration/gga.md).
# gentle-ai rewrites this file; re-run the installer or \`dreamcoder repair\` after it.
PROVIDER="codex"
GGA_PROVIDER="codex"
case ":\${PATH}:" in *":${shim_dir}:"*) ;; *) export PATH="${shim_dir}:\${PATH}" ;; esac
${BLOCK_END}
EOF
}

# Print the config without the pin block (and the blank line placed before
# it), then the block itself at the end.
render_config() {
  local rest=""
  if [[ -f "${config_file}" ]]; then
    if grep -qxF "${BLOCK_BEGIN}" "${config_file}" && ! grep -qxF "${BLOCK_END}" "${config_file}"; then
      printf 'install-gga-pin: %s has an unterminated pin block; fix it by hand\n' "${config_file}" >&2
      return 1
    fi
    rest="$(awk -v begin="${BLOCK_BEGIN}" -v end="${BLOCK_END}" '
      $0 == begin { skip = 1; held = 0; next }
      skip { if ($0 == end) skip = 0; next }
      {
        if (held) print ""
        held = 0
        if ($0 == "") held = 1; else print
      }
      END { if (held) print "" }
    ' "${config_file}")"
  fi
  if [[ -n "${rest}" ]]; then
    printf '%s\n\n' "${rest}"
  fi
  pin_block
}

install_config_block() {
  local rendered
  rendered="$(render_config)"
  printf '%s\n' "${rendered}" | write_if_changed "${config_file}" "gga config pin block"
}

install_environment_d() {
  write_if_changed "${env_file}" "gga pin for desktop sessions" <<EOF
# Managed by dreamcoder-dots scripts/install-gga-pin.sh (docs/configuration/gga.md).
GGA_PROVIDER=codex
PATH=${shim_dir}:\${PATH}
EOF
}

install_shim
install_pin_env
install_config_block
install_environment_d
