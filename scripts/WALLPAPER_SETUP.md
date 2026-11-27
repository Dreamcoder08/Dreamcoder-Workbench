# Wallpaper and palette setup

Applying a wallpaper re-themes Dreamcoder Workbench from it. The palette is **adaptive**: the active mode's tokens stay the base, and the wallpaper can tint the result. Identity tokens win where the guardrails require it.

## Quick path

```bash
./scripts/set-wallpaper.sh /path/to/wallpaper.png
```

The canonical set lives in `DreamcoderWallpapers/dreamcoder-light-*.png` and `dreamcoder-dark-*.png`. Its limits and finishing pipeline are defined in the [wallpaper contract](../docs/DREAMCODER_DESIGN_SYSTEM.md#wallpaper-contract) of the design-system page; this file does not repeat them.

## What happens

```text
set-wallpaper.sh   paints with swww, or hyprpaper through hyprctl
  → wallpaper-hook.sh   records the wallpaper for ML4W and a stable cache path, reloads hyprpaper
    → theme-auto.sh     picks light or dark from the clock (07:00-18:00 light by default)
      → apply-theme-mode.sh   syncs the theme from the wallpaper (Matugen, adaptive palette)
```

| Script | Role |
| --- | --- |
| `scripts/set-wallpaper.sh` | Entry point; normalizes the path, paints the wallpaper, then calls the hook |
| `scripts/wallpaper-hook.sh` | Writes the ML4W current-wallpaper record and the `~/.cache/dreamcoder/wallpaper.*` link, refreshes hyprpaper, calls `theme-auto.sh` |
| `scripts/theme-auto.sh` | Chooses the mode by hour (`DREAMCODER_LIGHT_START`, `DREAMCODER_DARK_START`) |
| `scripts/apply-theme-mode.sh` | Applies the mode with the wallpaper passed as `DREAMCODER_WALLPAPER`; runs Matugen when it is installed in a GUI session |

To apply the theme without changing the wallpaper, see [Choose a mode or regenerate](../docs/configuration/theme-system.md#choose-a-mode-or-regenerate).

## Hooking ML4W

`scripts/apply-ml4w-hooks.sh` (re)installs `wallpaper-hook.sh` into ML4W's wallpaper runner (`~/.config/ml4w/scripts/ml4w-wallpaper`, which receives the image as `$IMAGE_PATH`). ML4W upgrades overwrite the runner, so re-run it after every ML4W update. Its header documents the override variables.

## Reload behavior

Kitty reloads with `pkill -SIGUSR1 kitty`. Ghostty has no signal reload: use `reload_config` (`Ctrl + Shift + R`).

## Check a wallpaper before using it

```bash
scripts/check-wallpaper.py --mode light FILE.png
```

`make theme-check` runs the same check over `DreamcoderWallpapers/dreamcoder-light-*.png` and `dreamcoder-dark-*.png`.
