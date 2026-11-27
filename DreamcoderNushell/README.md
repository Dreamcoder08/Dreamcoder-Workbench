# Dreamcoder Nushell

Nushell config for Dreamcoder Dots, adapted from [Gentleman.Dots](https://github.com/Gentleman-Programming/gentleman-dots).

## Theme

**Dreamcoder Dark** — dark theme based on Dreamcoder Workbench visual tokens and its canonical surface policy.

| Token   | Color     |
| ------- | --------- |
| BG      | `#000000` |
| Text    | `#e0e0e0` |
| Accent  | `#a7b5fd` |
| Success | `#86cf90` |
| Warning | `#dcb55e` |
| Error   | `#fc9d95` |
| Info    | `#76c4f6` |

## Usage

```bash
nu
```

Or set as default shell:

```bash
chsh -s $(which nu)
```

## Integrations

- zoxide (frecency-based cd)
- carapace (completions)
- atuin (shell history)
- starship (prompt)
- ripgrep (grep)
- fd-find (find)

## Keybindings

- Vi mode
- `Ctrl+R` — history search
- `Ctrl+Q` — search history
- `Ctrl+Shift+C` — copy selection
- `F1` — help menu
- Tab — completion menu
