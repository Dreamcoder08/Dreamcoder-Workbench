# ============================================================================
# BATS tests: lib/waybar.sh — Dreamcoder Waybar active-workspace override
# ============================================================================
# Every test builds its own fake ML4W layout under the temporary HOME provided
# by tests/helpers/setup.bash, so the real ~/.config is never touched.

load '../helpers/setup'

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
