# Dreamcoder Nushell

Nushell config for Dreamcoder Dots, adapted from [Gentleman.Dots](https://github.com/Gentleman-Programming/gentleman-dots).

## Theme

**Dreamcoder Dark** — dark theme based on Dreamcoder OS visual tokens and its canonical surface policy.

| Token   | Color     |
| ------- | --------- |
| BG      | `#100f0d` |
| Text    | `#e8dfd0` |
| Accent  | `#d99555` |
| Success | `#4db35f` |
| Warning | `#e8b866` |
| Error   | `#ed8a7a` |
| Info    | `#5f95ca` |

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
