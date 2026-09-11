# Proposal: Reconcile renderer_registry.py With Actual sync.py Behavior

## Intent

`renderer_registry.py` is dead code in production — only pytest imports it
(confirmed by grep: nothing in `sync.py`, `cli_handlers.py`, or `scripts/`
calls it). It functions solely as a contract/validation layer describing
what sync is supposed to do. Exploration confirmed 7 bugs where its 33
`REGISTRATIONS` no longer match `sync.py`'s real behavior (wrong renderer
function, wrong active/repository/mutation strategy, or a missing enum
variant for behavior that exists — pinned-mode rendering, symlink-safe
writes, multi-profile herdr). A validation layer that asserts false things
about production is actively harmful: it gives false confidence and will
mask real regressions. This is a small, bounded correction, not a resumption
of the stalled 6-PR hexagonal-architecture-v2 migration (that remains
explicitly out of scope per orchestrator decision).

## Scope

### In Scope
- Fix `renderers_codex.py` codex_app registration: renderer + `output_kind`.
- Fix `renderers_antigravity.py` antigravity registration: represent the
  Dark-pinned active file (add a new `ActiveStrategy` variant only if no
  existing variant fits).
- Fix the ~20 registrations still declaring plain `WRITE_IF_CHANGED` where
  `sync.py` now uses `write_active_repo_file()` (unlink-stale-symlink guard).
- Fix `renderers_hypr_waybar_rofi.py` hypr_colors_lua/conf: declare the real
  `MODE_VARIANTS` repository output already matching design.md.
- Investigate `renderers_zellij.py` (registry claims `MODE_VARIANTS`; only
  Night is generated; dark/light `.kdl` files look orphaned) and record an
  explicit decision: fix the registry's claim, or wire real generation.
- Fix `renderers_herdr.py`/`herdr_contract.py`: represent all 3
  `SUPPORTED_PROFILES` × modes, not a single hardcoded profile/mode.
- Add new `ActiveStrategy`/`MutationStrategy` enum variants in
  `renderer_contract.py` only if no existing variant can represent reality.

### Out of Scope
- Wiring `renderer_registry.py` into `sync.py`'s live execution path.
- Any change to `sync.py`, the renderer *builder* functions, or runtime
  output — this is a registry-accuracy fix, not a behavior change (zellij's
  generation gap is the one exception, pending the decision above).
- Resuming hexagonal-architecture-v2 migration.
- Refreshing `legacy_sync_characterization.json` / `legacy_output_hashes.json`
  fixtures — noted as an explicit risk for a future migration attempt only.

## Capabilities

### New Capabilities
- `renderer-registry`: `renderer_registry.py`'s 33 `REGISTRATIONS` (adjacent
  to their leaf renderer modules) accurately describe `sync.py`'s real
  active/repository/mutation behavior per consumer, as a validation-only
  layer never wired into the live sync path.

### Modified Capabilities
None.

## Approach

Per-bug, targeted edits to each leaf registration's `REGISTRATIONS` tuple
and, where a strategy genuinely has no representable enum member today, add
one new `ActiveStrategy`/`MutationStrategy` value in `renderer_contract.py`
and apply it everywhere it's actually true (not just the one bug that
surfaced it). Zellij and herdr both need a design decision before edits — the
design phase should resolve zellij's orphaned-file question and herdr's
multi-profile representation before `sdd-tasks` slices the work.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/dreamcoder_theme/renderer_contract.py` | Modified | Possible new enum variants |
| `src/dreamcoder_theme/renderers_codex.py` | Modified | Fix renderer + output_kind |
| `src/dreamcoder_theme/renderers_antigravity.py` | Modified | Fix ActiveStrategy |
| `src/dreamcoder_theme/renderer_registry.py` + ~20 leaf modules | Modified | Fix MutationStrategy |
| `src/dreamcoder_theme/renderers_hypr_waybar_rofi.py` | Modified | Fix RepositoryStrategy |
| `src/dreamcoder_theme/renderers_zellij.py`, `DreamcoderZellij/.config/zellij/dreamcoder-{dark,light}.kdl` | Investigate | Decision required |
| `src/dreamcoder_theme/renderers_herdr.py`, `herdr_contract.py` | Modified | 3-profile representation |
| `tests/` | Modified | Update contract-layer expectations |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| 400-line review budget exceeded (7 bugs, ~20-consumer mutation fix, 2 open design decisions) | High | `auto-chain`: slice by bug into independently reviewable, independently revertable PRs |
| Zellij investigation reveals orphaned files needing deletion (data-loss adjacent) | Medium | Decide in design phase before any file deletion; never delete without explicit confirmation |
| New enum variant added but under-applied to only the bug that surfaced it | Medium | Audit all 33 registrations against each new variant, not just the triggering one |
| Legacy fixtures silently validate stale behavior for any future migration | Low (out of scope now) | Documented as explicit follow-up risk, not fixed here |

## Rollback Plan

Every bug fix is an isolated, independently revertable edit to declarative
data (enum values / registration fields) with no runtime side effects.
Revert the specific commit(s) for chained PRs; `validate_registry()` and
existing contract tests catch regressions immediately.

## Dependencies

- Design phase must resolve the zellij and herdr open questions before task
  slicing.

## Success Criteria

- [ ] All 33 `REGISTRATIONS` entries accurately describe `sync.py`'s current
      production behavior (verified by test assertions, not inspection).
- [ ] `sync.py`, renderer builder functions, and runtime output are
      unchanged (except zellij, if the decision selects real generation).
- [ ] Zellij dark/light `.kdl` status is explicitly resolved, not left
      ambiguous.
- [ ] `renderer_registry.py` remains unwired from the live sync path.
