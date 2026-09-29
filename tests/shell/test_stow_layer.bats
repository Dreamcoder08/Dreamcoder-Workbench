#!/usr/bin/env bats
# ============================================================================
# Tests for the Dreamcoder stow layer (scripts/dreamcoder-lib.sh)
# ============================================================================

setup() {
    REPO_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
    TEST_DIR="$(mktemp -d)"
    export HOME="${TEST_DIR}/home"
    export DREAMCODER_DOTS_DIR="${REPO_DIR}"
    export CONFIG_HOME="${HOME}/.config"
    export DATA_HOME="${HOME}/.local/share"
    CONFLICT_DIR="${TEST_DIR}/conflicts"
    FOREIGN="${TEST_DIR}/mydotfiles/.config"
    mkdir -p "${HOME}/.config" "${FOREIGN}/fish"
    printf '# foreign fish\n' >"${FOREIGN}/fish/config.fish"
    printf 'SETUVAR foo:bar\n' >"${FOREIGN}/fish/fish_variables"
    # shellcheck source=/dev/null
    source "${REPO_DIR}/scripts/dreamcoder-lib.sh"
}

teardown() {
    rm -rf "${TEST_DIR}"
}

resolved() { (cd -P "$1" 2>/dev/null && pwd) || readlink -f "$1"; }

@test "every stow module exists as a package directory" {
    [ "${#DREAMCODER_MODULES[@]}" -gt 0 ]
    for module in "${DREAMCODER_MODULES[@]}"; do
        [ -d "${REPO_DIR}/${module}" ] || { echo "missing module: ${module}"; false; }
    done
}

@test "stow modules match the installer plan" {
    expected="$(PYTHONPATH="${REPO_DIR}/src" python3 -c 'from dreamcoder_theme.installer import installer_plan; print(" ".join(installer_plan()["modules"]))')"
    [ "${expected}" = "${DREAMCODER_MODULES[*]}" ]
}

@test "stow dry run resolves every module into an empty HOME" {
    command -v stow >/dev/null || skip "stow not installed"
    run stow -n -v -d "${REPO_DIR}" -t "${HOME}" "${DREAMCODER_MODULES[@]}"
    [ "$status" -eq 0 ]
    [[ "$output" != *"conflict"* ]]
}

@test "a foreign directory symlink is moved aside as a link and relinked into the repo" {
    command -v stow >/dev/null || skip "stow not installed"
    ln -s "${FOREIGN}/fish" "${HOME}/.config/fish"

    run dreamcoder_stow_modules "${CONFLICT_DIR}"
    [ "$status" -eq 0 ]

    [ -L "${HOME}/.config/fish" ]
    [ "$(resolved "${HOME}/.config/fish")" = "$(resolved "${REPO_DIR}/DreamcoderShell/.config/fish")" ]
    # The foreign link is preserved as a link; its tree is untouched.
    [ -L "${CONFLICT_DIR}/.config/fish" ]
    [ "$(readlink "${CONFLICT_DIR}/.config/fish")" = "${FOREIGN}/fish" ]
    [ "$(cat "${FOREIGN}/fish/fish_variables")" = "SETUVAR foo:bar" ]
}

@test "regular-file conflicts are moved with their contents and never deleted" {
    command -v stow >/dev/null || skip "stow not installed"
    printf 'user zshrc\n' >"${HOME}/.zshrc"

    run dreamcoder_stow_modules "${CONFLICT_DIR}"
    [ "$status" -eq 0 ]

    [ -L "${HOME}/.zshrc" ]
    [ "$(cat "${CONFLICT_DIR}/.zshrc")" = "user zshrc" ]
}

@test "an absolute link into the repo is replaced by stow's own link" {
    command -v stow >/dev/null || skip "stow not installed"
    ln -s "${REPO_DIR}/DreamcoderShell/.config/starship.toml" "${HOME}/.config/starship.toml"

    run dreamcoder_stow_modules "${CONFLICT_DIR}"
    [ "$status" -eq 0 ]

    [ "$(readlink -f "${HOME}/.config/starship.toml")" = "${REPO_DIR}/DreamcoderShell/.config/starship.toml" ]
    [[ "$(readlink "${HOME}/.config/starship.toml")" != /* ]]
    [ -L "${CONFLICT_DIR}/.config/starship.toml" ]
}

@test "restowing an already linked HOME is a no-op" {
    command -v stow >/dev/null || skip "stow not installed"
    ln -s "${FOREIGN}/fish" "${HOME}/.config/fish"
    dreamcoder_stow_modules "${CONFLICT_DIR}" >/dev/null

    run dreamcoder_stow_modules "${TEST_DIR}/second"
    [ "$status" -eq 0 ]
    [ ! -e "${TEST_DIR}/second" ]
}

@test "maintenance relinks before hooks and keeps conflicts outside stowed trees" {
    maintenance="${REPO_DIR}/scripts/dreamcoder-maintenance.sh"
    stow_line="$(grep -n 'dreamcoder_stow_modules' "${maintenance}" | head -1 | cut -d: -f1)"
    hooks_line="$(grep -n '^dreamcoder_apply_hooks' "${maintenance}" | cut -d: -f1)"
    [ -n "${stow_line}" ] && [ -n "${hooks_line}" ]
    [ "${stow_line}" -lt "${hooks_line}" ]
    # shellcheck disable=SC2016 # literal match of the script source
    grep -qF 'CONFLICT_DIR="${DATA_HOME}/dreamcoder/install-conflicts/' "${maintenance}"
}
