#!/usr/bin/env bats
# Bounded theme-only activation: no desktop commands or real-home writes.

setup() {
    TEST_DIR="${BATS_TEST_TMPDIR}"
    export DREAMCODER_DOTS_DIR="${BATS_TEST_DIRNAME}/../.."
    export HOME="${TEST_DIR}/home"
    export XDG_CACHE_HOME="${TEST_DIR}/cache"
    export XDG_CONFIG_HOME="${TEST_DIR}/config"
    export XDG_DATA_HOME="${TEST_DIR}/data"
    export PI_AGENT_DIR="${HOME}/legacy-agent"
    export PI_CODING_AGENT_DIR="${HOME}/pi-agent"
    export GENTLE_SHELL_HOME="${HOME}/gentle-agent"
    export DREAMCODER_THEME_MODE="dark"
    export DREAMCODER_ADAPTIVE="0"
    export PYTHONDONTWRITEBYTECODE="1"
    unset PI_THEME PI_SETTINGS DREAMCODER_THEME_PROFILE DREAMCODER_TOKENS
    SCRIPT="${DREAMCODER_DOTS_DIR}/DreamcoderPi/.pi/agent/scripts/pi-theme.sh"
    mkdir -p "${PI_CODING_AGENT_DIR}/themes" "${GENTLE_SHELL_HOME}/themes"
    printf 'repository variant must not change\n' > "${TEST_DIR}/variant.json"
    for agent in "${PI_CODING_AGENT_DIR}" "${GENTLE_SHELL_HOME}"; do
        ln -s "${TEST_DIR}/variant.json" "${agent}/themes/dreamcoder.json"
        printf '{"theme":"light","packages":["keep"]}\n' > "${agent}/settings.json"
    done
}

portable_checkout() {
    CHECKOUT="${TEST_DIR}/checkout with spaces"
    mkdir -p "${CHECKOUT}/DreamcoderPi/.pi/agent/scripts" "${CHECKOUT}/src"
    cp "${SCRIPT}" "${CHECKOUT}/DreamcoderPi/.pi/agent/scripts/"
    mkdir -p "${TEST_DIR}/bin"
    printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' \
        'printf "%s\n" "${PYTHONPATH%%:*}" > "${TEST_DIR}/python-root"' \
        > "${TEST_DIR}/bin/python3"
    chmod +x "${TEST_DIR}/bin/python3"
    export TEST_DIR PATH="${TEST_DIR}/bin:${PATH}"
    SCRIPT="${CHECKOUT}/DreamcoderPi/.pi/agent/scripts/pi-theme.sh"
    cd "${HOME}"
}

@test "pi-theme discovers a spaced checkout from an unrelated cwd" {
    portable_checkout
    run env -u DREAMCODER_DOTS_DIR -u DOTS_DIR bash "${SCRIPT}"
    [[ "${status}" -eq 0 ]]
    [[ "$(<"${TEST_DIR}/python-root")" == "${CHECKOUT}/src" ]]
}

@test "pi-theme resolves a relative installed symlink" {
    portable_checkout
    ln -s '../checkout with spaces/DreamcoderPi/.pi/agent/scripts/pi-theme.sh' "${HOME}/installed"
    run env -u DREAMCODER_DOTS_DIR -u DOTS_DIR bash "${HOME}/installed"
    [[ "${status}" -eq 0 ]]
    [[ "$(<"${TEST_DIR}/python-root")" == "${CHECKOUT}/src" ]]
}

@test "pi-theme preserves DREAMCODER_DOTS_DIR then DOTS_DIR precedence" {
    portable_checkout
    for preferred in DREAMCODER_DOTS_DIR DOTS_DIR; do
        if [[ "${preferred}" == DREAMCODER_DOTS_DIR ]]; then
            run env DREAMCODER_DOTS_DIR="${CHECKOUT}" DOTS_DIR="${TEST_DIR}/wrong" bash "${SCRIPT}"
        else
            run env -u DREAMCODER_DOTS_DIR DOTS_DIR="${CHECKOUT}" bash "${SCRIPT}"
        fi
        [[ "${status}" -eq 0 ]]
        [[ "$(<"${TEST_DIR}/python-root")" == "${CHECKOUT}/src" ]]
    done
}

