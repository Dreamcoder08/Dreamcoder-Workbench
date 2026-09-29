#!/usr/bin/env bash
# ============================================================================
# verify-ml4w-setup.sh — Verify ML4W Dreamcoder integration health
# ============================================================================
# Post-reboot verification script. Checks all components of the Dreamcoder
# ML4W integration are correctly wired and operational.
#
# Usage:
#   ./scripts/verify-ml4w-setup.sh          # full check
#   ./scripts/verify-ml4w-setup.sh --quiet  # only report failures
#   ./scripts/verify-ml4w-setup.sh --help   # this message
#   ./scripts/verify-ml4w-setup.sh --profile asus-vivobook15  # specific profile
#
# Exit codes:
#   0 = all checks passed
#   1 = one or more checks failed
#   2 = pre-flight error (no Hyprland, missing commands)
# ============================================================================
set -euo pipefail

# ── configuration ─────────────────────────────────────────────────────────────
DREAMCODER_DOTS_DIR="${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
[[ -f "${DREAMCODER_DOTS_DIR}/lib/ml4w.sh" ]] && source "${DREAMCODER_DOTS_DIR}/lib/ml4w.sh"
QUIET=false
PROFILE_NAME=""
EXIT_CODE=0

# ── helpers ───────────────────────────────────────────────────────────────────
PASS=0
FAIL=0
WARN=0

info() { [[ "$QUIET" == "true" ]] || printf '  ✓ %s\n' "$*"; }
warn() {
  printf '  ⚠ %s\n' "$*" >&2
  ((++WARN))
}
ok() {
  [[ "$QUIET" == "true" ]] || printf '  ✅ %s\n' "$*"
  ((++PASS))
}
fail() {
  printf '  ❌ %s\n' "$*" >&2
  ((++FAIL))
  EXIT_CODE=1
}
die() {
  printf '✖ %s\n' "$*" >&2
  exit 2
}
title() { printf '\n——— %s ———\n' "$*"; }

usage() {
  grep -E '^# ' "$0" | sed -n '4,/^$/{s/^# //;p}' | head -n -2
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
  --quiet | -q) QUIET=true ;;
  --help | -h) usage ;;
  --profile)
    shift
    if [[ -z "${1:-}" ]]; then
      die "--profile requires a non-empty profile name"
    fi
    PROFILE_NAME="$1"
    ;;
  *) die "Unknown option: $1" ;;
  esac
  shift
done

# ── pre-flight ═════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════"
echo "  Dreamcoder ML4W — Post-Reboot Verification"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# ── 1. System checks ═════════════════════════════════════════════════════════
title "1. System"

have_jq=0
if command -v jq >/dev/null; then
  ok "jq is installed"
  have_jq=1
else
  fail "jq is not installed"
fi

if ! command -v hyprctl >/dev/null; then
  fail "hyprctl not found — Hyprland not installed?"
elif ((!have_jq)); then
  warn "Hyprland running check skipped (needs jq)"
elif hyprctl monitors -j 2>/dev/null | jq -e 'length > 0' >/dev/null 2>&1; then
  ok "Hyprland is running"
else
  fail "Hyprland is not running (no monitors detected)"
fi

HYPR_VERSION=""
if command -v hyprctl >/dev/null; then
  HYPR_VERSION="$(hyprctl version 2>/dev/null | head -1 | grep -oP 'Hyprland \K[^ ]+' || echo "unknown")"
  info "Hyprland version: ${HYPR_VERSION}"
fi

# ── 2. Dotfiles symlinks ═════════════════════════════════════════════════════
title "2. Dotfiles symlinks"

SYMLINKS=(
  "${HOME}/.config/rofi/config.rasi:Rofi config → ML4W managed"
  "${HOME}/.config/wlogout/layout:Wlogout layout → ML4W managed"
  "${HOME}/.config/swaync/config.json:Swaync config → ML4W managed"
)

for entry in "${SYMLINKS[@]}"; do
  path="${entry%%:*}"
  label="${entry#*:}"
  if path_is_ml4w_managed "$path"; then
    ok "${label} (→ $(readlink -f -- "$path"))"
  elif [[ -f "$path" ]]; then
    warn "${label} — regular file outside the ML4W dotfiles"
  else
    fail "${label} — NOT FOUND"
  fi
done

# Hyprland and Waybar are asserted as ML4W-managed rather than as symlinks:
# current ML4W keeps ~/.config/hypr and ~/.config/waybar as real directories
# backed by its own dotfiles repository, and only older ML4W symlinks the
# individual config files.
if hyprland_is_ml4w_managed; then
  ok "Hyprland config → ML4W managed"
else
  fail "Hyprland config → ML4W managed (neither ML4W layout found)"
fi

if waybar_is_ml4w_managed; then
  ok "Waybar config → ML4W managed"
else
  fail "Waybar config → ML4W managed (neither ML4W layout found)"
fi

# ── 3. Colour file symlinks ══════════════════════════════════════════════════
title "3. Colour file chain"

