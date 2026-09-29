#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-}"; shift || true
ENV_FILE="${DREAMCODER_DOTS_ENV:-${0%/*}/dreamcoder-env.sh}"
# shellcheck source=/dev/null
[[ -f "${ENV_FILE}" ]] && source "${ENV_FILE}"
LIB_FILE="${DREAMCODER_DOTS_DIR}/scripts/dreamcoder-lib.sh"
# shellcheck source=/dev/null
[[ -f "${LIB_FILE}" ]] && source "${LIB_FILE}"
fail() { printf '✗ %s\n' "${*}" >&2; exit 1; }
command -v python3 >/dev/null || fail 'Missing dependency: python3'
[[ "${MODE}" == install ]] && command -v stow >/dev/null || [[ "${MODE}" == repair ]] || fail 'Usage: dreamcoder-maintenance.sh {install|repair}'
BACKUP_JSON="$(dreamcoder_backup "${MODE}-preflight")"; BACKUP_ID="$(printf '%s' "${BACKUP_JSON}" | dreamcoder_json_get backup_id)"
printf '→ Backup manifest: %s\n  rollback: ./scripts/dreamcoder backup restore %s --json\n' "${BACKUP_ID}" "${BACKUP_ID}"
# Outside every stowed tree: ~/.config/dreamcoder is itself a stow target.
CONFLICT_DIR="${DATA_HOME}/dreamcoder/install-conflicts/${BACKUP_ID}"
cd "${DREAMCODER_DOTS_DIR}"
# Stow before the hooks so they write through Dreamcoder links, not through a
# target an upstream (e.g. an ML4W upgrade) re-pointed to its own tree.
if command -v stow >/dev/null; then
  dreamcoder_stow_modules "${CONFLICT_DIR}"
  [[ -d "${CONFLICT_DIR}" ]] && printf '→ Stow conflicts preserved in %s\n' "${CONFLICT_DIR}"
else
  printf '! stow not found: skipping relink (%s)\n' "${MODE}" >&2
fi
dreamcoder_apply_hooks
dreamcoder_enable_timer
"${DREAMCODER_DOTS_DIR}/scripts/theme-auto.sh"
[[ "${MODE}" == repair ]] && "${DREAMCODER_DOTS_DIR}/scripts/verify.sh"
printf '✓ Dreamcoder %s complete\n' "${MODE}"
