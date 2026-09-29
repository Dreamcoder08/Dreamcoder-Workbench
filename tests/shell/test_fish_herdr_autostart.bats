#!/usr/bin/env bats
# ============================================================================
# Fish autostart must launch Herdr with SHELL pinned to fish, because Herdr
# spawns every pane with $SHELL and the session may export another shell.
# ============================================================================

@test "fish config has valid syntax" {
    run fish -n DreamcoderShell/.config/fish/config.fish
    [ "$status" -eq 0 ]
}

@test "fish autostart pins SHELL to the running fish when launching Herdr" {
    grep -qF 'env SHELL=(status fish-path) herdr' DreamcoderShell/.config/fish/config.fish
}
