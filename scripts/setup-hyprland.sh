#!/usr/bin/env bash
# ============================================================================
# setup-hyprland.sh — Wire Dreamcoder theme into ML4W Hyprland environment
# ============================================================================
# Idempotent setup that integrates Dreamcoder theme colours and keybindings
# into an existing ML4W Hyprland installation.
#
# Usage:
#   ./scripts/setup-hyprland.sh                 # auto-detect profile
#   ./scripts/setup-hyprland.sh --profile asus-vivobook15  # explicit profile
#   ./scripts/setup-hyprland.sh --dry-run                 # preview only
#   ./scripts/setup-hyprland.sh --help                    # this message
#
# What it does:
#   1. Symlinks wlogout/colors.css → waybar/colors.css
#   2. Symlinks swaync/colors.css  → waybar/colors.css
#   3. Generates ~/.config/hypr/custom.lua from machine profile
#   4. Installs dreamcoder-toggle-theme.sh to ~/.config/hypr/scripts/
#   5. Applies wallpaper hooks (calls apply-ml4w-hooks.sh)
#   6. Reloads Hyprland configuration
#   7. Logs a summary of the integration
#
# Dependencies:
#   - jq (for custom.lua generation)
#   - luac (optional, for Lua syntax verification)
#   - Hyprland running (for reload)
# ============================================================================
set -euo pipefail

# ── configuration ───────────────────────────────────────────────────────────
DREAMCODER_DOTS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
[[ -f "${DREAMCODER_DOTS_DIR}/lib/ml4w.sh" ]] && source "${DREAMCODER_DOTS_DIR}/lib/ml4w.sh"
[[ -f "${DREAMCODER_DOTS_DIR}/lib/waybar.sh" ]] && source "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"
ASSETS_DIR="${DREAMCODER_DOTS_DIR}/ml4w_assets"
GENERATOR="${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh"
ML4W_HOOKS="${DREAMCODER_DOTS_DIR}/scripts/apply-ml4w-hooks.sh"

# System target paths
HYPR_DIR="${HOME}/.config/hypr"
HYPR_SCRIPTS="${HYPR_DIR}/scripts"
WLOGOUT_DIR="${HOME}/.config/wlogout"
SWAYNC_DIR="${HOME}/.config/swaync"

# Source assets
TOGGLE_SOURCE="${ASSETS_DIR}/hypr/scripts/dreamcoder-toggle-theme.sh"
TOGGLE_TARGET="${HYPR_SCRIPTS}/dreamcoder-toggle-theme.sh"

# ── flags ──────────────────────────────────────────────────────────────────
DRY_RUN=false
PROFILE_NAME=""

# ── helpers ─────────────────────────────────────────────────────────────────
info() { printf '  ✓ %s\n' "$*"; }
warn() { printf '  ⚠ %s\n' "$*" >&2; }
step() { printf '  • %s\n' "$*"; }
ok() { printf '  ✅ %s\n' "$*"; }
die() {
  printf '✖ %s\n' "$*" >&2
  exit 1
}
usage() {
  grep -E '^# ' "$0" | sed -n '4,/^$/{s/^# //;p}' | head -n -2
  echo ""
  echo "Options:"
  echo "  --profile NAME   Machine profile (default: auto-detect)"
  echo "  --dry-run        Preview changes without applying"
  echo "  --verbose        Show detailed output"
  echo "  --help, -h       Show this help"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
  --profile)
    shift
    if [[ -z "${1:-}" ]]; then
      die "--profile requires a non-empty profile name"
    fi
    PROFILE_NAME="$1"
    ;;
  --dry-run) DRY_RUN=true ;;
  --help | -h) usage ;;
  *) die "Unknown option: $1" ;;
  esac
  shift
done

# ── profile auto-detection ─────────────────────────────────────────────────
if [[ -z "${PROFILE_NAME}" ]]; then
  # Real hardware first (DMI), then hostname fallback. Hostnames like
  # "archlinux" never matched the ASUS laptop and the wrong profile
  # (no F1-F12 multimedia / brightness binds) was applied silently.
  DMI_PRODUCT="$(cat /sys/class/dmi/id/product_name 2>/dev/null || echo "unknown")"
  DMI_VENDOR="$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null || echo "unknown")"
  HOSTNAME="$(hostname -s 2>/dev/null || echo "unknown")"
  case "$(echo "${DMI_PRODUCT} ${DMI_VENDOR}" | tr '[:upper:]' '[:lower:]')" in
  *asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
  *) PROFILE_NAME="default" ;;
  esac
  if [[ "${PROFILE_NAME}" == "default" ]]; then
    case "$(echo "${HOSTNAME}" | tr '[:upper:]' '[:lower:]')" in
    *asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
    *) : ;;
    esac
  fi
  step "Auto-detected profile: ${PROFILE_NAME} (DMI: ${DMI_PRODUCT} / ${DMI_VENDOR})"
else
  step "Using profile: ${PROFILE_NAME}"
fi

