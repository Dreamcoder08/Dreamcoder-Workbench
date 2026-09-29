#!/usr/bin/env bash
# ── Dreamcoder Dots — Hyprland / ML4W Utilities ─────────────────────
set -euo pipefail

reload_hyprland() {
    if optional_command hyprctl; then
        hyprctl reload >/dev/null 2>&1 || true
    fi
}

restart_waybar() {
    if is_gui_session && optional_command pkill; then
        pkill waybar 2>/dev/null || true
        sleep 0.3
        local launch_script="${HOME}/.config/waybar/launch.sh"
        # Detach every stream: the relaunched bar outlives us, and an inherited
        # stdout pipe would block any caller capturing our output (theme apply).
        [[ -f "${launch_script}" ]] && "${launch_script}" </dev/null >/dev/null 2>&1 || true
    fi
}

signal_kitty() {
    if is_gui_session && optional_command pkill; then
        pkill -SIGUSR1 kitty 2>/dev/null || true
    fi
}