assert_themes() {
    for agent in "${PI_CODING_AGENT_DIR}" "${GENTLE_SHELL_HOME}"; do
        [[ ! -L "${agent}/themes/dreamcoder.json" ]]
        grep -q "${1}" "${agent}/themes/dreamcoder.json"
        grep -q '"theme": "dreamcoder"' "${agent}/settings.json"
        grep -q '"keep"' "${agent}/settings.json"
    done
    [[ "$(<"${TEST_DIR}/variant.json")" == 'repository variant must not change' ]]
    [[ ! -e "${PI_AGENT_DIR}/themes/dreamcoder.json" ]]
}

@test "pi-theme.sh generates canonical dark in both homes" {
    run bash "${SCRIPT}"
    [[ "${status}" -eq 0 ]]
    assert_themes '#A5B4FC'
}

@test "pi-theme.sh generates canonical light in both homes" {
    run env DREAMCODER_THEME_MODE=light bash "${SCRIPT}"
    [[ "${status}" -eq 0 ]]
    assert_themes '#824f16'
}

@test "pi-theme.sh stays canonical without invoking matugen when adaptation is inherited" {
    mkdir -p "${TEST_DIR}/bin"
    export MATUGEN_CALLS="${TEST_DIR}/matugen-calls"
    printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' \
        'printf "%s\n" "$*" >> "${MATUGEN_CALLS}"' 'exit 99' \
        > "${TEST_DIR}/bin/matugen"
    chmod +x "${TEST_DIR}/bin/matugen"
    # Valid one-pixel PNG: preparation must not invoke even the fake Matugen.
    printf '%s' 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1cAAAAASUVORK5CYII=' \
        | base64 --decode > "${TEST_DIR}/wallpaper.png"
    for mode in dark light; do
        run env PATH="${TEST_DIR}/bin:${PATH}" DREAMCODER_ADAPTIVE=1 \
            DREAMCODER_WALLPAPER="${TEST_DIR}/wallpaper.png" \
            DREAMCODER_THEME_MODE="${mode}" bash "${SCRIPT}"
        [[ ! -e "${MATUGEN_CALLS}" ]]
        [[ "${status}" -eq 0 ]]
        if [[ "${mode}" == dark ]]; then
            assert_themes '#A5B4FC'
        else
            assert_themes '#824f16'
        fi
    done
}

@test "pi-theme.sh ignores a stale DREAMCODER_THEME_PROFILE" {
    run env DREAMCODER_THEME_PROFILE=night bash "${SCRIPT}"
    [[ "${status}" -eq 0 ]]
    assert_themes '#A5B4FC'
}

@test "pi-theme.sh fails closed for invalid mode before modifying themes" {
    run env DREAMCODER_THEME_MODE=dusk bash "${SCRIPT}"
    [[ "${status}" -ne 0 ]]
    [[ -L "${PI_CODING_AGENT_DIR}/themes/dreamcoder.json" ]]
    [[ -L "${GENTLE_SHELL_HOME}/themes/dreamcoder.json" ]]
}

@test "pi-theme.sh honors explicit Pi destinations and a linked Gentle Shell home" {
    export PI_THEME="${TEST_DIR}/custom/themes/dreamcoder.json"
    export PI_SETTINGS="${TEST_DIR}/custom/settings.json"
    export GENTLE_SHELL_HOME="${PI_CODING_AGENT_DIR}"
    run bash "${SCRIPT}"
    [[ "${status}" -eq 0 ]]
    [[ -f "${PI_THEME}" && ! -L "${PI_THEME}" ]]
    grep -q '"theme": "dreamcoder"' "${PI_SETTINGS}"
    grep -q '#A5B4FC' "${GENTLE_SHELL_HOME}/themes/dreamcoder.json"
}
