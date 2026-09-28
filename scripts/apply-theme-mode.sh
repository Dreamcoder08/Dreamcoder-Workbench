#!/usr/bin/env bash
set -euo pipefail

source "${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}/lib/logging.sh"
source "${DREAMCODER_DOTS_DIR}/lib/env.sh"
source "${DREAMCODER_DOTS_DIR}/lib/checks.sh"
source "${DREAMCODER_DOTS_DIR}/lib/hyprland.sh"
[[ -f "${DREAMCODER_DOTS_DIR}/lib/waybar.sh" ]] && source "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"

ensure_dots_dir

# Define cache dirs — these are set in dreamcoder-env.sh but that file is NOT
# sourced here (its callers exec this script in a fresh process).
CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
ML4W_CACHE_DIR="${ML4W_CACHE_DIR:-${CACHE_HOME}/ml4w/hyprland-dotfiles}"

MODE="${1:-light}"
WALLPAPER="${2:-${DREAMCODER_WALLPAPER:-}}"
PROFILE="${3:-${DREAMCODER_THEME_PROFILE:-standard}}"
ML4W_WALLPAPER="${ML4W_CACHE_DIR}/current_wallpaper"
[[ "${MODE}" == "light" || "${MODE}" == "dark" ]] || {
  printf 'Invalid mode: %s\n' "${MODE}" >&2
  exit 1
}
case "${PROFILE}" in
standard | night) ;;
*)
  printf 'Invalid render profile: %s (expected standard|night)\n' "${PROFILE}" >&2
  exit 1
  ;;
esac
# Night is an orthogonal render profile on top of the base mode: while
# DREAMCODER_THEME_MODE stays "dark", DREAMCODER_THEME_PROFILE=night selects
# the generated *-night artifacts instead of the standard dark ones.
VARIANT="${MODE}"
[[ "${PROFILE}" == "night" ]] && VARIANT="night"
# Night always resolves the Dreamcoder Dark base (ADR-003): a light
# base with profile=night is a conflict, never a silent coercion.
if [[ "${PROFILE}" == "night" && "${MODE}" != "dark" ]]; then
  printf 'Invalid combination: render profile night requires base mode dark (got %s)\n' "${MODE}" >&2
  exit 1
fi
if [[ -z "${WALLPAPER}" && -f "${ML4W_WALLPAPER}" ]]; then WALLPAPER="$(cat "${ML4W_WALLPAPER}")"; fi

CURSOR_CLI_ENV="${CACHE_HOME:-${HOME}/.cache}/dreamcoder/cursor-cli.env"
case "${MODE}" in
light) CLI_COLORFGBG="0;15" ;;
dark) CLI_COLORFGBG="15;0" ;;
esac
mkdir -p "$(dirname "${CURSOR_CLI_ENV}")"
# Preparation gate: never mutate symlinks or system mode until the Night
# plan is ready. For profile=night every repo-generated *-night artifact
# referenced by the selectors below must already exist (Phase 3 generation
# plus the Python validation-first gate are the other halves); a missing
# artifact aborts with ZERO mutations.
if [[ "${PROFILE}" == "night" ]]; then
  REQUIRED_NIGHT_ARTIFACTS=(
    "${DREAMCODER_DOTS_DIR}/DreamcoderKitty/.config/kitty/colors-dreamcoder-night.conf"
    "${DREAMCODER_DOTS_DIR}/DreamcoderKitty/.config/kitty/dreamcoder-ui-night.conf"
    "${DREAMCODER_DOTS_DIR}/DreamcoderGhostty/.config/ghostty/themes/dreamcoder-night"
    "${DREAMCODER_DOTS_DIR}/DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder-Night.yaml"
    "${DREAMCODER_DOTS_DIR}/DreamcoderPi/.pi/agent/themes/dreamcoder-night.json"
    "${DREAMCODER_DOTS_DIR}/DreamcoderZellij/.config/zellij/dreamcoder-night.kdl"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/hyprland-night.conf"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/hypr-colors-night.lua"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/hypr-colors-night.conf"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/waybar-night.css"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/rofi-night.rasi"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/btop-dreamcoder-night.theme"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/delta-dreamcoder-night.gitconfig"
    "${DREAMCODER_DOTS_DIR}/DreamcoderThemes/dreamcoder/tmux-dreamcoder-night.conf"
    "${DREAMCODER_DOTS_DIR}/DreamcoderLazygit/.config/lazygit/config.night.yml"
  )
  for _artifact in "${REQUIRED_NIGHT_ARTIFACTS[@]}"; do
    if [[ ! -f "${_artifact}" ]]; then
      printf '✗ Night preparation failed: missing artifact %s\n' "${_artifact}" >&2
      printf '  Run repository Night generation first (DREAMCODER_THEME_PROFILE=night sync).\n' >&2
      exit 1
    fi
  done