# Waybar colors.css: a Dreamcoder symlink or a regular file rendered by the
# theme sync (same rule as the Hyprland colour files below).
waybar_colors_path="${HOME}/.config/waybar/colors.css"
if waybar_colors_is_dreamcoder "${waybar_colors_path}"; then
  if [[ -L "${waybar_colors_path}" ]]; then
    ok "waybar/colors.css → $(readlink "${waybar_colors_path}")"
  else
    ok "waybar/colors.css carries Dreamcoder colours (managed regular file)"
  fi
elif [[ -L "${waybar_colors_path}" ]]; then
  warn "waybar/colors.css → $(readlink "${waybar_colors_path}") (not dreamcoder)"
elif [[ -f "${waybar_colors_path}" ]]; then
  fail "waybar/colors.css has no Dreamcoder colours (Matugen overwrote it?) — run ./scripts/dreamcoder sync"
else
  fail "waybar/colors.css is missing"
fi

# Wlogout and Swaync share Waybar's colours through a symlink.
check_shared_waybar_colors() {
  local app="$1" link="${HOME}/.config/${1}/colors.css" target
  if [[ -L "$link" ]]; then
    target=$(readlink "$link")
    if [[ "$target" == *"waybar/colors.css" ]]; then
      ok "${app}/colors.css → waybar (shared)"
    else
      warn "${app}/colors.css → ${target}"
    fi
  else
    fail "${app}/colors.css is not a symlink"
  fi
}
check_shared_waybar_colors wlogout
check_shared_waybar_colors swaync

# Hyprland colors.lua / colors.conf: a Dreamcoder symlink or a managed regular
# file with Dreamcoder content (ML4W 2.16 ships regular files; the sync writes
# through them). Only foreign content or a missing file fails.
for hypr_colors in colors.lua colors.conf; do
  hypr_colors_path="${HOME}/.config/hypr/${hypr_colors}"
  if hypr_colors_is_dreamcoder "${hypr_colors_path}"; then
    if [[ -L "${hypr_colors_path}" ]]; then
      ok "hypr/${hypr_colors} → $(readlink "${hypr_colors_path}")"
    else
      ok "hypr/${hypr_colors} carries Dreamcoder colours (managed regular file)"
    fi
  elif [[ -L "${hypr_colors_path}" ]]; then
    warn "hypr/${hypr_colors} → $(readlink "${hypr_colors_path}") (not dreamcoder)"
  elif [[ -f "${hypr_colors_path}" ]]; then
    fail "hypr/${hypr_colors} has no Dreamcoder colours (Matugen overwrote it?) — run ./scripts/dreamcoder sync"
  else
    fail "hypr/${hypr_colors} is missing"
  fi
done

# ── 4. custom.lua ═══════════════════════════════════════════════════════════
title "4. Keybinding file"

if [[ -f "${HOME}/.config/hypr/custom.lua" ]]; then
  if command -v luac >/dev/null; then
    if luac -p "${HOME}/.config/hypr/custom.lua" 2>/dev/null; then
      ok "custom.lua exists and Lua syntax is valid"
    else
      fail "custom.lua exists but Lua syntax is INVALID"
    fi
  else
    ok "custom.lua exists (luac not available for syntax check)"
  fi

  # Count bindings
  BINDINGS=$(grep -c 'hl.bind' "${HOME}/.config/hypr/custom.lua" 2>/dev/null || echo "0")
  info "custom.lua: ${BINDINGS} keybinding(s) defined"

  # Check for known bindings
  if grep -q 'dreamcoder-toggle-theme' "${HOME}/.config/hypr/custom.lua" 2>/dev/null; then
    ok "Theme toggle binding found"
  else
    warn "Theme toggle binding NOT found in custom.lua"
  fi
else
  fail "custom.lua does not exist"
fi

# ── 5. Toggle script ════════════════════════════════════════════════════════
title "5. Toggle script"

TOGGLE="${HOME}/.config/hypr/scripts/dreamcoder-toggle-theme.sh"
if [[ -x "$TOGGLE" ]]; then
  ok "Toggle script installed and executable"
  # Shell syntax check
  if bash -n "$TOGGLE" 2>/dev/null; then
    ok "Toggle script shell syntax: valid"
  else
    fail "Toggle script shell syntax: INVALID"
  fi
else
  fail "Toggle script not found at ${TOGGLE}"
fi

# ── 6. Current theme state ═════════════════════════════════════════════════
title "6. Theme state"

ENV_FILE="${XDG_CACHE_HOME:-${HOME}/.cache}/dreamcoder/cursor-cli.env"
if [[ -f "$ENV_FILE" ]]; then
  CURRENT_MODE=""
  # shellcheck source=/dev/null
  source "$ENV_FILE" 2>/dev/null && CURRENT_MODE="${DREAMCODER_THEME_MODE:-}"
  if [[ -n "$CURRENT_MODE" ]]; then
    ok "Current theme mode: ${CURRENT_MODE}"

    # Verify colour files match the current mode
    COLOR_TARGET=$(readlink "${HOME}/.config/waybar/colors.css" 2>/dev/null || echo "")
    if [[ -z "$COLOR_TARGET" ]] && waybar_colors_is_dreamcoder "${HOME}/.config/waybar/colors.css"; then
      ok "waybar/colors.css is rendered by the sync for the active mode"
    elif [[ "$COLOR_TARGET" == *"${CURRENT_MODE}"* ]]; then
      ok "waybar/colors.css matches current mode"
    else
      warn "waybar/colors.css (${COLOR_TARGET}) may not match mode (${CURRENT_MODE})"
    fi
  else
    warn "Theme mode not readable from ${ENV_FILE}"
  fi
