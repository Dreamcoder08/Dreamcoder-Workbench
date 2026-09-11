#!/usr/bin/env bash
set -euo pipefail

source "${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}/lib/logging.sh"
source "${DREAMCODER_DOTS_DIR}/lib/env.sh"
source "${DREAMCODER_DOTS_DIR}/lib/checks.sh"
source "${DREAMCODER_DOTS_DIR}/lib/safety.sh"

ensure_dots_dir

CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"
CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
ML4W_CACHE="${ML4W_CACHE_DIR:-${CACHE_HOME}/ml4w/hyprland-dotfiles}"

ok() { printf '  ✅ %s\n' "$*"; }
warn() { printf '  ⚠ %s\n' "$*" >&2; }
fail() { printf '  ❌ %s\n' "$*" >&2; }
check_path() {
  if [[ -e "$1" ]]; then ok "present: $1"; else fail "missing: $1"; fi
}
check_symlink() {
  local path="$1" expected="$2" label="${3:-}"
  local label_str="${label:+ ($label)}"
  if [[ -L "$path" ]]; then
    local target
    target="$(readlink "$path")"
    if [[ -z "$expected" ]] || [[ "$target" == "$expected" ]]; then
      ok "symlink: ${path}${label_str} → ${target}"
    else
      warn "symlink: ${path} → ${target} (expected: ${expected})${label_str}"
    fi
  elif [[ -f "$path" ]]; then
    fail "regular file: ${path} (should be symlink)${label_str}"
  else
    fail "missing: ${path}${label_str}"
  fi
}

control() {
  PYTHONPATH="${DREAMCODER_DOTS_DIR}/scripts${PYTHONPATH:+:${PYTHONPATH}}" python3 -m dreamcoder_theme.control "$@"
}

# ── parse args ──────────────────────────────────────────────────────────────
ML4W_MODE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
  --ml4w)
    ML4W_MODE=true
    shift
    ;;
  *) shift ;;
  esac
done

# ── standard checks ─────────────────────────────────────────────────────────
if ! $ML4W_MODE; then
  printf '\nStructured health:\n'
  control doctor || true

  printf '\nLegacy checks:\n'
  printf 'Mode: '
  head -1 "${CONFIG_HOME}/ghostty/themes/dreamcoder" 2>/dev/null || warn 'ghostty theme missing'

  printf 'GTK: '
  if command -v gsettings >/dev/null; then
    gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null || warn 'unreadable'
  else
    warn 'gsettings unavailable'
  fi

  printf 'Wallpaper: '
  cat "${ML4W_CACHE}/current_wallpaper" 2>/dev/null || warn 'wallpaper cache missing'

  printf 'opencode: '
  if command -v python3 >/dev/null; then
    CONFIG_HOME="${CONFIG_HOME}" python3 -c '
import json, os, pathlib
p = pathlib.Path(os.environ["CONFIG_HOME"]) / "opencode/tui.json"
print(json.loads(p.read_text()).get("theme", "unset"))
' 2>/dev/null || printf 'unknown\n'
  else
    printf 'unknown\n'
  fi

  for path in \
    "${CONFIG_HOME}/kitty" \
    "${CONFIG_HOME}/ghostty" \
    "${CONFIG_HOME}/starship.toml" \
    "${CONFIG_HOME}/hypr/colors.lua" \
    "${CONFIG_HOME}/hypr/colors.conf" \
    "${CONFIG_HOME}/waybar/colors.css" \
    "${CONFIG_HOME}/rofi/colors.rasi"; do
    check_path "${path}"
  done

  if [[ -L "${CONFIG_HOME}/dunst/dreamcoder-dunst.conf" ]]; then
    target=$(readlink "${CONFIG_HOME}/dunst/dreamcoder-dunst.conf")
    printf '  dunst symlink → %s\n' "${target}"
  else
    warn 'dunst/dreamcoder-dunst.conf missing or not a symlink'
  fi

  if command -v systemctl >/dev/null && systemctl --user is-active --quiet dreamcoder-theme-auto.timer; then
    ok 'timer active'
  else
    warn 'timer inactive'
  fi

  printf 'Git integrity: '
  if git -C "${DREAMCODER_DOTS_DIR}" fsck --full --no-progress --no-dangling >/dev/null 2>&1; then
    ok 'object store consistent'
  else
    fail 'git fsck reported object-store errors (run: git fsck --full)'
  fi

  "${DREAMCODER_DOTS_DIR}/.venv/bin/python3" "${DREAMCODER_DOTS_DIR}/scripts/verify-theme-health.py"
  exit 0
