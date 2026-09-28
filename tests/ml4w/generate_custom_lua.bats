# ============================================================================
# BATS tests: generate-custom-lua.sh
# ============================================================================

load '../helpers/setup'

@test "generate-custom-lua: --help exits cleanly" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"generate-custom-lua.sh"* ]]
  [[ "$output" == *"machine profile"* ]]
}

@test "generate-custom-lua: --list-profiles shows all profiles" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" --list-profiles
  [ "$status" -eq 0 ]
  [[ "$output" == *"default"* ]]
  [[ "$output" == *"asus-vivobook15"* ]]
}

@test "generate-custom-lua: --validate passes for default" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile default --validate
  [ "$status" -eq 0 ]
}

@test "generate-custom-lua: --validate passes for asus-vivobook15" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --validate
  [ "$status" -eq 0 ]
}

@test "generate-custom-lua: --validate fails for missing profile" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile nonexistent --validate
  [ "$status" -ne 0 ]
}

@test "generate-custom-lua: --dry-run produces valid Lua for default" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile default --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"SUPER + SHIFT + D"* ]]
  [[ "$output" == *"Toggle Dreamcoder"* ]]
  [[ "$output" == *"local mainMod"* ]]
}

@test "generate-custom-lua: --dry-run produces valid Lua for asus-vivobook15" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"F1"* ]]
  [[ "$output" == *"Mutear audio"* ]]
  [[ "$output" == *"code:238"* ]]
  [[ "$output" == *"hl.bind"* ]]
}

@test "generate-custom-lua: dry-run output passes luac syntax check" {
  if ! command -v luac >/dev/null; then
    skip "luac not available"
  fi

  # Capture just the Lua body by finding lines between the two ═══ markers
  local lua_output
  lua_output="$(
    "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
      --profile default --dry-run 2>&1 \
      | sed -n '/^-- ===/,/^═══ Would write to/p' \
      | head -n -1
  )"

  # Write to temp and check with luac
  local tmpfile
  tmpfile="$(mktemp /tmp/test_generated_lua.XXXXXX)"
  echo "$lua_output" > "$tmpfile"
  run luac -p "$tmpfile"
  echo "# luac output: $output" >&3
  rm -f "$tmpfile"
  [ "$status" -eq 0 ]
}

@test "generate-custom-lua: generates correct number of bindings for default" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile default --dry-run
  [ "$status" -eq 0 ]
  local expected
  expected=$(jq '.keybindings.bindings | length' "${PROFILES_DIR}/default.json")
  local count
  count="$(echo "$output" | grep -cE '^hl\.(bind|bindl|mouse_bind)\(' || true)"
  echo "# bind function calls: $count (expected $expected)" >&3
  [ "$count" -eq "$expected" ]
}

@test "generate-custom-lua: asus-vivobook15 generates all profile bindings" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --dry-run
  [ "$status" -eq 0 ]
  local expected
  expected=$(jq '.keybindings.bindings | length' "${PROFILES_DIR}/asus-vivobook15.json")
  local count
  count="$(echo "$output" | grep -cE '^hl\.(bind|bindl|mouse_bind)\(' || true)"
  echo "# bind function calls: $count (expected $expected)" >&3
  [ "$count" -eq "$expected" ]
}

@test "generate-custom-lua: each binding has a dispatcher (exec_cmd or native)" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --dry-run
  [ "$status" -eq 0 ]
  local expected
  expected=$(jq '.keybindings.bindings | length' "${PROFILES_DIR}/asus-vivobook15.json")
  local cmds
  cmds="$(echo "$output" | grep -cE 'hl\.dsp\.' || true)"
  echo "# dispatcher count: $cmds (expected $expected)" >&3
  [ "$cmds" -eq "$expected" ]
}

@test "generate-custom-lua: hyprctl dispatch workspace binds use native dispatchers" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --dry-run
  [ "$status" -eq 0 ]
  # Legacy `hyprctl dispatch workspace N` fails on Hyprland >= 0.55 (Lua
  # parses the arg), so the generator must emit hl.dsp.focus({workspace=N}).
  [[ "$output" == *"hl.dsp.focus({ workspace = 1 })"* ]]
  [[ "$output" == *"hl.dsp.window.move({ workspace = 1 })"* ]]
  [[ "$output" != *'hyprctl dispatch workspace'* ]]
  [[ "$output" != *'hyprctl dispatch movetoworkspace'* ]]
}

@test "generate-custom-lua: bare Fn keys have no SUPER prefix" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --dry-run
  [ "$status" -eq 0 ]
  # F1-F12 should NOT have SUPER
  [[ "$output" == *'"F1"'* ]]
  [[ "$output" != *'SUPER + F1'* ]]
}

@test "generate-custom-lua: --validate reports profile name" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile default --validate
  [ "$status" -eq 0 ]
  [[ "$output" == *"default.json"* ]]
}

@test "generate-custom-lua: custom.lua loads dreamcoder-colors exactly once, guarded" {
  run bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" \
    --profile asus-vivobook15 --dry-run
  [ "$status" -eq 0 ]
  # ML4W upgrades rewrite hyprland.lua, so the loader lives in custom.lua.
  [ "$(grep -c 'require("dreamcoder-colors")' <<<"$output")" -eq 1 ]
  [[ "$output" == *'io.open(os.getenv("HOME") .. "/.config/hypr/dreamcoder-colors.lua", "r")'* ]]
}

@test "generate-custom-lua: regenerating keeps a single colour loader" {
  bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" --profile default >/dev/null
  bash "${DREAMCODER_DOTS_DIR}/scripts/generate-custom-lua.sh" --profile default >/dev/null
  [ "$(grep -c 'require("dreamcoder-colors")' "${HOME}/.config/hypr/custom.lua")" -eq 1 ]
}