# ── pre-flight validation ──────────────────────────────────────────────────
if $DRY_RUN; then
  step "Dry-run mode — no files will be modified"
  echo ""
fi

PASS=0

check() {
  local label="$1"
  shift 1
  if "$@" 2>/dev/null; then
    ok "${label}"
    ((++PASS))
  else
    die "${label}"
  fi
}

check_warn() {
  local label="$1"
  shift 1
  if "$@" 2>/dev/null; then
    ok "${label}"
    ((++PASS))
  else
    warn "${label}"
  fi
}

echo ""
echo "═══ Pre-flight checks ═══"

# Dependency checks
check "jq is installed" command -v jq
check_warn "luac available (Lua syntax)" command -v luac
check_warn "hyprctl available" command -v hyprctl

# Profile checks
SCHEMA_FILE="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/profile.schema.json"
PROFILE_FILE="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/${PROFILE_NAME}.json"

check "Profile exists: ${PROFILE_NAME}.json" test -f "${PROFILE_FILE}"
check "Profile is valid JSON" jq empty "${PROFILE_FILE}"
check "Schema file exists" test -f "${SCHEMA_FILE}"

# JSON Schema validation
SCHEMA_VALID=false
if command -v check-json >/dev/null; then
  if check-json --schema "${SCHEMA_FILE}" "${PROFILE_FILE}" 2>/dev/null; then
    SCHEMA_VALID=true
  fi
elif command -v python3 >/dev/null && python3 -c "import jsonschema" 2>/dev/null; then
  if python3 -c "
import json, sys
with open('${SCHEMA_FILE}') as f:
    schema = json.load(f)
with open('${PROFILE_FILE}') as f:
    profile = json.load(f)
import jsonschema
try:
    jsonschema.validate(instance=profile, schema=schema)
    sys.exit(0)
except jsonschema.ValidationError as e:
    print(e.message, file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
    SCHEMA_VALID=true
  fi
fi

if $SCHEMA_VALID; then
  ok "Profile matches schema"
  ((++PASS))
else
  warn "Profile schema validation — check profile.schema.json"
fi

# ML4W environment checks
check "Hyprland config is ML4W-managed" hyprland_is_ml4w_managed
check "Waybar config is ML4W-managed" waybar_is_ml4w_managed

# Hyprland running check
if command -v hyprctl >/dev/null; then
  check_warn "Hyprland is running" hyprctl monitors -j 2>/dev/null
fi

# Git worktree check
if command -v git >/dev/null; then
  REPO_ROOT="$(git -C "${DREAMCODER_DOTS_DIR}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "${REPO_ROOT}" ]] && ! git -C "${REPO_ROOT}" diff --quiet HEAD 2>/dev/null; then
    warn "Uncommitted changes in repo — commit before setup"
  fi
fi

echo ""
echo "  Pre-flight: ${PASS} passed"

# ── 1. Symlink wlogout → waybar colors ────────────────────────────────────
echo ""
echo "═══ Step 1: Symlink Wlogout colors → Waybar ═══"
if $DRY_RUN; then
  step "Would symlink: ${WLOGOUT_DIR}/colors.css → ../../waybar/colors.css"
  step "Would symlink: ${SWAYNC_DIR}/colors.css  → ../../waybar/colors.css"
else
  for target_dir in "${WLOGOUT_DIR}" "${SWAYNC_DIR}"; do
    local_colors="${target_dir}/colors.css"
    backup="${local_colors}.bak"

    if [[ -L "${local_colors}" ]]; then
      current_target=$(readlink "${local_colors}")
      if [[ "${current_target}" == "../../waybar/colors.css" ]]; then
        ok "Already linked: ${local_colors} → ${current_target}"
        continue
      fi
    fi

    # Backup if it's a regular file (not a symlink)
    if [[ -f "${local_colors}" && ! -L "${local_colors}" ]]; then
      cp "${local_colors}" "${backup}"
      info "Backed up: ${backup}"
    fi

    rm -f "${local_colors}"
    ln -sf "../../waybar/colors.css" "${local_colors}"
    info "Linked:  ${local_colors} → $(readlink "${local_colors}")"
  done
fi

# ── 2. Generate custom.lua from profile ───────────────────────────────────
echo ""
echo "═══ Step 2: Generate custom.lua from profile ═══"
if $DRY_RUN; then
  bash "${GENERATOR}" --profile "${PROFILE_NAME}" --dry-run 2>&1
else
  if [[ ! -f "${GENERATOR}" ]]; then
    die "Generator script not found: ${GENERATOR}"
  fi

  # Generate custom.lua
  bash "${GENERATOR}" --profile "${PROFILE_NAME}" 2>&1

  # Verify Lua syntax
  if command -v luac >/dev/null; then
    if luac -p "${HYPR_DIR}/custom.lua" 2>/dev/null; then
      ok "Lua syntax: valid"
    else
      warn "Lua syntax check FAILED — disabling custom.lua"
      mv "${HYPR_DIR}/custom.lua" "${HYPR_DIR}/custom.lua.err"
    fi
  fi
fi

