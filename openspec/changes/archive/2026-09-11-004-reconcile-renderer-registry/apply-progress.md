# Apply Progress: reconcile-renderer-registry

## Scope of this run

Slices A (PR 1), C (PR 2), B (PR 3), and D (PR 4) are complete. Slice D
is the permitted `sync.py` scope exception: it adds only the dark/light Zellij
repository writes and regenerates only those two files.

## Completed Tasks

- [x] A.1 `codex_app` registration renderer fixed: `codex_tmtheme_content` →
      `opencode_content` (imported from `.renderers_opencode`). `output_kind`,
      `active`, `repository` left unchanged (`active-and-repository`,
      `RESOLVED_ACTIVE_PATH`, `MODE_VARIANTS`) — implemented exactly as
      `tasks.md` specified.
- [x] A.2 `hypr_colors_lua`/`hypr_colors_conf` ownership fields fixed —
      **implemented differently from tasks.md's literal text; see Deviation
      below.** Final registration: `output_kind="active-and-repository"`,
      `active=ActiveStrategy.RESOLVED_ACTIVE_PATH` (unchanged), was
      `repository=RepositoryStrategy.NO_VARIANTS` → now `MODE_VARIANTS`, was
      `mutation=MutationStrategy.ACTIVE_ONLY_BRIDGE` → now
      `MutationStrategy.WRITE_IF_CHANGED`. No new enum members introduced —
      both `MODE_VARIANTS` and `WRITE_IF_CHANGED` already existed.
- [x] A.3 Added `TestSliceARegistrationFixes` class to
      `tests/test_renderer_registry.py` (6 new tests): codex_app renderer
      identity (2 tests), codex_app ownership fields unchanged (1),
      hypr_colors_lua ownership fields (1), hypr_colors_conf ownership fields
      (1), full-registry `validate_registry() == []` re-confirmation (1).
- [x] A.4 `python -m pytest tests/test_renderer_registry.py -v` → 20/20
      passed. `validate_registry(REGISTRATIONS) == []` confirmed.

## Deviation: hypr_colors_lua/hypr_colors_conf output_kind

**The conflict the orchestrator flagged in advance was real, and I resolved
it against live code — not by trusting either artifact, including
`tasks.md`'s own resolution.**

`tasks.md`'s A.2 text (and `spec.md`'s "repository-only" Requirement/Scenario
it was derived from) reasons only about `sync_repo_snippets()`: true that it
calls `write_variant_files()` for both consumers and never
`write_active_repo_file()`. But neither artifact accounts for
`sync_active_targets()` (wired into `main()` at `sync.py:1112` and
`cli_handlers.py:485,513`), which does:

```python
"hypr_colors_lua": write_if_changed(paths.hypr_colors_lua, hypr_colors_lua_content(active)),
"hypr_colors_conf": write_if_changed(paths.hypr_colors_conf, hypr_colors_conf_content(active)),
```

`paths.hypr_colors_lua`/`paths.hypr_colors_conf` resolve (via `settings.py`)
to `config_home / "hypr/colors.lua"` / `"hypr/colors.conf"` — real, live,
active-mode-tracking system config files, written on every sync exactly like
`hyprland`'s own `paths.hyprland` active write. This is a genuine "active"
output in the same sense the registry already assigns to every other
`active-and-repository` consumer; it is just not *repository-mirrored*
(unlike `hyprland`/`waybar`/`rofi`, there is no `write_active_repo_file()`
copy of it inside the repo tree).

