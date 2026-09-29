# gga reviews: Codex provider with the pinned model shim first on PATH.
# The shim only changes `codex exec` calls made by gga (docs/configuration/gga.md).
set -l _dc_config_home $HOME/.config
set -q XDG_CONFIG_HOME[1]; and test -n "$XDG_CONFIG_HOME"; and set _dc_config_home $XDG_CONFIG_HOME
set -l _dc_gga_bin $_dc_config_home/gga/bin
if test -d $_dc_gga_bin
    set -gx GGA_PROVIDER codex
    fish_add_path --global --move --path $_dc_gga_bin
end
