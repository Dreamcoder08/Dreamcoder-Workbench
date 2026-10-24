# ============================================================================
# BATS tests: lib/waybar.sh — Dreamcoder Waybar active-workspace override
# ============================================================================
# Every test builds its own fake ML4W layout under Bats' temporary HOME,
# so the real ~/.config is never touched.

# Bats owns fixture cleanup; do not load shell configs or shared HOME helpers.
setup() {
  export DREAMCODER_DOTS_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
  export TEST_TEMP_HOME="${BATS_TEST_TMPDIR}/home"
  export HOME="${TEST_TEMP_HOME}"
  mkdir -p "${HOME}"
}

waybar_lib_path() { printf '%s' "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"; }

# bats runs test bodies in the current shell, so sourcing defines the functions.
load_waybar_lib() {
  source "$(waybar_lib_path)"
}

# ML4W stores the theme pair as a single line "/<cfg>;/<style>".
write_selector() {
  local cfg="$1" style="$2"
  mkdir -p "${HOME}/.config/ml4w/settings"
  printf '/%s;%s\n' "${cfg}" "${style}" >"${HOME}/.config/ml4w/settings/waybar-theme.sh"
}

# Create the style theme directory and point the selector at it.
make_ml4w_layout() {
  local cfg="$1" style="$2"
  mkdir -p "${HOME}/.config/waybar/themes${style}"
  write_selector "${cfg}" "${style}"
}

# Independent oracle for the exact bytes install_waybar_override must write.
expected_override() {
  cat <<'CSS'
/* Dreamcoder Waybar override for the active ML4W theme.
 *
 * Installed as themes<cfg>/<style>/style-custom.css by lib/waybar.sh. ML4W's
 * launch.sh prefers that file over the theme's own style.css, which makes it the
 * only integration point that survives ML4W updates; a root-level
 * ~/.config/waybar/style.css is never read.
 *
 * Why this file exists: ML4W's theme CSS never styles the active workspace
 * button, so the Dreamcoder accent never reached the live chain. `@primary` is
 * the live colour-bridge value that the theme engine maps Dreamcoder's `accent`
 * onto (see _map_dc_to_material), so the rule is added without redefining any
 * colour and without replacing ML4W's layout.
 *
 * The @import pulls the theme's own style.css because this file replaces it in
 * the chain. The generated DreamcoderThemes/dreamcoder/waybar-{mode}.css layer is
 * deliberately NOT imported: it redefines `error` and `surface` with values that
 * differ from the live bridge.
 */
@import url("style.css");

#workspaces button.active {
    color: @primary;
}
CSS
}

# ── waybar_style_dir ─────────────────────────────────────────────────────────

@test "waybar lib: style dir resolves the style half of the selector" {
  make_ml4w_layout "ml4w-glass-center" "/ml4w-glass-center/default"

  load_waybar_lib
  run waybar_style_dir
  [ "$status" -eq 0 ]
  [ "${output}" = "${HOME}/.config/waybar/themes/ml4w-glass-center/default" ]
}

@test "waybar lib: style dir fails when the selector file is missing" {
  load_waybar_lib
  run waybar_style_dir
  [ "$status" -ne 0 ]
}

@test "waybar lib: style dir fails when the selector has no style component" {
  # Nothing after the ";" separator: the style half is empty.
  write_selector "ml4w-glass-center" ""

  load_waybar_lib
  run waybar_style_dir
  [ "$status" -ne 0 ]
}

# ── install_waybar_override ──────────────────────────────────────────────────

@test "waybar lib: install writes the accent override into the style dir" {
  make_ml4w_layout "ml4w-glass-center" "/ml4w-glass-center/default"

  load_waybar_lib
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -eq 0 ]

  local target="${HOME}/.config/waybar/themes/ml4w-glass-center/default/style-custom.css"
  [ -f "${target}" ]
  [ "$(cat "${target}")" = "$(expected_override)" ]

  run grep -F '@import url("style.css");' "${target}"
  [ "$status" -eq 0 ]
  run grep -F 'color: @primary;' "${target}"
  [ "$status" -eq 0 ]
}

