#!/usr/bin/env bats
# ============================================================================
# Tests for scripts/apply-ml4w-hooks.sh
# ============================================================================
# Primary target is ML4W's wallpaper runner. The fixture is ML4W tag 2.16's
# dotfiles/.config/ml4w/scripts/ml4w-wallpaper (upstream 3960570, trailing
# whitespace trimmed). ML4W upgrades overwrite that file, so the hook must be
# re-appliable: replaced on every run, never duplicated.
#
# The optional waypaper injection goes through `sed`. In a sed replacement, `&`
# expands to the whole match, and the injected hook text contains `2>&1`, so an
# unescaped `&` re-inserts the matched line and corrupts the config.
#
# The GTK theme listener fixture is a read-only copy of ML4W 2.16's installed
# ~/.config/ml4w/listeners/gtk-theme-switcher.sh. It runs Matugen over the
# wallpaper on every gtk settings.ini change; the hook restores Dreamcoder
# colours right after each Matugen call.

RUNNER_FIXTURE="${BATS_TEST_DIRNAME}/../fixtures/ml4w/ml4w-wallpaper-2.16"
LISTENER_FIXTURE="${BATS_TEST_DIRNAME}/../fixtures/ml4w/gtk-theme-switcher-2.16"
MATUGEN_FIXTURE="${BATS_TEST_DIRNAME}/../fixtures/ml4w/matugen-config-2.16.toml"

