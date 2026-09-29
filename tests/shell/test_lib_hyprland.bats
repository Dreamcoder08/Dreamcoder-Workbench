#!/usr/bin/env bats
# ============================================================================
# Tests for lib/hyprland.sh
# ============================================================================

setup() {
    TEST_HOME="$(mktemp -d)"
    mkdir -p "${TEST_HOME}/.config/waybar" "${TEST_HOME}/bin"
    # Fake launcher that leaves a long-lived background child, like waybar.
    cat >"${TEST_HOME}/.config/waybar/launch.sh" <<'SH'
#!/usr/bin/env bash
sleep 30 &
echo $! >"${HOME}/bar.pid"
echo launched
SH
    chmod +x "${TEST_HOME}/.config/waybar/launch.sh"
    printf '#!/bin/sh\nexit 0\n' >"${TEST_HOME}/bin/pkill"
    chmod +x "${TEST_HOME}/bin/pkill"
}

teardown() {
    [[ -f "${TEST_HOME}/bar.pid" ]] && kill "$(cat "${TEST_HOME}/bar.pid")" 2>/dev/null || true
    rm -rf "${TEST_HOME}"
}

@test "restart_waybar never hands its stdout to the relaunched bar" {
    # A caller capturing output (theme apply under Python/systemd) must not
    # block until the bar exits because the bar inherited the capture pipe.
    run timeout 10 bash -c '
        export HOME="'"${TEST_HOME}"'" PATH="'"${TEST_HOME}"'/bin:${PATH}"
        source lib/checks.sh; source lib/hyprland.sh
        is_gui_session() { return 0; }
        out="$(restart_waybar)"; echo "done:${out}"'
    [ "$status" -eq 0 ]
    [ "$output" = "done:" ]
}