fi

# ════════════════════════════════════════════════════════════════════════════
# ML4W MODE — comprehensive ML4W integration checks
# ════════════════════════════════════════════════════════════════════════════

PASS=0
FAIL=0
WARN=0

section() { printf '\n——— %s ———\n' "$*"; }
summary() {
  printf '\n═══════════════════════════════════════════════════════════════\n'
  if [[ "$FAIL" -eq 0 ]]; then
    printf '  ✅ ALL ML4W CHECKS PASSED  (%d passed, %d warnings)\n' "$PASS" "$WARN"
  else
    printf '  ❌ %d check(s) FAILED  (%d passed, %d failed, %d warnings)\n' "$FAIL" "$PASS" "$FAIL" "$WARN"
  fi
  printf '═══════════════════════════════════════════════════════════════\n'
}

# ── 1. System dependencies ──────────────────────────────────────────────────
section '1. Dependencies'

for cmd in hyprctl jq luac; do
  if command -v "$cmd" >/dev/null; then
    ok "$cmd is installed"
    ((++PASS))
  else
    warn "$cmd not found (some checks skipped)"
    ((++WARN))
  fi
done

# ── 2. ML4W symlinks (reinstall resilience) ────────────────────────────────
section '2. ML4W dotfiles symlinks'

ML4W_SYMLINKS=(
  "${CONFIG_HOME}/hypr"
  "${CONFIG_HOME}/waybar"
  "${CONFIG_HOME}/rofi"
  "${CONFIG_HOME}/wlogout"
  "${CONFIG_HOME}/swaync"
)

ML4W_EXPECTED_PREFIX="${HOME}/.mydotfiles"

