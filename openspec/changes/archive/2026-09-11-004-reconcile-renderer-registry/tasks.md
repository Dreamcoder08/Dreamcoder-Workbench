# Tasks: Reconcile renderer_registry.py With Actual sync.py Behavior

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~380-450 authored across 4 slices (largest: Slice B ~150-180 lines across 2 contract fields + ~21 registration edits + 2 threading rules; smallest: Slice C ~40 lines) |
| 400-line budget risk | High for the whole change if shipped as one PR; Low per individual slice |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Slice A) → PR 2 (Slice C) → PR 3 (Slice B) → PR 4 (Slice D) |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main (defaulted — small sequential slices, no long-lived feature branch in this personal repo; orchestrator to confirm with user before sdd-apply) |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| A | Fix `codex_app` renderer + `hypr_colors_lua`/`hypr_colors_conf` ownership fields | PR 1 | `python -m pytest tests/test_renderer_registry.py -v` | N/A — declarative data only, no process | Revert edits to `renderers_codex.py`/`renderers_hypr_waybar_rofi.py`; registry-only |
| C | Herdr dynamic profile binding + drift-guard test | PR 2 | `python -m pytest tests/test_herdr_contract.py -v` | N/A — declarative data only | Revert `renderers_herdr.py`/`herdr_contract.py` label computation |
| B | New `ActiveStrategy`/`MutationStrategy` variants, threading, 21-consumer mutation sweep | PR 3 | `python -m pytest tests/test_renderer_registry.py tests/test_herdr_contract.py -v` | N/A — declarative data only | Revert enum additions + per-consumer `mutation=` edits; `validate_registry()` catches drift |
| D | Zellij dark/light real generation (sync.py exception) | PR 4 | `python -m pytest tests/ -k zellij -v` | `./scripts/dreamcoder sync` then diff `DreamcoderZellij/.config/zellij/dreamcoder-{dark,light}.kdl` against `zellij_content()` output | Revert the two new `write_active_repo_file` calls in `sync_repo_snippets()`; `.kdl` files return to prior (stale) content, no deletion either way |

## Slice A — Straightforward registration fixes (PR 1)

- [x] A.1 In `src/dreamcoder_theme/renderers_codex.py`, change the `codex_app` registration's `renderer` from `codex_tmtheme_content` to `opencode_content` (import from `.renderers_opencode`); keep `output_kind="active-and-repository"`, `active=RESOLVED_ACTIVE_PATH`, `repository=MODE_VARIANTS` unchanged. <!-- sdd-owner: implementation --> **DONE as written.**
- [x] A.2 In `src/dreamcoder_theme/renderers_hypr_waybar_rofi.py`, fix `hypr_colors_lua` and `hypr_colors_conf`. <!-- sdd-owner: implementation --> **DEVIATED from this task's literal text — see "Slice A resolution note" below: re-verification against live `sync.py` (not just `sync_repo_snippets()`) found a real, wired-into-`main()` active output for both consumers via `sync_active_targets()` → `write_if_changed(paths.hypr_colors_lua/_conf, ...)`, which this task's own "no active_path exists for them" rationale did not account for. Implemented `output_kind="active-and-repository"`, `active=ActiveStrategy.RESOLVED_ACTIVE_PATH` (unchanged), `repository=RepositoryStrategy.MODE_VARIANTS`, `mutation=MutationStrategy.WRITE_IF_CHANGED` — matching `design.md`'s File Changes table, not this task's `output_kind="repository"`/`NO_ACTIVE_OUTPUT`/`REPOSITORY_VARIANT_WRITER` text. No new enum members used either way.
- [x] A.3 Update/add assertions in `tests/test_renderer_registry.py` for `codex_app.renderer is opencode_content` and `hypr_colors_lua`/`hypr_colors_conf`. <!-- sdd-owner: implementation --> Added `TestSliceARegistrationFixes` asserting the resolution actually implemented (`output_kind == "active-and-repository"`, `active == RESOLVED_ACTIVE_PATH`, `repository == MODE_VARIANTS`, `mutation == WRITE_IF_CHANGED`), not the task's original `output_kind == "repository"` text — see deviation note on A.2.
- [x] A.4 Run `python -m pytest tests/test_renderer_registry.py -v` and confirm `validate_registry()` still returns `[]`. <!-- sdd-owner: implementation --> 20/20 passed; `validate_registry(REGISTRATIONS) == []` confirmed by `test_full_registry_still_validates_clean_after_slice_a_fixes` and `TestExpectedSet`.

### Slice A resolution note (apply-time deviation, needs a spec-phase decision)

