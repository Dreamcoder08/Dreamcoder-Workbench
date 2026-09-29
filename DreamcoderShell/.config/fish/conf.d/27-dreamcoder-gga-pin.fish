# gga reviews use the Codex provider. The model itself is pinned by the shim in
# ~/.config/gga/bin (docs/configuration/gga.md); putting that directory on PATH happens in
# config.fish, because conf.d runs before it and config.fish prepends ~/.local/bin, which
# would leave the real codex ahead of the shim.
set -l _dc_config_home $HOME/.config
set -q XDG_CONFIG_HOME[1]; and test -n "$XDG_CONFIG_HOME"; and set _dc_config_home $XDG_CONFIG_HOME
test -d $_dc_config_home/gga/bin; and set -gx GGA_PROVIDER codex
