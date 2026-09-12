#!/usr/bin/env bats
# ============================================================================
# Tests for scripts/apply-ml4w-hooks.sh
# ============================================================================
# The waypaper injection goes through `sed`. In a sed replacement, `&` expands to
# the whole match, and the injected hook text contains `2>&1`, so an unescaped
# `&` re-inserts the matched line and corrupts the config with a nested copy.

setup() {
    TEST_DIR="$(mktemp -d)"
    DREAMCODER_DOTS_DIR="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
    mkdir -p "${TEST_DIR}/lib" "${TEST_DIR}/scripts"
    cp "${DREAMCODER_DOTS_DIR}"/lib/*.sh "${TEST_DIR}/lib/"
    printf '#!/usr/bin/env bash\nexit 0\n' >"${TEST_DIR}/scripts/theme-auto.sh"
    printf '#!/usr/bin/env bash\nexit 0\n' >"${TEST_DIR}/scripts/wallpaper-hook.sh"
    chmod +x "${TEST_DIR}/scripts/"*.sh
    WAYPAPER_CONFIG="${TEST_DIR}/config.ini"
    ML4W_WALLPAPER_SCRIPT="${TEST_DIR}/wallpaper.sh"
    printf '[Settings]\npost_command = ~/.config/ml4w/scripts/ml4w-wallpaper "$wallpaper" --skip > /dev/null 2>&1\n' >"${WAYPAPER_CONFIG}"
    printf '#!/usr/bin/env bash\n' >"${ML4W_WALLPAPER_SCRIPT}"
}

teardown() {
    rm -rf "${TEST_DIR}"
}

run_hooks() {
    WAYPAPER_CONFIG="${WAYPAPER_CONFIG}" \
        ML4W_WALLPAPER_SCRIPT="${ML4W_WALLPAPER_SCRIPT}" \
        DREAMCODER_DOTS_DIR="${TEST_DIR}" \
        bash "${DREAMCODER_DOTS_DIR}/scripts/apply-ml4w-hooks.sh"
}

count_in_post_command() {
    grep '^post_command' "${WAYPAPER_CONFIG}" | grep -o "$1" | wc -l | tr -d ' '
}

@test "apply-ml4w-hooks: the injected post_command stays a single well-formed line" {
    run run_hooks
    [ "$status" -eq 0 ]
    [ "$(count_in_post_command 'post_command =')" -eq 1 ]
    [ "$(count_in_post_command 'wallpaper-hook.sh')" -eq 1 ]
    grep -q 'wallpaper-hook.sh.*2>&1$' "${WAYPAPER_CONFIG}"
}

@test "apply-ml4w-hooks: running twice does not inject a second hook" {
    run_hooks
    run_hooks
    [ "$(count_in_post_command 'wallpaper-hook.sh')" -eq 1 ]
    [ "$(count_in_post_command 'post_command =')" -eq 1 ]
}

@test "apply-ml4w-hooks: the ML4W wallpaper block is appended exactly once" {
    run_hooks
    run_hooks
    [ "$(grep -c 'Dreamcoder final wallpaper/theme sync' "${ML4W_WALLPAPER_SCRIPT}")" -eq 1 ]
}

@test "apply-ml4w-hooks: the config is not left with an unescaped match copy" {
    run_hooks
    # The corrupt form repeats the original assignment inside the line.
    [ "$(count_in_post_command 'ml4w-wallpaper')" -eq 1 ]
}
