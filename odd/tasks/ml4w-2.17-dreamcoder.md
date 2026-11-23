# ML4W 2.17 Dreamcoder integration

Objective: move Dreamcoder Workbench's ML4W overlay from tag 2.16.1 to tag 2.17 without touching the live desktop. Branch: at rest on `chore/herdr-drop-changes-panel` (no branch created, nothing committed); delivery: ask-on-risk; runners: bats, pytest, `scripts/validate-markdown-links.py`.

## Specs

- S1: User request, verbatim: "hey bro actualiza ml4w".
- S2: Scope decision, chosen by the user: "Repositorio primero (recomendado)" — "Actualizar y probar Dreamcoder Workbench contra ML4W estable; retirar solo lo demostrado obsoleto, sin tocar tu instalación activa." The live `~/.mydotfiles/com.ml4w.dotfiles` copy is NOT modified.
- S3: Upstream base is ML4W tag `2.17`, commit `9ead14e78a9bff5f1ae7df3aec7a775730cf4431`, resolved with `git ls-remote https://github.com/mylinuxforwork/dotfiles.git 'refs/tags/2.17*'` (no peeled ref). `dotfiles/.config/ml4w/version.json` at that tag reads `"Version": "2.17"`.
- S4: The curated keybinding variant `ml4w_assets/hypr/conf/keybindings/dreamcoder.lua` tracks upstream `default.lua` at 2.17 minus the binds the machine profile owns. The 2.17 additions must be ported:
  - `SUPER + W` opens the wallpaper carousel (`ml4w-wallpaper-app --carousel`).
  - `ALT + Tab` / `ALT + SHIFT + Tab` drive the Hypr App Switcher (`qs -p ~/.local/share/hypr-app-switcher ipc call app-switcher next|prev`).
  - The workspace scroll binds use 2.17's 200 ms throttle with `binds.pass_mouse_when_bound = false` and `binds.scroll_event_delay = 1`.
- S5: The wallpaper hook stays re-appliable against the 2.17 runner. At 2.17 the cache file is written only when theming is not skipped, and the runner accepts `--transition TYPE`.
- S6: The pin and the docs name 2.17: `docs/upstream-manifest.json`, `docs/sources.md`, `docs/configuration/ml4w.md`, and the fixture set the bats tests load.
- S7: No live desktop mutation. `~/.config/hypr`, `~/.config/waybar` and `~/.mydotfiles` stay untouched; the overlay is generated and tested only.

## Tasks

| ID | Spec | Route | Status | Evidence |
| --- | --- | --- | --- | --- |
| T1 | S4 | inline | done | `ml4w_assets/hypr/conf/keybindings/dreamcoder.lua`: `SUPER + W`, app switcher, 200 ms scroll throttle; `luac -p` ok |
| T2 | S4, S7 | inline | done | `tests/ml4w/keybindings_variant.bats`: 11/11; `tests/fixtures/ml4w/capture-keybindings.lua` gains `hl.config`/`hl.dispatch`/`hl.timer` |
| T3 | S5, S6 | inline | done | fixtures at 2.17 (`ml4w-wallpaper`, `gtk-theme-switcher`, `matugen-config`); `apply_ml4w_hooks.bats`: 39/39 |
| T4 | S3, S6 | inline | done | `docs/upstream-manifest.json` + `docs/sources.md` pin `9ead14e` |
| T5 | S6 | inline | done | `docs/configuration/ml4w.md` 2.17 sections and fixture list |
| T6 | S3, S7 | inline | done | `bats tests/ml4w/` 144/144; pytest 1136 + 72 subtests; links exit 0; `verify-repo-sync` OK |

### Verification

- `bats tests/ml4w/` → 144 ok, 0 failures.
- `python3 -m pytest` → 1136 tests, 72 subtests, exit 0.
- `python3 scripts/validate-markdown-links.py` → exit 0.
- `PYTHONPATH=src python3 scripts/verify-repo-sync.py` → OK (manifest schema, pins, docs consistency).
- `luac -p ml4w_assets/hypr/conf/keybindings/dreamcoder.lua` → ok.
- Live desktop untouched: no write to `~/.config/hypr`, `~/.config/waybar`, or `~/.mydotfiles`.

## Log

- L1: "hey bro actualiza ml4w"
- L2: Scope answer: "Repositorio primero (recomendado)".
- L3: Evidence — upstream latest release is `2.17` (published 2026-11-04). Local `~/.mydotfiles/com.ml4w.dotfiles` is not a git checkout (no remote, no tags, no history), so no `git pull` path exists; the only local marker is `config.dotinst.backup-2.13.0`.
- L4: Evidence — 2.16.1 → 2.17 touches 39 files. Relevant to this overlay: `hypr/conf/keybindings/default.lua`, `hypr/conf/ml4w.lua`, `hypr/hyprland.lua`, `waybar/modules.json`, `ml4w/scripts/ml4w-wallpaper`, `ml4w/scripts/ml4w-autostart`, `ml4w/version.json`, new `ml4w/scripts/ml4w-window-mode`.
- L5: Evidence — `hyprland.lua` at 2.17 loads `require("hyprland-gui")` before `custom.lua`, so `custom.lua` now overrides HyprMod. The overlay already generates `custom.lua`; ordering now favours it.
- L6: Evidence — fixture files are verbatim upstream with trailing whitespace trimmed. `gtk-theme-switcher.sh` and `matugen/config.toml` are byte-identical between 2.16.1 and 2.17, but the copies in the repo were from tag 2.16 and had already drifted (they lacked `hyprtoolkit`, `walker`, and `ml4w_powermenu` templates), so all three fixtures were refreshed to 2.17.
- L7: T1/T2 — ported `SUPER + W` → `ml4w-wallpaper-app --carousel`, `ALT + Tab`/`ALT + SHIFT + Tab` → `hypr-app-switcher`, and the 200 ms `throttled_scroll` with `binds.pass_mouse_when_bound = false` / `binds.scroll_event_delay = 1`. The recording stub gained no-op `hl.config`, `hl.dispatch`, and `hl.timer` so the variant loads under `lua`.
- L8: T3 — the 2.17 runner moves the `current_wallpaper` cache write inside the theming branch and accepts `--transition TYPE`; the hook writes that same cache itself, so `--skip-theming` still leaves it current. A new test pins the moved cache write and the new option so `strip_runner_hook` cannot eat them.
- L9: T4/T5 — `git ls-remote` returned `9ead14e78a9bff5f1ae7df3aec7a775730cf4431` for tag `2.17` (no peeled ref); release page returns 200. `version.json` at that tag reads `"Version": "2.17"`. Manifest, sources, and configuration docs repinned; the two 2.16.1 rows in the tracking table stay because they describe entry points introduced at that tag.
- L10: T6 — `bats tests/ml4w/` 144/144; pytest 1136 + 72 subtests; link validator exit 0; `verify-repo-sync` OK.
- L11: Scope check — `~/.mydotfiles/com.ml4w.dotfiles` was not modified; no write reached `~/.config/hypr` or `~/.config/waybar`.
- L12: Delivery — nothing committed; the user did not ask for a commit.
- L13: Final alignment — test names that described upstream-2.16-era binds lost the version prefix (`standalone power menu`, `autohide toggles`), and `apply-ml4w-hooks.sh`'s header/waypaper message now say 2.17. Re-run: bats 144/144, links 0, sync OK. Live `~/.config/hypr/custom.lua` mtime is 2026-11-02 and `~/.config/hypr/conf/keybindings/dreamcoder.lua` is 2026-09-28, so no write reached them.
