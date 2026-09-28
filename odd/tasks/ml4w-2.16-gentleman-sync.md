# ML4W 2.16 + Gentleman.Dots sync

## Objective

Keep the Dreamcoder design system layered correctly on top of ML4W 2.16 and the
latest Gentleman.Dots `main`, so upstream upgrades no longer erase Dreamcoder hooks.

## Problem

- The user upgraded ML4W to 2.16 (upstream `3960570`); the repo pins `46f2ca7`.
- 2.16 moved the Quickshell overview to `~/.local/share/quickshell-overview`, dropped
  waypaper from its install set, and added new keybinds.
- The ML4W upgrade rewrote ML4W-owned files, so Dreamcoder hooks injected into them
  (`ml4w-wallpaper` block, `require('dreamcoder-colors')` in `hyprland.lua`) are gone.
- Gentleman.Dots `main` advanced to `6f44b79` (nvim clipboard over SSH); the pin is `0258450`.

## Why

Dreamcoder must survive upstream upgrades: its hooks should live in files ML4W never
ships (`custom.lua`, `keybindings/dreamcoder.lua`, Dreamcoder scripts), not in lines
injected into ML4W-owned files.

## Scope

- In: `ml4w_assets/hypr/conf/keybindings/dreamcoder.lua`, `scripts/apply-ml4w-hooks.sh`,
  `scripts/generate-custom-lua.sh`, doctor/verify checks, `tests/ml4w/*`,
  `docs/upstream-manifest.json`, `docs/configuration/ml4w.md`.
- Out: unrelated working-tree edits already present on `main` (fish prompt, warp,
  apply-system-mode, bun completions) — never staged in this feature.

## Constraints

- Colors only from `DreamcoderThemes/dreamcoder/tokens.json`.
- Idempotent scripts; no secrets.
- TDD: off (no project/session TDD configuration found). Source: none. Runners:
  `bats tests/ml4w/`, `python -m pytest tests/`.

## Tasks

- [x] T1 — Keybindings: point SUPER+Tab at `~/.local/share/quickshell-overview`
  (fallback to the legacy path only if the new one is missing) and port the 2.16
  upstream keybind additions (ALT+B statusbar autohide, ALT+D dock autohide,
  SHIFT+D reload dock, AZERTY detection) into `dreamcoder.lua`. Route: delegated writer.
  - Evidence: commit `f7c2b9b` (`fix(ml4w): align the Dreamcoder keybind variant with ML4W 2.16`);
    `bats tests/ml4w/keybindings_variant.bats` 4/4, `luac -p` ok.
  - Rationale: mirrors upstream 2.16 exactly (no legacy fallback, a clean 2.16 install
    has no `~/.config/quickshell/overview`); Reload Dock left unbound because SHIFT+D is
    the profile theme toggle; AZERTY keysyms bound only on AZERTY (profile owns digits).
    Pre-existing SUPER+SHIFT+arrows overlap (variant resize vs profile move) allowlisted
    in the collision test, pending a product decision.
- [x] T2 — Upgrade-proof hooks: load `dreamcoder-colors` from `custom.lua` instead of
  relying on an injected line in ML4W's `hyprland.lua`; update doctor to accept it.
  Make the wallpaper hook idempotent, re-appliable after ML4W upgrades, with waypaper
  optional; update bats fixtures to the 2.16 layout. Route: delegated writer.
  - Evidence: commit `2ebb433` (`fix(ml4w): make Dreamcoder hooks survive ML4W upgrades`);
    `bats tests/ml4w/` 85/85 ok; `python -m pytest tests/ -q` exit 0; shellcheck clean.
  - Rationale: runner hook is a marked block replaced on each run (byte-identical on
    re-run, migrates the old unmarked block, keeps symlinks); waypaper only when its
    config exists. `custom.lua` now loads `dreamcoder-colors` (guarded) and doctor
    prefers it. colors.lua/colors.conf checks accept managed regular files whose bytes
    match a DreamcoderThemes `hypr-colors-*` variant: the sync writer writes through the
    path and `_flip_bridge_symlinks` only flips existing symlinks, and the live 2.16
    files are regular and byte-identical to `hypr-colors-dark.*`.
  - Caveat: `custom.lua` is required after ML4W's `conf.*`, so the late
    `dreamcoder-colors` require only re-defines colour globals; borders get Dreamcoder
    colours because the sync writes `colors.lua` itself. Live
    `~/.config/hypr/hypr-colors-*.lua` (the `dreamcoder-colors.lua` targets) are stale
    (Sep 10, older palette) — refresh in T4.
- [x] T3 — Pins and docs: bump `docs/upstream-manifest.json` (ML4W `3960570` / tag 2.16,
  Gentleman.Dots `6f44b79`), update `docs/configuration/ml4w.md`. Route: delegated writer.
  - Evidence: commit `chore(upstream): pin ML4W 2.16 and Gentleman.Dots 6f44b79`;
    `git ls-remote` (2026-09-28): ML4W `HEAD` and `refs/tags/2.16` (lightweight) =
    `3960570`, Gentleman.Dots `main` = `6f44b79`; `upstream-diff.py --check-pins` both
    current; `verify-repo-sync.py` ok; markdown links ok.
  - Rationale: the manifest schema forbids extra upstream keys, so the tag is recorded
    in `provenance.method` and `docs/sources.md`. `docs/sources.md` and the
    `test_verify_repo_sync.py` fixture must track the pins (docs-consistency check).
    `docs/configuration/ml4w.md` documents the 2.16 keybind delta and the
    "hooks live in Dreamcoder-owned files" rule; `docs/installation/linux.md` now
    checks `custom.lua` for the loader. `docs/migration/*` had no stale references.
- [x] T4 — Apply to the live system and verify (`./scripts/dreamcoder sync`, hooks
  re-applied, doctor/verify clean). Route: inline.
  - Evidence: backup at `~/.config/hypr/.dreamcoder-backup-20260928`; refreshed
    `hypr-colors-*`; `setup-hyprland.sh --profile asus-vivobook15` (custom.lua loader,
    dreamcoder.lua, marked wallpaper hook); `dreamcoder sync` rewrote hypr colors;
    `verify-ml4w-setup.sh` 20 passed / 0 failed; `dreamcoder doctor` guardrails passed;
    `hyprctl configerrors` empty; SUPER+Tab → `~/.local/share/quickshell-overview`.
  - Fixes found while applying: `61a1ec8` dispatcher exported PYTHONPATH only for
    CONTROL routes (`dreamcoder sync` raised ModuleNotFoundError); `e715d09` verify
    required a symlink for the sync-rendered `waybar/colors.css`.
  - Pre-existing, out of scope: `tests/shell/test_apply_theme.bats` "kanagawa bridge
    carries night-derived colors" also fails on clean `main`.

## Acceptance criteria

- `bats tests/ml4w/` and `python -m pytest tests/` pass.
- Re-running the ML4W hook application after an ML4W upgrade restores every Dreamcoder
  hook without duplication.
- SUPER+Tab works on a clean ML4W 2.16 install.

## Progress

- Baseline (2026-09-28): bats 66/66 ok, pytest green.
- `~/Gentleman.Dots` moved from detached `1c3dcb3` (origin/nix-migration) to `main` @ `6f44b79`.
- Branch: `chore/ml4w-2.16-gentleman-sync`.

## Next step

Feature complete. Pending user decisions: SUPER+SHIFT+arrows overlap (resize vs
move), the pre-existing kanagawa bridge test, push/PR of the branch.
