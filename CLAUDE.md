# CLAUDE.md

Dreamcoder Workbench is the personal Arch Linux dotfiles repo for the **Dreamcoder**
identity.

## Project overview

This repo manages terminal and shell configuration for a fixed visual identity:

- Kitty
- Ghostty
- Fish/Zsh/Bash
- Starship
- Fastfetch
- AI tooling integration

The theme strategy is **identity-first**. Do not replace Dreamcoder colors with
wallpaper-derived palettes unless explicitly requested.

## Important commands

```bash
./scripts/dreamcoder sync
./scripts/generate-palette-tokens.py
bash -n scripts/update-colors.sh
ghostty +validate-config
STARSHIP_CONFIG=DreamcoderShell/.config/starship.toml starship explain
fish -n DreamcoderShell/.config/fish/config.fish
```

## Structure

```txt
├── DreamcoderShell/      # shell configs, Starship, Fish conf.d
├── DreamcoderKitty/      # Kitty config and Dreamcoder colors
├── DreamcoderGhostty/    # Ghostty config and Dreamcoder theme
├── DreamcoderFastfetch/  # Fastfetch config and Dreamcoder01 image
├── DreamcoderThemes/     # Generated theme tokens and snippets
└── scripts/              # sync/update helpers
```

## Dreamcoder identity

Canonical palettes (see `DreamcoderThemes/dreamcoder/tokens.json`):

**Dark — Dreamcoder Dark**

```txt
bg          #000000
text        #E6E6E6
accent      #A5B4FC
accent_2    #D4B5FD
error       #FB8585
focus       #3B82F6
opacity     0.76
```

Dark and Light are the only user-facing modes. Legacy Dusk remains a
compatibility token set, and OLED behavior is defined by
`modes.dark.surface_policy`.

**Light — Cocoa/Lúcuma ("Lúcuma paper")**

```txt
bg          #f9f6f2
bg_soft     #f2eee9   recessed chrome (sidebars)
surface0    #fefdfa   cards above the canvas
surface1    #eee9e2   hover
selection   #f1d7c2   selected rows and text
text        #1e1814
muted       #352f29
comment     #675d53
accent      #8b440c
accent_2    #a73b15
error       #a12623
warning     #795700
focus       #006973
opacity     0.96
```

Light is designed in OKLCH: warm paper neutrals (hue 78, chroma <= 0.02),
colour only in accents and iso-lightness semantics. Every text token keeps
>= 4.5:1 on bg, bg_soft, surface0, surface1, surface2 and selection; borders
>= 3:1 on resting surfaces. Selected rows use `selection`, hover uses
`surface1`, sidebars use `bg_soft` (see `odd/tasks/dreamcoder-light-paper.md`).

Rules:

- visible theme name is `Dreamcoder`
- edit colors only in `DreamcoderThemes/dreamcoder/tokens.json`, then `./scripts/dreamcoder sync`
- Starship palette is `dreamcoder`
- Ghostty theme is `dreamcoder` / `dreamcoder-dark` / `dreamcoder-light`
- Fastfetch logo is `Dreamcoder01.jpg`
- do not commit secrets or tokens

## GitHub MCP

GitHub MCP is configured outside the repo using:

```txt
~/.local/bin/github-mcp-dreamcoder
~/.config/github/pat
```

Never print or commit the token.
