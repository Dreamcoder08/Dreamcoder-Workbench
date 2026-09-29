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
