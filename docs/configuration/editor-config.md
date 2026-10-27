# Configure Neovim

The repository provides a thin Neovim layer over Gentleman.Dots, not a standalone LazyVim installation. Complete the upstream setup and review the [desktop installation guide](../../INSTALL.md) or a component guide before using it.

## Use the theme

`DreamcoderNvim/.config/nvim/init.lua` loads `$HOME/Gentleman.Dots/GentlemanNvim/nvim/init.lua` and then selects the `dreamcoder` colorscheme. The `colors/` directory contains the dispatcher and generated dark and light variants. Ensure the configuration and colors directory are installed where Neovim reads them; generation alone does not install the editor configuration.

The dispatcher uses the mode and cached selection; an already running editor may need a reload or restart. To change mode, use the wrapper described in the [theme system guide](theme-system.md), with its configuration write and reload implications. If the upstream clone lives elsewhere, inspect the configured path before loading this layer.

## Customize the editor

Gentleman.Dots owns the bootstrap, keymaps and plugin configuration loaded by this layer. Consult that upstream configuration for installed plugins and bindings rather than assuming that this repository supplies them. For terminal appearance, continue to [terminal configuration](terminal-config.md), or return to the [documentation hub](../README.md).