resolve_symlink() {
  local p="$1"
  local dir
  dir="$(dirname "$p")"
  local target
  target="$(readlink "$p")"
  if [[ "$target" == /* ]]; then
    echo "$target"
  else
    # Resolve relative symlink from parent dir
    (cd "$dir" 2>/dev/null && readlink -f "$p" 2>/dev/null) || echo "$dir/$target"
  fi
}

for path in "${ML4W_SYMLINKS[@]}"; do
  if [[ -L "$path" ]]; then
    abs_target="$(resolve_symlink "$path")"
    if [[ "$abs_target" == "${ML4W_EXPECTED_PREFIX}"* ]]; then
      ok "ML4W symlink: ${path}"
      ((++PASS))
    else
      warn "ML4W symlink: ${path} → ${abs_target} (outside ${ML4W_EXPECTED_PREFIX})"
      ((++WARN))
    fi
  elif [[ -d "$path" ]]; then
    fail "ML4W: ${path} is a regular directory (NOT a symlink) — run setup-hyprland.sh"
    ((++FAIL))
  else
    fail "ML4W: ${path} does not exist"
    ((++FAIL))
  fi
done

# ── 3. Colour file chain ────────────────────────────────────────────────────
section '3. Colour file chain'

check_symlink "${CONFIG_HOME}/waybar/colors.css" "" "waybar → dreamcoder"
check_symlink "${CONFIG_HOME}/wlogout/colors.css" "../../waybar/colors.css" "wlogout → waybar"
check_symlink "${CONFIG_HOME}/swaync/colors.css" "../../waybar/colors.css" "swaync → waybar"
check_symlink "${CONFIG_HOME}/hypr/colors.lua" "" "hypr → dreamcoder"

# Verify colour files exist
if [[ -L "${CONFIG_HOME}/waybar/colors.css" ]]; then
  target=$(readlink "${CONFIG_HOME}/waybar/colors.css")
  full="${CONFIG_HOME}/waybar/$(dirname "${target}")/$(basename "${target}")"
  # Normalize path
  if [[ "$target" == */* ]]; then
    full="${CONFIG_HOME}/waybar/${target}"
  fi
  if [[ -f "$full" ]]; then
    ok "Colour target exists: ${full}"
    ((++PASS))
  else
    fail "Colour target missing: ${full} (broken symlink?)"
    ((++FAIL))
  fi
fi

# Dreamcoder colour variants (both naming conventions)
for variant in colors-light.css colors-dark.css dreamcoder-colors-light.css dreamcoder-colors-dark.css dreamcoder-colors.css; do
  if [[ -f "${CONFIG_HOME}/waybar/${variant}" ]]; then
    ok "Colour variant: ${variant}"
    ((++PASS))
  fi
done

# ── 4. custom.lua ───────────────────────────────────────────────────────────
section '4. Keybinding file'

CUSTOM_LUA="${CONFIG_HOME}/hypr/custom.lua"
if [[ -f "$CUSTOM_LUA" ]]; then
  if command -v luac >/dev/null; then
    if luac -p "$CUSTOM_LUA" 2>/dev/null; then
      ok "custom.lua — syntax valid"
      ((++PASS))
    else
      fail "custom.lua — INVALID syntax"
      ((++FAIL))
    fi
  else
    ok "custom.lua exists"
    ((++PASS))
  fi

  count=$(grep -c 'hl.bind' "$CUSTOM_LUA" 2>/dev/null || echo 0)
  ok "custom.lua: ${count} binding(s) defined"
  ((++PASS))

  if grep -q 'dreamcoder-toggle-theme' "$CUSTOM_LUA" 2>/dev/null; then
    ok "Theme toggle binding present"
    ((++PASS))
  else
    warn "Theme toggle binding missing"
    ((++WARN))
  fi
else
  fail "custom.lua not found — run generate-custom-lua.sh"
  ((++FAIL))
fi

# ── 5. Toggle script ────────────────────────────────────────────────────────
section '5. Toggle script'

TOGGLE="${CONFIG_HOME}/hypr/scripts/dreamcoder-toggle-theme.sh"
if [[ -x "$TOGGLE" ]]; then
  ok "Toggle script installed and executable"
  ((++PASS))
  if bash -n "$TOGGLE" 2>/dev/null; then
    ok "Toggle script shell syntax valid"
    ((++PASS))
  else
    fail "Toggle script shell syntax INVALID"
    ((++FAIL))
  fi
else
  fail "Toggle script not found at ${TOGGLE}"
  ((++FAIL))
fi

# ── 6. Theme state ──────────────────────────────────────────────────────────
section '6. Theme state'

ENV_FILE="${CACHE_HOME}/dreamcoder/cursor-cli.env"
if [[ -f "$ENV_FILE" ]]; then
  mode=""
  # shellcheck source=/dev/null
  source "$ENV_FILE" 2>/dev/null && mode="${DREAMCODER_THEME_MODE:-}"
  if [[ -n "$mode" ]]; then
    ok "Theme mode: ${mode}"
    ((++PASS))

    # Check waybar colors.css matches current mode
    if [[ -L "${CONFIG_HOME}/waybar/colors.css" ]]; then
      target=$(readlink "${CONFIG_HOME}/waybar/colors.css")
      if [[ "$target" == *"${mode}"* ]]; then
        ok "waybar/colors.css matches current mode (${mode})"
        ((++PASS))
      else
        warn "waybar/colors.css (${target}) vs mode (${mode}) — may be out of sync"
        ((++WARN))
      fi
    fi
  else
    warn "Theme mode not readable from env file"
    ((++WARN))
  fi
else
  warn "Theme env file not found: ${ENV_FILE}"
  ((++WARN))
fi

# ── 7. Profile detection ────────────────────────────────────────────────────
section '7. Machine profile'

PROFILES_DIR="/DreamcoderProfiles/dreamcoder"
HOSTNAME="$(hostname -s 2>/dev/null || echo "unknown")"

case "$(echo "${HOSTNAME}" | tr '[:upper:]' '[:lower:]')" in
*asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
*) PROFILE_NAME="default" ;;
esac