fi
# Bounded preparation + settings persistence (control path). Runs only
# when this script is the entry point (theme-auto / manual). When
# invoked by the control transaction (DREAMCODER_SYNC_DONE=1),
# preparation, validation, and settings persistence already succeeded;
# this script is then purely the post-validation system/reload adapter
# (design §7/§8): system mode, symlink flips, and reloads run only
# after preparation and settings persistence succeed.
if [[ "${DREAMCODER_SYNC_DONE:-0}" != "1" ]]; then
  _CONTROL_CHOICE="${MODE}"
  [[ "${PROFILE}" == "night" ]] && _CONTROL_CHOICE="night"
  DREAMCODER_SYNC_DONE=1 \
    DREAMCODER_THEME_MODE="${MODE}" \
    DREAMCODER_THEME_PROFILE="${PROFILE}" \
    DREAMCODER_WALLPAPER="${WALLPAPER}" \
    PYTHONPATH="${DREAMCODER_DOTS_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
    python3 -m dreamcoder_theme.control theme apply "${_CONTROL_CHOICE}" --json >/dev/null
fi
printf 'export COLORFGBG="%s"\nexport DREAMCODER_THEME_MODE="%s"\nexport DREAMCODER_THEME_PROFILE="%s"\nexport COLORTERM="truecolor"\nexport FORCE_COLOR="3"\nexport CLICOLOR_FORCE="1"\nunset NO_COLOR\n' "${CLI_COLORFGBG}" "${MODE}" "${PROFILE}" >"${CURSOR_CLI_ENV}"

"${DREAMCODER_DOTS_DIR}/scripts/apply-system-mode.sh" "${MODE}"
if [[ -n "${WALLPAPER}" && -f "${WALLPAPER}" ]] && optional_command matugen; then
  if is_gui_session; then
    timeout 10 matugen image "${WALLPAPER}" -m "${MODE}" >/dev/null 2>&1 || true
  fi
fi
# --- Waybar: flip colors.css symlink to mode-specific variant BEFORE sync ---
# This ensures the Python sync writes to the correct variant file
# instead of overwriting the wrong one through a stale symlink.
WAYBAR_COLORS="${HOME}/.config/waybar/colors.css"
if [[ -L "${WAYBAR_COLORS}" ]]; then
  ln -sf "colors-${VARIANT}.css" "${WAYBAR_COLORS}"
fi
# --- Rofi: same treatment for colors.rasi symlink ---
ROFI_COLORS="${HOME}/.config/rofi/colors.rasi"
if [[ -L "${ROFI_COLORS}" ]]; then
  ln -sf "colors-${VARIANT}.rasi" "${ROFI_COLORS}"
fi
# --- Hyprland: flip colors.lua and colors.conf symlinks ---
HYPR_LUA="${HOME}/.config/hypr/colors.lua"
HYPR_CONF="${HOME}/.config/hypr/colors.conf"
if [[ -L "${HYPR_LUA}" ]]; then
  ln -sf "colors-${VARIANT}.lua" "${HYPR_LUA}"
