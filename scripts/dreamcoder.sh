#!/usr/bin/env bash
set -euo pipefail

source "${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}/lib/logging.sh"
source "${DREAMCODER_DOTS_DIR}/lib/env.sh"

ensure_dots_dir
APPLY_SCRIPT="${DREAMCODER_DOTS_DIR}/scripts/apply-theme-mode.sh"
DOCTOR_SCRIPT="${DREAMCODER_DOTS_DIR}/scripts/doctor.sh"

case "${1:-}" in
dark | light)
  export DREAMCODER_THEME_MODE="${1}"
  if [[ -f "${APPLY_SCRIPT}" ]]; then
    bash "${APPLY_SCRIPT}" "${1}"
  else
    echo "Error: ${APPLY_SCRIPT} not found" >&2
    exit 1
  fi
  ;;
status)
  echo "=== Dreamcoder Workbench Status ==="
  echo "Theme mode: ${DREAMCODER_THEME_MODE:-dark}"
  echo "Dotfiles dir: "
  echo "Git branch: $(cd "${DREAMCODER_DOTS_DIR}" && git branch --show-current 2>/dev/null || echo 'N/A')"
  echo "Last commit: $(cd "${DREAMCODER_DOTS_DIR}" && git log -1 --oneline 2>/dev/null || echo 'N/A')"
  echo ""
  if command -v systemctl &>/dev/null; then
    echo "Timer: $(systemctl --user is-active dreamcoder-theme-auto.timer 2>/dev/null || echo 'inactive')"
  fi
  if [[ -f "${HOME}/.cache/dreamcoder/ai-session.state" ]]; then
    echo "AI session: $(cat "${HOME}/.cache/dreamcoder/ai-session.state")"
  else
    echo "AI session: inactive"
  fi
  ;;
doctor)
  if [[ -f "${DOCTOR_SCRIPT}" ]]; then
    shift
    bash "${DOCTOR_SCRIPT}" "$@"
  else
    echo "Error: ${DOCTOR_SCRIPT} not found" >&2
    exit 1
  fi
  ;;
help | --help | -h)
  echo "Usage: dreamcoder <command>"
  echo ""
  echo "Commands:"
  echo "  dark          Switch to Dreamcoder Dark"
  echo "  light         Switch to Dreamcoder Light"
  echo "  status        Show system status overview"
  echo "  doctor        Run health checks on all components"
  echo "  doctor --ml4w Run ML4W integration health checks"
  echo "  help          Show this help"
  exit 0
  ;;
*)
  echo "Usage: dreamcoder {dark|light|status|doctor|help}" >&2
  exit 1
  ;;
esac
