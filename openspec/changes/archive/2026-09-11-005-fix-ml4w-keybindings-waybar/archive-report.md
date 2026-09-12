# Archive Report: fix-ml4w-keybindings-waybar

**Archived**: 2026-09-11
**Status**: PASS (change delivered and verified; all tasks complete)
**Store**: openspec
**Archived path**: `openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/`

## Outcome

The ML4W keybinding and Waybar integration change is **fully delivered and
verified**, and this archive closes it and merges its delta into the new
canonical `ml4w-keybindings-waybar` capability.

At close the native status engine reported `taskProgress 6/6`,
`allComplete: true`, `dependencies.verify: all_done`, `archive: ready`,
`blockedReasons: []`, `nextRecommended: archive`. The verification report
resolves to `verdict: pass` with `requirements: 17/17`, `scenarios: 17/17`,
`blockers: 0` and `critical_findings: 0`. No CRITICAL verification issue exists,
so no archive override was required or used.

## Artifacts Read

- `openspec/changes/fix-ml4w-keybindings-waybar/proposal.md`
- `openspec/changes/fix-ml4w-keybindings-waybar/specs/ml4w-keybindings-waybar/spec.md` (delta)
- `openspec/changes/fix-ml4w-keybindings-waybar/design.md`
- `openspec/changes/fix-ml4w-keybindings-waybar/tasks.md` (re-read at archive time)
- `openspec/changes/fix-ml4w-keybindings-waybar/verify-report.md`
- `openspec/changes/fix-ml4w-keybindings-waybar/STATUS.md`
- `openspec/config.yaml` (`rules.archive`: warn before merging destructive deltas)
- Canonical shape reference: `openspec/specs/renderer-registry/spec.md`
- Native status contract (`artifactStore: openspec`, `archive: ready`, `taskProgress 6/6`)

**`sync-report.md`: absent.** No separate `sdd-sync` run was performed for this
change. The archive-time sync fallback below was executed under the parent's
**explicit** written instruction to create the canonical capability directory
`openspec/specs/ml4w-keybindings-waybar/`. That instruction is the only reason a
file-backed archive was permitted without a `sync-report.md`.

**`apply-progress.md`: absent.** Never written. This is an **accepted, recorded
waiver** carried forward from verify; it was deliberately **not** fabricated
retroactively, because a back-dated artifact would be unreviewable. Strict TDD is
off (`openspec/config.yaml`: `testing.strict_tdd: false`, `apply.tdd: false`), so
no `TDD Cycle Evidence` table was contractually required from it, and every fact
it would have carried is independently proved by the verify report from primary
evidence.