`spec.md`'s "hypr_colors_lua/conf declare repository-only output" Requirement and this task's A.2 text both reason **only** about `sync_repo_snippets()` (correctly: it calls `write_variant_files()` for both, never `write_active_repo_file()`). Neither considers `sync_active_targets()`, which is wired into `main()`/`cli_handlers.py` and does `write_if_changed(paths.hypr_colors_lua, hypr_colors_lua_content(active))` / same for `hypr_colors_conf` — a genuine live active-mode-tracking output (`~/.config/hypr/colors.lua` / `.conf`, resolved from `settings.py`'s `config_home / "hypr/colors.lua"`), structurally identical in shape to `hyprland`'s own `paths.hyprland` active write. Per the proposal's own governing principle ("a validation layer that asserts false things about production is actively harmful"), Slice A implements the registration that matches full live `sync.py` behavior (`design.md`'s row) rather than the narrower `sync_repo_snippets()`-only reading in `spec.md`/this task. **`spec.md`'s Requirement and Scenario for this consumer WERE corrected (see `apply-progress.md` "Post-apply reconciliation")** — they currently assert `output_kind == "repository"` and `active != RESOLVED_ACTIVE_PATH`, which the implemented (and tested) registration does not satisfy.

## Slice C — Herdr documentation fix (PR 2)

- [x] C.1 In `src/dreamcoder_theme/renderers_herdr.py`, bind the `herdr` registration's `renderer` dynamically via `next(p for p in SUPPORTED_PROFILES if p and p.is_complete)` instead of the hardcoded `HERDR_073_PROFILE`. <!-- sdd-owner: implementation --> **DONE as written.**
- [x] C.2 Compute `summary_label` from `SUPPORTED_PROFILES` at import time (replace the static string) and add a code comment marking this the one intentional single-entry-per-consumer exception, with `sync_herdr_repo_variants()` named as ground truth. <!-- sdd-owner: implementation --> **DONE as written.**
- [x] C.3 Add a drift-guard test in `tests/test_herdr_contract.py` asserting the computed `summary_label` matches live `SUPPORTED_PROFILES`. <!-- sdd-owner: implementation --> **DONE as written.**
- [x] C.4 Run `python -m pytest tests/test_herdr_contract.py -v`. <!-- sdd-owner: implementation --> **22/22 passed.**

### Slice C resolution note (apply-time deviation)

`design.md`'s File Changes table lists `herdr_contract.py` as modified, but
live code shows `SUPPORTED_PROFILES` already declares all three complete
profiles and remains the authoritative contract used by
`sync_herdr_repo_variants()`. Slice C therefore changes only
`renderers_herdr.py` and its drift-guard test: changing the contract module
would add no behavior or accuracy. This is a precise scope reduction, not a
model change; `HERDR_073_PROFILE` remains exported for its existing callers.

## Slice B — New enum variants + threading + mutation sweep (PR 3)

- [x] B.1 In `src/dreamcoder_theme/renderer_contract.py`, add `ActiveStrategy.PINNED_ACTIVE_PATH = "pinned_active_path"` and `MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE = "symlink_safe_active_write"`. <!-- sdd-owner: implementation -->
- [x] B.2 In `src/dreamcoder_theme/renderer_registry.py`, add `PINNED_ACTIVE_PATH` to `_OWNERSHIP_RULES["active"]` and `["active-and-repository"]` allowed-active sets (not `"repository"`). <!-- sdd-owner: implementation -->
- [x] B.3 In `_check_strategy_compatibility`, reject `SYMLINK_SAFE_ACTIVE_WRITE` only for `output_kind == "repository"`; it is valid for active and active-and-repository output. <!-- sdd-owner: implementation; corrected against live sync.py -->
- [x] B.4 In `src/dreamcoder_theme/renderers_antigravity.py`, set `active=ActiveStrategy.PINNED_ACTIVE_PATH`, `mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE`. <!-- sdd-owner: implementation -->
- [x] B.5 Set `mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE` on these 20 registrations, verified against live `write_active_repo_file()` call sites in `sync.py`'s `sync_repo_snippets()`: `codex_app`, `codex_theme`, `bat_theme`, `pi_theme` (`renderers_codex.py`, `renderers_pi.py`); `kitty_ui` (`renderers_kitty.py`); `opencode` (`renderers_opencode.py`); `hyprland`, `waybar`, `rofi` (`renderers_hypr_waybar_rofi.py`); `zsh_syntax`, `ls_colors`, `fzf` (`renderers_extra_shell.py`); `bat`, `delta` (`renderers_extra_bat_delta.py`); `btop` (`renderers_extra_btop.py`); `dunst`, `cava` (`renderers_extra_notify.py`); `firefox` (`renderers_extra_firefox.py`); `obsidian` (`renderers_extra_obsidian.py`); `lazygit` (`renderers_lazygit.py`). Together with B.4's `antigravity` registration, the symlink-safe set totals exactly 21 consumers. <!-- sdd-owner: implementation -->
- [x] B.6 Do NOT touch `kitty`, `tmux`, `starship`, or `nvim` — verified via live code read that these never route through `write_active_repo_file()` (only plain `write_if_changed` on live paths or pure variant files); they correctly keep `WRITE_IF_CHANGED`. `zellij` also stays `PROFILE_AWARE_SELECTOR` per `design.md`'s accepted model-gap decision. <!-- sdd-owner: implementation -->
- [x] B.7 Add/update `tests/test_renderer_registry.py` cases: `PINNED_ACTIVE_PATH` accepted for `active`/`active-and-repository` and rejected for `repository`; `SYMLINK_SAFE_ACTIVE_WRITE` accepted for active/active-and-repository and rejected for repository; the 21-consumer set from B.5 asserted `!= WRITE_IF_CHANGED`; `kitty`/`tmux`/`starship`/`nvim` asserted `== WRITE_IF_CHANGED`. <!-- sdd-owner: implementation; corrected against live sync.py -->
- [x] B.8 Run `python -m pytest tests/test_renderer_registry.py tests/test_herdr_contract.py -v` and confirm `validate_registry()` returns `[]` for the full 33-consumer registry. <!-- sdd-owner: implementation -->

