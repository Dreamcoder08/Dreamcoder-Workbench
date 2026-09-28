#!/usr/bin/env bats
# ============================================================================
# Tests for scripts/apply-theme-mode.sh
# ============================================================================

setup() {
    TEST_DIR="$(mktemp -d)"
    export DREAMCODER_DOTS_DIR="${TEST_DIR}"
    mkdir -p "${TEST_DIR}/lib" "${TEST_DIR}/scripts" "${TEST_DIR}/DreamcoderThemes/dreamcoder"
    cp lib/*.sh "${TEST_DIR}/lib/"
    cp scripts/apply-theme-mode.sh "${TEST_DIR}/scripts/"
    echo '{"active_mode":"light","modes":{"light":{"bg":"#fff"},"dark":{"bg":"#000"}}}' > "${TEST_DIR}/DreamcoderThemes/dreamcoder/tokens.json"
}

teardown() {
    rm -rf "${TEST_DIR}"
}

@test "apply-theme-mode.sh has valid syntax" {
    run bash -n scripts/apply-theme-mode.sh
    [ "$status" -eq 0 ]
}

@test "apply-theme-mode.sh with invalid mode exits non-zero" {
    run bash scripts/apply-theme-mode.sh invalid 2>&1
    [ "$status" -eq 1 ]
}

@test "apply-theme-mode.sh with invalid profile exits non-zero" {
    run bash scripts/apply-theme-mode.sh dark "" dusk 2>&1
    [ "$status" -eq 1 ]
    [[ "$output" == *"Invalid render profile"* ]]
}

@test "apply-theme-mode.sh night profile: missing artifact blocks with zero mutation" {
    export HOME="${TEST_DIR}/home"
    mkdir -p "${HOME}/.config/waybar"
    ln -sf colors-dark.css "${HOME}/.config/waybar/colors.css"

    run bash scripts/apply-theme-mode.sh dark "" night 2>&1
    [ "$status" -eq 1 ]
    [[ "$output" == *"Night preparation failed"* ]]
    # Zero mutation pre-preparation: symlink untouched, cursor-cli env absent.
    [ "$(readlink "${HOME}/.config/waybar/colors.css")" = "colors-dark.css" ]
    [ ! -e "${HOME}/.cache/dreamcoder/cursor-cli.env" ]
}

@test "apply-theme-mode.sh selects night artifacts when profile=night" {
    # Manual trace: the selector code paths must resolve the *-night
    # artifacts through VARIANT while DREAMCODER_THEME_MODE stays dark.
    script="scripts/apply-theme-mode.sh"
    grep -q 'VARIANT="${MODE}"' "$script"
    grep -q '\[\[ "${PROFILE}" == "night" \]\] && VARIANT="night"' "$script"
    grep -q 'ln -sf "colors-${VARIANT}.css"' "$script"
    grep -q 'ln -sf "colors-${VARIANT}.rasi"' "$script"
    grep -q 'ln -sf "colors-${VARIANT}.lua"' "$script"
    grep -q 'ln -sf "hypr-colors-${VARIANT}.lua"' "$script"
    grep -q '"${_link%.conf}-${VARIANT}.conf"' "$script"
    grep -q 'Dreamcoder-${VARIANT^}.yaml' "$script"
    grep -q 'ln -sf "dreamcoder-${VARIANT}.theme"' "$script"
        grep -qF 'theme \"dreamcoder-${VARIANT}\"' "$script"
    grep -q 'delta-dreamcoder-${VARIANT}.gitconfig' "$script"
    grep -q 'config.${VARIANT}.yml' "$script"
    grep -q 'LAZYGIT_LINK=' "$script"
    grep -q 'DreamcoderLazygit/.config/lazygit/config.night.yml' "$script"
    grep -q 'DREAMCODER_THEME_PROFILE="${PROFILE}"' "$script"
    grep -q 'REQUIRED_NIGHT_ARTIFACTS' "$script"
}

@test "apply-theme-mode.sh kanagawa bridge carries night-derived colors" {
    grep -q '@ukiyo-color-text "#beccd8"' scripts/apply-theme-mode.sh
    grep -q '@ukiyo-color-bg-pane "#07090f"' scripts/apply-theme-mode.sh
}

@test "apply-theme-mode.sh flips the live lazygit config to the current variant" {
    # The live ~/.config/lazygit/config.yml must be pointed at the repo's
    # generated config.<variant>.yml (same absolute-into-repo pattern as the
    # existing delta selector), never at the static mode-tracking config.yml.
    script="scripts/apply-theme-mode.sh"
    grep -q 'LAZYGIT_LINK="${HOME}/.config/lazygit/config.yml"' "$script"
    grep -q 'LAZYGIT_VARIANT="${DOTS_DIR}/DreamcoderLazygit/.config/lazygit/config.${VARIANT}.yml"' "$script"
    grep -qF 'ln -sf "${LAZYGIT_VARIANT}" "${LAZYGIT_LINK}"' "$script"
}

@test "apply-theme-mode.sh night gate requires the generated lazygit night artifact" {
    script="scripts/apply-theme-mode.sh"
    grep -q 'DreamcoderLazygit/.config/lazygit/config.night.yml' "$script"
    run bash -n "$script"
    [ "$status" -eq 0 ]
}

@test "apply-theme-mode.sh re-selects the Dreamcoder btop theme after ML4W resets it" {
    # ML4W upgrades rewrite btop.conf with color_theme = "matugen"; every apply
    # must point it back at the Dreamcoder theme without rewriting it needlessly.
    script="scripts/apply-theme-mode.sh"
    grep -q 'BTOP_CONF="${HOME}/.config/btop/btop.conf"' "$script"
    grep -qF "grep -q '^color_theme = \"dreamcoder\"\$' \"\${BTOP_CONF}\"" "$script"
    grep -qF "sed -i 's/^color_theme = .*/color_theme = \"dreamcoder\"/' \"\${BTOP_CONF}\"" "$script"
}