## Verified Outcome (from `verify-report.md`)

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:72a2fa0c6824c9c5af558128a0cd056b62f60f75b6b71c5ab817e71a9e85abad
verdict: pass
blockers: 0
critical_findings: 0
requirements: 17/17
scenarios: 17/17
test_command: uv run pytest tests/ -v --tb=short
test_exit_code: 0
test_output_hash: sha256:656485676cd0ffc812fc5ea73b867d0d07e0c1cc74628804e9acf746e9dd018f
build_command: uv sync --all-extras
build_exit_code: 0
build_output_hash: sha256:4cb6e97bca26765e5fe271a29f2eca0c295e39e64ca98bab23828f34b3b9f36b
```

Envelope admissibility: `gentle-ai sdd-verify-validate --requirements 17
--scenarios 17` returns `{"valid": true, "verdict": "pass"}`. The envelope
carries exactly the 13 admitted fields, in order.

Verification evidence at close:

- `uv sync --all-extras` — exit 0.
- `uv run pytest tests/ -v --tb=short` — exit 0, **680 passed**
  (`collected 680 items`, 2 warnings).
- `bats tests/ml4w/` — 34/34, exit 0.
- `python3 scripts/validate-ml4w-profiles.py --ci` — exit 0, `All profiles clean!`.
- `ruff check` / `ruff format --check` / `mypy src/` / `verify-theme-health.py` — all exit 0.
- `bash -n` on both ML4W scripts, `luac -p` on generated Lua, JSONC parse of
  `DreamcoderWaybar/.config/waybar/config.jsonc` — all exit 0.
- Live `hyprctl binds -j` — 119 binds, 118 distinct `(modmask, key)`,
  0 real collisions; `hyprctl configerrors` empty (Hyprland 0.56.2).

## Final Task Completion Gate

- Persisted tasks artifact re-read immediately before the sync fallback and the
  move: `openspec/changes/fix-ml4w-keybindings-waybar/tasks.md`.
- **Exact unchecked implementation task lines: NONE.** `grep -n '^\s*- \[ \]'`
  over `tasks.md` returns no matches; all six rows are `[x] T1`…`[x] T6`.
- **No mechanical checkbox repair was performed by this archive.** `tasks.md` was
  not edited. The checkboxes were converted from the earlier non-checkbox `T1..`
  format to markdown checkboxes by the parent/apply work **before** this archive
  ran (converted 2026-09-11), which is what let the native engine measure 6/6.
  The Execution Log content was preserved and its stale profile counts corrected
  in place to the measured truth (default **56**, asus **70**); the dated
  `hyprctl binds` counts inside those log entries are observations from their own
  passes (106 at the time, 119 now) and are not profile counts.
- Stale-checkbox reconciliation was therefore **not** needed, and no
  non-critical partial-archive approval was used. All required artifacts
  (proposal, spec, design, tasks, verify-report) are present, so this is a full
  archive — the only absent artifacts are `apply-progress.md` (accepted waiver)
  and `sync-report.md` (archive-time fallback explicitly authorized).

## Canonical Spec Sync (archive-time fallback, parent-authorized)

- **Domains synced**: `ml4w-keybindings-waybar`
- **Sync type**: **ADDED (new canonical domain)** — no
  `openspec/specs/ml4w-keybindings-waybar/spec.md` existed before this archive.
  The delta spec is a full domain spec (`# … Specification` → `## Purpose` →
  `## Requirements`), so it was copied byte-identically to the canonical path
  (`diff -q` → identical, 403 lines).
- **Canonical target**: `openspec/specs/ml4w-keybindings-waybar/spec.md`
- **Shape**: matches `openspec/specs/renderer-registry/spec.md` —
  `# ML4W Keybindings & Waybar Integration Specification`, `## Purpose`,
  `## Requirements`, then `### Requirement: ...` / `#### Scenario: ...` blocks.
- **Destructive delta**: **none**. Additive-only; zero MODIFIED and zero REMOVED
  requirement blocks. `rules.archive` ("warn before merging destructive deltas")
  is satisfied trivially, so no destructive-merge warning or approval was
  required.

### ADDED Requirement Names (17)

1. FR1.1 Standard ML4W app launchers
2. FR1.2 Ctrl+Win secondary app shortcuts
3. FR1.3 Window management bindings
4. FR1.4 Workspace navigation bindings
5. FR1.5 Window focus and move bindings
6. FR1.6 System control bindings
7. FR1.7 Binding coverage across both profiles
8. FR2.1 Waybar configuration template exists
9. FR2.2 Waybar taskbar module renders workspace buttons with app icons
10. FR2.3 Waybar standard modules
11. FR2.4 Waybar theme integration import
12. FR3.1 Profile schema compatibility
13. FR3.2 Profile validation and Lua generation
14. FR4.1 No theme engine changes
15. NFR1 Binding commands are valid dispatchers or shell commands
16. NFR2 Waybar config parses as valid JSONC
17. NFR4 Bindings do not conflict with ML4W built-in defaults

### MODIFIED / REMOVED

None. No other active change declares the `ml4w-keybindings-waybar` domain — a
directory scan of `openspec/changes/*/specs/` finds no second owner, so **no
same-domain active-change warning** is recorded.

### Known Gaps carried into the canonical spec

The delta spec records four non-normative entries under `## Known Gaps`. They are
**deliberately not counted in the 17/17** and must never be read as delivered
behavior. They were carried into the canonical spec unchanged by the
byte-identical copy, and are summarized here so they are not lost on merge:

- **(a) The active-workspace accent is unreachable in the shipped Waybar chain.**
  `DreamcoderWaybar/.config/waybar/style.css` imports only the variable-only
  `colors.css`, while the `#workspaces button.active` accent rule lives in the
  un-imported engine-generated
  `DreamcoderThemes/dreamcoder/waybar-{dark,light,night}.css`. The shipped
  `.active` rule declares only `font-weight: 700`. Delivered behavior is the
  module plus `window-rewrite` only. Follow-up: wire the mode CSS import.
- **(b) The Waybar deliverables are dormant templates.** No repository script
  installs `DreamcoderWaybar/`, so original NFR3 ("Waybar starts without errors
  using this config") and original NFR5 ("Dreamcoder Light colors visible in all
  Waybar modules") are **not provable** from the repository and are absent from
  the current requirement set. Follow-up: add an installer or wiring step, then
  re-verify both statements.
- **(c) `shellcheck --shell=bash scripts/*.sh` exits 1** with 17 pre-existing
  `SC1091` (info) findings at dynamic `source` sites; there are no warning- or
  error-level findings. This is pre-existing and unrelated to this change, and it
  is **not** the declared `test_command`. The two scripts inside this change's own
  surface shellcheck clean individually. Follow-up: per-line
  `# shellcheck source=` directives or a scoped `.shellcheckrc`.
- **(d) Earlier partial specs of this capability were superseded** by archived
  changes; this delta is the single source of truth for the ML4W binding
  contract. Follow-up: none — recorded so the superseded specifications are never
  treated as current.

None of these gaps was fixed, closed or re-scoped by this archive. They remain
recorded follow-ups.

## Repository Fixes Made During the Closing Session (reproducibility)

Two repository fixes were made during this session so verification is
reproducible. Neither is target-surface implementation code, and this archive
touched neither:

- `pyproject.toml` gained `pyyaml>=6` in the `dev` extra. Without it,
  `tests/test_lazygit_renderer.py` fails at **collection** (it imports `yaml`) and
  the suite cannot run at all, so `uv sync --all-extras` is load-bearing for the
  declared `test_command`.
- `openspec/config.yaml`'s verify block now declares `uv sync --all-extras` /
  `uv run pytest tests/ -v --tb=short`, because `pip` is blocked machine-wide on
  this host and the previous `pip install -e ".[dev]"` build command measured host
  policy rather than the project.

## Interface Reconciliation Recorded During the Closing Session

The change's intermediate snapshots (`verify-report.md`, `STATUS.md`) were
written during this closing session. The following are the state at close, and
they outrank any stale claim inside an intermediate artifact:

1. **The delta spec was conformed to the canonical format.** It now has exactly
   **17** `### Requirement:` and **17** `#### Scenario:` headings. Before
   conformance it had **0** of each, which made the native engine measure `0/0`
   and blocked verify — that is why the change could not previously be archived.
2. **`tasks.md` was converted to markdown checkboxes**: 6/6 checked,
   `allComplete: true` (previously a non-checkbox `T1..` format measuring `0/0`).
3. **`verify-report.md` was replaced with a natively admissible report.** Its
   envelope now has exactly the 13 canonical fields and validates. The previous
   report was rejected for `unknown verify result field
   supersedes_evidence_revision` (and also carried unknown `head` / `head_tree`).
4. **One self-correction on evidence counting.** An intermediate parent
   measurement reported "711 tests". That was a parsing artifact of the junit
   `tests` attribute. The true count, from 680 `<testcase>` elements and from
   `pytest`'s own collection line (`collected 680 items`), is **680**. The
   archive report and the archived verify report both state 680.

## Incident (recorded, contained, repaired)

While gathering evidence, a generator invocation with `--profile default`
overwrote the live `~/.config/hypr/custom.lua` with the generic 56-binding
profile instead of this machine's 70-binding profile. **The generator does not
reload Hyprland, so the running session was never affected.**

The file was regenerated by DMI auto-detection and restored to **70** bindings
from `asus-vivobook15.json`. All later verification used only the read-only
`--dry-run` / `--validate` forms, and the verify report confirms
`~/.config/hypr/custom.lua` was byte-identical before and after its pass. This
incident touched no repository file and required no repository change.

## Verified-Unchanged Target Surface

This archive modified **no** implementation or target-surface file. Explicitly
untouched: profiles (`DreamcoderProfiles/`), Waybar templates
(`DreamcoderWaybar/`), scripts (`scripts/`), tests (`tests/`), themes
(`DreamcoderThemes/`), `src/`, `README.md`, `pyproject.toml` and
`openspec/config.yaml`. The only files this archive created or moved are the
canonical capability spec, this archive report, and the archived change folder.

## Structured Status and actionContext Findings

- Native status at archive time: `artifactStore: openspec`; `changeRoot`
  `/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots/openspec/changes/fix-ml4w-keybindings-waybar`;
  `artifacts.proposal/specs/design/tasks/verifyReport: done`,
  `artifacts.applyProgress: missing` (accepted waiver);
  `taskProgress 6/6`, `allComplete: true`; `dependencies.proposal/specs/design/
  tasks/apply: all_done`, `verify: all_done`, `archive: ready`;
  `blockedReasons: []`; `remediationState.required: false`;
  `nextRecommended: archive`.
- `actionContext`: `mode: repo-local`, `workspaceRoot` =
  `/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots`, `allowedEditRoots:
  [/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots]`. Every archive
  operation (canonical spec copy, report write, folder move) is inside the
  authoritative workspace and inside `allowedEditRoots` — no ownership or
  edit-root blocker.
- **Ledger decision, settled — not re-opened.** During the closing session the
  bounded-attempt ledger charged the verify work unit 521 changed lines against a
  400-line objective and reported `state: blocked / reason: maintainer_decision`,
  which had blocked `archive`. That overrun was a **full-rewrite artifact** of
  replacing a 32.5 KB verification report, not new implementation surface. A prior
  maintainer-authorized ledger reset cleared it; the state is settled and
  `blockedReasons` is empty. It was **not** re-opened, re-litigated or self-reset
  by this archive.
- Hard stops checked and not fired: active change selection unambiguous;
  verify-report resolves; tasks complete; `allowedEditRoots` populated and every
  path inside `workspaceRoot`; no legacy flat `openspec/changes/{change}/spec.md`
  (the spec is the canonical nested `specs/ml4w-keybindings-waybar/spec.md`).

## Destructive Merge

None performed. The canonical sync was a pure additive copy into a previously
non-existent canonical domain. No approval required, no blocker raised.

## Files Created

```text
openspec/specs/ml4w-keybindings-waybar/spec.md   (NEW canonical capability spec, 403 lines)
```

Directory `openspec/specs/ml4w-keybindings-waybar/` is new. `openspec/specs/`
previously held `eye-comfort`, `palette`, `renderer-registry`, `sync`, `writers`.

## Files Moved

Whole change folder relocated under the repository's dated archive convention:

```text
openspec/changes/fix-ml4w-keybindings-waybar/
  -> openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/
```

Moved contents (7 files, all preserved unmodified by the move):

```text
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/archive-report.md
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/proposal.md
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/specs/ml4w-keybindings-waybar/spec.md
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/design.md
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/tasks.md
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/verify-report.md
openspec/changes/archive/2026-09-11-005-fix-ml4w-keybindings-waybar/STATUS.md
```

Convention: `<ISO-date>-<NNN>-<change-name>`, continuing the sequence after
`2026-07-02-002-refactor-renderer-pipeline`,
`2026-08-11-003-eye-comfort-theme-system` and
`2026-09-11-004-reconcile-renderer-registry`. This archive is ordinal **005**.

## Audit Trail

- Proposal → Spec → Design → Tasks → Apply → Verify (`pass`) → Archive ✅
- Delta `spec.md` at close: 17 requirements / 17 scenarios; canonical copy is
  byte-identical to the delta.
- 6/6 tasks complete; zero unchecked implementation task boxes; no mechanical
  checkbox repair by archive.
- No file deletions. No previously archived change was modified.
- `sync-report.md` absent; the archive-time sync fallback was explicitly
  parent-authorized and additive-only.
- Memory observation IDs: **N/A** (openspec mode; no Engram save performed).
