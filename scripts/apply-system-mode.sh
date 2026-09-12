#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-light}"
GTK3="${XDG_CONFIG_HOME:-${HOME}/.config}/gtk-3.0/settings.ini"
GTK4="${XDG_CONFIG_HOME:-${HOME}/.config}/gtk-4.0/settings.ini"
if [[ "${MODE}" == "dark" ]]; then
    GTK3_VALUE="1"; GTK4_VALUE="true"; SCHEME="prefer-dark"
else
    GTK3_VALUE="0"; GTK4_VALUE="false"; SCHEME="prefer-light"
fi

set_gtk_key() {
    local file="${1}" key="${2}" value="${3}"
    mkdir -p "$(dirname "${file}")"
    [[ -f "${file}" ]] || printf '[Settings]\n' >"${file}"
    # Rewriting an unchanged value still bumps the mtime, which fires ML4W's
    # settings.ini watcher and re-runs matugen over Dreamcoder's colours.
    grep -q "^${key}=${value}$" "${file}" && return 0
    if grep -q "^${key}=" "${file}"; then
        sed -i "s/^${key}=.*/${key}=${value}/" "${file}"
    else
        printf '%s=%s\n' "${key}" "${value}" >>"${file}"
    fi
}

set_gtk_key "${GTK3}" "gtk-application-prefer-dark-theme" "${GTK3_VALUE}"
set_gtk_key "${GTK4}" "gtk-application-prefer-dark-theme" "${GTK4_VALUE}"
command -v gsettings >/dev/null && gsettings set org.gnome.desktop.interface color-scheme "${SCHEME}" || true
