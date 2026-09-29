#!/usr/bin/env bash
# ============================================================================
# generate-custom-lua.sh — Generate Hyprland custom.lua from machine profile
# ============================================================================
# Reads keybinding definitions from the active Dreamcoder machine profile
# (JSON) and emits a well-formed Lua file at ~/.config/hypr/custom.lua.
#
# Usage:
#   ./scripts/generate-custom-lua.sh                           # auto-detect profile
#   ./scripts/generate-custom-lua.sh --profile asus-vivobook15  # explicit profile
#   ./scripts/generate-custom-lua.sh --dry-run                  # preview only
#   ./scripts/generate-custom-lua.sh --validate                 # validate + exit
#   ./scripts/generate-custom-lua.sh --list-profiles            # list available
#   ./scripts/generate-custom-lua.sh --help                    # this message
#
# Dependencies: jq (JSON processor)
# ============================================================================
set -euo pipefail

# ── helpers ─────────────────────────────────────────────────────────────────
info() { printf '  ✓ %s\n' "$*"; }
warn() { printf '  ⚠ %s\n' "$*" >&2; }
die() {
  printf '✖ %s\n' "$*" >&2
  exit 1
}

# ── paths ────────────────────────────────────────────────────────────────────
# shellcheck disable=SC1091  # dynamic path (DREAMCODER_DOTS_DIR fallback)
source "${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}/lib/env.sh"
ensure_dots_dir
OUTPUT="${HOME}/.config/hypr/custom.lua"
PROFILES_DIR="${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder"

# ── profile resolution ──────────────────────────────────────────────────────
PROFILE_NAME="${DREAMCODER_PROFILE:-}"
DRY_RUN=false
VALIDATE_ONLY=false
LIST_PROFILES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
  --profile)
    shift
    PROFILE_NAME="$1"
    ;;
  --dry-run) DRY_RUN=true ;;
  --validate) VALIDATE_ONLY=true ;;
  --list-profiles) LIST_PROFILES=true ;;
  --help | -h)
    sed -n '/^# ====/,/^# ====/p' "$0" | grep -E '^# ' | sed 's/^# //'
    exit 0
    ;;
  *) die "Unknown option: $1" ;;
  esac
  shift
done

