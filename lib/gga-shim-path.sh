#!/usr/bin/env bash
# ============================================================================
# gga-shim-path.sh — put the gga codex shim directory first on PATH, exactly once
# ============================================================================
# Sourced, never executed (installed as ~/.config/gga/shim-path.sh by
# scripts/install-gga-pin.sh); it must not set shell options. Callers set
# _dc_gga_bin to the shim directory first: the gga config block and .bashrc.
#
# Precedence, not membership, decides which codex runs. A directory that is
# already on PATH but behind ~/.local/bin would leave the real codex in front
# and bypass the model pin, so any existing entry is dropped before prepending.
# ============================================================================
# _dc_gga_bin is set by the caller (see the header); a guard that aborts would kill gga itself.
# shellcheck disable=SC2154
_dc_gga_path=":${PATH}:"
# The substitution consumes both separators, so adjacent duplicates (a:a:b) need another pass.
while [[ "${_dc_gga_path}" == *":${_dc_gga_bin}:"* ]]; do
  _dc_gga_path="${_dc_gga_path//":${_dc_gga_bin}:"/:}"
done
_dc_gga_path="${_dc_gga_path#:}"
export PATH="${_dc_gga_bin}${_dc_gga_path:+:${_dc_gga_path%:}}"
unset _dc_gga_path
