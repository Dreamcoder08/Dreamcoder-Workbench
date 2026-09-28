#!/usr/bin/env bash
# ============================================================================
# apply-ml4w-hooks.sh — (re)install Dreamcoder's wallpaper hook into ML4W
# ============================================================================
# Primary target: ML4W's wallpaper runner (~/.config/ml4w/scripts/ml4w-wallpaper,
# which receives the image as $IMAGE_PATH). ML4W 2.16 drives it directly from
# its Quickshell wallpaper app; waypaper is no longer part of its install set,
# so waypaper's post_command is hooked only when that config exists.
#
# ML4W upgrades overwrite the runner, so re-run this script after every ML4W
# update. The runner hook sits between markers and is replaced on each run,
# never duplicated; the unmarked block older releases of this script appended
# is migrated to the marked form.
#
# Overrides: ML4W_WALLPAPER_SCRIPT, ML4W_WALLPAPER_VAR (older ML4W releases used
# ~/.config/hypr/scripts/wallpaper.sh with $used_wallpaper), WAYPAPER_CONFIG.
# ============================================================================
set -euo pipefail

source "${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}/lib/env.sh"
ensure_dots_dir
WAYPAPER_CONFIG="${WAYPAPER_CONFIG:-${HOME}/.config/waypaper/config.ini}"
ML4W_WALLPAPER_SCRIPT="${ML4W_WALLPAPER_SCRIPT:-${HOME}/.config/ml4w/scripts/ml4w-wallpaper}"
ML4W_WALLPAPER_VAR="${ML4W_WALLPAPER_VAR:-IMAGE_PATH}"
HOOK_SCRIPT="${DREAMCODER_DOTS_DIR}/scripts/wallpaper-hook.sh"
BEGIN_MARK='# >>> Dreamcoder wallpaper hook >>>'
END_MARK='# <<< Dreamcoder wallpaper hook <<<'
LEGACY_MARK='# Dreamcoder final wallpaper/theme sync'

# Print the runner without any Dreamcoder block (marked or legacy) and without
# trailing blank lines, so re-appending always yields the same bytes.
strip_runner_hook() {
  awk -v begin="${BEGIN_MARK}" -v end="${END_MARK}" -v legacy="${LEGACY_MARK}" '
    $0 == begin { skip = 1; next }
    skip && $0 == end { skip = 0; next }
    $0 == legacy { in_legacy = 1; next }
    in_legacy { if ($0 ~ /^fi[[:space:]]*$/) in_legacy = 0; next }
    skip { next }
    { lines[++n] = $0 }
    END {
      while (n > 0 && lines[n] ~ /^[[:space:]]*$/) n--
      for (i = 1; i <= n; i++) print lines[i]
    }
  ' "$1"
}

hook_ml4w_runner() {
  if [[ ! -f "${ML4W_WALLPAPER_SCRIPT}" ]]; then
    printf '⚠ ML4W wallpaper runner not found, skipped: %s\n' "${ML4W_WALLPAPER_SCRIPT}" >&2
    return 0
  fi
  local current desired
  current="$(cat "${ML4W_WALLPAPER_SCRIPT}")"
  desired="$(strip_runner_hook "${ML4W_WALLPAPER_SCRIPT}")

${BEGIN_MARK}
# Managed by dreamcoder-dots scripts/apply-ml4w-hooks.sh; re-run it after ML4W upgrades.
if [[ -x \"${HOOK_SCRIPT}\" ]]; then
    \"${HOOK_SCRIPT}\" \"\$${ML4W_WALLPAPER_VAR}\"
fi
${END_MARK}"
  if [[ "${current}" == "${desired}" ]]; then
    printf '✓ ML4W wallpaper runner hook already current\n'
    return 0
  fi
  # Write through the path (no temp-file rename) so a symlinked runner stays a
  # symlink and keeps its executable mode.
  printf '%s\n' "${desired}" >"${ML4W_WALLPAPER_SCRIPT}"
  printf '✓ ML4W wallpaper runner hooked: %s\n' "${ML4W_WALLPAPER_SCRIPT}"
}

hook_waypaper() {
  if [[ ! -f "${WAYPAPER_CONFIG}" ]]; then
    printf '✓ waypaper config absent (not used by ML4W 2.16), skipped\n'
    return 0
  fi
  if grep -q 'wallpaper-hook.sh' "${WAYPAPER_CONFIG}"; then
    printf '✓ waypaper post_command hook already present\n'
    return 0
  fi
  local hook="${HOOK_SCRIPT} \"\$wallpaper\" > /dev/null 2>&1"
  # `&` in a sed replacement expands to the whole match, and the hook text
  # contains `2>&1`; unescaped it corrupts the line by re-inserting the match.
  local hook_sed="${hook//&/\\&}"
  sed -i "s|^post_command = \(.*\)|post_command = \1; ${hook_sed}|" "${WAYPAPER_CONFIG}"
  printf '✓ waypaper post_command hooked: %s\n' "${WAYPAPER_CONFIG}"
}

hook_ml4w_runner
hook_waypaper

"${DREAMCODER_DOTS_DIR}/scripts/theme-auto.sh"
printf '✓ Dreamcoder ML4W hooks applied\n'
