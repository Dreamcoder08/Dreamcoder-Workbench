#!/usr/bin/env bats
# ============================================================================
# Tests for scripts/apply-theme-mode.sh
# ============================================================================

setup() {
    TEST_DIR="${BATS_TEST_TMPDIR}"
    export HOME="${TEST_DIR}/home" XDG_CACHE_HOME="${TEST_DIR}/cache"
    export XDG_CONFIG_HOME="${TEST_DIR}/config" XDG_DATA_HOME="${TEST_DIR}/data"
    export DREAMCODER_DOTS_DIR="${TEST_DIR}/checkout with spaces"
    export DREAMCODER_SYNC_DONE=1 CALLS="${TEST_DIR}/calls"
    unset DOTS_DIR DREAMCODER_WALLPAPER ML4W_CACHE_DIR
    mkdir -p "${HOME}" "${DREAMCODER_DOTS_DIR}/scripts" "${TEST_DIR}/bin"
    cp "${BATS_TEST_DIRNAME}/../../scripts/apply-theme-mode.sh" "${DREAMCODER_DOTS_DIR}/scripts/"
    printf '%s\n' '#!/usr/bin/env bash' 'printf "system\\n" >> "${CALLS}"' \
        > "${DREAMCODER_DOTS_DIR}/scripts/apply-system-mode.sh"
    chmod +x "${DREAMCODER_DOTS_DIR}/scripts/apply-system-mode.sh"
    printf '%s\n' '#!/usr/bin/env bash' 'exit 0' > "${TEST_DIR}/bin/tmux"
    chmod +x "${TEST_DIR}/bin/tmux"
    export PATH="${TEST_DIR}/bin:${PATH}"
    fixture_libs "${DREAMCODER_DOTS_DIR}"
}

fixture_libs() {
    local root="${1}" missing="${2:-}"
    mkdir -p "${root}/lib"
    for lib in logging env checks hyprland; do
        [[ "${lib}" != "${missing}" ]] || continue
        printf 'printf "sourced %s\\n" >> "${CALLS}"\n' "${lib}" > "${root}/lib/${lib}.sh"
    done
    [[ "${missing}" == env ]] || printf 'ensure_dots_dir() { :; }\nis_gui_session() { return 1; }\n' >> "${root}/lib/env.sh"
    [[ "${missing}" == checks ]] || printf 'optional_command() { return 1; }\n' >> "${root}/lib/checks.sh"
    [[ "${missing}" == hyprland ]] || printf 'signal_kitty() { :; }\n' >> "${root}/lib/hyprland.sh"
}

real_waybar_fixture() {
    cp "${BATS_TEST_DIRNAME}/../../lib/waybar.sh" "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"
    mkdir -p "${DREAMCODER_DOTS_DIR}/DreamcoderWaybar/.config/waybar"
    if [[ "${1:-}" != source-absent ]]; then
        printf '/* fixture override */\n' > "${DREAMCODER_DOTS_DIR}/DreamcoderWaybar/.config/waybar/style-custom.css"
    fi
}

applicable_waybar_fixture() {
    real_waybar_fixture "${1:-}"
    mkdir -p "${HOME}/.config/ml4w/settings" "${HOME}/.config/waybar/themes/test"
    printf 'config;/test\n' > "${HOME}/.config/ml4w/settings/waybar-theme.sh"
}

@test "apply-theme with the real Waybar library skips an absent ML4W selector" {
    real_waybar_fixture
    run bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" light
    [[ "${status}" -eq 0 ]]
    [[ "${output}" == *"✓ Dreamcoder light mode applied"* ]]
    grep -q '^system$' "${CALLS}"
}