@test "waybar lib: install leaves an identical style-custom.css untouched" {
  make_ml4w_layout "ml4w-glass-center" "/ml4w-glass-center/default"

  load_waybar_lib
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -eq 0 ]

  local target="${HOME}/.config/waybar/themes/ml4w-glass-center/default/style-custom.css"
  local before after
  before="$(stat -c '%Y' "${target}")"

  sleep 1
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -eq 0 ]
  after="$(stat -c '%Y' "${target}")"

  [ "${before}" = "${after}" ]
  [ "$(cat "${target}")" = "$(expected_override)" ]
}

@test "waybar lib: install fails without writing when the selector is missing" {
  load_waybar_lib
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -ne 0 ]
  [ -z "$(find "${HOME}" -name 'style-custom.css' -print -quit)" ]
}

@test "waybar lib: install fails without writing when the style dir is missing" {
  write_selector "ml4w-glass-center" "/ml4w-glass-center/missing"

  load_waybar_lib
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -ne 0 ]
  [ -z "$(find "${HOME}" -name 'style-custom.css' -print -quit)" ]
}

@test "waybar lib: switching the selector writes into the new theme dir only" {
  make_ml4w_layout "ml4w-glass-center" "/ml4w-glass-center/default"

  load_waybar_lib
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -eq 0 ]

  local first="${HOME}/.config/waybar/themes/ml4w-glass-center/default/style-custom.css"
  local before
  before="$(stat -c '%Y' "${first}")"

  sleep 1
  make_ml4w_layout "ml4w-custom" "/ml4w-custom/default"
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -eq 0 ]

  local second="${HOME}/.config/waybar/themes/ml4w-custom/default/style-custom.css"
  [ -f "${second}" ]
  [ "$(cat "${second}")" = "$(expected_override)" ]
  [ "$(stat -c '%Y' "${first}")" = "${before}" ]
  [ "$(cat "${first}")" = "$(expected_override)" ]
}

@test "waybar lib: refuses a personal override symlink without changing its referent" {
  make_ml4w_layout "ml4w-glass-center" "/ml4w-glass-center/default"
  local personal="${HOME}/personal.css"
  local target="${HOME}/.config/waybar/themes/ml4w-glass-center/default/style-custom.css"
  printf '/* personal override */\n' >"${personal}"
  ln -s "${personal}" "${target}"

  load_waybar_lib
  run install_waybar_override "${DREAMCODER_DOTS_DIR}"
  [ "$status" -ne 0 ]
  [ "$(readlink "${target}")" = "${personal}" ]
  [ "$(cat "${personal}")" = '/* personal override */' ]
}

