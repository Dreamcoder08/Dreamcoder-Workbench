#!/usr/bin/env bash
set -euo pipefail
# used by sourcing scripts (dreamcoder.sh, dreamcoder-maintenance.sh)
# Stow packages owned by install/repair; keep in sync with
# src/dreamcoder_theme/installer.py (installer_plan()["modules"]).
DREAMCODER_MODULES=(DreamcoderShell DreamcoderKitty DreamcoderGhostty DreamcoderFastfetch DreamcoderWarp DreamcoderBat DreamcoderSystemd)
DREAMCODER_TARGETS=("${CONFIG_HOME}/kitty" "${CONFIG_HOME}/ghostty" "${CONFIG_HOME}/fastfetch" "${CONFIG_HOME}/dreamcoder" "${CONFIG_HOME}/fish" "${CONFIG_HOME}/starship.toml" "${CONFIG_HOME}/bat" "${DATA_HOME}/warp-terminal/themes" "${HOME}/.zshrc" "${HOME}/.bashrc" "${HOME}/.inputrc" "${CONFIG_HOME}/systemd/user/dreamcoder-theme-auto.service" "${CONFIG_HOME}/systemd/user/dreamcoder-theme-auto.timer")
dreamcoder_control() { PYTHONPATH="${DREAMCODER_DOTS_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" python3 -m dreamcoder_theme.control "$@"; }
dreamcoder_json_get() { python3 -c 'import json,sys; print(json.load(sys.stdin)[sys.argv[1]])' "$1"; }
dreamcoder_backup() { dreamcoder_control backup create "${DREAMCODER_TARGETS[@]}" --reason "${1}" --json; }
dreamcoder_apply_hooks() { "${DREAMCODER_DOTS_DIR}/scripts/apply-ml4w-hooks.sh"; "${DREAMCODER_DOTS_DIR}/scripts/apply-cli-env-hooks.sh"; "${DREAMCODER_DOTS_DIR}/scripts/apply-fastfetch-assets.sh"; }
dreamcoder_enable_timer() { command -v systemctl >/dev/null || return 0; systemctl --user daemon-reload || true; systemctl --user enable --now dreamcoder-theme-auto.timer || true; }

# Print every target (relative to $HOME) that blocks stowing the modules,
# as reported by a stow dry run: regular files/directories where stow wants a
# link, and symlinks stow does not own (foreign trees such as ML4W's
# ~/.mydotfiles, or absolute links into the repo).
dreamcoder_stow_conflicts() {
  local report
  report="$(stow -n -v -d "${DREAMCODER_DOTS_DIR}" -t "${HOME}" "${DREAMCODER_MODULES[@]}" 2>&1)" || true
  printf '%s\n' "${report}" | sed -n \
    -e 's/^  \* existing target is not owned by stow: //p' \
    -e 's/^  \* cannot stow .* over existing target \(.*\) since neither a link nor a directory.*$/\1/p'
}

# Move one conflicting target into CONFLICT_DIR, keeping its $HOME-relative
# path. Symlinks are moved as links (never followed), so the tree they point
# to is left untouched. Nothing is ever deleted.
dreamcoder_move_conflict() {
  local rel="${1}" conflict_dir="${2}"
  local src="${HOME}/${rel}" dest="${conflict_dir}/${rel}"
  [[ -e "${src}" || -L "${src}" ]] || return 0
  if [[ -e "${dest}" || -L "${dest}" ]]; then
    printf '✗ Refusing to overwrite %s while moving stow conflict %s\n' "${dest}" "${src}" >&2
    return 1
  fi
  mkdir -p "$(dirname "${dest}")"
  if [[ -L "${src}" ]]; then
    printf '→ Moved foreign symlink %s (-> %s) to %s\n' "${src}" "$(readlink "${src}")" "${dest}"
  else
    printf '→ Moved stow conflict %s to %s\n' "${src}" "${dest}"
  fi
  mv "${src}" "${dest}"
}

# Clear stow conflicts into CONFLICT_DIR, then stow every module into $HOME.
# Bounded passes: moving a target never creates a new conflict, but a second
# dry run proves the tree is clean before the real stow runs.
dreamcoder_stow_modules() {
  local conflict_dir="${1}" rel moved _
  for _ in 1 2 3; do
    moved=0
    while IFS= read -r rel; do
      [[ -n "${rel}" ]] || continue
      dreamcoder_move_conflict "${rel}" "${conflict_dir}"
      moved=1
    done < <(dreamcoder_stow_conflicts)
    (( moved )) || break
  done
  stow -d "${DREAMCODER_DOTS_DIR}" -t "${HOME}" "${DREAMCODER_MODULES[@]}"
}