fi
if [[ -L "${HYPR_CONF}" ]]; then
  ln -sf "colors-${VARIANT}.conf" "${HYPR_CONF}"
fi
# --- Hyprland: flip dreamcoder-colors.lua ---
HYPR_DC_LUA="${HOME}/.config/hypr/dreamcoder-colors.lua"
if [[ -L "${HYPR_DC_LUA}" ]]; then
  ln -sf "hypr-colors-${VARIANT}.lua" "${HYPR_DC_LUA}"
fi
# --- Kitty: flip colors-dreamcoder.conf and dreamcoder-ui.conf symlinks BEFORE sync ---
# This ensures the Python sync writes to the correct variant file
# instead of overwriting the wrong one through a stale symlink.
KITTY_DIR="${HOME}/.config/kitty"
if [[ -d "${KITTY_DIR}" ]]; then
  for _link in colors-dreamcoder.conf dreamcoder-ui.conf; do
    _target="${KITTY_DIR}/${_link}"
    if [[ -L "${_target}" ]]; then
      ln -sf "${_link%.conf}-${VARIANT}.conf" "${_target}"
    fi
  done
fi
# Ghostty uses native dual-mode (light:dreamcoder-light,dark:dreamcoder-dark)
# No symlink flipping needed — Ghostty auto-detects system theme
# --- Pi CLI: flip theme symlink ---
PI_SCRIPT="${DREAMCODER_DOTS_DIR}/DreamcoderPi/.pi/agent/scripts/pi-theme.sh"
if [[ -f "${PI_SCRIPT}" ]]; then
  DREAMCODER_THEME_MODE="${MODE}" DREAMCODER_THEME_PROFILE="${PROFILE}" bash "${PI_SCRIPT}" &>/dev/null || true
  printf '  pi theme switched to %s mode (profile: %s)\n' "${MODE}" "${PROFILE}"
fi

# The Python preparation + validation + settings persistence + commit ran
# above (or, when invoked by the control transaction, in that caller). This
# section is purely the post-validation system/reload surface.
signal_kitty
# Refresh the Waybar accent override before Waybar restarts; machines without
# the ML4W selector must not break the mode switch.
install_waybar_override "${DREAMCODER_DOTS_DIR}" || true
restart_waybar

