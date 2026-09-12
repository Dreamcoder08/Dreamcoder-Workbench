#!/usr/bin/env bash
set -euo pipefail

source "${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}/lib/env.sh"
ensure_dots_dir
WAYPAPER_CONFIG="${WAYPAPER_CONFIG:-${HOME}/.config/waypaper/config.ini}"
# Current ML4W runs ~/.config/ml4w/scripts/ml4w-wallpaper with $IMAGE_PATH; an older release symlinked ~/.config/hypr/scripts/wallpaper.sh and used $used_wallpaper. Both overridable.
ML4W_WALLPAPER_SCRIPT="${ML4W_WALLPAPER_SCRIPT:-${HOME}/.config/ml4w/scripts/ml4w-wallpaper}"
ML4W_WALLPAPER_VAR="${ML4W_WALLPAPER_VAR:-IMAGE_PATH}"
HOOK="${DREAMCODER_DOTS_DIR}/scripts/wallpaper-hook.sh \"\$wallpaper\" > /dev/null 2>&1"
BLOCK="\"${DREAMCODER_DOTS_DIR}/scripts/wallpaper-hook.sh\" \"\$${ML4W_WALLPAPER_VAR}\""

if [[ -f "${WAYPAPER_CONFIG}" ]] && ! grep -q 'wallpaper-hook.sh' "${WAYPAPER_CONFIG}"; then
  # `&` in a sed replacement expands to the whole match, and the hook text
  # contains `2>&1`; unescaped it corrupts the line by re-inserting the match.
  HOOK_SED="${HOOK//&/\\&}"
  sed -i "s|^post_command = \(.*\)|post_command = \1; ${HOOK_SED}|" "${WAYPAPER_CONFIG}"
fi

if [[ -f "${ML4W_WALLPAPER_SCRIPT}" ]] && ! grep -q 'wallpaper-hook.sh' "${ML4W_WALLPAPER_SCRIPT}"; then
  cat >>"${ML4W_WALLPAPER_SCRIPT}" <<ML4W_HOOK

# Dreamcoder final wallpaper/theme sync
if [[ -x "${DREAMCODER_DOTS_DIR}/scripts/wallpaper-hook.sh" ]]; then
    ${BLOCK}
fi
ML4W_HOOK
fi

"${DREAMCODER_DOTS_DIR}/scripts/theme-auto.sh"
printf '✓ Dreamcoder ML4W hooks applied\n'