else
  warn "Theme env file not found: ${ENV_FILE} (run apply-theme-mode.sh first)"
fi

# ── 7. ML4W profile ═══════════════════════════════════════════════════════
title "7. ML4W profile"

if [[ -z "${PROFILE_NAME}" ]]; then
  # Auto-detect
  HOSTNAME="$(hostname -s 2>/dev/null || echo "unknown")"
  case "$(echo "${HOSTNAME}" | tr '[:upper:]' '[:lower:]')" in
  *asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
  *) PROFILE_NAME="default" ;;
  esac
  info "Auto-detected profile: ${PROFILE_NAME}"
fi
PROFILES_DIR="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder"
PROFILE_FILE="${PROFILES_DIR}/${PROFILE_NAME}.json"

if [[ -f "$PROFILE_FILE" ]]; then
  if ((!have_jq)); then
    warn "Profile ${PROFILE_NAME}.json JSON check skipped (needs jq)"
  elif jq empty "$PROFILE_FILE" 2>/dev/null; then
    ok "Profile ${PROFILE_NAME}.json is valid JSON"
  else
    fail "Profile ${PROFILE_NAME}.json is INVALID JSON"
  fi
else
  fail "Profile not found: ${PROFILE_FILE}"
fi

# Schema validation
SCHEMA_FILE="${PROFILES_DIR}/profile.schema.json"
if [[ -f "$SCHEMA_FILE" ]]; then
  ok "Schema file exists"
  if command -v python3 >/dev/null && python3 -c "import jsonschema" 2>/dev/null; then
    # Paths travel through argv: interpolating them into Python source breaks on a
    # quote and would let a crafted path run code.
    if python3 - "$SCHEMA_FILE" "$PROFILE_FILE" 2>/dev/null <<'PY'
import json
import sys

import jsonschema

with open(sys.argv[1]) as f:
    schema = json.load(f)
with open(sys.argv[2]) as f:
    profile = json.load(f)
jsonschema.validate(instance=profile, schema=schema)
PY
    then
      ok "Profile matches schema"
    else
      warn "Profile does NOT match schema"
    fi
  else
    warn "Schema validation skipped (python3 with jsonschema not available)"
  fi
else
  warn "Schema file not found"
fi

# ── 8. Git repo health ═════════════════════════════════════════════════════
title "8. Git repo"

if command -v git >/dev/null; then
  REPO_ROOT="$(git -C "${DREAMCODER_DOTS_DIR}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "${REPO_ROOT}" ]]; then
    # Check working tree
    if git -C "${REPO_ROOT}" diff --quiet HEAD 2>/dev/null; then
      ok "Git working tree is clean"
    else
      warn "Git working tree has uncommitted changes"
    fi

    # Check ahead of origin
    AHEAD="$(git -C "${REPO_ROOT}" rev-list --count origin/main..HEAD 2>/dev/null || echo "0")"
    if [[ "$AHEAD" -gt 0 ]]; then
      info "${AHEAD} commit(s) ahead of origin/main"
    fi

    # Last commit
    LAST_COMMIT="$(git -C "${REPO_ROOT}" log -1 --format='%h %s' 2>/dev/null || true)"
    info "Last commit: ${LAST_COMMIT}"
  else
    warn "Not a git repository"
  fi
else
  warn "git not available"
fi

# ── 9. Renderers and generators ════════════════════════════════════════════
title "9. Dreamcoder generators"

GENERATOR="${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh"
if [[ -f "$GENERATOR" ]]; then
  ok "custom.lua generator exists"
else
  fail "custom.lua generator missing: ${GENERATOR}"
fi

SETUP_SCRIPT="${DREAMCODER_DOTS_DIR}/scripts/setup-hyprland.sh"
if [[ -f "$SETUP_SCRIPT" ]]; then
  ok "setup-hyprland.sh exists"
else
  fail "setup-hyprland.sh missing: ${SETUP_SCRIPT}"
fi

# ── summary ═══════════════════════════════════════════════════════════════════
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
if [[ "$EXIT_CODE" -eq 0 ]]; then
  echo "  ✅ ALL CHECKS PASSED  (${PASS} passed, ${FAIL} failed, ${WARN} warnings)"
else
  echo "  ❌ CHECKS FAILED  (${PASS} passed, ${FAIL} failed, ${WARN} warnings)"
fi
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Recommended next steps:"
echo "  1. Run: SUPER + SHIFT + D  → toggle theme"
echo "  2. Run: SUPER + SHIFT + U  → blue light filter"
echo "  3. Run: hyprctl reload     → if config changed"
echo "  4. Run: SUPER + F11        → lock screen"
echo ""

exit "$EXIT_CODE"