# --- tmux integration: propagate theme to running sessions ---
KANAGAWA_DIR="${HOME}/.tmux/plugins/tmux-kanagawa"
if command -v tmux >/dev/null 2>&1; then
  # Start a headless server if none exists so options persist for new sessions
  if ! tmux list-sessions &>/dev/null 2>&1; then
    tmux start-server 2>/dev/null || true
    sleep 0.1
  fi
  # Update global environment so NEW panes/windows inherit the right vars
  tmux set-environment -g DREAMCODER_THEME_MODE "${MODE}" 2>/dev/null || true
  tmux set-environment -g DREAMCODER_THEME_PROFILE "${PROFILE}" 2>/dev/null || true
  tmux set-environment -g COLORFGBG "${CLI_COLORFGBG}" 2>/dev/null || true

  # Switch tmux-kanagawa theme variant to match Dreamcoder mode/profile
  # SOURCE OF TRUTH: colors MUST match DreamcoderThemes/dreamcoder/tokens.json
  # When updating tokens, update BOTH light AND dark sections here (and
  # night, derived through the canonical night transform in the package).
  if [[ -d "${KANAGAWA_DIR}" ]]; then
    case "${VARIANT}" in
    light)
      KANAGAWA_VARIANT="lotus"
      # Dreamcoder Light palette — source: tokens.json modes.light.{text,accent,error,...}
      tmux set-option -g @ukiyo-color-text "#17120d" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-bg-bar "#e6d7c4" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-bg-pane "#f3eadc" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-info "#0d4a68" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-notice "#a7471c" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-accent "#824f16" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-muted "#352e22" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-error "#842f24" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-alert "#654300" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-highlight "#0f6570" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-selection "#c8ad89" 2>/dev/null || true
      # Restore default plugin color order (fg=bg_pane claro sobre bg=color)
      tmux set-option -gu "@ukiyo-git-colors" 2>/dev/null || true
      tmux set-option -gu "@ukiyo-cpu-usage-colors" 2>/dev/null || true
      tmux set-option -gu "@ukiyo-ram-usage-colors" 2>/dev/null || true
      ;;
    dark)
      KANAGAWA_VARIANT="dragon"
      # Dreamcoder Dark palette — source: tokens.json modes.dark.{text,accent,error,...}
      tmux set-option -g @ukiyo-color-text "#E6E6E6" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-bg-bar "#0D0D0F" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-bg-pane "#0B0B0B" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-accent "#A5B4FC" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-info "#7DD3FC" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-notice "#C7C7C7" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-muted "#C7C7C7" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-error "#FB8585" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-alert "#FBBF24" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-highlight "#3B82F6" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-selection "#3A3A3A" 2>/dev/null || true
      # Swap plugin color order: fg=bg_bar (oscuro) sobre bg=color vibrante
      tmux set-option -g @ukiyo-git-colors "accent bg_bar" 2>/dev/null || true
      tmux set-option -g @ukiyo-cpu-usage-colors "notice bg_bar" 2>/dev/null || true
      tmux set-option -g @ukiyo-ram-usage-colors "info bg_bar" 2>/dev/null || true
      ;;
    night)
      KANAGAWA_VARIANT="dragon"
      # Dreamcoder Night profile — derived from Dreamcoder Dark in tokens.json modes.dark
      # via the canonical night transform (brightness 0.86 / saturation 0.72).
      tmux set-option -g @ukiyo-color-text "#c6c6c6" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-bg-bar "#0b0b0d" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-bg-pane "#090909" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-accent "#a4afee" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-info "#62b9e2" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-notice "#ababab" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-muted "#ababab" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-error "#e88484" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-alert "#d1a126" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-highlight "#3a76d6" 2>/dev/null || true
      tmux set-option -g @ukiyo-color-selection "#323232" 2>/dev/null || true
      # Swap plugin color order (same as dark: fg=bg_bar sobre bg=color)
      tmux set-option -g @ukiyo-git-colors "accent bg_bar" 2>/dev/null || true
      tmux set-option -g @ukiyo-cpu-usage-colors "notice bg_bar" 2>/dev/null || true
      tmux set-option -g @ukiyo-ram-usage-colors "info bg_bar" 2>/dev/null || true
      ;;
    esac
    tmux set-option -g @ukiyo-theme "kanagawa/${KANAGAWA_VARIANT}" 2>/dev/null || true
    # Reload plugin to apply new theme colors immediately
    bash "${KANAGAWA_DIR}/ukiyo.tmux" 2>/dev/null || true
  fi

  # Source standalone tmux theme (pane borders, mode, bell colors)
  # When kanagawa is active, skip status-bar lines to preserve kanagawa layout
  TMUX_THEME="${HOME}/.config/tmux/tmux-dreamcoder.conf"
  if [[ -f "${TMUX_THEME}" && ! -d "${KANAGAWA_DIR}" ]]; then
    tmux source-file "${TMUX_THEME}" 2>/dev/null || true
  elif [[ -f "${TMUX_THEME}" && -d "${KANAGAWA_DIR}" ]]; then
    # Kanagawa active: only source color lines, skip status-bar layout
    grep -vE '^(set -g status-(left|right|position|interval|justify)|setw -g window-status-(format|current-format|separator))' \
      "${TMUX_THEME}" | tmux source-file /dev/stdin 2>/dev/null || true
  fi

  printf '  tmux environment and theme updated for %s mode\n' "${MODE}"
fi
# --- /tmux integration ---

# --- Herdr: switch config symlink + reload ---
HERDR_SCRIPT="${DREAMCODER_DOTS_DIR}/scripts/herdr-theme-switch.sh"
if [[ -f "${HERDR_SCRIPT}" ]]; then
  bash "${HERDR_SCRIPT}" "${VARIANT}"
