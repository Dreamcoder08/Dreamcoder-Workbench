# Public setup entry, isolated from the live desktop and networking services.
load '../helpers/setup'
bats_require_minimum_version 1.5.0

setup() {
  TEST_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  export TEST_TEMP_HOME="$(mktemp -d)"
  # Keep installed Python test dependencies visible under the isolated HOME.
  export PYTHONUSERBASE="$(python3 -m site --user-base)"
  export HOME="${TEST_TEMP_HOME}/home"
  export XDG_CACHE_HOME="${HOME}/.cache"
  export ROUTE="${HOME}/.config/ml4w/scripts/ml4w-network"
  export LAUNCHER="${HOME}/.local/bin/dreamcoder-nmtui"
  export REPO="${TEST_TEMP_HOME}/repo"
  mkdir -p "${REPO}/scripts" "${REPO}/lib" "${HOME}/.config/hypr/conf" \
    "${HOME}/.config/waybar" "${HOME}/.config/wlogout" "${HOME}/.config/swaync" \
    "$(dirname "${ROUTE}")" "${TEST_TEMP_HOME}/bin"
  cp "${TEST_DIR}/scripts/setup-hyprland.sh" "${REPO}/scripts/"
  cp -R "${TEST_DIR}/lib/." "${REPO}/lib/"
  cp -R "${TEST_DIR}/DreamcoderProfiles" "${TEST_DIR}/ml4w_assets" "${TEST_DIR}/DreamcoderShell" "${REPO}/"
  touch "${HOME}/.config/hypr/conf/keybinding.lua" "${HOME}/.config/waybar/launch.sh"
  printf '#!/bin/bash\nexit 0\n' >"${REPO}/scripts/apply-ml4w-hooks.sh"
  cat >"${REPO}/scripts/generate-custom-lua.sh" <<'SCRIPT'
#!/bin/bash
[[ " $* " == *' --dry-run '* ]] && exit 0
printf '%s\n' '-- Valid isolated generator fixture' >"${HOME}/.config/hypr/custom.lua"
SCRIPT
  for command in hyprctl sudo systemctl nmtui; do
    printf '#!/bin/bash\nprintf "%%s\\n" "%s $*" >>"${TEST_TEMP_HOME}/calls"\necho ok\n' "${command}" >"${TEST_TEMP_HOME}/bin/${command}"
    chmod +x "${TEST_TEMP_HOME}/bin/${command}"
  done
  printf '#!/bin/bash\nexit 0\n' >"${TEST_TEMP_HOME}/bin/check-json"
  chmod +x "${TEST_TEMP_HOME}/bin/check-json"
  export PATH="${TEST_TEMP_HOME}/bin:${PATH}"
  cat >"${ROUTE}" <<'SCRIPT'
#!/bin/bash
# Keep this customization and whitespace exactly.
if systemctl is-active --quiet NetworkManager; then
    nmtui
else
    sudo systemctl start NetworkManager
    if [ $? -eq 0 ]; then
        nmtui
    else
        echo "NetworkManager could not start"
    fi
fi
SCRIPT
  chmod +x "${ROUTE}"
  cp "${ROUTE}" "${TEST_TEMP_HOME}/original"
}

apply_setup() {
  run --separate-stderr bash "${REPO}/scripts/setup-hyprland.sh" --profile default "$@"
  [[ "${status}" -eq 0 ]]
}

snapshot() {
  # Bytes, links, permissions and timestamps, including command counters.
  python3 - "${@:-${HOME}}" "${TEST_TEMP_HOME}/calls" <<'PY'
import hashlib, os, pathlib, sys
for root in sys.argv[1:]:
    paths = [pathlib.Path(root)]
    if paths[0].is_dir():
        paths += sorted(paths[0].rglob('*'))
    for p in paths:
        if not p.exists() and not p.is_symlink():
            continue
        s = p.lstat()
        value = os.readlink(p) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ''
        print(str(p), s.st_mode, s.st_mtime_ns, value)
PY
}

use_python_schema_paths() {
  # Hide the optional validator so the public command exercises its fallback.
  mv "${TEST_TEMP_HOME}/bin/check-json" "${TEST_TEMP_HOME}/check-json-disabled"
  local repo_name="$1"
  mv "${REPO}" "${TEST_TEMP_HOME}/${repo_name}"
  export REPO="${TEST_TEMP_HOME}/${repo_name}"
  mv "${HOME}" "${TEST_TEMP_HOME}/home's desktop"
  export HOME="${TEST_TEMP_HOME}/home's desktop"
  export ROUTE="${HOME}/.config/ml4w/scripts/ml4w-network"
  export LAUNCHER="${HOME}/.local/bin/dreamcoder-nmtui"
  # Suppress the existing read-only probe in snapshots of dry-run/rejection.
  printf '#!/bin/bash\nexit 0\n' >"${TEST_TEMP_HOME}/bin/hyprctl"
}

