# Tasks: Implement Herdr Dreamcoder Themes

The work is split into two separately reviewable slices because the first apply attempt exceeded the 400-line review budget. A Git commit boundary is REQUIRED between Slice 1 and Slice 2; do not combine them into one review or commit. Preserve existing user-owned WIP.

## Review Workload Forecast — Slice 1: Static renderer and checked-in variants

| Field                   | Value                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| Estimated changed lines | 90–180 authored lines                                                                      |
| 400-line budget risk    | Low                                                                                        |
| Chained PRs recommended | No                                                                                         |
| Suggested split         | Slice 1 only: renderer, checked-in variants, focused generation tests, scoped verification |
| Delivery strategy       | single-pr                                                                                  |
| Chain strategy          | pending                                                                                    |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### RED

- [x] Extend `tests/test_herdr_theme_generation.py` to require exactly `dark` and `light`, reject `dusk` and arbitrary modes, parse valid TOML, enforce LF endings and one trailing newline, and assert byte-stable output. <!-- sdd-owner: implementation -->
- [x] Assert that palette differences are confined to `[theme]` and `[theme.custom]`; require byte-identical canonical upstream `[ui]` and `[keys]` values: `accent = "#6FA0AF"`, `prefix = "ctrl+a"`, `previous_agent = "prefix+alt+k"`, `next_agent = "prefix+alt+j"`, and `focus_agent = "prefix+ctrl+1..9"`; reject `window-title`, `tab-title`, and `dusk`. <!-- sdd-owner: implementation -->

### GREEN

- [x] Update only `src/dreamcoder_theme/renderers_herdr.py` as a pure Light/Dark renderer with fixed section/field order `[theme]`, `[theme.custom]`, `[ui]`, `[keys]`, canonical upstream constants, deterministic UTF-8/LF output, and exactly one trailing newline. <!-- sdd-owner: implementation -->
- [x] Regenerate only `DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3/config.dark.toml` and `DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3/config.light.toml`; add no active or third variant. <!-- sdd-owner: implementation -->

### TRIANGULATE

- [x] Run `python -m pytest tests/test_herdr_theme_generation.py -v` and `ruff check src/dreamcoder_theme/renderers_herdr.py tests/test_herdr_theme_generation.py`; run `PYTHONPATH=src python scripts/verify-theme-health.py` and record the known baseline failure on unchanged `.opencode/themes/dreamcoder.json` when present, proving the failure is attributable only to that unrelated artifact and that no scoped or protected files changed; do not repair the artifact. <!-- sdd-owner: implementation -->

### REFACTOR

- [x] Keep canonical `[ui]`/`[keys]` values independent of palette tokens and preserve repository-only sync behavior; document ownership boundaries beside `src/dreamcoder_theme/renderers_herdr.py` only if needed. <!-- sdd-owner: implementation -->

### Slice 1 boundary

- [x] Verify the diff contains only Slice 1 paths, focused acceptance criteria pass, and authored changes remain below 400 lines; rollback only this slice without changing unrelated WIP. <!-- sdd-owner: implementation -->
- [ ] Create the required Git commit boundary for Slice 1 before beginning Slice 2; do not amend or include Slice 2 changes. <!-- sdd-owner: parent -->

## Review Workload Forecast — Slice 2: Exact-version activation transaction

| Field                   | Value                                                                       |
| ----------------------- | --------------------------------------------------------------------------- |
| Estimated changed lines | 300–390 authored lines                                                      |
| 400-line budget risk    | Low                                                                         |
| Chained PRs recommended | No                                                                          |
| Suggested split         | Slice 2 only: activation module, safety/recovery tests, scoped verification |
| Delivery strategy       | single-pr                                                                   |
| Chain strategy          | pending                                                                     |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### RED

