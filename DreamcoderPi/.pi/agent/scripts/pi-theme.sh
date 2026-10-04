#!/usr/bin/env bash
set -euo pipefail

# Resolve installed symlinks before deriving the checkout, independent of cwd.
DC="${DREAMCODER_DOTS_DIR:-${DOTS_DIR:-}}"
if [[ -z "${DC}" ]]; then
  SCRIPT_PATH="$(readlink -f -- "${BASH_SOURCE[0]}")"
  DC="$(cd -- "$(dirname -- "${SCRIPT_PATH}")/../../../.." && pwd)"
fi

detect() {
  # First check env var (e.g. called from apply-theme-mode.sh)
  if [[ -n "${DREAMCODER_THEME_MODE:-}" ]]; then
    echo "${DREAMCODER_THEME_MODE}"
    return
  fi
  if command -v gsettings &>/dev/null; then
    s="$(gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null || true)"
    [[ "$s" == *prefer-dark* ]] && {
      echo dark
      return
    }
    [[ "$s" == *default* || "$s" == *prefer-light* ]] && {
      echo light
      return
    }
  fi
  if [[ -f "$HOME/.theme-mode" ]]; then
    m="$(<"$HOME/.theme-mode")"
    [[ "$m" == dark || "$m" == light ]] && {
      echo "$m"
      return
    }
  fi
  if [[ -n "${COLORFGBG:-}" ]]; then
    bg="${COLORFGBG##*;}"
    [[ "$bg" -lt 8 ]] && echo light || echo dark
    return
  fi
  echo light
}

mode="$(detect)"
# Use canonical validated colors and the same destination precedence as sync.
# Disable adaptation locally: Matugen can write unrelated desktop templates.
# This helper touches only Pi/Gentle Shell themes and settings, not the desktop.
DREAMCODER_ADAPTIVE=0 PYTHONPATH="${DC}/src${PYTHONPATH:+:${PYTHONPATH}}" \
  python3 - "${mode}" <<'PY'
import sys
from dreamcoder_theme.settings import theme_paths
from dreamcoder_theme.sync import prepare, sync_pi_targets

prepared = prepare(sys.argv[1])
sync_pi_targets(theme_paths(), prepared.active)
PY
printf '→ Pi / Gentle Shell theme: %s\n' "${mode}"