@test "setup schema: apostrophes in repository and HOME remain literal paths" {
  use_python_schema_paths "repo's checkout"
  before="$(snapshot)"
  apply_setup --dry-run
  [[ "${output}" == *'Profile matches schema'* ]]
  [[ "${output}" == *'Pre-flight: 10 passed'* ]]
  [[ -z "${stderr}" ]]
  [[ "$(snapshot)" == "${before}" ]]
}

@test "setup schema: Python-shaped path cannot execute code and rejected input is inert" {
  use_python_schema_paths "repo'+str(__import__('os').system('touch injected'))+'"
  cd "${TEST_TEMP_HOME}"
  before="$(snapshot "${HOME}" "${REPO}")"
  apply_setup --dry-run
  [[ "${output}" == *'Profile matches schema'* ]]
  [[ "${output}" == *'Pre-flight: 10 passed'* ]]
  [[ -z "${stderr}" && ! -e injected ]]
  [[ "$(snapshot "${HOME}" "${REPO}")" == "${before}" ]]
  run --separate-stderr bash "${REPO}/scripts/setup-hyprland.sh" --unknown
  [[ "${status}" -eq 1 && -z "${output}" ]]
  [[ "${stderr}" == '✖ Unknown option: --unknown' ]]
  [[ ! -e injected ]]
  [[ "$(snapshot "${HOME}" "${REPO}")" == "${before}" ]]
}

@test "setup colors: preview, install and repeat resolve both links to Waybar" {
  printf 'waybar colors\n' >"${HOME}/.config/waybar/colors.css"
  printf 'original logout colors\n' >"${HOME}/.config/wlogout/colors.css"
  ln -s '../../waybar/colors.css' "${HOME}/.config/swaync/colors.css"
  # Respond successfully to reload without recording a dry-run probe as a write.
  printf '#!/bin/bash\necho ok\n' >"${TEST_TEMP_HOME}/bin/hyprctl"
  before="$(snapshot)"
  apply_setup --dry-run
  [[ -z "${stderr}" ]]
  [[ "${output}" == *"${HOME}/.config/wlogout/colors.css → ../waybar/colors.css"* ]]
  [[ "${output}" == *"${HOME}/.config/swaync/colors.css  → ../waybar/colors.css"* ]]
  [[ "$(snapshot)" == "${before}" ]]
  apply_setup
  [[ -z "${stderr}" ]]
  for directory in wlogout swaync; do
    link="${HOME}/.config/${directory}/colors.css"
    [[ -L "${link}" && "$(readlink "${link}")" == '../waybar/colors.css' ]]
    [[ "$(readlink -f "${link}")" == "${HOME}/.config/waybar/colors.css" ]]
    [[ "$(<"${link}")" == 'waybar colors' ]]
  done
  [[ "$(<"${HOME}/.config/wlogout/colors.css.bak")" == 'original logout colors' ]]
  [[ ! -e "${HOME}/.config/swaync/colors.css.bak" ]]
  before="$(snapshot "${HOME}/.config/wlogout" "${HOME}/.config/swaync")"
  apply_setup
  [[ -z "${stderr}" ]]
  [[ "${output}" == *"Already linked:"* ]]
  [[ "$(snapshot "${HOME}/.config/wlogout" "${HOME}/.config/swaync")" == "${before}" ]]
}