fi
# --- /Herdr ---

printf '✓ Dreamcoder %s mode applied (profile: %s)\n' "${MODE}" "${PROFILE}"

# --- Post-sync: fix any stale symlinks ---
# Waybar colors.css, Rofi colors.rasi, and Hyprland colors.lua/colors.conf
# are written by the activation transaction (which owns the bridge symlink
# selection before commit). Only Dunst needs a symlink check since its
# config is a plain file in the repo.
DOTS_DIR="${DREAMCODER_DOTS_DIR:-${HOME}/Documents/PROYECTOS/dreamcoder-dots}"
DUNST_CONF="${HOME}/.config/dunst/dreamcoder-dunst.conf"
WARP_THEME="${HOME}/.local/share/warp-terminal/themes/Dreamcoder.yaml"
WARP_VARIANT="${DOTS_DIR}/DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder-${VARIANT^}.yaml"

if [[ -L "${DUNST_CONF}" ]]; then
  target=$(readlink "${DUNST_CONF}")
  case "${target}" in
  *dunst-dreamcoder-dark.conf | *dunst-dreamcoder-light.conf | *dunst-dreamcoder-night.conf)
    ln -sf "${DOTS_DIR}/DreamcoderThemes/dreamcoder/dunst-dreamcoder.conf" "${DUNST_CONF}"
    ;;
  esac
fi

# Warp: flip active theme symlink to variant-specific artifact
[[ -f "${WARP_VARIANT}" ]] && ln -sf "${WARP_VARIANT}" "${WARP_THEME}"

# Btop: flip theme symlink to variant-specific artifact
BTOP_THEME="${HOME}/.config/btop/themes/dreamcoder.theme"
if [[ -L "${BTOP_THEME}" ]]; then
  ln -sf "dreamcoder-${VARIANT}.theme" "${BTOP_THEME}"
fi
# btop.conf is ML4W-owned and upgrades reset color_theme (to "matugen"), so
# re-select the Dreamcoder theme on every apply; a no-op when already set.
BTOP_CONF="${HOME}/.config/btop/btop.conf"
if [[ -f "${BTOP_THEME}" && -f "${BTOP_CONF}" ]] && ! grep -q '^color_theme = "dreamcoder"$' "${BTOP_CONF}"; then
  sed -i 's/^color_theme = .*/color_theme = "dreamcoder"/' "${BTOP_CONF}"
fi

# Zellij: update theme in config.kdl
ZELLIJ_CONF="${HOME}/.config/zellij/config.kdl"
if [[ -f "${ZELLIJ_CONF}" ]]; then
  sed -i "s/^theme \".*\"/theme \"dreamcoder-${VARIANT}\"/" "${ZELLIJ_CONF}"
fi

# Delta: flip git diff theme symlink to variant-specific artifact
DELTA_LINK="${HOME}/.config/git/delta-dreamcoder.gitconfig"
DELTA_VARIANT="${DOTS_DIR}/DreamcoderThemes/dreamcoder/delta-dreamcoder-${VARIANT}.gitconfig"
if [[ -f "${DELTA_VARIANT}" ]]; then
  ln -sf "${DELTA_VARIANT}" "${DELTA_LINK}"
fi

# Lazygit: flip live config symlink to variant-specific artifact.
# The live ~/.config/lazygit/config.yml must point at the current variant
# (config.<variant>.yml) exactly like the Delta/btop selectors above; the
# repo keeps the generated active config.yml (mode-tracking) for COPY-style
# installs. ln -sf replaces the link atomically.
LAZYGIT_LINK="${HOME}/.config/lazygit/config.yml"
LAZYGIT_VARIANT="${DOTS_DIR}/DreamcoderLazygit/.config/lazygit/config.${VARIANT}.yml"
if [[ -f "${LAZYGIT_VARIANT}" ]]; then
  ln -sf "${LAZYGIT_VARIANT}" "${LAZYGIT_LINK}"
fi
