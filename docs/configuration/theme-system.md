# Dreamcoder Workbench Theme System

## Choose a mode or regenerate

From the repository root, activate the Python environment described in [INSTALL.md](../../INSTALL.md), then choose the operation you need:

```bash
./scripts/dreamcoder dark  # or light: activate a mode
./scripts/dreamcoder sync  # regenerate using the selected active mode
```

Mode activation prepares and validates the theme, persists the choice, writes configurations and invokes reload adapters. Sync regenerates palette tokens and writes live targets and, by default, repository outputs; it can also update selectors and the Bat cache. Both can affect your existing configuration. Inspect changes and reload or restart applications where needed. Neither operation installs applications or their configuration. For the desktop installation and recovery path, see [INSTALL.md](../../INSTALL.md).

`dreamcoder-theme` is the installed control CLI: its parser offers `theme apply dark` and `theme apply light`, but no `sync` command. Use the repository wrapper above for sync. `DREAMCODER_THEME_MODE=light` or `dark` selects sync's mode; otherwise it uses the persisted live mode, then dark. `DREAMCODER_WRITE_REPO=0` skips repository theme outputs, not live configuration writes.

## Architecture

```text
tokens.json → generate-palette-tokens.py → palette_tokens.py
            → palette and renderers → sync writers → live and repository outputs
```

Semantic roles are derived from canonical tokens; optional wallpaper adaptation can modify the active palette. The coverage declaration and registry in `src/dreamcoder_theme/sync.py` describe rendered consumers, not proof that every application is installed or tested on every platform.

## Canonical tokens

Single source of truth: [`DreamcoderThemes/dreamcoder/tokens.json`](../../DreamcoderThemes/dreamcoder/tokens.json)

The user-facing modes are **dark** and **light**. The token data also contains an internal legacy variant. Dark's `surface_policy` permits pure black only for the canvas; functional
and scrollable surfaces use the near-black ladder (`surface0`–`surface3`) to
reduce OLED smear.

| Layer       | Examples                                                       |
| ----------- | -------------------------------------------------------------- |
| Surfaces    | `bg`, `bg_soft`, `surface0`–`surface3`                         |
| Text        | `text`, `text_heading`, `muted`, `subtle`, `comment`           |
| Brand       | `accent`, `accent_2`, `link`, `link_hover`                     |
| Feedback    | `error`, `warning`, `success`, `info`, `diagnostic`            |
| On-colors   | `on_surface`, `on_accent`, `on_error`, `on_focus`              |
| Interaction | `selection_bg`, `selection_fg`, `hover`, `pressed`, `disabled` |
| Chrome      | `border`, `border_ui`, `border_hi`, `focus`, `panel_rgba`      |

## Regenerating themes

After editing `tokens.json`:

```bash
python scripts/generate-palette-tokens.py  # write generated palette_tokens.py
python scripts/generate-dark-css.py         # write dreamcoder-dark.css variables
./scripts/dreamcoder sync                  # write live and repository outputs
python scripts/verify-theme-health.py      # check theme health
```

CI or local drift checks can use:

```bash
python scripts/generate-palette-tokens.py --check
python scripts/generate-dark-css.py --check
```

## Bat compiled cache

`dreamcoder sync` checks Bat's compiled cache after all theme source and variant
writes. Missing `themes.bin` or `syntaxes.bin`, or theme sources newer than either
binary, trigger `bat cache --build`; an up-to-date cache is left unchanged.
`BAT_THEME_DIR` selects the sources (default: `$XDG_CONFIG_HOME/bat/themes`, or
`~/.config/bat/themes`). `BAT_CACHE_PATH` selects the compiled cache (default:
`$XDG_CACHE_HOME/bat`, or `~/.cache/bat`). Builds ignore user Bat options by setting
`BAT_CONFIG_PATH` to the null device. Bat is optional: when it is absent, sync
continues without compiling. A build failure stops sync with a diagnostic and
paths to check before retrying; generated theme sources remain available.

## Pi and Gentle Shell

`dreamcoder light`, `dreamcoder dark`, and `dreamcoder sync` generate the same
`dreamcoder` theme for Pi and Gentle Shell and select it in each agent's
`settings.json`. These commands retain wallpaper adaptation when enabled;
unrelated settings are preserved.

