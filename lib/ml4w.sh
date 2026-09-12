#!/usr/bin/env bash
# ============================================================================
# ml4w.sh — ML4W ownership predicates (pure; no side effects)
# ============================================================================
# This library deliberately omits `set -euo pipefail` (and <30 lines total):
# sourcing a library must not mutate the caller's shell options. Both callers
# set their own options before sourcing this file.
#
# ML4W ownership is accepted from either supported layout:
#   - old layout: individual config files symlinked from the ML4W dotfiles
#   - current layout: ~/.config/<app> is a real directory (or a symlink) backed
#     by the ML4W dotfiles repo and carrying ML4W-specific marker files
# ============================================================================

hyprland_is_ml4w_managed() {
    [[ -L "${HOME}/.config/hypr/hyprland.conf" ]] && return 0
    [[ -L "${HOME}/.config/hypr" ]] && return 0
    [[ -f "${HOME}/.config/hypr/conf/keybinding.lua" ]] && return 0
    return 1
}

waybar_is_ml4w_managed() {
    [[ -L "${HOME}/.config/waybar/config.jsonc" ]] && return 0
    [[ -L "${HOME}/.config/waybar" ]] && return 0
    [[ -f "${HOME}/.config/waybar/launch.sh" ]] && return 0
    return 1
}
