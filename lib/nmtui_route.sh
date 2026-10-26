#!/usr/bin/env bash
# Optional ML4W network route. Sourced: leave the caller's shell options alone.

_nmtui_route() {
  # A strict known-body check protects arbitrary personal network scripts. Work
  # in bytes so comments, indentation, line endings and final newlines survive.
  python3 - "$1" "$2" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
data = path.read_bytes()
launcher = b'"${HOME}/.local/bin/dreamcoder-nmtui"'
lines = [line.strip() for line in data.splitlines()
         if line.strip() and not line.lstrip().startswith(b'#')]
expected = [b'if systemctl is-active --quiet NetworkManager; then', b'nmtui',
            b'else', b'sudo systemctl start NetworkManager', b'if [ $? -eq 0 ]; then',
            b'nmtui', b'else', b'echo "NetworkManager could not start"', b'fi', b'fi']
normalized = [b'nmtui' if line == launcher else line for line in lines]
if normalized != expected:
    print('unknown')
elif sys.argv[2] == 'write':
    path.write_bytes(re.sub(rb'(?m)^([ \t]*)nmtui([ \t]*\r?)$',
                            lambda m: m[1] + launcher + m[2], data))
else:
    print('current' if lines.count(launcher) == 2 else 'pending')
PY
}

_nmtui_route_prerequisites() {
  local route="$1" source_file="$2"
  if [[ ! -f "${route}" && ! -L "${route}" ]]; then
    warn "ML4W network script missing, skipped: ${route}"
    return 1
  fi
  if [[ -L "${route}" || ! -f "${route}" ]]; then
    warn "Unrecognized ML4W network script, skipped: ${route}"
    return 1
  fi
  if ! command -v python3 >/dev/null || [[ ! -f "${source_file}" ]]; then
    warn "nmtui route prerequisites missing, skipped: ${route}"
    return 1
  fi
}

install_nmtui_route() {
  # setup-hyprland has already checked ML4W ownership. Use its logging helpers
  # and the same compare-before-copy / no-personal-symlink policy as Waybar.
  local source_file="$1/DreamcoderShell/.local/bin/dreamcoder-nmtui"
  local route="${HOME}/.config/ml4w/scripts/ml4w-network"
  local launcher="${HOME}/.local/bin/dreamcoder-nmtui" state
  _nmtui_route_prerequisites "${route}" "${source_file}" || return 0
  state="$(_nmtui_route "${route}" probe)" || return 1
  if [[ "${state}" == unknown ]]; then
    warn "Unrecognized ML4W network script, skipped: ${route}"
    return 0
  fi
  if [[ -L "${launcher}" ]] || { [[ -e "${launcher}" ]] &&
    { [[ ! -f "${launcher}" ]] || ! cmp -s "${source_file}" "${launcher}"; }; }; then
    warn "Conflicting nmtui launcher, skipped: ${launcher}"
    return 0
  fi
  if [[ "${state}" == current && -x "${launcher}" ]]; then
    info "ML4W network route already current: ${route}"
    return 0
  fi
  if [[ "${DRY_RUN}" == true ]]; then
    step "Would install ML4W network route: ${route}"
    return 0
  fi
  # Never point the network menu at a launcher that has not installed safely.
  if [[ ! -f "${launcher}" ]]; then
    mkdir -p "$(dirname "${launcher}")" || return 1
    cp "${source_file}" "${launcher}" || return 1
  fi
  if [[ ! -x "${launcher}" ]]; then
    chmod +x "${launcher}" || return 1
  fi
  if [[ "${state}" != current ]]; then
    if [[ ! -e "${route}.bak" && ! -L "${route}.bak" ]]; then
      cp -p "${route}" "${route}.bak" || return 1
    fi
    _nmtui_route "${route}" write || return 1
  fi
  info "ML4W network route installed: ${route}"
}