@test "apply-theme with the real Waybar library skips empty or invalid themes and nonexistent style dirs" {
    real_waybar_fixture
    for selection in '' 'config;' 'invalid' 'config;/missing'; do
        export HOME="${TEST_DIR}/home-${selection//\//_}"
        mkdir -p "${HOME}/.config/ml4w/settings"
        printf '%s\n' "${selection}" > "${HOME}/.config/ml4w/settings/waybar-theme.sh"
        run bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" light
        [[ "${status}" -eq 0 ]]
        [[ "${output}" == *"✓ Dreamcoder light mode applied"* ]]
    done
}

@test "apply-theme with the real Waybar library skips absent source CSS" {
    applicable_waybar_fixture source-absent
    run bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" light
    [[ "${status}" -eq 0 ]]
    [[ ! -e "${HOME}/.config/waybar/themes/test/style-custom.css" ]]
}

@test "apply-theme propagates a real Waybar copy failure when applicable" {
    applicable_waybar_fixture
    ln -s "${TEST_DIR}/nonexistent/target.css" "${HOME}/.config/waybar/themes/test/style-custom.css"
    run env LC_ALL=C bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" light
    [[ "${status}" -eq 1 ]]
    [[ "${output}" == *"cp:"* ]]
    [[ "${output}" != *"✓ Dreamcoder light mode applied"* ]]
}

@test "apply-theme propagates restart failure after a real Waybar install" {
    applicable_waybar_fixture
    printf 'restart_waybar() { printf "restart failed\\n" >&2; return 29; }\n' >> "${DREAMCODER_DOTS_DIR}/lib/hyprland.sh"
    run bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" light
    [[ "${status}" -eq 29 ]]
    [[ "${output}" == *"restart failed"* ]]
    [[ "${output}" != *"✓ Dreamcoder light mode applied"* ]]
    cmp "${DREAMCODER_DOTS_DIR}/DreamcoderWaybar/.config/waybar/style-custom.css" "${HOME}/.config/waybar/themes/test/style-custom.css"
}

@test "apply-theme discovers a spaced checkout from an unrelated cwd without Waybar" {
    cd "${HOME}"
    run env -u DREAMCODER_DOTS_DIR -u DOTS_DIR bash "${TEST_DIR}/checkout with spaces/scripts/apply-theme-mode.sh" dark
    [[ "${status}" -eq 0 ]]
    grep -q '^system$' "${CALLS}"
}

@test "apply-theme resolves an installed symlink and DOTS_DIR override" {
    ln -s '../checkout with spaces/scripts/apply-theme-mode.sh' "${HOME}/installed"
    cd "${HOME}"
    run env -u DREAMCODER_DOTS_DIR -u DOTS_DIR bash "${HOME}/installed" light
    [[ "${status}" -eq 0 ]]
    run env -u DREAMCODER_DOTS_DIR DOTS_DIR="${TEST_DIR}/checkout with spaces" bash "${HOME}/installed" dark
    [[ "${status}" -eq 0 ]]
}

@test "apply-theme explicit DREAMCODER_DOTS_DIR wins over DOTS_DIR" {
    run env DOTS_DIR="${TEST_DIR}/wrong" bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" light
    [[ "${status}" -eq 0 ]]
}

@test "apply-theme rejects every missing required library before sourcing or side effects" {
    for missing in logging env checks hyprland; do
        root="${TEST_DIR}/missing-${missing}"
        fixture_libs "${root}" "${missing}"
        run env DREAMCODER_DOTS_DIR="${root}" bash "${TEST_DIR}/checkout with spaces/scripts/apply-theme-mode.sh" dark
        [[ "${status}" -ne 0 ]]
        [[ "${output}" == *"Required library not found: ${root}/lib/${missing}.sh"* ]]
        [[ ! -e "${CALLS}" && ! -e "${XDG_CACHE_HOME}/dreamcoder/cursor-cli.env" ]]
    done
}

@test "apply-theme guards optional Waybar functions individually" {
    applicable_waybar_fixture
    for helper in install_waybar_override restart_waybar; do
        printf '%s() { printf "waybar %s\\n" >> "${CALLS}"; }\n' "${helper}" "${helper}" \
            > "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"
        printf 'waybar_style_dir() { printf "%%s\\n" "${HOME}/.config/waybar/themes/test"; }\n' >> "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"
        run bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" dark
        [[ "${status}" -eq 0 ]]
        grep -q "waybar ${helper}" "${CALLS}"
    done
}

