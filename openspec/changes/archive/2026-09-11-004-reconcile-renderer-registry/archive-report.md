# Archive Report: reconcile-renderer-registry

**Archived**: 2026-09-11
**Status**: PASS (change delivered and verified; all tasks complete)
**Store**: openspec
**Change ID**: SDD reconciliation of `renderer_registry.py` against live `sync.py`

## Outcome

The renderer-registry reconciliation is **fully delivered and verified**. All 7 delta
requirements and all 10 scenarios are compliant, all 22 task rows are complete (zero
`- [ ]` boxes remain), the full pytest suite is green (680 passed), and the health gate
passes. This archive closes the change and merges the delta spec into the canonical
`renderer-registry` capability.

This change was a bounded registry-accuracy correction: it did **not** resume the stalled
hexagonal-architecture-v2 migration, did **not** wire `renderer_registry.py` into
`sync.py`'s live execution path, and made exactly one explicit `sync.py` scope exception
(Slice D's two dark/light Zellij repository writes).

## Artifacts Read

- `openspec/changes/reconcile-renderer-registry/proposal.md`
- `openspec/changes/reconcile-renderer-registry/specs/renderer-registry/spec.md`
- `openspec/changes/reconcile-renderer-registry/design.md` (incl. ADR decisions on
  `PINNED_ACTIVE_PATH`, `SYMLINK_SAFE_ACTIVE_WRITE`, Zellij real generation, herdr
  single-entry exception)
- `openspec/changes/reconcile-renderer-registry/tasks.md` (22/22 rows, re-read at archive time)
- `openspec/changes/reconcile-renderer-registry/apply-progress.md`
- `openspec/changes/reconcile-renderer-registry/verify-report.md` (verdict `pass`)
- `openspec/config.yaml` (`rules.archive`: warn before destructive deltas)
- Native status contract (`artifactStore: openspec`, `archive: ready`, `taskProgress 22/22`)
- Repository archive convention:
  `openspec/changes/archive/2026-08-11-003-eye-comfort-theme-system/`

**`sync-report.md`: absent.** No `sdd-sync` run was performed for this change. The
archive-time sync fallback below was executed under the parent's **explicit** written
authorization to "merge the delta spec into the canonical
`openspec/specs/renderer-registry/spec.md` (creating that canonical capability spec if
absent)". This is the only reason a file-backed archive was permitted without a
`sync-report.md`.

## Verified Outcome (from `verify-report.md`)

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:c99787483e9649b4eea5db45bf7cffafc98d77f7c6b4302354dfa09878a6d02f
verdict: pass
blockers: 0
critical_findings: 0
requirements: 7/7
scenarios: 10/10
test_command: python -m pytest tests/ -v --tb=short
test_exit_code: 0
test_output_hash: sha256:fef36362f7a90e90b6677df8604b22e6226eeb9f4abd8ca0c06c7eae9b871460
build_command: python scripts/verify-theme-health.py
build_exit_code: 0
build_output_hash: sha256:3c7e2daebe1d283e4238be33a3693302681d5bdc2e0fce3640459e2bdbb21898
```

- Full suite: **680 passed, 2 pre-existing unrelated warnings**.
- Health gate: `✓ Dreamcoder theme health guardrails passed`.
- Static gates: `ruff check`, `ruff format --check` (111 files), `mypy src/` (56 files),
  `validate-markdown-links.py`, `git diff --check` — all exit 0.
- Coverage: 83.31% (threshold 40%).
- Strict TDD: **not active** (`openspec/config.yaml`: `testing.strict_tdd: false`,
  `apply.tdd: false`); changed tests were audited for assertion quality only, with no
  blockers found and one voluntary RED→GREEN pair recorded for Slice D.

## Canonical Spec Sync (archive-time fallback, parent-authorized)

- **Domains synced**: `renderer-registry`
- **Sync type**: **ADDED (new canonical domain)** — no
  `openspec/specs/renderer-registry/spec.md` existed before this archive; the delta spec
  was a full domain spec (Purpose + Requirements) and was copied to the canonical path
  byte-identically (`diff -q` → identical, 150 lines).
- **Canonical target**: `openspec/specs/renderer-registry/spec.md`
- **Destructive delta**: **none**. Additive-only; zero MODIFIED/REMOVED requirement
  blocks. No destructive-merge warning or approval was required
  (`rules.archive` satisfied trivially).

### ADDED Requirement Names (7)

1. codex_app declares its real renderer
2. antigravity declares a pinned-active strategy
3. symlink-safe consumers use the matching MutationStrategy
4. hypr_colors_lua/conf declare active output plus repository variants
5. zellij registration matches an explicit generation decision
6. herdr registration represents all 3 supported profiles
7. all corrected registrations remain valid under validate_registry()

### MODIFIED / REMOVED

None. No other active change declares the `renderer-registry` domain (directory scan of
`openspec/changes/*/specs/` → only `reconcile-renderer-registry` owns it), so there is no
same-domain active-change warning to record.

## Task Completion State

- **Unchecked implementation task lines**: **none**. `grep -n '^\s*- \[ \]'` over
  `tasks.md` returns no matches at archive time; all 22 rows are `[x]`.
- **No mechanical checkbox repair was performed by this archive.** Both previously
  pending rows are `<!-- sdd-owner: parent -->` lifecycle rows, and they were marked
  complete by the parent with their resolutions recorded inline in `tasks.md` **before**
  this archive ran. Archive did not edit `tasks.md`.

### Parent-owned lifecycle rows — recorded resolutions (verbatim substance from `tasks.md`)

1. *"Start or reuse the bounded native review for each slice after its implementation and
   validate its receipt at the applicable lifecycle gate; never bypass a review lock."*
   → **DEFERRED — RDD OFF.** `gentle-ai review mode status` reports receipt-driven
   development off for this clone (global on, clone-local off) and `gentle_review`
   inspect returns `stop / rdd_disabled`. Per the repository's delivery contract,
   delivery follows ordinary repository policy: **there is no review lock to satisfy and
   none was bypassed.** Truthfully recorded: **no native review receipt exists for this
   change.**
2. *"Confirm `stacked-to-main` chain strategy with the user before `sdd-apply` begins
   Slice A."*
   → **DELIVERED as sequential conventional commits on `main`.** The change shipped as
   `214ef56`, `cf8274c`, `4632f00`, `5f98101`, `2f2db3d` — no long-lived feature branch,
   no stacked PRs, confirmed with the user before each commit. The task's literal
   `stacked-to-main` text was superseded by that decision; this is recorded as a
   deliberate delivery decision, not as `stacked-to-main` having been executed.

Because every unchecked-box concern is resolved and **zero implementation tasks** were
ever pending, the archive Final Task Completion Gate passes without exception. No
non-critical partial-archive approval was needed or used: all required artifacts
(proposal, spec, design, tasks, apply-progress, verify-report) are present, so this is a
full, not partial, archive.

## Verification Findings Carried Forward (non-blocking)

- **WARNING-1 — review boundary**: the `tasks.md` forecast (chained PRs, `stacked-to-main`,
  4 slices A→C→B→D) was not executed as PRs; slices A and B landed together in `cf8274c`
  and C landed after. Whole-change diff is 413 lines (over the 400 budget as one unit),
  but the largest single work unit was 255 lines — under budget. Process fidelity, not a
  defect.
- **WARNING-2 — herdr single-entry model**: the registry still holds one `herdr` entry
  with a dynamically-bound representative profile. The "all 3 profiles" requirement is
  satisfied at `summary_label` granularity (`0.7.3, 0.8.0, 0.8.2`) plus a drift-guard
  test, per `design.md`'s explicit intentional single-entry exception.
- **INFO-1 — stale recorded failure**: `apply-progress.md` D.4 records a full-suite
  Herdr `0.8.2` `config.dark.toml` failure that is **resolved** in the current tree
  (out-of-change commit `5a2b7ba`); the suite is green at 680 passed.
- **INFO-2 — runtime harness**: `./scripts/dreamcoder sync` does not set `PYTHONPATH`, so
  it fails under a plain `python3` unless the package is installed. Slice D's two Zellij
  writes were verified by isolated parity test + direct canonical `zellij_content()`
  invocation instead. Not introduced by this change.
- **Out-of-scope working-tree state**: four modified-but-uncommitted files
  (`.github/workflows/theme-validation.yml`, `.pi/gentle-ai/sdd-preflight.json`,
  `scripts/doctor.sh`, `tests/test_active_mirror_identity_consistency.py`) are not part of
  this change and were untouched by this archive.

## Structured Status and actionContext Findings

- Native status at archive time: `artifactStore: openspec`;
  `artifactPaths` proposal/specs/design/tasks/applyProgress/verifyReport all resolve;
  `taskProgress 22/22`, `allComplete: true`; `dependencies.proposal/specs/design/tasks:
  all_done`, `apply: all_done`, `verify: all_done`; `archive: ready`;
  `blockedReasons: []`; `remediationState.required: false`; `nextRecommended: archive`.
- **Divergence recorded for traceability**: the on-disk `verify-report.md` was written
  when `taskProgress` was 20/22 and therefore states "NOT ready for archive" and reports
  the engine's then-current `verify/archive: blocked`. The two blocking rows were
  subsequently resolved by the parent, and the native engine now reports
  22/22 with `archive: ready`. The verify **verdict itself is `pass` with 0 blockers and
  0 critical findings**; the earlier blocked state was a non-critical process-gate state,
  not a verification failure. No CRITICAL verification issue exists, so no archive
  override was needed.
- `actionContext`: `mode: repo-local`, `workspaceRoot` =
  `/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots`, `allowedEditRoots:
  [/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots]`. Every archive operation
  (canonical spec copy, report write, folder move) is inside the authoritative workspace
  and inside `allowedEditRoots` — no ownership or edit-root blocker.

## Destructive Merge

None performed. The canonical sync was a pure additive copy into a previously
non-existent canonical domain. No approval required, no blocker raised.

## Files Moved

Whole change folder relocated under the repository's dated archive convention:

```text
openspec/changes/reconcile-renderer-registry/
  -> openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/
```

Moved contents (6 files, all preserved unmodified by the move):

```text
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/proposal.md
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/specs/renderer-registry/spec.md
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/design.md
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/tasks.md
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/apply-progress.md
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/verify-report.md
```

Plus the archive report written into the change folder immediately before the move:

```text
openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/archive-report.md
```

## Files Created

```text
openspec/specs/renderer-registry/spec.md   (NEW canonical capability spec, 150 lines)
```

Directory `openspec/specs/renderer-registry/` is new (no canonical `renderer-registry`
spec existed; `openspec/specs/` previously held `eye-comfort`, `palette`, `sync`,
`writers`).

## Archived Path

`openspec/changes/archive/2026-09-11-004-reconcile-renderer-registry/`

Convention: `<ISO-date>-<NNN>-<change-name>`, continuing the sequence after
`2026-07-02-002-refactor-renderer-pipeline` and
`2026-08-11-003-eye-comfort-theme-system`.

## Audit Trail

- Proposal → Spec → Design → Tasks → Apply (4 slices) → Verify (`pass`) → Archive ✅
- 22/22 tasks complete; zero unchecked implementation task boxes; 2 parent-owned
  lifecycle rows reconciled by the parent per the RDD-off deferral and the
  sequential-delivery decision recorded above.
- No file deletions. No archived change was modified. No `sync-report.md` existed; the
  archive-time sync fallback was explicitly parent-authorized and is additive-only.
- Memory observation IDs: N/A (openspec mode; no Engram save performed).