- [x] Add `tests/test_herdr_activation.py` with temporary directories and a fake `herdr` executable covering exact `herdr 0.7.3` gating, missing/non-zero/timeout/malformed/extra/other-version output, proving failures precede backup, staging, directory creation, or target mutation. <!-- sdd-owner: implementation -->
- [x] Test `HERDR_CONFIG_PATH` precedence, XDG fallback via `XDG_CONFIG_HOME` and `HOME`, rejection of empty/relative/root/NUL paths, target directory/symlink, symlinked parent, unsafe source, and unsupported mode. <!-- sdd-owner: implementation -->
- [x] Test existing and absent targets, exclusive sibling backup before mutation, restrictive staging, byte-exact atomic replacement, fsync/write/replace failures, target identity changes, cleanup, and write confinement to the target directory. <!-- sdd-owner: implementation -->
- [x] Test reload omission and exact `herdr server reload-config` argv after replacement, bounded reload failures, atomic restoration from retained backup, safe removal of a newly created target, and explicit `restore-failed` reporting with backup path. <!-- sdd-owner: implementation -->

### GREEN

- [x] Implement `src/dreamcoder_theme/herdr_activation.py` with typed `ActivationResult`, explicit `activate_herdr(mode: Literal["dark", "light"], reload_requested: bool)`, checked-in 0.7.3 source validation, exact version gating, and actionable content-free errors. <!-- sdd-owner: implementation -->
- [x] Implement pure safe target resolution in `src/dreamcoder_theme/herdr_activation.py`: non-empty override first, then `${XDG_CONFIG_HOME}/herdr/config.toml`, then `${HOME}/.config/herdr/config.toml`; reject unsafe paths and create only missing XDG-derived parents after non-filesystem preconditions pass. <!-- sdd-owner: implementation -->
- [x] Implement same-directory exclusive backup/staging, flush plus `fsync`, identity recheck, atomic `os.replace`, parent-directory `fsync`, optional bounded reload, one restoration transaction, and truthful statuses and reload/restoration fields. <!-- sdd-owner: implementation -->
- [x] Keep activation explicit and disabled from automatic switching; if a CLI is needed, expose only the bounded mode and `--reload` boundary inside `src/dreamcoder_theme/herdr_activation.py`, with no new framework or entry point. <!-- sdd-owner: implementation -->

### TRIANGULATE

- [x] Run `python -m pytest tests/test_herdr_theme_generation.py tests/test_herdr_activation.py -v`, `ruff check src/dreamcoder_theme/renderers_herdr.py src/dreamcoder_theme/herdr_activation.py tests/test_herdr_theme_generation.py tests/test_herdr_activation.py`, and `python scripts/verify-theme-health.py`; confirm focused tests never access the real home directory. <!-- sdd-owner: implementation -->

### REFACTOR

- [x] Review only the Slice 2 diff against `specs/herdr/spec.md` and `design.md`; remove convenience scope or duplication needed to remain below 400 authored changed lines without weakening exact gating, upstream parity, backup, atomicity, reload, rollback, or fail-closed behavior. <!-- sdd-owner: implementation -->

### Slice 2 boundary

- [x] Verify only Slice 2 paths, focused acceptance criteria, named commands, and protected paths; rollback only Slice 2 without changing Slice 1 or unrelated WIP. The under-400-line budget was NOT met (see apply-progress: 497 + 782 authored lines); a `size:exception` decision is requested rather than trimming fault-injection coverage. <!-- sdd-owner: implementation -->

## Parent-owned lifecycle actions

- [ ] Start or reuse the bounded native review for each slice after implementation and validate its receipt at the applicable lifecycle gate; never bypass a review lock. <!-- sdd-owner: parent -->

## Protected paths and explicit non-goals

The implementation MUST NOT modify:

- `openspec/changes/repair-dreamcoder-theme-rollout/` or any artifact within it.
- `DreamcoderGhostty/`, `src/dreamcoder_theme/renderers_ghostty_warp.py`, or Ghostty writer/repair behavior.
- `themes/dreamcoder/tokens.json`, generated palette tokens, token values, or WCAG/APCA validation rules.
- Fish startup, shell scripts, schedulers, automatic mode selection, Hyprland, unrelated renderers, or unrelated user-owned targets.
- Any proposal, spec, or design artifact for this change, or any artifact belonging to another OpenSpec change.

Do not support versions other than exactly `herdr 0.7.3`; do not add `dusk`, migration/merge/adoption/repair frameworks, process discovery, undocumented reload behavior, palette-driven `[ui]`/`[keys]` values, or writes outside the resolved Herdr target and its directly associated sibling backup/staging files.
