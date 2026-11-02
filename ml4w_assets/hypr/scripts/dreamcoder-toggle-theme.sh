#!/usr/bin/env bash
# ============================================================================
# dreamcoder-toggle-theme.sh — Toggle Dreamcoder light/dark theme mode
# ============================================================================
# Installed to: ~/.config/hypr/scripts/ via setup-hyprland.sh
# Called by: Hyprland keybinding (custom.lua)
#
# Reads the current mode from the cache env file, toggles it, and invokes
# the canonical apply-theme-mode.sh to handle all theme switching logic.
#
# Dependencies:
#   - apply-theme-mode.sh (in dreamcoder-dots repo)
#   - cursor-cli.env (written by apply-theme-mode.sh)
# ============================================================================
set -euo pipefail

# --- paths ---
DREAMCODER_DOTS_DIR="${DREAMCODER_DOTS_DIR:-${HOME}/Documents/PROYECTOS/dreamcoder08/dreamcoder-workbench}"
CACHE_DIR="${XDG_CACHE_HOME:-${HOME}/.cache}/dreamcoder"
ENV_FILE="${CACHE_DIR}/cursor-cli.env"
TOGGLE_SCRIPT="${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh"

# --- detect current mode ---
CURRENT="dark"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  if source "${ENV_FILE}" 2>/dev/null && [[ -n "${DREAMCODER_THEME_MODE:-}" ]]; then
    CURRENT="${DREAMCODER_THEME_MODE}"
  fi
fi

# --- compute new mode ---
case "${CURRENT}" in
light) NEW="dark" ;;
dark) NEW="light" ;;
*) NEW="dark" ;;
esac

# --- apply ---
if [[ ! -f "${TOGGLE_SCRIPT}" ]]; then
  notify-send -a "Dreamcoder" "Error: apply-theme-mode.sh not found" -u critical -t 5000
  exit 1
fi

bash "${TOGGLE_SCRIPT}" "${NEW}"

# --- notify ---
notify-send -a "Dreamcoder" "Theme toggled to ${NEW}" -t 2000
