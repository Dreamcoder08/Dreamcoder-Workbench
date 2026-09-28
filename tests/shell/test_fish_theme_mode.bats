#!/usr/bin/env bats
# ============================================================================
# 05-dreamcoder-theme.fish must start in the persisted live mode, even when the
# parent process exported a stale DREAMCODER_THEME_MODE.
# ============================================================================

setup() {
    TEST_HOME="$(mktemp -d)"
    mkdir -p "${TEST_HOME}/.cache/dreamcoder"
    CONF="${PWD}/DreamcoderShell/.config/fish/conf.d/05-dreamcoder-theme.fish"
}

teardown() {
    rm -rf "${TEST_HOME}"
}

mode_after_startup() {
    HOME="${TEST_HOME}" DREAMCODER_DOTS_DIR="${PWD}" fish --no-config -c "source '${CONF}'; echo \$DREAMCODER_THEME_MODE"
}

@test "persisted light mode overrides a stale inherited dark mode" {
    printf 'export DREAMCODER_THEME_MODE="light"\n' >"${TEST_HOME}/.cache/dreamcoder/cursor-cli.env"
    DREAMCODER_THEME_MODE=dark run mode_after_startup
    [ "$output" = "light" ]
}

@test "inherited mode is kept when nothing was persisted" {
    DREAMCODER_THEME_MODE=light run mode_after_startup
    [ "$output" = "light" ]
}

@test "defaults to dark without env or persisted mode" {
    run env -u DREAMCODER_THEME_MODE bash -c "$(declare -f mode_after_startup); TEST_HOME='${TEST_HOME}' CONF='${CONF}' mode_after_startup"
    [ "$output" = "dark" ]
}
