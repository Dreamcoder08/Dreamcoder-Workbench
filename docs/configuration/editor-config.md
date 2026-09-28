# Editor Configuration

## Neovim (LazyVim)

### Structure

```
DreamcoderNvim/.config/nvim/
├── init.lua           # Bootstrap
├── lua/
│   ├── config/        # Core config
│   ├── plugins/       # Plugin specs
│   └── colors/        # Dreamcoder colorscheme
```

### Theme

Dreamcoder colorscheme generated from `tokens.json`:

```lua
-- lua/plugins/colorscheme.lua
return {
  "dreamcoder.nvim",
  opts = {
    variant = "dark", -- or "light"
  },
}
```

### Key Maps

LazyVim provides the default keymaps for this setup. See the [Theme](#theme) section above for the Dreamcoder colorscheme setup.

### Plugins

Core plugins:

- LazyVim (framework)
- LSP (nvim-lspconfig)
- Treesitter (syntax)
- Telescope (fuzzy finder)
- Git signs
- Which-key (key hints)
