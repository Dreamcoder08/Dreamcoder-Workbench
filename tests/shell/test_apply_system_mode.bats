#!/usr/bin/env bats
# ============================================================================
# Tests for scripts/apply-system-mode.sh
# ============================================================================
# The GTK key write must be idempotent. Rewriting an unchanged value still
# updates settings.ini's mtime, which fires ML4W's gtk-theme-switcher inotify
# listener; that listener runs matugen, which overwrites the colour files the
# Dreamcoder sync just committed.
#
# The tests are hermetic: HOME is a temp dir, XDG_CONFIG_HOME is cleared (it is
# exported in some sessions and would otherwise redirect the write into the real
# user config), and gsettings is stubbed so the real GNOME setting is untouched.

setup() {
    TEST_HOME="$(mktemp -d)"
    TEST_BIN="$(mktemp -d)"
    printf '#!/bin/sh\nexit 0\n' >"${TEST_BIN}/gsettings"
    chmod +x "${TEST_BIN}/gsettings"
    DREAMCODER_DOTS_DIR="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
    GTK3="${TEST_HOME}/.config/gtk-3.0/settings.ini"
}

teardown() {
    rm -rf "${TEST_HOME}" "${TEST_BIN}"
}

run_system_mode() {
    env -u XDG_CONFIG_HOME HOME="${TEST_HOME}" PATH="${TEST_BIN}:${PATH}" \
        bash "${DREAMCODER_DOTS_DIR}/scripts/apply-system-mode.sh" "$1" >/dev/null 2>&1
}

@test "apply-system-mode: writes the key on first run" {
    run_system_mode dark
    [ -f "${GTK3}" ]
    grep -q '^gtk-application-prefer-dark-theme=1$' "${GTK3}"
}

@test "apply-system-mode: re-running the same mode does not rewrite the file" {
    run_system_mode dark
    local before
    before="$(stat -c %Y "${GTK3}")"
    sleep 1
    run_system_mode dark
    [ "$(stat -c %Y "${GTK3}")" = "${before}" ]
}

@test "apply-system-mode: a real mode change is written" {
    run_system_mode dark
    local before
    before="$(stat -c %Y "${GTK3}")"
    sleep 1
    run_system_mode light
    grep -q '^gtk-application-prefer-dark-theme=0$' "${GTK3}"
    [ "$(stat -c %Y "${GTK3}")" != "${before}" ]
}

@test "apply-system-mode: unrelated keys are preserved" {
    mkdir -p "$(dirname "${GTK3}")"
    printf '[Settings]\ngtk-theme-name=Adwaita\n' >"${GTK3}"
    run_system_mode dark
    grep -q '^gtk-theme-name=Adwaita$' "${GTK3}"
    grep -q '^gtk-application-prefer-dark-theme=1$' "${GTK3}"
}

@test "apply-system-mode: the real user config is never written" {
    run_system_mode dark
    # The run must land in the temp home, never in the invoking user's config.
    [ -f "${GTK3}" ]
    [ "${GTK3}" != "${HOME}/.config/gtk-3.0/settings.ini" ]
}