@test "apply-theme does not mask a present Waybar helper failure" {
    applicable_waybar_fixture
    for helper in install_waybar_override restart_waybar; do
        printf '%s() { return 23; }\n' "${helper}" > "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"
        printf 'waybar_style_dir() { printf "%%s\\n" "${HOME}/.config/waybar/themes/test"; }\n' >> "${DREAMCODER_DOTS_DIR}/lib/waybar.sh"
        run bash "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" dark
        [[ "${status}" -eq 23 ]]
    done
}

@test "apply-theme-mode.sh has valid syntax" {
    run bash -n scripts/apply-theme-mode.sh
    [ "$status" -eq 0 ]
}

@test "apply-theme-mode.sh with invalid mode exits non-zero" {
    run bash scripts/apply-theme-mode.sh invalid 2>&1
    [ "$status" -eq 1 ]
}

@test "apply-theme-mode.sh rejects night as a mode" {
    run bash scripts/apply-theme-mode.sh night 2>&1
    [ "$status" -eq 1 ]
    [[ "$output" == *"Invalid mode: night"* ]]
}

@test "apply-theme-mode.sh selects mode artifacts with no render profile" {
    # Every selector resolves the *-dark / *-light artifacts straight from
    # MODE; the retired Night profile and its artifacts are gone.
    script="scripts/apply-theme-mode.sh"
    grep -q 'ln -sf "colors-${MODE}.css"' "$script"
    grep -q 'ln -sf "colors-${MODE}.rasi"' "$script"
    grep -q 'ln -sf "colors-${MODE}.lua"' "$script"
    grep -q 'ln -sf "hypr-colors-${MODE}.lua"' "$script"
    grep -q '"${_link%.conf}-${MODE}.conf"' "$script"
    grep -q 'Dreamcoder-${MODE^}.yaml' "$script"
    grep -q 'ln -sf "dreamcoder-${MODE}.theme"' "$script"
    grep -qF 'theme \"dreamcoder-${MODE}\"' "$script"
    grep -q 'delta-dreamcoder-${MODE}.gitconfig' "$script"
    grep -q 'config.${MODE}.yml' "$script"
    ! grep -qi 'night' "$script"
    ! grep -q 'PROFILE=' "$script"
}

@test "apply-theme-mode.sh flips the live lazygit config to the current variant" {
    # The live ~/.config/lazygit/config.yml must be pointed at the repo's
    # generated config.<variant>.yml (same absolute-into-repo pattern as the
    # existing delta selector), never at the static mode-tracking config.yml.
    script="scripts/apply-theme-mode.sh"
    grep -q 'LAZYGIT_LINK="${HOME}/.config/lazygit/config.yml"' "$script"
    grep -q 'LAZYGIT_VARIANT="${DOTS_DIR}/DreamcoderLazygit/.config/lazygit/config.${MODE}.yml"' "$script"
    grep -qF 'ln -sf "${LAZYGIT_VARIANT}" "${LAZYGIT_LINK}"' "$script"
}

@test "apply-theme-mode.sh re-selects the Dreamcoder btop theme after ML4W resets it" {
    # ML4W upgrades rewrite btop.conf with color_theme = "matugen"; every apply
    # must point it back at the Dreamcoder theme without rewriting it needlessly.
    script="scripts/apply-theme-mode.sh"
    grep -q 'BTOP_CONF="${HOME}/.config/btop/btop.conf"' "$script"
    grep -qF "grep -q '^color_theme = \"dreamcoder\"\$' \"\${BTOP_CONF}\"" "$script"
    grep -qF "sed -i 's/^color_theme = .*/color_theme = \"dreamcoder\"/' \"\${BTOP_CONF}\"" "$script"
}
