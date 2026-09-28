#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${DREAMCODER_DOTS_ENV:-${0%/*}/dreamcoder-env.sh}"
# shellcheck source=/dev/null
[[ -f "${ENV_FILE}" ]] && source "${ENV_FILE}"
# Ensure DREAMCODER_DOTS_DIR is set
: "${DREAMCODER_DOTS_DIR:=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LIGHT_START="${DREAMCODER_LIGHT_START:-7}"
DARK_START="${DREAMCODER_DARK_START:-18}"
HOUR="$(date +%H)"
MODE="dark"
if (( 10#${HOUR} >= LIGHT_START && 10#${HOUR} < DARK_START )); then MODE="light"; fi
# Light/Dark schedule; the bounded adapter routes through the control
# activation path.
exec "${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh" "${MODE}" "${DREAMCODER_WALLPAPER:-}"
