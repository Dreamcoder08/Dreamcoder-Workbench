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

if command -v hyprctl >/dev/null; then
  if hyprctl monitors -j 2>/dev/null | jq -e 'length > 0' >/dev/null 2>&1; then
    ok "Hyprland is running"
  else
    fail "Hyprland is not running (no monitors detected)"
  fi
else
  fail "hyprctl not found — Hyprland not installed?"
fi

if command -v jq >/dev/null; then
  ok "jq is installed"
else
  fail "jq is not installed"
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
  if [[ -L "$path" ]]; then
    target=$(readlink "$path")
    ok "${label} (→ ${target})"
  elif [[ -f "$path" ]]; then
    warn "${label} — regular file, not symlink"
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

# Waybar colors.css (pointing to dreamcoder-colors-{mode}.css)
if [[ -L "${HOME}/.config/waybar/colors.css" ]]; then
  target=$(readlink "${HOME}/.config/waybar/colors.css")
  if [[ "$target" == *"dreamcoder"* ]]; then
    ok "waybar/colors.css → ${target}"
  else
    warn "waybar/colors.css → ${target} (not dreamcoder)"
  fi
else
  fail "waybar/colors.css is not a symlink"
fi

# Wlogout → waybar
if [[ -L "${HOME}/.config/wlogout/colors.css" ]]; then
  target=$(readlink "${HOME}/.config/wlogout/colors.css")
  if [[ "$target" == *"waybar/colors.css" ]]; then
    ok "wlogout/colors.css → waybar (shared)"
  else
    warn "wlogout/colors.css → ${target}"
  fi
else
  fail "wlogout/colors.css is not a symlink"
fi

# Swaync → waybar
if [[ -L "${HOME}/.config/swaync/colors.css" ]]; then
  target=$(readlink "${HOME}/.config/swaync/colors.css")
  if [[ "$target" == *"waybar/colors.css" ]]; then
    ok "swaync/colors.css → waybar (shared)"
  else
    warn "swaync/colors.css → ${target}"
  fi
else
  fail "swaync/colors.css is not a symlink"
fi

# Hyprland colors.lua
if [[ -L "${HOME}/.config/hypr/colors.lua" ]]; then
  target=$(readlink "${HOME}/.config/hypr/colors.lua")
  if [[ "$target" == *"dreamcoder"* ]]; then
    ok "hypr/colors.lua → ${target}"
  else
    warn "hypr/colors.lua → ${target} (not dreamcoder)"
  fi
else
  fail "hypr/colors.lua is not a symlink"
fi

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
    if [[ "$COLOR_TARGET" == *"${CURRENT_MODE}"* ]]; then
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

if [[ -n "${PROFILE_NAME}" ]]; then
  PROFILE_FILE="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/${PROFILE_NAME}.json"
else
  # Auto-detect
  HOSTNAME="$(hostname -s 2>/dev/null || echo "unknown")"
  case "$(echo "${HOSTNAME}" | tr '[:upper:]' '[:lower:]')" in
  *asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
  *) PROFILE_NAME="default" ;;
  esac
  PROFILE_FILE="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/${PROFILE_NAME}.json"
  info "Auto-detected profile: ${PROFILE_NAME}"
fi

if [[ -f "$PROFILE_FILE" ]]; then
  if jq empty "$PROFILE_FILE" 2>/dev/null; then
    ok "Profile ${PROFILE_NAME}.json is valid JSON"
  else
    fail "Profile ${PROFILE_NAME}.json is INVALID JSON"
  fi
else
  fail "Profile not found: ${PROFILE_FILE}"
fi

# Schema validation
SCHEMA_FILE="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/profile.schema.json"
if [[ -f "$SCHEMA_FILE" ]]; then
  ok "Schema file exists"
  if command -v python3 >/dev/null && python3 -c "import jsonschema" 2>/dev/null; then
    if python3 -c "
import json, sys
with open('${SCHEMA_FILE}') as f: schema = json.load(f)
with open('${PROFILE_FILE}') as f: profile = json.load(f)
import jsonschema
jsonschema.validate(instance=profile, schema=schema)
print('OK')
" 2>/dev/null; then
      ok "Profile matches schema"
    else
      warn "Profile does NOT match schema"
    fi
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