@test "nmtui route: setup installs launcher before replacing only the two invocations" {
  apply_setup
  [[ "${output}" == *"ML4W network route installed:"* ]]
  cmp "${LAUNCHER}" "${REPO}/DreamcoderShell/.local/bin/dreamcoder-nmtui"
  [[ -x "${LAUNCHER}" && -x "${ROUTE}" ]]
  cmp "${ROUTE}.bak" "${TEST_TEMP_HOME}/original"
  python3 - "${TEST_TEMP_HOME}/original" "${ROUTE}" <<'PY'
import pathlib, sys
original, actual = (pathlib.Path(p).read_bytes() for p in sys.argv[1:])
assert actual == original.replace(b'    nmtui', b'    "${HOME}/.local/bin/dreamcoder-nmtui"')
PY
  [[ "$(cat "${TEST_TEMP_HOME}/calls")" == 'hyprctl monitors -j
hyprctl reload' ]]
}

@test "nmtui route: dry-run is byte and counter identical" {
  # monitors is an existing read-only setup probe; don't count that query.
  printf '#!/bin/bash\nexit 0\n' >"${TEST_TEMP_HOME}/bin/hyprctl"
  before="$(snapshot)"
  apply_setup --dry-run
  [[ "${output}" == *"Would install ML4W network route:"* ]]
  [[ "$(snapshot)" == "${before}" ]]
}

@test "nmtui route: repeated and already patched installs preserve bytes and old backup" {
  apply_setup
  printf 'older backup\n' >"${ROUTE}.bak"
  before="$(snapshot "${ROUTE}" "${ROUTE}.bak" "${LAUNCHER}" | grep -v '/calls ')"
  apply_setup
  [[ "${output}" == *"ML4W network route already current:"* ]]
  [[ "$(snapshot "${ROUTE}" "${ROUTE}.bak" "${LAUNCHER}" | grep -v '/calls ')" == "${before}" ]]
  # Other setup actions intentionally run again; compare only owned route files.
  [[ "$(cat "${ROUTE}.bak")" == 'older backup' ]]
  [[ "$(grep -c 'dreamcoder-nmtui' "${ROUTE}")" -eq 2 ]]
  cmp "${LAUNCHER}" "${REPO}/DreamcoderShell/.local/bin/dreamcoder-nmtui"
}

@test "nmtui route: unknown script and missing optional script are skipped" {
  printf '#!/bin/bash\nnmtui --custom\n' >"${ROUTE}"
  cp "${ROUTE}" "${TEST_TEMP_HOME}/unknown"
  apply_setup
  [[ "${stderr}" == *"Unrecognized ML4W network script, skipped:"* ]]
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/unknown"
  [[ ! -e "${LAUNCHER}" && ! -e "${ROUTE}.bak" ]]
  mv "${ROUTE}" "${TEST_TEMP_HOME}/absent"
  apply_setup
  [[ "${stderr}" == *"ML4W network script missing, skipped:"* ]]
  [[ ! -e "${ROUTE}" && ! -e "${LAUNCHER}" ]]
}

@test "nmtui route: unrelated launcher is never overwritten or routed" {
  mkdir -p "$(dirname "${LAUNCHER}")"
  printf '#!/bin/bash\necho custom\n' >"${LAUNCHER}"
  cp "${LAUNCHER}" "${TEST_TEMP_HOME}/custom"
  apply_setup
  [[ "${stderr}" == *"Conflicting nmtui launcher, skipped:"* ]]
  cmp "${LAUNCHER}" "${TEST_TEMP_HOME}/custom"
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/original"
  [[ ! -e "${ROUTE}.bak" ]]
}

@test "nmtui route: custom control flow is preserved even with two bare invocations" {
  printf '\nlogger custom-network-action\n' >>"${ROUTE}"
  cp "${ROUTE}" "${TEST_TEMP_HOME}/custom-route"
  apply_setup
  [[ "${stderr}" == *"Unrecognized ML4W network script, skipped:"* ]]
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/custom-route"
  [[ ! -e "${LAUNCHER}" && ! -e "${ROUTE}.bak" ]]
}

@test "nmtui route: personal route and launcher symlinks are never followed" {
  mv "${ROUTE}" "${TEST_TEMP_HOME}/linked-route"
  ln -s "${TEST_TEMP_HOME}/linked-route" "${ROUTE}"
  apply_setup
  [[ "${stderr}" == *"Unrecognized ML4W network script, skipped:"* ]]
  [[ -L "${ROUTE}" && ! -e "${LAUNCHER}" && ! -e "${ROUTE}.bak" ]]
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/original"
  # Restore the regular fixture without removing the personal link.
  mv "${ROUTE}" "${TEST_TEMP_HOME}/personal-route-link"
  cp "${TEST_TEMP_HOME}/original" "${ROUTE}"
  mkdir -p "$(dirname "${LAUNCHER}")"
  ln -s "${TEST_TEMP_HOME}/missing-launcher" "${LAUNCHER}"
  apply_setup
  [[ "${stderr}" == *"Conflicting nmtui launcher, skipped:"* ]]
  [[ -L "${LAUNCHER}" && ! -e "${TEST_TEMP_HOME}/missing-launcher" && ! -e "${ROUTE}.bak" ]]
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/original"
}

@test "nmtui route: already patched script repairs missing launcher without a backup" {
  python3 - "${ROUTE}" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_bytes(p.read_bytes().replace(b'    nmtui', b'    "${HOME}/.local/bin/dreamcoder-nmtui"'))
PY
  cp -p "${ROUTE}" "${TEST_TEMP_HOME}/patched"
  apply_setup
  [[ -z "${stderr}" ]]
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/patched"
  cmp "${LAUNCHER}" "${REPO}/DreamcoderShell/.local/bin/dreamcoder-nmtui"
  [[ -x "${LAUNCHER}" && ! -e "${ROUTE}.bak" ]]
}

@test "nmtui route: failed launcher installation cannot patch or back up the route" {
  cat >"${TEST_TEMP_HOME}/bin/cp" <<'SCRIPT'
#!/bin/bash
if [[ "${*: -1}" == "${LAUNCHER}" ]]; then
  echo 'isolated launcher install failure' >&2
  exit 1
fi
exec /usr/bin/cp "$@"
SCRIPT
  chmod +x "${TEST_TEMP_HOME}/bin/cp"
  run --separate-stderr bash "${REPO}/scripts/setup-hyprland.sh" --profile default
  [[ "${status}" -eq 1 ]]
  [[ "${stderr}" == 'isolated launcher install failure' ]]
  cmp "${ROUTE}" "${TEST_TEMP_HOME}/original"
  [[ ! -e "${LAUNCHER}" && ! -e "${ROUTE}.bak" ]]
  [[ "$(cat "${TEST_TEMP_HOME}/calls")" == 'hyprctl monitors -j' ]]
}