PROFILE_FILE="${PROFILES_DIR}/${PROFILE_NAME}.json"
SCHEMA_FILE="${PROFILES_DIR}/profile.schema.json"

ok "Auto-detected profile: ${PROFILE_NAME} (hostname: ${HOSTNAME})"
((++PASS))

if [[ -f "$PROFILE_FILE" ]]; then
  if jq empty "$PROFILE_FILE" 2>/dev/null; then
    ok "Profile ${PROFILE_NAME}.json is valid JSON"
    ((++PASS))
  else
    fail "Profile ${PROFILE_NAME}.json is INVALID JSON"
    ((++FAIL))
  fi
else
  warn "Profile not found: ${PROFILE_FILE} — using default fallback"
  ((++WARN))
fi

# Optional schema validation
if [[ -f "$SCHEMA_FILE" ]] && command -v python3 >/dev/null && python3 -c "import jsonschema" 2>/dev/null; then
  if python3 -c "
import json, sys
with open('${SCHEMA_FILE}') as f: schema = json.load(f)
with open('${PROFILE_FILE}') as f: data = json.load(f)
import jsonschema
jsonschema.validate(instance=data, schema=schema)
print('OK')
" 2>/dev/null; then
    ok "Profile matches schema"
    ((++PASS))
  else
    warn "Profile does NOT match schema"
    ((++WARN))
  fi
fi

# ── 8. Hyprland running? ────────────────────────────────────────────────────
section '8. Hyprland status'

if command -v hyprctl >/dev/null; then
  if hyprctl monitors -j 2>/dev/null | jq -e 'length > 0' >/dev/null 2>&1; then
    ok "Hyprland is running"
    ((++PASS))
  else
    warn "Hyprland not running (no monitors)"
    ((++WARN))
  fi
fi

# ── 9. Reinstall resilience ─────────────────────────────────────────────────
section '9. Reinstall resilience'

BROKEN=false
for path in "${ML4W_SYMLINKS[@]}"; do
  if [[ -d "$path" ]] && [[ ! -L "$path" ]]; then
    fail "RESILIENCE: ${path} is a regular directory, not symlink — ML4W installer overwrote it!"
    ((++FAIL))
    BROKEN=true
  fi
  if [[ -L "$path" ]]; then
    abs_target="$(resolve_symlink "$path")"
    if [[ "$abs_target" != "${ML4W_EXPECTED_PREFIX}"* ]]; then
      warn "RESILIENCE: ${path} → ${abs_target} (outside ML4W managed dirs)"
      ((++WARN))
    fi
  fi
done

if $BROKEN; then
  printf '\n  🛠️  ML4W reinstalled detected! Run:\n'
  printf '     ./scripts/setup-hyprland.sh --profile %s\n\n' "${PROFILE_NAME}"
else
  ok "All ML4W dotfiles symlinks intact"
  ((++PASS))
fi

# ── 10. Dreamcoder generators available ────────────────────────────────────
section '10. Dreamcoder generators'

for script in generate-custom-lua.sh setup-hyprland.sh verify-ml4w-setup.sh validate-ml4w-profiles.py; do
  if [[ -f "/scripts/${script}" ]]; then
    ok "Script available: ${script}"
    ((++PASS))
  else
    warn "Script missing: ${script}"
    ((++WARN))
  fi
done

summary
exit $((FAIL > 0 ? 1 : 0))