# ── --list-profiles ─────────────────────────────────────────────────────────
if $LIST_PROFILES; then
  echo "Available profiles:"
  for f in "${PROFILES_DIR}"/*.json; do
    name="$(basename "${f}" .json)"
    [[ "${name}" == "profile.schema" ]] && continue
    desc="$(jq -r '.description // "(no description)"' "${f}" 2>/dev/null || echo "(invalid)")"
    printf '  • %-20s %s\n' "${name}" "${desc}"
  done
  exit 0
fi

# ── auto-detect profile ─────────────────────────────────────────────────────
if [[ -z "${PROFILE_NAME}" ]]; then
  # Detect real hardware first (DMI), fall back to hostname. Hostnames like
  # "archlinux" never matched the ASUS laptop, silently applying the wrong
  # profile (no F1-F12 multimedia / brightness bindings).
  DMI_PRODUCT="$(cat /sys/class/dmi/id/product_name 2>/dev/null || echo "unknown")"
  DMI_VENDOR="$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null || echo "unknown")"
  HOSTNAME="$(hostname -s 2>/dev/null || echo "unknown")"
  DETECT_SOURCE="DMI"
  case "$(echo "${DMI_PRODUCT} ${DMI_VENDOR}" | tr '[:upper:]' '[:lower:]')" in
  *asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
  *) PROFILE_NAME="default" ;;
  esac
  if [[ "${PROFILE_NAME}" == "default" ]]; then
    case "$(echo "${HOSTNAME}" | tr '[:upper:]' '[:lower:]')" in
    *asus* | *vivobook*) PROFILE_NAME="asus-vivobook15" ;;
    *) : ;;
    esac
    [[ "${PROFILE_NAME}" == "default" ]] && DETECT_SOURCE="DMI+hostname"
  fi
  info "Auto-detected profile: ${PROFILE_NAME} (${DETECT_SOURCE}: ${DMI_PRODUCT} / ${DMI_VENDOR})"
fi

PROFILE_FILE="${PROFILES_DIR}/${PROFILE_NAME}.json"
SCHEMA_FILE="${PROFILES_DIR}/profile.schema.json"

if [[ ! -f "${PROFILE_FILE}" ]]; then
  die "Profile not found: ${PROFILE_FILE}"
fi

# ── pre-flight ──────────────────────────────────────────────────────────────
command -v jq >/dev/null || die "jq is required but not installed."

# Validate JSON syntax
if ! jq empty "${PROFILE_FILE}" 2>/dev/null; then
  die "Profile is not valid JSON: ${PROFILE_FILE}"
fi

# Validate against schema (optional — requires check-json or Python + jsonschema)
if [[ -f "${SCHEMA_FILE}" ]]; then
  SCHEMA_OK=false
  if command -v check-json >/dev/null; then
    if check-json --schema "${SCHEMA_FILE}" "${PROFILE_FILE}" 2>/dev/null; then
      SCHEMA_OK=true
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
        print(f'Schema error: {e.message}', file=sys.stderr)
        sys.exit(1)
    " 2>/dev/null; then
      SCHEMA_OK=true
    fi
  fi
  if $SCHEMA_OK; then
    info "Profile JSON valid — matches schema"
  else
    warn "Profile schema validation unavailable or failed"
  fi
fi

# Exit early if --validate only
if $VALIDATE_ONLY; then
  info "Profile validation complete: ${PROFILE_FILE}"
  exit 0
fi

# ── read keybindings from profile ───────────────────────────────────────────
SUPER_MOD=$(jq -r '.keybindings.super_mod // "SUPER"' "${PROFILE_FILE}")
BINDINGS_COUNT=$(jq '.keybindings.bindings | length' "${PROFILE_FILE}")

if [[ "${BINDINGS_COUNT}" -eq 0 ]]; then
  warn "No keybindings defined in profile '${PROFILE_NAME}' — generating empty custom.lua"
fi

# ── generate Lua ────────────────────────────────────────────────────────────
# Header plus the Dreamcoder colour loader. Emitted even for an empty
# profile: custom.lua is a file ML4W never ships (its hyprland.lua only
# requires it when present), so ML4W upgrades that rewrite hyprland.lua
# cannot drop this require the way they dropped the old injected line.
emit_header() {
  cat <<LUA_HEADER
-- ============================================================================
-- custom.lua — AUTO-GENERATED by generate-custom-lua.sh
-- Source: ${PROFILE_FILE}
-- Last generated: $(date '+%Y-%m-%d %H:%M:%S')
-- ============================================================================
-- Edit the profile JSON (${PROFILE_NAME}.json) and re-run this script.
-- Manual changes to this file will be overwritten.
-- ============================================================================

-- Dreamcoder colours (dreamcoder-colors.lua, flipped per mode by
-- apply-theme-mode.sh). Guarded so a missing file never breaks the config.
do
  local dc = io.open(os.getenv("HOME") .. "/.config/hypr/dreamcoder-colors.lua", "r")
  if dc then
    dc:close()
    require("dreamcoder-colors")
  end
end

local mainMod = "${SUPER_MOD}"

-- Keybindings (${BINDINGS_COUNT} total)
LUA_HEADER
}

generate() {
  emit_header

  while IFS=$'\t' read -r mods_json key command description locked repeating disable_workspace_consume bind_type mouse button submap_entry; do
    # Build modifier string: SUPER + SHIFT + ... or empty for bare keys
    local mod_string=""
    local mods_count
    mods_count=$(echo "${mods_json}" | jq 'length' 2>/dev/null || echo "0")
    local bind_type="${bind_type:-press}"
    local mouse="${mouse:-false}"
    local button="${button:-}"
    local submap_entry="${submap_entry:-}"

    if [[ "${mods_count}" -gt 0 ]]; then
      # Collect mods (already uppercase from JSON)
      while IFS= read -r mod; do
        mod_string="${mod_string}${mod} + "
      done < <(echo "${mods_json}" | jq -r '.[]')
      mod_string="${mod_string}${key}"
    else
      # Bare key (F1, code:238, etc.) — no SUPER prefix
      mod_string="${key}"
    fi

    # Build Lua options table
    local opts=""
    local opts_parts=()
    if [[ "${locked}" == "true" ]]; then opts_parts+=("locked = true"); fi
    if [[ "${repeating}" == "true" ]]; then opts_parts+=("repeating = true"); fi
    if [[ "${disable_workspace_consume}" == "true" ]]; then opts_parts+=("disable_workspace_consume = true"); fi
    # Release trigger: hl.bindl() does NOT exist in the Hyprland Lua API
    # (errors with "attempt to call a nil value (field 'bindl')").
    # The documented flag is `release = true` on a regular hl.bind().
    if [[ "${bind_type}" == "release" ]]; then opts_parts+=("release = true"); fi
    # Mouse bindings: hl.mouse_bind() does NOT exist in the Hyprland Lua
    # API. The button goes in the key string and `mouse = true` is a
    # flag on a regular hl.bind() (same pattern ML4W uses for mouse:272).
    if [[ "${mouse}" == "true" ]]; then opts_parts+=("mouse = true"); fi

    if [[ ${#opts_parts[@]} -gt 0 ]]; then
      local joined=""
      local first=true
      for part in "${opts_parts[@]}"; do
        if $first; then
          joined="${part}"
          first=false
        else joined="${joined}, ${part}"; fi
      done
      opts="{ ${joined}, description = \"${description}\" }"
    else
      opts="{ description = \"${description}\" }"
    fi

    # Binding function: always hl.bind(); release and mouse are flags.
    # (release = true and mouse = true are flags on hl.bind).
    local bind_fn="hl.bind"
    local mod_display="${mod_string}"
    if [[ "${mouse}" == "true" && -n "${button}" ]]; then
      # Mouse bindings: use button name instead of key in the mod string
      if [[ "${mods_count}" -gt 0 ]]; then
        # Remove trailing " + " and append button
        local mod_prefix="${mod_string% + *}"
        mod_display="${mod_prefix} + ${button}"
      else
        mod_display="${button}"
      fi
    fi

    # Handle submap_entry
    local cmd="${command}"
    if [[ -n "${submap_entry}" && "${command}" != hl.submap* ]]; then
      cmd="hl.submap('${submap_entry}')"
    fi

    # Translate known `hyprctl dispatch <X>` shell commands to native Lua
    # dispatchers. Hyprland >= 0.55 parses `hyprctl dispatch` arguments as
    # Lua (hl.dispatch(...)), so legacy strings like "workspace 2" fail at
    # runtime. Native hl.dsp.* dispatchers avoid the broken subprocess call.
    local dispatcher
    local last_arg="${cmd##* }"
    last_arg="${last_arg#+}" # Lua has no +N literal (workspace +1 from mouse binds)
    case "${cmd}" in
    hyprctl\ dispatch\ workspace\ *)
      dispatcher="hl.dsp.focus({ workspace = ${last_arg} })"
      ;;
    hyprctl\ dispatch\ movetoworkspace\ *)
      dispatcher="hl.dsp.window.move({ workspace = ${last_arg} })"
      ;;
    hyprctl\ dispatch\ killactive)
      dispatcher="hl.dsp.window.close()"
      ;;
    hyprctl\ dispatch\ fullscreen\ *)
      dispatcher='hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" })'
      ;;
    hyprctl\ dispatch\ togglefloating)
      dispatcher='hl.dsp.window.float({ action = "toggle" })'
      ;;
    hyprctl\ dispatch\ togglesplit)
      dispatcher='hl.dsp.layout("togglesplit")'
      ;;
    hyprctl\ dispatch\ movefocus\ *)
      dispatcher="hl.dsp.focus({ direction = \"${last_arg}\" })"
      ;;
    hyprctl\ dispatch\ movewindow\ *)
      dispatcher="hl.dsp.window.move({ direction = \"${last_arg}\" })"
      ;;
    *)
      dispatcher=""
      ;;
    esac
    if [[ -z "${dispatcher}" ]]; then
      dispatcher="hl.dsp.exec_cmd(\"${cmd}\")"
    fi

    cat <<LUA_BINDING

-- ${description}
${bind_fn}(
  "${mod_display}",
  ${dispatcher},
  ${opts}
)
LUA_BINDING
  done

  # Close with a blank line
  echo ""
}

# ── build the file ──────────────────────────────────────────────────────────
build() {
  # Extract bindings from JSON, flatten options onto each record as tab-separated fields
  jq -r '
    .keybindings.bindings[] |
    [
      ((.mods // []) | @json),
      .key,
      .command,
      .description,
      (.options.locked // false),
      (.options.repeating // false),
      (.options.disable_workspace_consume // false),
      (.bind_type // "press"),
      (.mouse // false),
      (.button // ""),
      (.submap_entry // "")
    ] | @tsv
  ' "${PROFILE_FILE}" | generate
}

# ── dry-run or write ────────────────────────────────────────────────────────
if $DRY_RUN; then
  echo "═══ Dry-run: ${PROFILE_FILE} ═══"
  echo ""
  build
  echo ""
  echo "═══ Would write to: ${OUTPUT} ═══"
  exit 0
fi

mkdir -p "$(dirname "${OUTPUT}")"
build >"${OUTPUT}"

# Verify Lua syntax
if command -v luac >/dev/null; then
  if luac -p "${OUTPUT}" 2>/dev/null; then
    info "Generated: ${OUTPUT} (${BINDINGS_COUNT} bindings from ${PROFILE_NAME})"
  else
    warn "Lua syntax check FAILED — check ${OUTPUT} for errors"
    exit 1
  fi
else
  info "Generated: ${OUTPUT} (${BINDINGS_COUNT} bindings from ${PROFILE_NAME}) — luac not available, syntax not verified"
fi
