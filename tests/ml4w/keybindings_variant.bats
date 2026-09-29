# ============================================================================
# BATS tests: ml4w_assets/hypr/conf/keybindings/dreamcoder.lua
# ============================================================================
# The curated variant tracks upstream ML4W default.lua (tag 2.16) minus the
# binds the machine profile owns. These checks keep it aligned with the 2.16
# layout and free of collisions with the profile.

load '../helpers/setup'

variant() { printf '%s' "${DREAMCODER_DOTS_DIR}/ml4w_assets/hypr/conf/keybindings/dreamcoder.lua"; }
profile() { printf '%s' "${DREAMCODER_DOTS_DIR}/DreamcoderProfiles/dreamcoder/asus-vivobook15.json"; }

@test "keybindings variant: parses as Lua" {
  command -v luac >/dev/null || skip "luac not installed"
  run luac -p "$(variant)"
  [ "$status" -eq 0 ]
}

@test "keybindings variant: SUPER+Tab opens the 2.16 overview location" {
  run grep -F 'qs -p ~/.local/share/quickshell-overview ipc call overview toggle' "$(variant)"
  [ "$status" -eq 0 ]
  run grep -F '.config/quickshell/overview' "$(variant)"
  [ "$status" -ne 0 ]
}

@test "keybindings variant: ports the 2.16 autohide toggles" {
  run grep -F '" + ALT + B", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-statusbar-autohide")' "$(variant)"
  [ "$status" -eq 0 ]
  run grep -F '" + ALT + D", hl.dsp.exec_cmd("~/.config/ml4w/scripts/ml4w-toggle-dock-autohide")' "$(variant)"
  [ "$status" -eq 0 ]
}


@test "keybindings variant: no mainMod bind collides with the profile" {
  command -v jq >/dev/null || skip "jq not installed"
  # Profile combos, normalised to "MOD+MOD+KEY" in upper case.
  jq -r '.keybindings.bindings[] | select((.mouse // false) | not)
         | ((.mods // []) + [.key]) | join("+") | ascii_upcase' "$(profile)" \
    | sort -u >"${BATS_TEST_TMPDIR}/profile"
  # Static variant combos: hl.bind(mainMod .. " + X + Y", ...).
  grep -oE 'hl\.bind\(mainMod \.\. " \+ [^"]+"' "$(variant)" \
    | sed -E 's/.*" \+ ([^"]+)"/SUPER + \1/; s/ \+ /+/g' | tr '[:lower:]' '[:upper:]' \
    | sort -u >"${BATS_TEST_TMPDIR}/variant"
  run comm -12 "${BATS_TEST_TMPDIR}/profile" "${BATS_TEST_TMPDIR}/variant"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "keybindings variant: keyboard resize uses SUPER + CTRL + arrows, leaving SUPER + SHIFT + arrows to the profile's move-window" {
  for dir in right left down up; do
    run grep -F "mainMod .. \" + CTRL + ${dir}\", hl.dsp.window.resize(" "$(variant)"
    [ "$status" -eq 0 ]
    run grep -F "mainMod .. \" + SHIFT + ${dir}\"" "$(variant)"
    [ "$status" -ne 0 ]
  done
}
