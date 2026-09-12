#!/usr/bin/env bash
# ── Dreamcoder Dots — Waybar accent override for the active ML4W theme ──────
# ML4W prefers themes${style}/style-custom.css over style.css, so the override
# rides ML4W's own point; a root-level ~/.config/waybar/style.css is never read.
# No `set -euo pipefail`: sourcing must not mutate the caller's shell options.

waybar_style_dir() {
    # Print the style theme directory ML4W's selector currently points at.
    local selector="${HOME}/.config/ml4w/settings/waybar-theme.sh" pair style
    [[ -f "${selector}" ]] || return 1
    read -r pair <"${selector}" || return 1
    style="${pair#*;}"
    [[ -n "${style}" ]] || return 1
    printf '%s\n' "${HOME}/.config/waybar/themes${style}"
}

install_waybar_override() {
    # $1 = repository root. Install the Dreamcoder override into the active
    # style theme directory, where ML4W's launch.sh prefers it. Idempotent.
    local source_file="$1/DreamcoderWaybar/.config/waybar/style-custom.css"
    local style_dir target
    [[ -f "${source_file}" ]] || return 1
    style_dir="$(waybar_style_dir)" || return 1
    [[ -d "${style_dir}" ]] || return 1
    target="${style_dir}/style-custom.css"
    if [[ -f "${target}" ]] && cmp -s "${source_file}" "${target}"; then
        return 0
    fi
    cp "${source_file}" "${target}"
}
