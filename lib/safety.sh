#!/usr/bin/env bash
# ── Dreamcoder Dots — Safety Utilities ───────────────────────────────
set -euo pipefail

safe_source() {
    local file="$1"
    # safe_source takes an arbitrary caller-supplied path, so there is no
    # static target to follow; the directive records that intent.
    # shellcheck source=/dev/null
    [[ -f "${file}" ]] && source "${file}" || true
}

on_error() {
    log_error "Script failed at line ${1} (exit code: ${2})"
    exit "${2}"
}

enable_error_trapping() { trap 'on_error ${LINENO} $?' ERR; }
