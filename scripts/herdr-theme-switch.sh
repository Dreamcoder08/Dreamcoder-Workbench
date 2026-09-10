#!/usr/bin/env bash
# Select a version-matched generated Herdr theme without replacing regular configs.
set -euo pipefail

MODE="${1:-dark}"
DOTS_DIR="${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"

case "${MODE}" in
dark | light | night) ;;
*)
  printf 'Usage: %s {dark|light|night}\n' "$0" >&2
  exit 2
  ;;
esac

PYTHONPATH="${DOTS_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
  python3 -m dreamcoder_theme.herdr_activation "${MODE}"