# Execute the actual adapter, but copy only its narrow inputs to a fixture repo.
# All executable desktop/sync entry points are stubs; no installed shell is read.
make_mode_fixture() {
  export FIXTURE_DOTS="${HOME}/dots" EVENTS="${HOME}/events"
  mkdir -p "${FIXTURE_DOTS}"/{lib,scripts,bin,DreamcoderWaybar/.config/waybar}
  cp "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" "${FIXTURE_DOTS}/scripts/"
  cp "$(waybar_lib_path)" "${FIXTURE_DOTS}/lib/"
  cp "${DREAMCODER_DOTS_DIR}/DreamcoderWaybar/.config/waybar/style-custom.css" \
    "${FIXTURE_DOTS}/DreamcoderWaybar/.config/waybar/"
  printf 'ensure_dots_dir() { :; }\n' >"${FIXTURE_DOTS}/lib/env.sh"
  printf '# fixture only\n' >"${FIXTURE_DOTS}/lib/logging.sh"
  printf 'optional_command() { return 1; }\nis_gui_session() { return 1; }\n' \
    >"${FIXTURE_DOTS}/lib/checks.sh"
  cat >"${FIXTURE_DOTS}/lib/hyprland.sh" <<'SH'
signal_kitty() { :; }
restart_waybar() {
  local selected
  selected="$(waybar_style_dir)" || return 1
  [[ "$(readlink "${HOME}/.config/waybar/colors.css")" == "colors-${MODE}.css" ]] || return 1
  cmp "${HOME}/bridge-${MODE}.css" "${HOME}/.config/waybar/colors.css" || return 1
  if [[ "${EXPECT_OVERRIDE}" == 1 ]]; then
    cmp "${DREAMCODER_DOTS_DIR}/DreamcoderWaybar/.config/waybar/style-custom.css" \
      "${selected}/style-custom.css" || return 1
  fi
  printf 'restart %s\n' "${MODE}" >>"${EVENTS}"
}
SH
  cat >"${FIXTURE_DOTS}/scripts/apply-system-mode.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
printf 'system %s\n' "$1" >>"${EVENTS}"
SH
  cat >"${FIXTURE_DOTS}/bin/python3" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
[[ "$*" == "-m dreamcoder_theme.control theme apply ${DREAMCODER_THEME_MODE} --json" ]]
[[ "${HOME}" == "${FIXTURE_HOME}" && "${DREAMCODER_DOTS_DIR}" == "${HOME}/dots" ]]
[[ "${XDG_CONFIG_HOME}" == "${HOME}/.config" && "${XDG_CACHE_HOME}" == "${HOME}/.cache" ]]
[[ "${XDG_DATA_HOME}" == "${HOME}/.local/share" && "${XDG_STATE_HOME}" == "${HOME}/.local/state" ]]
[[ "${XDG_RUNTIME_DIR}" == "${HOME}/run" && -z "${BASH_ENV:-}${ENV:-}" ]]
printf 'sync %s\n' "${DREAMCODER_THEME_MODE}" >>"${EVENTS}"
[[ "${FAIL_SYNC}" == 0 ]] || exit 23
# Model the transaction's bridge selection/write, not Python rendering itself.
ln -sf "colors-${DREAMCODER_THEME_MODE}.css" "${HOME}/.config/waybar/colors.css"
cp "${HOME}/bridge-${DREAMCODER_THEME_MODE}.css" "${HOME}/.config/waybar/colors.css"
SH
  printf '#!/usr/bin/env bash\nexit 0\n' >"${FIXTURE_DOTS}/bin/tmux"
  chmod +x "${FIXTURE_DOTS}/scripts/apply-system-mode.sh" "${FIXTURE_DOTS}/bin/"*
  local mode
  for mode in dark light; do
    printf '@define-color primary %s;\n' "$([[ "${mode}" == dark ]] && printf '#A5B4FC' || printf '#824f16')" \
      >"${HOME}/bridge-${mode}.css"
    printf 'unwritten %s\n' "${mode}" >"${HOME}/.config/waybar/colors-${mode}.css"
  done
  ln -s colors-light.css "${HOME}/.config/waybar/colors.css"
}

run_mode_fixture() {
  # Validate isolation before executing the real mode script, not just afterward.
  [[ "${HOME}" == "${BATS_TEST_TMPDIR}/home" ]]
  [[ "${FIXTURE_DOTS}" == "${HOME}/dots" ]]
  run env -i PATH="${FIXTURE_DOTS}/bin:/usr/bin:/bin" HOME="${HOME}" \
    FIXTURE_HOME="${HOME}" DREAMCODER_DOTS_DIR="${FIXTURE_DOTS}" EVENTS="${EVENTS}" \
    XDG_CONFIG_HOME="${HOME}/.config" XDG_CACHE_HOME="${HOME}/.cache" \
    XDG_DATA_HOME="${HOME}/.local/share" XDG_STATE_HOME="${HOME}/.local/state" \
    XDG_RUNTIME_DIR="${HOME}/run" EXPECT_OVERRIDE="${2:-1}" FAIL_SYNC="${3:-0}" \
    bash --noprofile --norc "${FIXTURE_DOTS}/scripts/apply-theme-mode.sh" "$1"
}