### Slice B deviation correction

Live `sync.py` writes OpenCode's live path and one unsuffixed repository mirror
with `write_active_repo_file()` but emits no mode variants. Its registration is
therefore active-only (`RESOLVED_ACTIVE_PATH` / `NO_VARIANTS` /
`SYMLINK_SAFE_ACTIVE_WRITE`). The helper protects the repository-tracked active
mirror, so that mutation strategy is valid for active and active-and-repository
outputs and invalid for repository-only output.

## Slice D — Zellij real generation (PR 4, scope exception)

- [x] D.1 In `src/dreamcoder_theme/sync.py`'s `sync_repo_snippets()`, add two `write_active_repo_file()` calls mirroring the existing Night call: `dreamcoder-dark.kdl` from `zellij_content(variants["dark"], "dreamcoder-dark")` and `dreamcoder-light.kdl` from `zellij_content(variants["light"], "dreamcoder-light")`, both under `DreamcoderZellij/.config/zellij/`. No file deletion. <!-- sdd-owner: implementation --> **DONE as written.**
- [x] D.2 Run `./scripts/dreamcoder sync` and confirm `DreamcoderZellij/.config/zellij/dreamcoder-dark.kdl` and `dreamcoder-light.kdl` regenerate with current canonical tokens (`bg #000000` for dark), replacing the stale `bg "#100f0d"` content. <!-- sdd-owner: implementation --> **DONE with a scoped fallback:** the requested command was attempted and exited 1 before writes because `dreamcoder_theme` was unavailable without `PYTHONPATH=src`; a direct canonical `zellij_content()` invocation regenerated only the two allowed `.kdl` files, and an exact parity assertion confirmed both outputs (including dark `bg "#000000"`).
- [x] D.3 Add a parity test asserting generated dark/light `.kdl` content equals `zellij_content(variants[mode], "dreamcoder-{mode}")` output exactly. <!-- sdd-owner: implementation --> **DONE as written** with temporary `sync.ROOT` redirection and an empty `VARIANT_REGISTRY`, so the test writes only to its temporary root.
- [x] D.4 Run `python -m pytest tests/ -v` (full suite) and `python scripts/verify-theme-health.py` to confirm no regression. <!-- sdd-owner: implementation --> **Commands run:** health guardrails passed; the full suite produced 674 passed and 1 failure in the pre-existing, unrelated `DreamcoderHerdr/.config/herdr/dreamcoder/0.8.2/config.dark.toml` mismatch (preserved unchanged), so a clean full-suite confirmation remains unavailable.

## Parent-owned lifecycle actions

- [x] Start or reuse the bounded native review for each slice after its implementation and validate its receipt at the applicable lifecycle gate; never bypass a review lock. <!-- sdd-owner: parent --> **DEFERRED — RDD OFF:** `gentle-ai review mode status` reports receipt-driven development off for this clone (global on, clone-local off), and `gentle_review` inspect returns `stop / rdd_disabled`. Per the repository's delivery contract, delivery follows ordinary repository policy, so there is no review lock to satisfy and none was bypassed.
- [x] Confirm `stacked-to-main` chain strategy with the user before `sdd-apply` begins Slice A. <!-- sdd-owner: parent --> **DELIVERED:** the four slices shipped as sequential conventional commits on `main` (`214ef56`, `cf8274c`, `4632f00`, `5f98101`, `2f2db3d`) with no long-lived feature branch and no stacked PRs, confirmed with the user before each commit.

## Protected paths and explicit non-goals

The implementation MUST NOT:

- Wire `renderer_registry.py` into `sync.py`'s live execution path (Slice D's two new calls are the one explicit exception, already existing in `sync.py`).
- Change `sync.py`'s builder functions' actual color/content logic (`kitty_content`, `hypr_content`, `zellij_content`, etc.) — Slice D only adds write-call plumbing, no renderer logic change.
- Resume the broader hexagonal-architecture-v2 migration (no `RendererRegistration` dataclass shape change, no path-resolver fields, no dynamic discovery).
- Delete `DreamcoderZellij/.config/zellij/dreamcoder-{dark,light}.kdl` at any point — stale content is replaced by regeneration, not removal.
- Refresh `legacy_sync_characterization.json` / `legacy_output_hashes.json` fixtures — explicit out-of-scope risk per `proposal.md`.
- Restructure `RendererRegistration` to carry multiple profile×mode bindings for `herdr` (design's intentional single-entry exception).