setup() {
    TEST_DIR="$(mktemp -d)"
    DREAMCODER_DOTS_DIR="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
    mkdir -p "${TEST_DIR}/lib" "${TEST_DIR}/scripts"
    cp "${DREAMCODER_DOTS_DIR}"/lib/*.sh "${TEST_DIR}/lib/"
    printf '#!/usr/bin/env bash\nexit 0\n' >"${TEST_DIR}/scripts/theme-auto.sh"
    printf '#!/usr/bin/env bash\nexit 0\n' >"${TEST_DIR}/scripts/wallpaper-hook.sh"
    chmod +x "${TEST_DIR}/scripts/"*.sh
    # Exported: every invocation of the script under test, including ones that do not go
    # through run_hooks, must be unable to reach the real ~/.config files.
    export WAYPAPER_CONFIG="${TEST_DIR}/config.ini"
    export ML4W_WALLPAPER_SCRIPT="${TEST_DIR}/ml4w-wallpaper"
    printf '[Settings]\npost_command = ~/.config/ml4w/scripts/ml4w-wallpaper "$wallpaper" --skip > /dev/null 2>&1\n' >"${WAYPAPER_CONFIG}"
    cp "${RUNNER_FIXTURE}" "${ML4W_WALLPAPER_SCRIPT}"
    chmod +x "${ML4W_WALLPAPER_SCRIPT}"
    # Exported so no invocation can reach the live ML4W listener or restart it.
    export ML4W_GTK_LISTENER="${TEST_DIR}/gtk-theme-switcher.sh"
    export ML4W_LISTENERS_SCRIPT="${TEST_DIR}/listeners.sh"
    cp "${LISTENER_FIXTURE}" "${ML4W_GTK_LISTENER}"
    chmod +x "${ML4W_GTK_LISTENER}"
    printf '#!/usr/bin/env bash\necho "$*" >>"%s/restarts"\n' "${TEST_DIR}" >"${ML4W_LISTENERS_SCRIPT}"
    chmod +x "${ML4W_LISTENERS_SCRIPT}"
    # This suite runs with the real HOME: without an override the hooks would edit the
    # live ~/.config/matugen/config.toml.
    export MATUGEN_CONFIG="${TEST_DIR}/matugen.toml"
    cp "${MATUGEN_FIXTURE}" "${MATUGEN_CONFIG}"
}

teardown() {
    rm -rf "${TEST_DIR}"
}

run_hooks() {
    WAYPAPER_CONFIG="${WAYPAPER_CONFIG}" \
        ML4W_WALLPAPER_SCRIPT="${ML4W_WALLPAPER_SCRIPT}" \
        DREAMCODER_DOTS_DIR="${TEST_DIR}" \
        bash "${DREAMCODER_DOTS_DIR}/scripts/apply-ml4w-hooks.sh"
}

count_in_post_command() {
    grep '^post_command' "${WAYPAPER_CONFIG}" | grep -o "$1" | wc -l | tr -d ' '
}

count_blocks() {
    grep -c '^# >>> Dreamcoder wallpaper hook >>>$' "${ML4W_WALLPAPER_SCRIPT}" || true
}

count_listener_blocks() {
    grep -c '^[[:space:]]*# >>> Dreamcoder listener hook >>>$' "${ML4W_GTK_LISTENER}" || true
}

count_restarts() {
    if [[ -f "${TEST_DIR}/restarts" ]]; then wc -l <"${TEST_DIR}/restarts" | tr -d ' '; else echo 0; fi
}

# ── ML4W runner (primary) ────────────────────────────────────────────────────

@test "apply-ml4w-hooks: the 2.16 runner gets exactly one marked block" {
    run run_hooks
    [ "$status" -eq 0 ]
    [ "$(count_blocks)" -eq 1 ]
    grep -q 'wallpaper-hook.sh "\$IMAGE_PATH"' "${ML4W_WALLPAPER_SCRIPT}"
}

@test "apply-ml4w-hooks: the hook runs after the runner's own work" {
    run_hooks
    local done_line hook_line
    done_line="$(grep -n '^info "Done"$' "${ML4W_WALLPAPER_SCRIPT}" | cut -d: -f1)"
    hook_line="$(grep -n 'Dreamcoder wallpaper hook >>>' "${ML4W_WALLPAPER_SCRIPT}" | cut -d: -f1)"
    [ "${hook_line}" -gt "${done_line}" ]
}

@test "apply-ml4w-hooks: the hooked runner is still valid bash and executable" {
    run_hooks
    bash -n "${ML4W_WALLPAPER_SCRIPT}"
    [ -x "${ML4W_WALLPAPER_SCRIPT}" ]
}

@test "apply-ml4w-hooks: re-running leaves the runner byte-identical" {
    run_hooks
    cp "${ML4W_WALLPAPER_SCRIPT}" "${TEST_DIR}/first"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"already current"* ]]
    cmp -s "${TEST_DIR}/first" "${ML4W_WALLPAPER_SCRIPT}"
}

@test "apply-ml4w-hooks: an ML4W upgrade that restores the runner is re-hooked" {
    run_hooks
    cp "${RUNNER_FIXTURE}" "${ML4W_WALLPAPER_SCRIPT}"
    [ "$(count_blocks)" -eq 0 ]
    run_hooks
    [ "$(count_blocks)" -eq 1 ]
}

@test "apply-ml4w-hooks: a stale block is replaced, not duplicated" {
    run_hooks
    sed -i 's|wallpaper-hook.sh|old-path/wallpaper-hook.sh|' "${ML4W_WALLPAPER_SCRIPT}"
    run_hooks
    [ "$(count_blocks)" -eq 1 ]
    run grep -q 'old-path' "${ML4W_WALLPAPER_SCRIPT}"
    [ "$status" -ne 0 ]
}

@test "apply-ml4w-hooks: the unmarked block of older releases is migrated" {
    cat >>"${ML4W_WALLPAPER_SCRIPT}" <<LEGACY

# Dreamcoder final wallpaper/theme sync
if [[ -x "${TEST_DIR}/scripts/wallpaper-hook.sh" ]]; then
    "${TEST_DIR}/scripts/wallpaper-hook.sh" "\$IMAGE_PATH"
fi
LEGACY
    run_hooks
    [ "$(count_blocks)" -eq 1 ]
    run grep -q 'Dreamcoder final wallpaper/theme sync' "${ML4W_WALLPAPER_SCRIPT}"
    [ "$status" -ne 0 ]
    [ "$(grep -c 'wallpaper-hook.sh "\$IMAGE_PATH"' "${ML4W_WALLPAPER_SCRIPT}")" -eq 1 ]
}

@test "apply-ml4w-hooks: a symlinked runner stays a symlink" {
    mv "${ML4W_WALLPAPER_SCRIPT}" "${TEST_DIR}/runner-target"
    ln -s "${TEST_DIR}/runner-target" "${ML4W_WALLPAPER_SCRIPT}"
    run_hooks
    [ -L "${ML4W_WALLPAPER_SCRIPT}" ]
    [ "$(count_blocks)" -eq 1 ]
}

@test "apply-ml4w-hooks: a missing runner is skipped without failing" {
    rm -f "${ML4W_WALLPAPER_SCRIPT}"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"runner not found"* ]]
}

@test "apply-ml4w-hooks: the older layout's variable is reachable by override" {
    WAYPAPER_CONFIG="${WAYPAPER_CONFIG}" \
        ML4W_WALLPAPER_SCRIPT="${ML4W_WALLPAPER_SCRIPT}" \
        ML4W_WALLPAPER_VAR="used_wallpaper" \
        DREAMCODER_DOTS_DIR="${TEST_DIR}" \
        bash "${DREAMCODER_DOTS_DIR}/scripts/apply-ml4w-hooks.sh"
    grep -q 'wallpaper-hook.sh "\$used_wallpaper"' "${ML4W_WALLPAPER_SCRIPT}"
}

@test "apply-ml4w-hooks: the default target is the current ML4W runner" {
    grep -q 'ml4w/scripts/ml4w-wallpaper' "${DREAMCODER_DOTS_DIR}/scripts/apply-ml4w-hooks.sh"
}

# ── waypaper (optional) ──────────────────────────────────────────────────────

@test "apply-ml4w-hooks: without a waypaper config the run still succeeds" {
    rm -f "${WAYPAPER_CONFIG}"
    run run_hooks
    [ "$status" -eq 0 ]
    [ ! -e "${WAYPAPER_CONFIG}" ]
    [[ "$output" == *"waypaper config absent"* ]]
    [ "$(count_blocks)" -eq 1 ]
}

@test "apply-ml4w-hooks: the injected post_command stays a single well-formed line" {
    run run_hooks
    [ "$status" -eq 0 ]
    [ "$(count_in_post_command 'post_command =')" -eq 1 ]
    [ "$(count_in_post_command 'wallpaper-hook.sh')" -eq 1 ]
    grep -q 'wallpaper-hook.sh.*2>&1$' "${WAYPAPER_CONFIG}"
}

@test "apply-ml4w-hooks: running twice does not inject a second waypaper hook" {
    run_hooks
    run_hooks
    [ "$(count_in_post_command 'wallpaper-hook.sh')" -eq 1 ]
    [ "$(count_in_post_command 'post_command =')" -eq 1 ]
}

@test "apply-ml4w-hooks: the config is not left with an unescaped match copy" {
    run_hooks
    # The corrupt form repeats the original assignment inside the line.
    [ "$(count_in_post_command 'ml4w-wallpaper')" -eq 1 ]
}

# ── GTK theme listener (Matugen over Dreamcoder colours) ─────────────────────

@test "apply-ml4w-hooks: a hook block follows each Matugen call in the listener" {
    run run_hooks
    [ "$status" -eq 0 ]
    [ "$(count_listener_blocks)" -eq 2 ]
    local matugen_lines block_lines
    matugen_lines="$(grep -n 'MATUGEN_BIN image' "${ML4W_GTK_LISTENER}" | cut -d: -f1 | tr '\n' ' ')"
    block_lines="$(grep -n 'Dreamcoder listener hook >>>' "${ML4W_GTK_LISTENER}" | cut -d: -f1 | tr '\n' ' ')"
    read -r m1 m2 <<<"${matugen_lines}"
    read -r b1 b2 <<<"${block_lines}"
    [ "${b1}" -eq $((m1 + 1)) ]
    [ "${b2}" -eq $((m2 + 1)) ]
    bash -n "${ML4W_GTK_LISTENER}"
    [ -x "${ML4W_GTK_LISTENER}" ]
}

@test "apply-ml4w-hooks: the listener is restarted once when its hook changes" {
    run_hooks
    [ "$(count_restarts)" -eq 1 ]
    grep -qx -- '--restart gtk-theme-switcher' "${TEST_DIR}/restarts"
}

@test "apply-ml4w-hooks: re-running leaves the listener byte-identical and running" {
    run_hooks
    cp "${ML4W_GTK_LISTENER}" "${TEST_DIR}/first-listener"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"listener hook already current"* ]]
    cmp -s "${TEST_DIR}/first-listener" "${ML4W_GTK_LISTENER}"
    [ "$(count_listener_blocks)" -eq 2 ]
    [ "$(count_restarts)" -eq 1 ]
}

@test "apply-ml4w-hooks: a stale listener block is replaced, not duplicated" {
    run_hooks
    sed -i 's|timeout 120|timeout 5|' "${ML4W_GTK_LISTENER}"
    run_hooks
    [ "$(count_listener_blocks)" -eq 2 ]
    run grep -q 'timeout 5 ' "${ML4W_GTK_LISTENER}"
    [ "$status" -ne 0 ]
}

@test "apply-ml4w-hooks: a listener without a Matugen call is left untouched" {
    grep -v 'MATUGEN_BIN image' "${LISTENER_FIXTURE}" >"${ML4W_GTK_LISTENER}"
    cp "${ML4W_GTK_LISTENER}" "${TEST_DIR}/no-matugen"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"no Matugen call found"* ]]
    cmp -s "${TEST_DIR}/no-matugen" "${ML4W_GTK_LISTENER}"
    [ "$(count_restarts)" -eq 0 ]
}

@test "apply-ml4w-hooks: a missing listener is skipped without failing" {
    rm -f "${ML4W_GTK_LISTENER}"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"GTK theme listener not found"* ]]
    [ ! -e "${ML4W_GTK_LISTENER}" ]
    [ "$(count_blocks)" -eq 1 ]
}

@test "apply-ml4w-hooks: a symlinked listener stays a symlink" {
    mv "${ML4W_GTK_LISTENER}" "${TEST_DIR}/listener-target"
    ln -s "${TEST_DIR}/listener-target" "${ML4W_GTK_LISTENER}"
    run_hooks
    [ -L "${ML4W_GTK_LISTENER}" ]
    [ "$(count_listener_blocks)" -eq 2 ]
}

@test "apply-ml4w-hooks: the listener block runs a colours-only dispatcher sync" {
    run_hooks
    # Stub dispatcher records its arguments and the environment it gets.
    cat >"${TEST_DIR}/scripts/dreamcoder" <<STUB
#!/usr/bin/env bash
printf '%s|%s|%s\n' "\$*" "\${DREAMCODER_THEME_MODE}" "\${DREAMCODER_WRITE_REPO}" >>"${TEST_DIR}/dispatched"
STUB
    chmod +x "${TEST_DIR}/scripts/dreamcoder"
    mkdir -p "${TEST_DIR}/home"
    extract_block() {
        awk -v want="$1" '/# >>> Dreamcoder listener hook >>>/ { n++; on = (n == want) } on { print } on && /# <<< Dreamcoder listener hook <<</ { exit }' \
            "${ML4W_GTK_LISTENER}"
    }
    extract_block 1 >"${TEST_DIR}/block-dark.sh"
    extract_block 2 >"${TEST_DIR}/block-light.sh"
    # The mode comes from each branch's Matugen call, not from settings.ini.
    printf '[Settings]\ngtk-application-prefer-dark-theme=0\n' >"${TEST_DIR}/settings.ini"
    HOME="${TEST_DIR}/home" SETTINGS_FILE="${TEST_DIR}/settings.ini" bash "${TEST_DIR}/block-dark.sh"
    printf '[Settings]\ngtk-application-prefer-dark-theme=1\n' >"${TEST_DIR}/settings.ini"
    HOME="${TEST_DIR}/home" SETTINGS_FILE="${TEST_DIR}/settings.ini" bash "${TEST_DIR}/block-light.sh"
    [ "$(sed -n 1p "${TEST_DIR}/dispatched")" = "sync|dark|0" ]
    [ "$(sed -n 2p "${TEST_DIR}/dispatched")" = "sync|light|0" ]
    [ -f "${TEST_DIR}/home/.cache/dreamcoder/ml4w-listener-sync.log" ]
    cat "${TEST_DIR}/block-dark.sh" "${TEST_DIR}/block-light.sh" >"${TEST_DIR}/block.sh"
    # The block must never write the file the listener watches (no loop).
    run grep -E 'settings\.ini"? *>|>>? *"?\$\{?SETTINGS_FILE' "${TEST_DIR}/block.sh"
    [ "$status" -ne 0 ]
}

@test "apply-ml4w-hooks: without listeners.sh the hook is applied with a warning" {
    rm -f "${ML4W_LISTENERS_SCRIPT}"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"listeners.sh not found"* ]]
    [ "$(count_listener_blocks)" -eq 2 ]
}

@test "apply-ml4w-hooks: a Matugen call without -m falls back to settings.ini" {
    sed 's| -m "dark"||; s| -m "light"||' "${LISTENER_FIXTURE}" >"${ML4W_GTK_LISTENER}"
    run_hooks
    [ "$(count_listener_blocks)" -eq 2 ]
    printf '#!/usr/bin/env bash\necho "${DREAMCODER_THEME_MODE}" >>"%s/dispatched"\n' "${TEST_DIR}" >"${TEST_DIR}/scripts/dreamcoder"
    chmod +x "${TEST_DIR}/scripts/dreamcoder"
    mkdir -p "${TEST_DIR}/home"
    awk '/# >>> Dreamcoder listener hook >>>/ { on = 1 } on { print } /# <<< Dreamcoder listener hook <<</ { exit }' \
        "${ML4W_GTK_LISTENER}" >"${TEST_DIR}/block.sh"
    printf 'gtk-application-prefer-dark-theme=true\n' >"${TEST_DIR}/settings.ini"
    HOME="${TEST_DIR}/home" SETTINGS_FILE="${TEST_DIR}/settings.ini" bash "${TEST_DIR}/block.sh"
    printf 'gtk-application-prefer-dark-theme=0\n' >"${TEST_DIR}/settings.ini"
    HOME="${TEST_DIR}/home" SETTINGS_FILE="${TEST_DIR}/settings.ini" bash "${TEST_DIR}/block.sh"
    [ "$(tr '\n' ' ' <"${TEST_DIR}/dispatched")" = "dark light " ]
}

# ── Matugen templates that write Dreamcoder-owned files ─────────────────────
# Matugen rewrites hypr/colors.{conf,lua}, waybar/colors.css, rofi/colors.rasi and (through
# a symlink into waybar) swaync/colors.css from the wallpaper. Restoring Dreamcoder colours
# after Matugen is a race that can be lost, so the templates themselves are disabled.

template_ids() {
    python3 - "$1" <<'PY'
import sys
import tomllib

with open(sys.argv[1], "rb") as f:
    print(" ".join(sorted(tomllib.load(f).get("templates", {}))))
PY
}

@test "matugen: templates that write Dreamcoder-owned files are disabled, the rest kept" {
    run run_hooks
    [ "$status" -eq 0 ]
    before="$(template_ids "${MATUGEN_FIXTURE}")"
    after="$(template_ids "${MATUGEN_CONFIG}")"
    for owned in hyprland hyprland-lua waybar rofi swaync; do
        [[ " ${before} " == *" ${owned} "* ]]
        [[ " ${after} " != *" ${owned} "* ]]
    done
    for kept in colorsjson kitty btop gtk3 gtk4 quickshell_overview; do
        [[ " ${after} " == *" ${kept} "* ]]
    done
}

@test "matugen: the patched config is still valid TOML" {
    run run_hooks
    [ "$status" -eq 0 ]
    run template_ids "${MATUGEN_CONFIG}"
    [ "$status" -eq 0 ]
}

@test "matugen: re-running leaves the config byte-identical" {
    run run_hooks
    first="$(cat "${MATUGEN_CONFIG}")"
    run run_hooks
    [ "$status" -eq 0 ]
    [ "$(cat "${MATUGEN_CONFIG}")" = "${first}" ]
    [[ "$output" == *"Matugen"*"already current"* ]]
}

@test "matugen: an ML4W upgrade that restores the stock config is disabled again" {
    run run_hooks
    cp "${MATUGEN_FIXTURE}" "${MATUGEN_CONFIG}"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ " $(template_ids "${MATUGEN_CONFIG}") " != *" waybar "* ]]
}

@test "matugen: a missing config is skipped without failing" {
    rm -f "${MATUGEN_CONFIG}"
    run run_hooks
    [ "$status" -eq 0 ]
    [[ "$output" == *"Matugen config not found"* ]]
}

# ── robustness (paths with spaces, missing tools) ───────────────────────────

@test "harness: every file the hooks write is isolated under the temp dir" {
    # A test that reaches the live ~/.config once already left the real wallpaper runner
    # pointing at a deleted temp path.
    for var in WAYPAPER_CONFIG ML4W_WALLPAPER_SCRIPT ML4W_GTK_LISTENER ML4W_LISTENERS_SCRIPT MATUGEN_CONFIG; do
        [[ "${!var}" == "${TEST_DIR}/"* ]]
    done
}

@test "waypaper: the hook executable is quoted so a dots path with spaces still works" {
    SPACED="${TEST_DIR}/dots with space"
    mkdir -p "${SPACED}/lib" "${SPACED}/scripts"
    cp "${TEST_DIR}/lib/"*.sh "${SPACED}/lib/"
    cp "${TEST_DIR}/scripts/"*.sh "${SPACED}/scripts/"
    DREAMCODER_DOTS_DIR="${SPACED}" run bash "${BATS_TEST_DIRNAME}/../../scripts/apply-ml4w-hooks.sh"
    [ "$status" -eq 0 ]
    grep -qF 'dots\ with\ space/scripts/wallpaper-hook.sh' "${WAYPAPER_CONFIG}"
}

@test "hooks: a hostile dots path is escaped in the generated runner and waypaper commands" {
    # The path goes into generated shell source. Quotes, $(...), backticks, |, & and a
    # backslash must reach the hook as literal characters and must not execute anything.
    HOSTILE="${TEST_DIR}"'/we$(touch INJECTED)`touch INJECTED2`"q|a&b\c'
    mkdir -p "${HOSTILE}/lib" "${HOSTILE}/scripts" "${TEST_DIR}/work"
    cp "${TEST_DIR}/lib/"*.sh "${HOSTILE}/lib/"
    cp "${TEST_DIR}/scripts/theme-auto.sh" "${HOSTILE}/scripts/"
    printf '#!/usr/bin/env bash\nprintf "%%s" "$1" >"%s/called"\n' "${TEST_DIR}/work" >"${HOSTILE}/scripts/wallpaper-hook.sh"
    chmod +x "${HOSTILE}/scripts/"*.sh
    DREAMCODER_DOTS_DIR="${HOSTILE}" run bash "${BATS_TEST_DIRNAME}/../../scripts/apply-ml4w-hooks.sh"
    [ "$status" -eq 0 ]

    # Runner block: run it as the ML4W runner would.
    sed -n '/^# >>> Dreamcoder wallpaper hook >>>$/,/^# <<< Dreamcoder wallpaper hook <<<$/p' \
        "${ML4W_WALLPAPER_SCRIPT}" >"${TEST_DIR}/block.sh"
    (cd "${TEST_DIR}/work" && IMAGE_PATH=runner-image bash "${TEST_DIR}/block.sh")
    [ "$(cat "${TEST_DIR}/work/called")" = "runner-image" ]

    # waypaper post_command: run the appended command with $wallpaper set.
    rm -f "${TEST_DIR}/work/called"
    cmd="$(grep '^post_command' "${WAYPAPER_CONFIG}" | sed 's/^[^;]*; //')"
    (cd "${TEST_DIR}/work" && wallpaper=waypaper-image bash -c "${cmd}")
    [ "$(cat "${TEST_DIR}/work/called")" = "waypaper-image" ]

    [ ! -e "${TEST_DIR}/work/INJECTED" ]
    [ ! -e "${TEST_DIR}/work/INJECTED2" ]
    [ ! -e "${TEST_DIR}/INJECTED" ]
}

@test "hooks: a wallpaper variable that is not a shell identifier is rejected" {
    ML4W_WALLPAPER_VAR='x; touch INJECTED' run run_hooks
    [ "$status" -ne 0 ]
    [[ "$output" == *"not a valid shell identifier"* ]]
}

# A PATH holding only the tools the script needs, so a specific one can be left out.
restricted_path() {
    local skip="$1" bin="${TEST_DIR}/restricted-bin" tool src
    mkdir -p "${bin}"
    for tool in bash env dirname awk sed grep cat tr cut head tail sort uniq date git readlink \
        chmod mkdir cp rm mktemp python3 timeout printf hostname; do
        [[ "${tool}" == "${skip}" ]] && continue
        src="$(command -v "${tool}" 2>/dev/null)" && ln -sf "${src}" "${bin}/${tool}"
    done
    printf '%s' "${bin}"
}

# Set PATH only around the hooks, not around bats' own `run` bookkeeping.
run_hooks_with_path() {
    PATH="$1" run_hooks
}

@test "listener: without timeout(1) the hook is skipped with a warning, not applied unbounded" {
    before="$(cat "${ML4W_GTK_LISTENER}")"
    run run_hooks_with_path "$(restricted_path timeout)"
    [[ "$output" == *"timeout(1) not found"* ]]
    [ "$(cat "${ML4W_GTK_LISTENER}")" = "${before}" ]
}

@test "matugen: without a TOML validator the config is left untouched with a warning" {
    before="$(cat "${MATUGEN_CONFIG}")"
    bin="${TEST_DIR}/nopy"
    mkdir -p "${bin}"
    printf '#!/bin/sh\nexit 1\n' >"${bin}/python3"
    chmod +x "${bin}/python3"
    run run_hooks_with_path "${bin}:${PATH}"
    [[ "$output" == *"to validate the Matugen config, left untouched"* ]]
    [ "$(cat "${MATUGEN_CONFIG}")" = "${before}" ]
}

@test "hooks: a missing required library fails with a clear message" {
    empty="${TEST_DIR}/no-lib"
    mkdir -p "${empty}"
    DREAMCODER_DOTS_DIR="${empty}" run bash "${BATS_TEST_DIRNAME}/../../scripts/apply-ml4w-hooks.sh"
    [ "$status" -ne 0 ]
    [[ "$output" == *"Required library not found"* ]]
}
