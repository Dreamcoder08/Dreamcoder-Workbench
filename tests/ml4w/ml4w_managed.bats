# ============================================================================
# BATS tests: lib/ml4w.sh — ML4W ownership predicates
# ============================================================================
# Every test builds its own ML4W layout under the temporary HOME provided by
# tests/helpers/setup.bash, so results never depend on the machine running the
# suite or on the ML4W install under test.

load '../helpers/setup'

ml4w_lib_path() { printf '%s' "${DREAMCODER_DOTS_DIR}/lib/ml4w.sh"; }

# bats runs test bodies in the current shell, so sourcing defines the predicates.
load_ml4w_lib() {
  source "$(ml4w_lib_path)"
}

# ── hyprland_is_ml4w_managed ─────────────────────────────────────────────────

@test "ml4w lib: hyprland managed when ~/.config/hypr is a symlink" {
  mkdir -p "${HOME}/.config" "${HOME}/.mydotfiles/hypr"
  ln -s "${HOME}/.mydotfiles/hypr" "${HOME}/.config/hypr"

  load_ml4w_lib
  run hyprland_is_ml4w_managed
  [ "$status" -eq 0 ]
}

@test "ml4w lib: hyprland managed when only hyprland.conf is a symlink" {
  mkdir -p "${HOME}/.config/hypr" "${HOME}/.mydotfiles"
  printf 'config\n' >"${HOME}/.mydotfiles/hyprland.conf"
  ln -s "${HOME}/.mydotfiles/hyprland.conf" "${HOME}/.config/hypr/hyprland.conf"

  load_ml4w_lib
  run hyprland_is_ml4w_managed
  [ "$status" -eq 0 ]
}

@test "ml4w lib: hyprland managed when conf/keybinding.lua exists" {
  mkdir -p "${HOME}/.config/hypr/conf"
  printf '%s\n' '-- bindings' >"${HOME}/.config/hypr/conf/keybinding.lua"

  load_ml4w_lib
  run hyprland_is_ml4w_managed
  [ "$status" -eq 0 ]
}

@test "ml4w lib: hyprland not managed when no marker exists" {
  load_ml4w_lib
  run hyprland_is_ml4w_managed
  [ "$status" -ne 0 ]
}

@test "ml4w lib: hyprland not managed when hyprland.conf is a regular file" {
  mkdir -p "${HOME}/.config/hypr"
  printf 'config\n' >"${HOME}/.config/hypr/hyprland.conf"

  load_ml4w_lib
  run hyprland_is_ml4w_managed
  [ "$status" -ne 0 ]
}

# ── waybar_is_ml4w_managed ───────────────────────────────────────────────────

@test "ml4w lib: waybar managed when ~/.config/waybar is a symlink" {
  mkdir -p "${HOME}/.config" "${HOME}/.mydotfiles/waybar"
  ln -s "${HOME}/.mydotfiles/waybar" "${HOME}/.config/waybar"

  load_ml4w_lib
  run waybar_is_ml4w_managed
  [ "$status" -eq 0 ]
}

@test "ml4w lib: waybar managed when only config.jsonc is a symlink" {
  mkdir -p "${HOME}/.config/waybar" "${HOME}/.mydotfiles"
  printf '{}\n' >"${HOME}/.mydotfiles/config.jsonc"
  ln -s "${HOME}/.mydotfiles/config.jsonc" "${HOME}/.config/waybar/config.jsonc"

  load_ml4w_lib
  run waybar_is_ml4w_managed
  [ "$status" -eq 0 ]
}

@test "ml4w lib: waybar managed when launch.sh exists" {
  mkdir -p "${HOME}/.config/waybar"
  printf '#!/usr/bin/env bash\n' >"${HOME}/.config/waybar/launch.sh"

  load_ml4w_lib
  run waybar_is_ml4w_managed
  [ "$status" -eq 0 ]
}

@test "ml4w lib: waybar not managed when no marker exists" {
  load_ml4w_lib
  run waybar_is_ml4w_managed
  [ "$status" -ne 0 ]
}

@test "ml4w lib: waybar not managed when config.jsonc is a regular file" {
  mkdir -p "${HOME}/.config/waybar"
  printf '{}\n' >"${HOME}/.config/waybar/config.jsonc"

  load_ml4w_lib
  run waybar_is_ml4w_managed
  [ "$status" -ne 0 ]
}

# ── purity ───────────────────────────────────────────────────────────────────

@test "ml4w lib: sourcing never enables errexit in the caller shell" {
  # The library is read in a fresh shell with a controlled HOME so the assertion
  # is about the library, not about the bats test runner.
  run env HOME="${TEST_TEMP_HOME}" bash -c '
    set -u
    source "$1"
    printf "flags:%s\n" "$-"
    false
    printf "survived\n"
  ' _ "$(ml4w_lib_path)"

  [ "$status" -eq 0 ]
  [[ "$output" == *"survived"* ]]
  [[ "${lines[0]}" == "flags:"* ]]
  [[ "${lines[0]#flags:}" != *e* ]]
}
