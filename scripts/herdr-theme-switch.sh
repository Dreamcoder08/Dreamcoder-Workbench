#!/usr/bin/env bash
# Select the installed Herdr version's generated variant and reload the server.
set -euo pipefail

MODE="${1:-dark}"
DOTS_DIR="${DREAMCODER_DOTS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"

PYTHONPATH="${DOTS_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
  python3 -m dreamcoder_theme.herdr_switch "${MODE}"
