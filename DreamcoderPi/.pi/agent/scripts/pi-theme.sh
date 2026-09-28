#!/usr/bin/env bash
set -euo pipefail

DD="${DOTS_DIR:-$HOME/Documents/PROYECTOS/dreamcoder-dots}"
DC="${DREAMCODER_DOTS_DIR:-$DD}"
LN="$HOME/.pi/agent/themes/dreamcoder.json"

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
src="$DC/DreamcoderPi/.pi/agent/themes/dreamcoder-$mode.json"
[[ -f "$src" ]] || {
  echo "✗ $src not found" >&2
  exit 1
}
mkdir -p "$(dirname "$LN")"
ln -sf "$src" "$LN"
echo "→ pi-theme: $mode"