- Pi defaults to `~/.pi/agent`. `PI_CODING_AGENT_DIR` takes precedence over the
  legacy `PI_AGENT_DIR`; `PI_THEME` and `PI_SETTINGS` override their respective
  Pi destinations.
- Gentle Shell defaults to `~/.gentle-shell/agent`. `GENTLE_SHELL_HOME` overrides
  that agent directory, including when it points to the Pi agent directory.
- Each active `themes/dreamcoder.json` is a regular generated file. Legacy
  symlinks are replaced without modifying their repository variant targets.
- Theme selection is the pair `dreamcoder-light/dreamcoder-dark`, so Pi follows
  the terminal appearance and switches live when the terminal reports a change.
  `themes/dreamcoder-dark.json` and `themes/dreamcoder-light.json` declare their
  own filename as `name` and the matching `appearance`; the stable
  `themes/dreamcoder.json` keeps `name: dreamcoder` for manual `--use-theme`
  selection.

The theme-only helper `DreamcoderPi/.pi/agent/scripts/pi-theme.sh` uses the same
validation and destination rules but always generates canonical, non-adaptive
colors, even with inherited `DREAMCODER_ADAPTIVE=1` and a wallpaper. It disables
adaptation only for its own generation process so Matugen cannot run templates
that change unrelated desktop files; normal theme commands remain adaptive.
Running sessions can reload the active user theme when supported; restart a
session if it retains its previous theme selection.

## GTK and Qt

The Dark GTK surfaces write `dreamcoder-dark.css` into `~/.config/gtk-3.0` and
`~/.config/gtk-4.0` and add a managed import to each `gtk.css`. That file is a
named-colour sheet (`@define-color` only), not a widget stylesheet.

Measured reach (headless GTK 3.24.52, GTK 4.22.5, libadwaita 1.9):

- libadwaita applications adopt the Dark names, so their windows, headers and
  controls follow the palette.
- Plain GTK 3 applications and GTK 4 applications that do not use libadwaita
  keep the colours of their active GTK theme. A `@define-color` name resolves
  inside the sheet that defines it, so an import-only sheet never overrides the
  widget styles those applications already set.
- Qt applications read `qt6ct-dark.conf`, a palette file with 21 ARGB roles per
  state, and are not affected by the GTK sheets.

Ownership is reversible. The canonical file, the managed import and an
`*-ownership.json` record change together, and Light removes the import and
restores the previous content instead of writing a Light GTK asset.

Growing this coverage to plain GTK 3 and non-Adw GTK 4 would require explicit
widget rules in `gtk-dark.css`. That is a visible design change, not a
documentation gap.

## Quality gates

Use the [Dark state validation reference](dark-theme-validation.md) for cross-application checks, repeatable capture scenarios and limits of generated-color evidence.

- WCAG 2.2: body text ≥ 4.5:1 (main text ≥ 7:1)
- APCA: body Lc ≥ 75 light / ≥ 50 dark; `on_accent` Lc ≥ 54 on filled accent
- CI validates **both** light and dark Kitty, Starship, Ghostty, Waybar, Hypr, Rofi, Btop, Dunst, Fzf

## Design decisions

- **brand alias** = indigo `#6366F1`; the runtime `accent` is a lighter accessible role where filled controls must pass the existing WCAG/APCA gates
- **focus** = blue `#3B82F6`, kept distinct from brand and diagnostic colors
- **border aliases** = `#12121A` (subtle) and `#1F1F2B` (medium); significant runtime borders remain brighter because the non-text contrast gate is not weakened
- **generated CSS** = [`dreamcoder-dark.css`](../../DreamcoderThemes/dreamcoder/dreamcoder-dark.css), sourced only from `tokens.json`
- **stable Dark identifiers** = `dreamcoder-dark.css` and `:root[data-theme="dark"]`; OLED compatibility naming is retired, and OLED behavior remains a surface policy of Dreamcoder Dark rather than a separate mode
- **adaptive/matugen** may tint surfaces but identity tokens win per `CLAUDE.md`

## Adding new targets

Follow the renderer and testing workflow in [Contributing](../../CONTRIBUTING.md), under “Add or change a theme renderer”. Review target-specific output and application behavior separately from generation.