Given `output_kind="repository"` + `active=NO_ACTIVE_OUTPUT` would assert
"no active output exists" while a live active write demonstrably does exist
and is exercised on every sync, applying `tasks.md`'s literal text would
reintroduce exactly the kind of false registry claim this whole change
exists to eliminate (per `proposal.md`'s own stated Intent). I implemented
the registration matching **all** of `sync.py`'s real behavior for this
consumer (`design.md`'s File Changes table row), not just the
`sync_repo_snippets()` slice `spec.md`/`tasks.md` examined.

**Follow-up needed**: `spec.md`'s "hypr_colors_lua/conf declare
repository-only output" Requirement and its Scenario
(`output_kind == "repository"`, `active != RESOLVED_ACTIVE_PATH`) should be
corrected in a future spec-phase pass to match what was actually
implemented and tested here (`active-and-repository` /
`RESOLVED_ACTIVE_PATH` / `MODE_VARIANTS` / `WRITE_IF_CHANGED`). I did not
edit `spec.md` myself — that is outside the apply phase's authority and
outside Slice A's declared file scope.

## Files Changed

| File | Action | What Was Done |
|------|--------|----------------|
| `src/dreamcoder_theme/renderers_codex.py` | Modified | `codex_app` renderer → `opencode_content`; added import |
| `src/dreamcoder_theme/renderers_hypr_waybar_rofi.py` | Modified | `hypr_colors_lua`/`hypr_colors_conf` → `active-and-repository` / `MODE_VARIANTS` / `WRITE_IF_CHANGED`, with inline comments citing the verified `sync.py` call sites |
| `tests/test_renderer_registry.py` | Modified | Added `TestSliceARegistrationFixes` (6 tests) + related imports |
| `openspec/changes/reconcile-renderer-registry/tasks.md` | Modified | Marked A.1–A.4 and C.1–C.4 `[x]`, documented their precise deviations inline |
| `src/dreamcoder_theme/renderers_herdr.py` | Modified | Bound the representative adapter and summary label to live complete supported profiles |
| `tests/test_herdr_contract.py` | Modified | Added a summary-label drift guard derived from `SUPPORTED_PROFILES` |
| `src/dreamcoder_theme/sync.py` | Modified | Slice D only: added dark/light Zellij `write_active_repo_file()` calls mirroring the existing night call |
| `tests/test_dreamcoder_sync.py` | Modified | Added temporary-root dark/light Zellij parity coverage against `zellij_content()` |
| `DreamcoderZellij/.config/zellij/dreamcoder-dark.kdl` | Modified | Regenerated from current canonical dark tokens; `bg "#000000"` |
| `DreamcoderZellij/.config/zellij/dreamcoder-light.kdl` | Modified | Regenerated from current canonical light tokens |

## Slice C Work Unit Evidence (PR 2)

### Completed Tasks

- [x] C.1 Replaced `HERDR_073_PROFILE` with the first complete live entry
      from `SUPPORTED_PROFILES` for the representative `VersionedHerdrAdapter`.
- [x] C.2 Derived the `herdr` summary label from the complete profile versions
      at import time and documented the intentional single-entry exception;
      `sync_herdr_repo_variants()` remains the fan-out ground truth.
- [x] C.3 Added a drift guard that derives the expected label from live
      `SUPPORTED_PROFILES`.
- [x] C.4 Ran the required focused test command successfully.

| Evidence | Result |
|---|---|
| Focused test command | `python -m pytest tests/test_herdr_contract.py -v` → 22 passed |
| Static checks | `.venv/bin/ruff check src/dreamcoder_theme/renderers_herdr.py tests/test_herdr_contract.py` → all checks passed; `.venv/bin/mypy src/dreamcoder_theme/renderers_herdr.py` → success, no issues in 1 source file |
| Runtime harness | `PYTHONPATH=src python -c 'from dreamcoder_theme.renderer_registry import validate_registry; assert validate_registry() == []'` → exit 0; imports the assembled registry and confirms full conformance. The first equivalent command without `PYTHONPATH=src` failed only because the repository uses a `src/` layout; no product failure occurred. |
| Rollback boundary | Revert `src/dreamcoder_theme/renderers_herdr.py` and `tests/test_herdr_contract.py`; restores the prior fixed 0.7.3 representative and static label without touching sync behavior or profile contracts. |

## Slice C Deviation: no herdr_contract.py mutation

`design.md`'s File Changes table names `herdr_contract.py`, but live code
already exposes all three complete `SUPPORTED_PROFILES` consumed by
`sync_herdr_repo_variants()`. The assigned C.1–C.4 tasks require dynamic
registry binding and a drift guard, both fully satisfied by
`renderers_herdr.py` and `tests/test_herdr_contract.py`. No contract-module
change would improve accuracy, so it was intentionally left untouched;
`HERDR_073_PROFILE` remains stable for existing callers.

## Slice B deviation correction

Live `sync.py` writes OpenCode's live path and one unsuffixed repository mirror
with `write_active_repo_file()` but does not emit mode variants. OpenCode is
therefore active-only (`RESOLVED_ACTIVE_PATH` / `NO_VARIANTS` /
`SYMLINK_SAFE_ACTIVE_WRITE`). The mutation strategy protects that tracked active
mirror, so registry compatibility accepts active and active-and-repository
outputs and rejects repository-only output.

## Slice D Work Unit Evidence (PR 4)

| Evidence | Result |
|---|---|
| RED | `python -m pytest tests/test_dreamcoder_sync.py -k zellij -v` → 1 failed before implementation: `dreamcoder-dark.kdl` was absent under the temporary redirected `sync.ROOT`. |
| GREEN | The same focused command → 1 passed after the two calls were added. |
| Focused sync tests | `python -m pytest tests/test_dreamcoder_sync.py -v` → 22 passed, 1 existing fixture warning. |
| Requested generation command | `./scripts/dreamcoder sync` → exit 1 before writes: `ModuleNotFoundError: No module named 'dreamcoder_theme'`. The repository's `src/` layout was not on `PYTHONPATH`. |
| Scoped regeneration fallback | `PYTHONPATH=src python -c '<load_variants + zellij_content writes>'` → exit 0; wrote only the two allowed Zellij files. A subsequent `PYTHONPATH=src python -c '<exact parity and dark bg assertions>'` → exit 0. |
| Full suite | `python -m pytest tests/ -v` → 674 passed, 1 failed, 2 warnings. Failure: `tests/test_herdr_theme_generation.py::test_checked_in_repository_variants_match_the_renderer`, caused by the already-modified, preserved `DreamcoderHerdr/.config/herdr/dreamcoder/0.8.2/config.dark.toml`; not changed by Slice D. |
| Health | `python scripts/verify-theme-health.py` → `✓ Dreamcoder theme health guardrails passed`. |
| Diff hygiene | `git diff --check` → exit 0; exact canonical parity assertion and dark `bg "#000000"` assertion → exit 0. |

## Scope Compliance

- Slice D changed only `sync.py`, its focused sync test, and the two permitted
  Zellij generated files. No kitty, tmux, starship, nvim, or other generated
  files were modified by this slice.
- The pre-existing `DreamcoderHerdr/.config/herdr/dreamcoder/0.8.2/config.dark.toml`
  modification was preserved unchanged; it is the source of the full-suite
  failure recorded above.

- `renderer_registry.py`: modified only for the Slice B compatibility
      correction; `SYMLINK_SAFE_ACTIVE_WRITE` accepts active and
      active-and-repository output and rejects repository-only output.


- `sync.py`: modified only for Slice D's two dark/light Zellij repository writes; no builder logic changed.
- No `ActiveStrategy`/`MutationStrategy` new enum variants added — Slice A
  used only pre-existing members (`RESOLVED_ACTIVE_PATH`, `MODE_VARIANTS`,
  `WRITE_IF_CHANGED`).
- herdr (Slice C): modified only in `renderers_herdr.py`; `herdr_contract.py`
  remains unchanged because its existing `SUPPORTED_PROFILES` is authoritative.
  Zellij (Slice D): dark/light repository variants were regenerated only.
- Slice B received only the verified compatibility and OpenCode ownership
      correction; Slice D is complete.

## Slice B Verification Evidence (historical)

| Evidence | Result |
|---|---|
| Focused test command | `python -m pytest tests/test_renderer_registry.py -v` → 20 passed |
| Full suite (system Python, per instructions) | `python -m pytest tests/ -v` → 664 passed, 0 failed, 2 pre-existing unrelated warnings |
| `.venv` mypy | `.venv/bin/mypy src/` → "Success: no issues found in 56 source files" |
| `.venv` ruff | `.venv/bin/ruff check src/ tests/` → "All checks passed!" |
| pre-commit (changed files only) | `pre-commit run --files <3 changed files>` → all hooks Passed, including the pytest hook and mypy |
| Runtime harness | N/A — declarative registry data only, no process/filesystem mutation (`validate_registry()` is pure; confirmed by `TestDiscoveryPurity`, unaffected) |
| Rollback boundary | Revert the 3 changed files (`renderers_codex.py`, `renderers_hypr_waybar_rofi.py`, `tests/test_renderer_registry.py`); registry-only, no runtime behavior change, `sync.py` untouched |

## Historical Remaining Tasks (before Slice D)

- [x] Slice D (PR 4) — zellij real generation (sync.py exception); completed in the Slice D update above.
- [ ] Parent-owned: confirm `stacked-to-main` chain strategy with user; start
      bounded native review for Slice A after this apply batch

## Historical Status (before Slice D)

> Current status: 20/22 tasks complete (A.1–A.4, B.1–B.8, C.1–C.4, D.1–D.4).
> Slice D's focused and health checks pass; final `sdd-verify` remains blocked
> on the preserved, unrelated Herdr repository-variant mismatch in the full suite.

8/22 tasks complete (A.1–A.4, C.1–C.4). Ready for the next bounded apply
slice (B); final `sdd-verify` remains deferred until B and D are complete.

## Post-apply reconciliation (spec artifacts + test isolation)

Completed while continuing this change:

- `specs/renderer-registry/spec.md` Slice A requirement corrected:
  `hypr_colors_lua`/`hypr_colors_conf` now require
  `output_kind="active-and-repository"`,
  `ActiveStrategy.RESOLVED_ACTIVE_PATH`, `RepositoryStrategy.MODE_VARIANTS`,
  and `MutationStrategy.WRITE_IF_CHANGED`, matching the implementation and
  the verified live `sync.py` (`sync_active_targets()` active write +
  `sync_repo_snippets()` mode variants, neither through
  `write_active_repo_file()`). The prior "repository-only" requirement
  asserted behavior the registry does not have.
- `specs/renderer-registry/spec.md` symlink-safe requirement's consumer list
  corrected to the exact 21 consumers whose repo active-mirror write routes
  through `write_active_repo_file()`; `kitty`, `tmux`, `starship`, `nvim` are
  named as keeping `WRITE_IF_CHANGED`, and `zellij`/`ghostty`/`warp` keep
  `PROFILE_AWARE_SELECTOR`.
- `tests/test_dreamcoder_sync.py`: the pre-existing
  `test_kitty_ui_active_write_does_not_corrupt_symlinked_sibling` now empties
  `VARIANT_REGISTRY` (its entries bake absolute repo paths at import time), so
  the suite no longer rewrites the checked-in `codex_app`/`codex_theme`/
  `bat_theme`/`pi_theme` active mirrors as a side effect. The Slice D parity
  test already guarded this way.
- `tests/test_herdr_contract.py` and `tests/test_renderer_registry.py`
  reformatted with `ruff format` so `make python-lint`
  (`ruff format --check src/ tests/`) passes.

Verification after reconciliation: `python -m pytest tests/` ->
**674 passed, 1 failed, 31 subtests passed**. The single failure is
`tests/test_herdr_theme_generation.py::test_checked_in_repository_variants_match_the_renderer`,
caused by the pre-existing, unrelated
`DreamcoderHerdr/.config/herdr/dreamcoder/0.8.2/config.dark.toml` drift
(`onboarding = false`) documented under `implement-herdr-dreamcoder-themes`;
this change does not touch that file. `ruff check` / `ruff format --check`,
`mypy src/`, `scripts/verify-theme-health.py`, and
`scripts/validate-markdown-links.py` all pass; `scripts/verify-repo-sync.py`
reports only that same herdr drift.
