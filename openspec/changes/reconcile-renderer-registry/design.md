# Design: Reconcile renderer_registry.py With Actual sync.py Behavior

## Technical Approach

Per-bug edits to `REGISTRATIONS` tuples in leaf renderer modules, plus two
additive `renderer_contract.py` enum variants threaded through
`renderer_registry.py`'s `_OWNERSHIP_RULES` and `_check_strategy_compatibility`.
Zellij and herdr required investigation (done below) before slicing. No
change to `RendererRegistration`'s dataclass shape; no wiring into `sync.py`'s
execution path except the one explicit zellij exception.

## Architecture Decisions

### Decision: New `ActiveStrategy.PINNED_ACTIVE_PATH`

Antigravity's repo active mirror (`DreamcoderAntigravity/Dreamcoder.json`) is
always written from `antigravity_content(variants["dark"])`
(`sync.py:716-721`, comment confirms: button colors must always resolve
Dark, independent of live mode). No existing `ActiveStrategy` represents
"active output that ignores the live active mode."

| Option | Tradeoff | Decision |
|---|---|---|
| Reuse `RESOLVED_ACTIVE_PATH` | Lies about mode-tracking; the bug we're fixing | Rejected |
| Model as `REPOSITORY_ONLY` | Antigravity has a real, unsuffixed active-path file; wrong ownership shape | Rejected |
| Add `PINNED_ACTIVE_PATH` | One new closed value, precise semantics | **Chosen** |

**Threading**: add `ActiveStrategy.PINNED_ACTIVE_PATH` to
`_OWNERSHIP_RULES["active"]` and `["active-and-repository"]` allowed-active
sets (not `"repository"` — repository-only consumers have no active
dimension). No `_check_strategy_compatibility` rule needed — pinning is
orthogonal to mutation strategy.

### Decision: New `MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE`

`write_active_repo_file()` (added this session) unlinks a stale symlink
before `write_if_changed` for every repo-tracked active-mirror write in
`sync_repo_snippets()`. `WRITE_IF_CHANGED` no longer describes these paths.

| Option | Tradeoff | Decision |
|---|---|---|
| Keep `WRITE_IF_CHANGED`, add prose comment | Comment drift already caused this bug | Rejected |
| Split `mutation` into active/repo sub-fields | Touches all 33 registrations' dataclass shape; disproportionate | Rejected |
| Add `SYMLINK_SAFE_ACTIVE_WRITE` | One new value, matches the real helper 1:1 | **Chosen** |

**Threading**: add a `_check_strategy_compatibility` rule — rejects only
`output_kind="repository"`; the helper protects a repository-tracked active mirror even when the registry consumer declares no mode variants. (No
variant generation is required.) Applies to every registration whose
repo active-mirror write in `sync_repo_snippets()` calls
`write_active_repo_file()` (audit against sync.py call sites, not the
consumer that surfaced the bug).

**Slice B deviation correction**: live `sync.py` writes OpenCode's live path
and its unsuffixed repository mirror through `write_active_repo_file()` but
never generates mode variants. OpenCode therefore owns active output only:
`RESOLVED_ACTIVE_PATH` / `NO_VARIANTS` / `SYMLINK_SAFE_ACTIVE_WRITE`.
`PROFILE_AWARE_SELECTOR` consumers
(ghostty, warp, zellij) keep that value — it describes the *live selector
patch*, a separate dimension `_check_strategy_compatibility` doesn't
conflict on; documented as an accepted model gap below, not fixed now.

### Decision: Zellij dark/light — real generation gap, not orphaned files

Investigated `renderers_zellij.py`, `sync.py`'s `VARIANT_REGISTRY`/
`sync_repo_snippets`, `update_zellij_config`, and the on-disk `.kdl` files.
Findings: (1) only `dreamcoder-night.kdl` is generated
(`sync.py:872-877`); (2) `update_zellij_config` sets
`theme "dreamcoder-{mode}"` for the **standard (non-night) path**
(`writers.py:168-169`) — this is the everyday case; (3) the committed
`dreamcoder-dark.kdl`/`dreamcoder-light.kdl` carry an older, different color
set (`bg "#100f0d"`) that does not match current canonical tokens
(`bg #000000`), yet both still carry an "auto-generated, do not edit
manually" header.

**Decision**: this is a live production gap, not dead cruft — standard-mode
Zellij users are actively selecting a theme file nothing regenerates, with
stale colors. Wire real generation, mirroring the existing Night call
exactly (`write_active_repo_file(..., zellij_content(variants[mode],
f"dreamcoder-{mode}"))` for `dark` and `light` in `sync_repo_snippets()`).
This is the deliberate, explicit scope exception the proposal names. No
enum change needed — `zellij`'s registration already correctly declares
`RepositoryStrategy.MODE_VARIANTS`; sync.py catches up to it. **No file
deletion.**

### Decision: Herdr — intentional single-registry-entry exception