assert_mode_chain() {
  local mode="$1" other="$2" style="${HOME}/.config/waybar/themes/ml4w-glass-center/default"
  make_ml4w_layout ml4w-glass-center /ml4w-glass-center/default
  make_mode_fixture
  printf '@import url("../../../colors.css");\n@import url("glass.css");\n' >"${style}/style.css"
  printf '/* glass layout */\n' >"${style}/glass.css"
  cp "${style}/style.css" "${HOME}/original-style.css"
  printf '/* root personal override */\n' >"${HOME}/.config/waybar/style-custom.css"
  printf '/* selected personal file */\n' >"${HOME}/personal.css"
  ln -s "${HOME}/personal.css" "${style}/personal.css"
  run_mode_fixture "${mode}"
  [ "$status" -eq 0 ]
  [ "$(cat "${EVENTS}")" = "$(printf 'sync %s\nsystem %s\nrestart %s' "${mode}" "${mode}" "${mode}")" ]
  cmp "${HOME}/bridge-${mode}.css" "${HOME}/.config/waybar/colors.css"
  [ "$(cat "${style}/style-custom.css")" = "$(expected_override)" ]
  [ "$(cat "${HOME}/.config/waybar/colors-${other}.css")" = "unwritten ${other}" ]
  # Re-select a different layout and apply the opposite mode in the same HOME.
  make_ml4w_layout ml4w-custom /ml4w-custom/default
  run_mode_fixture "${other}"
  [ "$status" -eq 0 ]
  [ "$(cat "${EVENTS}")" = "$(printf 'sync %s\nsystem %s\nrestart %s\nsync %s\nsystem %s\nrestart %s' "${mode}" "${mode}" "${mode}" "${other}" "${other}" "${other}")" ]
  cmp "${HOME}/bridge-${mode}.css" "${HOME}/.config/waybar/colors-${mode}.css"
  cmp "${HOME}/bridge-${other}.css" "${HOME}/.config/waybar/colors.css"
  [ "$(cat "${HOME}/.config/waybar/themes/ml4w-custom/default/style-custom.css")" = "$(expected_override)" ]
  [ "$(cat "${style}/style-custom.css")" = "$(expected_override)" ]
  cmp "${HOME}/original-style.css" "${style}/style.css"
  [ "$(cat "${style}/glass.css")" = '/* glass layout */' ]
  [ "$(cat "${HOME}/.config/waybar/style-custom.css")" = '/* root personal override */' ]
  [ "$(readlink "${style}/personal.css")" = "${HOME}/personal.css" ]
  [ "$(cat "${HOME}/personal.css")" = '/* selected personal file */' ]
}

@test "mode chain: Dark bridge and override precede restart, then Light selector change" {
  assert_mode_chain dark light
}

@test "mode chain: Light bridge and override precede restart, then Dark selector change" {
  assert_mode_chain light dark
}

@test "mode chain: failed preparation never installs or restarts" {
  make_ml4w_layout ml4w-glass-center /ml4w-glass-center/default
  make_mode_fixture
  run_mode_fixture dark 1 1
  [ "$status" -eq 23 ]
  [ "$(cat "${EVENTS}")" = 'sync dark' ]
  [ "$(readlink "${HOME}/.config/waybar/colors.css")" = colors-light.css ]
  [ ! -e "${HOME}/.config/waybar/themes/ml4w-glass-center/default/style-custom.css" ]
  [[ "${output}" != *'mode applied'* ]]
}

@test "mode chain: rejected dangling personal override remains nonfatal and untouched" {
  make_ml4w_layout ml4w-glass-center /ml4w-glass-center/default
  make_mode_fixture
  local target="${HOME}/.config/waybar/themes/ml4w-glass-center/default/style-custom.css"
  ln -s "${HOME}/absent-personal.css" "${target}"
  run_mode_fixture dark 0
  [ "$status" -eq 0 ]
  [ "$(cat "${EVENTS}")" = "$(printf 'sync dark\nsystem dark\nrestart dark')" ]
  [ "$(readlink "${target}")" = "${HOME}/absent-personal.css" ]
  [ ! -e "${HOME}/absent-personal.css" ]
}

# ── purity ───────────────────────────────────────────────────────────────────

@test "waybar lib: sourcing never enables errexit in the caller shell" {
  # The library is read in a fresh shell with a controlled HOME so the assertion
  # is about the library, not about the bats test runner.
  run env HOME="${TEST_TEMP_HOME}" bash -c '
    set -u
    source "$1"
    printf "flags:%s\n" "$-"
    false
    printf "survived\n"
  ' _ "$(waybar_lib_path)"

  [ "$status" -eq 0 ]
  [[ "$output" == *"survived"* ]]
  [[ "${lines[0]}" == "flags:"* ]]
  [[ "${lines[0]#flags:}" != *e* ]]
}