# ── 3. Install keybindings variant (dreamcoder.lua) ────────────────────────
# ML4W ships default.lua and restores it on updates; editing it directly is
# fragile (official docs: use a separate keybinding VARIANT + selector). The
# selector (conf/keybinding.lua) points at our curated dreamcoder.lua variant,
# which only holds native binds the generator cannot emit. Re-applying both
# keeps the profile JSON the single source of truth for keyboard bindings.
KEYBIND_SELECTOR="${DREAMCODER_DOTS_DIR}/ml4w_assets/hypr/conf/keybinding.lua"
KEYBIND_VARIANT="${DREAMCODER_DOTS_DIR}/ml4w_assets/hypr/conf/keybindings/dreamcoder.lua"
KEYBIND_SELECTOR_TARGET="${HYPR_DIR}/conf/keybinding.lua"
KEYBIND_VARIANT_TARGET="${HYPR_DIR}/conf/keybindings/dreamcoder.lua"
echo ""
echo "═══ Step 3: Install keybindings variant (dreamcoder.lua) ═══"
if $DRY_RUN; then
  step "Would install keybindings selector + variant"
elif [[ -f "${KEYBIND_VARIANT}" ]] && grep -q "CONTRACT: This file only defines keybindings NOT managed" "${KEYBIND_VARIANT}" 2>/dev/null; then
  mkdir -p "$(dirname "${KEYBIND_SELECTOR_TARGET}")" "$(dirname "${KEYBIND_VARIANT_TARGET}")"
  cp "${KEYBIND_SELECTOR}" "${KEYBIND_SELECTOR_TARGET}"
  cp "${KEYBIND_VARIANT}" "${KEYBIND_VARIANT_TARGET}"
  info "Installed keybindings selector + dreamcoder.lua variant"
else
  warn "Keybindings variant missing or malformed: ${KEYBIND_VARIANT}"
fi

# ML4W's launch.sh prefers style-custom.css in the selected style theme dir.
# Optional: a machine without the ML4W selector must not fail setup.
if $DRY_RUN; then
  step "Would install Waybar accent override (style-custom.css)"
else
  install_waybar_override "${DREAMCODER_DOTS_DIR}" || true
fi

# ── 4. Install dreamcoder-toggle-theme.sh ─────────────────────────────────
echo ""
echo "═══ Step 4: Install dreamcoder-toggle-theme.sh ═══"
if $DRY_RUN; then
  step "Would install: ${TOGGLE_TARGET}"
else
  mkdir -p "${HYPR_SCRIPTS}"
  cp "${TOGGLE_SOURCE}" "${TOGGLE_TARGET}"
  chmod +x "${TOGGLE_TARGET}"
  info "Installed: ${TOGGLE_TARGET}"

  # Verify shell syntax
  if command -v bash >/dev/null; then
    bash -n "${TOGGLE_TARGET}" && ok "Shell syntax: valid"
  fi
fi

# ── 5. Apply ML4W wallpaper hooks ─────────────────────────────────────────
echo ""
echo "═══ Step 5: Apply ML4W wallpaper hooks ═══"
if $DRY_RUN; then
  step "Would run: ${ML4W_HOOKS}"
else
  if [[ -f "${ML4W_HOOKS}" ]]; then
    bash "${ML4W_HOOKS}" 2>&1
    ok "ML4W wallpaper hooks applied"
  else
    warn "ML4W hooks script not found: ${ML4W_HOOKS} — skipping"
  fi
fi

# ── 6. Reload Hyprland ────────────────────────────────────────────────────
echo ""
echo "═══ Step 6: Reload Hyprland ═══"
if $DRY_RUN; then
  step "Would run: hyprctl reload"
else
  if command -v hyprctl >/dev/null; then
    if hyprctl reload 2>&1 | grep -q "ok"; then
      ok "Hyprland reloaded successfully"
    else
      warn "Hyprland reload failed — check config syntax"
    fi
  else
    warn "hyprctl not available — Hyprland may not be running"
  fi
fi

# ── summary ────────────────────────────────────────────────────────────────
bindings_count=0
if [[ -f "${HYPR_DIR}/custom.lua" ]]; then
  bindings_count=$(grep -c 'hl.bind' "${HYPR_DIR}/custom.lua" || true)
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Dreamcoder ML4W setup complete"
echo "═══════════════════════════════════════════════"
echo "  Profile:       ${PROFILE_NAME}"
echo "  Keybindings:   ${bindings_count} in custom.lua"
echo "  Toggle script: installed → ${TOGGLE_TARGET}"
echo "  Wlogout/Swaync: shared → waybar/colors.css"
echo ""
echo "  Next steps:"
echo "    1. Edit keybindings → DreamcoderProfiles/dreamcoder/${PROFILE_NAME}.json"
echo "    2. Regenerate    → ./scripts/generate-custom-lua.sh [--profile ${PROFILE_NAME}]"
echo "    3. Reload        → hyprctl reload"
echo "    4. Verify        → ./scripts/dreamcoder doctor"
echo "═══════════════════════════════════════════════"