`sync_herdr_repo_variants()` fans out over all complete
`SUPPORTED_PROFILES` (0.7.3/0.8.0/0.8.2) × dark/light/(night). The registry
model is one `consumer_id` → one `Renderer` callable
(`render(palette) -> str`); restructuring `RendererRegistration` to carry
N profile×mode bindings for one consumer breaks that invariant for all 33
entries — disproportionate for a registry that only proves port conformance,
never executes.

**Decision**: keep one `consumer_id="herdr"` entry. Bind the representative
renderer dynamically — `next(p for p in SUPPORTED_PROFILES if p and
p.is_complete)` instead of the hardcoded `HERDR_073_PROFILE` — and compute
`summary_label` from `SUPPORTED_PROFILES` at import time so it can't
silently drift again. Add an explicit code comment stating this is the one
intentional single-entry exception, with `sync_herdr_repo_variants()` as
ground truth, plus a drift-guard test in `tests/test_herdr_contract.py`
asserting the label matches `SUPPORTED_PROFILES` live.

## File Changes

| File | Action | Description |
|---|---|---|
| `src/dreamcoder_theme/renderer_contract.py` | Modify | Add `ActiveStrategy.PINNED_ACTIVE_PATH`, `MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE` |
| `src/dreamcoder_theme/renderer_registry.py` | Modify | Thread both into `_OWNERSHIP_RULES`, `_check_strategy_compatibility` |
| `src/dreamcoder_theme/renderers_antigravity.py` | Modify | `active=PINNED_ACTIVE_PATH`, `mutation=SYMLINK_SAFE_ACTIVE_WRITE` |
| `src/dreamcoder_theme/renderers_codex.py` | Modify | `codex_app` renderer → `opencode_content`-based (verify `output_kind` against `VARIANT_REGISTRY` at task time) |
| `src/dreamcoder_theme/renderers_hypr_waybar_rofi.py` | Modify | `hypr_colors_lua`/`hypr_colors_conf` → `output_kind="active-and-repository"`, `repository=MODE_VARIANTS`, `mutation=WRITE_IF_CHANGED` |
| `src/dreamcoder_theme/renderers_herdr.py`, `herdr_contract.py` | Modify | Dynamic representative-profile binding, computed `summary_label`, exception comment |
| ~20 leaf modules (audit `sync.py` `write_active_repo_file` call sites) | Modify | `mutation` → `SYMLINK_SAFE_ACTIVE_WRITE` |
| `src/dreamcoder_theme/sync.py` | Modify (scope exception) | Add dark/light zellij `write_active_repo_file` calls in `sync_repo_snippets()` |
| `DreamcoderZellij/.config/zellij/dreamcoder-{dark,light}.kdl` | Regenerate | Replace stale content via new sync.py writes; no deletion |
| `tests/test_renderer_registry.py`, `tests/test_herdr_contract.py` | Modify | Cover new variants, drift guard, zellij dark/light parity |

## Candidate PR Slices (400-line budget, `auto-chain`)

| Slice | Scope | Touches sync.py? | Order |
|---|---|---|---|
| A — Straightforward registration fixes | codex_app renderer, hypr_colors_lua/conf ownership fields | No | 1st |
| C — Herdr documentation fix | Dynamic profile binding, computed label, drift-guard test | No | 2nd |
| B — New enum variants + threading + mutation sweep | Both new variants, `_OWNERSHIP_RULES`/`_check_strategy_compatibility`, antigravity + ~20-consumer mutation audit | No | 3rd |
| D — Zellij real generation | dark/light write calls, `.kdl` regeneration, parity test | **Yes (explicit exception)** | 4th, last |

Each slice is independently revertable declarative-data/one-function-add
edits; `validate_registry()` and existing contract tests catch regressions
per slice. D is ordered last and isolated so a revert never touches A/B/C.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | New enum variants accepted/rejected by `_check_strategy_compatibility`/`_OWNERSHIP_RULES` | `tests/test_renderer_registry.py` |
| Unit | Herdr `summary_label` matches live `SUPPORTED_PROFILES` | `tests/test_herdr_contract.py` drift guard |
| Integration | `validate_registry()` returns zero problems post-fix | Existing suite |
| Integration | Zellij dark/light `.kdl` content equals `zellij_content(variants[mode], ...)` | New parity test, Slice D only |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary. Slice D adds one
declarative file-generation call reusing the existing
`write_active_repo_file` guard; no new I/O surface.

## Migration / Rollout

No migration. Slice D changes on-disk zellij theme content for dark/light
(stale → current palette); this is a visual content correction, not a
schema/data migration, and ships as an independently revertable slice.

## Open Questions

- [ ] `PROFILE_AWARE_SELECTOR` doesn't separately flag whether a consumer's
      repo mirror also needs the symlink guard (ghostty/warp have no repo
      mirror; zellij does). Accepted model gap — not fixed this change.
- [ ] Exact ~20-consumer list for Slice B must be enumerated against live
      `write_active_repo_file()` call sites in `sync.py` during task
      breakdown, not guessed from this design.
