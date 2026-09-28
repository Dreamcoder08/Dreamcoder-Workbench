#!/usr/bin/env bash
# ============================================================================
# apply-ml4w-hooks.sh — (re)install Dreamcoder's hooks into ML4W
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
# Second target: ML4W's GTK theme listener
# (~/.config/ml4w/listeners/gtk-theme-switcher.sh). It watches
# ~/.config/gtk-3.0/settings.ini and, on every change (including Dreamcoder's
# own light/dark switch), runs Matugen over the wallpaper, which overwrites
# Dreamcoder's colour files, then reloads Quickshell, Waybar, GTK and swaync.
# A marked block after each Matugen call re-applies Dreamcoder colours
# synchronously through `dreamcoder sync`, so those reloads pick up Dreamcoder
# colours. The sync never writes settings.ini, so the listener cannot loop.
# The running listener already parsed the old body, so it is restarted through
# ML4W's listeners.sh whenever the file changes.
#
# Overrides: ML4W_WALLPAPER_SCRIPT, ML4W_WALLPAPER_VAR (older ML4W releases used
# ~/.config/hypr/scripts/wallpaper.sh with $used_wallpaper), WAYPAPER_CONFIG,
# ML4W_GTK_LISTENER, ML4W_LISTENERS_SCRIPT.
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
ML4W_GTK_LISTENER="${ML4W_GTK_LISTENER:-${HOME}/.config/ml4w/listeners/gtk-theme-switcher.sh}"
ML4W_LISTENERS_SCRIPT="${ML4W_LISTENERS_SCRIPT:-${HOME}/.config/ml4w/listeners.sh}"
LISTENER_BEGIN_MARK='# >>> Dreamcoder listener hook >>>'
LISTENER_END_MARK='# <<< Dreamcoder listener hook <<<'

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

# Print the listener with a fresh Dreamcoder block after every Matugen call
# (existing blocks are dropped first, so re-running yields the same bytes).
# The sync mode is the branch's own `-m dark|light`; a Matugen call without
# one falls back to reading gtk-application-prefer-dark-theme at run time,
# because `dreamcoder sync` renders Dark when DREAMCODER_THEME_MODE is unset.
# Exits 3 when no Matugen call is found, leaving the decision to the caller.
render_listener_hook() {
  awk -v begin="${LISTENER_BEGIN_MARK}" -v end="${LISTENER_END_MARK}" \
    -v dispatcher="${DREAMCODER_DOTS_DIR}/scripts/dreamcoder" '
    function trim(s) { sub(/^[[:space:]]+/, "", s); sub(/[[:space:]]+$/, "", s); return s }
    trim($0) == begin { skip = 1; next }
    skip && trim($0) == end { skip = 0; next }
    skip { next }
    {
      print
      if ($0 ~ /^[[:space:]]*[^#]*(\$MATUGEN_BIN|\$\{MATUGEN_BIN\}|(^|[[:space:]])matugen)[[:space:]]+image([[:space:]]|$)/) {
        found++
        match($0, /^[[:space:]]*/)
        pad = substr($0, 1, RLENGTH)
        print pad begin
        print pad "# Managed by dreamcoder-dots scripts/apply-ml4w-hooks.sh; re-run it after ML4W upgrades."
        print pad "# Matugen just rewrote the colour files from the wallpaper: restore Dreamcoder"
        print pad "# colours before the reloads below. The sync never writes gtk settings.ini."
        print pad "if [[ -x \"" dispatcher "\" ]]; then"
        if (match($0, /-m[[:space:]]+"?(dark|light)"?/)) {
          # The branch passes its mode to Matugen: reuse it verbatim.
          mode = substr($0, RSTART, RLENGTH)
          sub(/^-m[[:space:]]+"?/, "", mode)
          sub(/"$/, "", mode)
          print pad "    _dreamcoder_mode=" mode
        } else {
          print pad "    _dreamcoder_mode=light"
          print pad "    grep -Eq \"^gtk-application-prefer-dark-theme=(1|true)$\" \"${SETTINGS_FILE:-$HOME/.config/gtk-3.0/settings.ini}\" && _dreamcoder_mode=dark"
        }
        print pad "    mkdir -p \"$HOME/.cache/dreamcoder\""
        print pad "    DREAMCODER_THEME_MODE=\"$_dreamcoder_mode\" DREAMCODER_WRITE_REPO=0 timeout 120 \"" dispatcher "\" sync </dev/null >\"$HOME/.cache/dreamcoder/ml4w-listener-sync.log\" 2>&1 || true"
        print pad "fi"
        print pad end
      }
    }
    END { if (!found) exit 3 }
  ' "$1"
}

hook_gtk_listener() {
  if [[ ! -f "${ML4W_GTK_LISTENER}" ]]; then
    printf '⚠ ML4W GTK theme listener not found, skipped: %s\n' "${ML4W_GTK_LISTENER}" >&2
    return 0
  fi
  local current desired rc=0
  current="$(cat "${ML4W_GTK_LISTENER}")"
  desired="$(render_listener_hook "${ML4W_GTK_LISTENER}")" || rc=$?
  if [[ "${rc}" -eq 3 ]]; then
    printf '⚠ no Matugen call found in the ML4W GTK theme listener, left untouched: %s\n' "${ML4W_GTK_LISTENER}" >&2
    return 0
  elif [[ "${rc}" -ne 0 ]]; then
    return "${rc}"
  fi
  if [[ "${current}" == "${desired}" ]]; then
    printf '✓ ML4W GTK theme listener hook already current\n'
    return 0
  fi
  # Write through the path, like the runner hook (keeps symlink and mode).
  printf '%s\n' "${desired}" >"${ML4W_GTK_LISTENER}"
  printf '✓ ML4W GTK theme listener hooked: %s\n' "${ML4W_GTK_LISTENER}"
  restart_gtk_listener
}

# The live listener keeps the body it parsed at start, so restart it through
# ML4W's own control script. Runs in the foreground (listeners.sh returns after
# ~1s) so the theme apply below never races a half-restarted listener; every
# stream is detached so the relaunched listener cannot hold the caller's pipes.
restart_gtk_listener() {
  if [[ ! -x "${ML4W_LISTENERS_SCRIPT}" ]]; then
    printf '⚠ ML4W listeners.sh not found, restart the GTK theme listener manually: %s\n' "${ML4W_LISTENERS_SCRIPT}" >&2
    return 0
  fi
  if timeout 30 "${ML4W_LISTENERS_SCRIPT}" --restart gtk-theme-switcher </dev/null >/dev/null 2>&1; then
    printf '✓ ML4W GTK theme listener restarted\n'
  else
    printf '⚠ ML4W GTK theme listener restart failed; run: %s --restart gtk-theme-switcher\n' "${ML4W_LISTENERS_SCRIPT}" >&2
  fi
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
hook_gtk_listener
hook_waypaper

"${DREAMCODER_DOTS_DIR}/scripts/theme-auto.sh"
printf '✓ Dreamcoder ML4W hooks applied\n'
