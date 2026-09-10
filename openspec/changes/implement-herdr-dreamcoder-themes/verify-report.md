```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:c0a8990bf1496d9cf7059091f228fc7d33d6035cbcd13ca16b33905a724f6d2e
verdict: fail
blockers: 1
critical_findings: 1
requirements: 5/6
scenarios: 11/12
test_command: PYTHONPATH=src python -m pytest tests/ --color=no
test_exit_code: 0
test_output_hash: sha256:d8b813f5f12586a07f40ae8a709c5ecf8c1f2a16721fc52734a6cf6f1b9d2da1
build_command: ruff check src/dreamcoder_theme/herdr_activation.py src/dreamcoder_theme/cli_handlers.py src/dreamcoder_theme/herdr_contract.py src/dreamcoder_theme/renderers_herdr.py
build_exit_code: 0
build_output_hash: sha256:5b196eb3a6acb50d3fa398d04ca284985cc1ffec870e940264b00780bfd2c971
```

## Verification Report

**Change**: implement-herdr-dreamcoder-themes
**Version**: N/A (single spec delta, no prior version)
**Mode**: Standard (Strict TDD not declared active for this repo)

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 20 |
| Tasks complete | 18 |
| Tasks incomplete | 2 (`sdd-owner: parent` — "start/reuse bounded native review", "validate review receipt") |

The 2 incomplete rows are parent-owned lifecycle rows gated on receipt-driven development (RDD). `gentle-ai review mode status` for this clone reports RDD OFF (default deciding source). Per this repository's own delivery contract, delivery under a disabled RDD switch follows ordinary repository policy and these rows are correctly unmanaged/deferred, not an apply-phase failure. This does not block spec/implementation verification, which is independent of review-lock state per the sdd-verify hard rules ("Review state is informational and never a verification prerequisite").

### Build & Tests Execution

**Build**: PASSED
```text
$ ruff check src/dreamcoder_theme/herdr_activation.py src/dreamcoder_theme/cli_handlers.py src/dreamcoder_theme/herdr_contract.py src/dreamcoder_theme/renderers_herdr.py
All checks passed!
```

**Tests**: 609 passed, 2 warnings, 31 subtests passed (full suite); 95 passed (focused: `test_herdr_contract.py`, `test_herdr_theme_generation.py`, `test_herdr_activation.py`, `test_cli_theme_activation.py`)
```text
$ PYTHONPATH=src python -m pytest tests/test_herdr_contract.py tests/test_herdr_theme_generation.py tests/test_herdr_activation.py tests/test_cli_theme_activation.py -v
95 passed in 1.23s

$ PYTHONPATH=src python -m pytest tests/ --color=no
609 passed, 2 warnings, 31 subtests passed in 11.15s
(2 warnings are pre-existing and unrelated: a palette-divergence UserWarning
in test_dreamcoder_sync.py from a separate in-flight lowercase-hex refactor,
and a pytest fixture-deprecation warning in test_renderer_contract.py)
```

`PYTHONPATH=src python scripts/verify-theme-health.py` — PASSED (exit 0, "Dreamcoder theme health guardrails passed"), independently re-run.

**Coverage**: Not measured in this verify pass (project convention is `--cov-fail-under=40`, not re-run here; not gating for this report).

All test executions above were run independently by this verify phase, not copied from `apply-progress.md`.

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Exact supported runtime | Version gate fails closed | `test_herdr_activation.py::*version*` (missing/non-zero/timeout/malformed/wrong-version) | COMPLIANT |
| Environment-derived active target | Override and fallback resolution | `test_herdr_activation.py::*resolve_herdr_target*`, `*override*`, `*xdg*` | COMPLIANT |
| Environment-derived active target | Unsafe target resolution | `test_herdr_activation.py::*unsafe*`, `*symlink*`, `*nul*`, `*relative*` | COMPLIANT |
| Complete bounded variants | Light and Dark preserve canonical non-theme values | `test_herdr_theme_generation.py::test_herdr_output_uses_exact_allow_list_and_canonical_tokens` | **FAILING** (test asserts the wrong value; see CRITICAL-1) |
| Backup-before-mutation and atomic replacement | Existing target is safely replaced | `test_herdr_activation.py::*existing_target*`, `*backup*` | COMPLIANT (mechanism-level, synthetic fixtures only) |
| Backup-before-mutation and atomic replacement | Absent target is created safely | `test_herdr_activation.py::*absent_target*` | COMPLIANT |
| Backup-before-mutation and atomic replacement | Backup or write failure | `test_herdr_activation.py::*backup_failure*`, `*stage_write*`, `*replace_failure*` | COMPLIANT |
| Documented reload and truthful recovery | Applicable reload succeeds | `test_herdr_activation.py::*reload_succeeds*` | COMPLIANT |
| Documented reload and truthful recovery | Reload is not applicable | `test_herdr_activation.py::*reload*not_requested*` | COMPLIANT |
| Documented reload and truthful recovery | Reload failure restores prior state | `test_herdr_activation.py::*reload_failure*restore*` | COMPLIANT |
| Bounded failure safety and non-goals | Unsafe active configuration is rejected | `test_herdr_activation.py::*source_safety*`, `*malformed*` | COMPLIANT |
| Bounded failure safety and non-goals | Scope remains bounded | Manual `git status`/`git diff --stat` scoping (see Protected Paths below); no automated scope test exists | COMPLIANT (verified by inspection, not by an automated test) |

**Compliance summary**: 11/12 scenarios compliant, 1 FAILING.

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Exact version gate (`herdr 0.7.3`) | Implemented | `_herdr_version_matches` in `herdr_activation.py`; strict equality after trailing-newline strip. |
| XDG/override path resolution | Implemented | `resolve_herdr_target` matches design.md precedence exactly; no hardcoded path. |
| Backup/staging/atomic replace/fsync | Implemented | `_run_transaction` matches design.md step sequence exactly, including identity re-check and parent `fsync`. |
| Documented reload only | Implemented | `_attempt_reload` invokes exactly `["herdr", "server", "reload-config"]`, no shell, bounded timeout. |
| Restoration on failure | Implemented | `_attempt_restore` covers both existing-target and absent-target cases. |
| `[ui]`/`[keys]` canonical, palette-independent | **NOT implemented** | See CRITICAL-1. |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| §1 Static configuration ownership — `[ui]`/`[keys]` are fixed renderer constants, not palette tokens | **No** | `renderers_herdr.py` still maps `[ui].accent` to the Dreamcoder palette `accent` token via `_PALETTE_UI_FIELDS = {"accent": "accent"}`, inherited unchanged from the pre-existing PR1 `herdr_contract.py`/`HERDR_073_EVIDENCE.allowed_ui_fields = ("accent",)` architecture. Design.md explicitly specifies `[ui]\naccent = "#6FA0AF"` as a fixed constant. |
| §2 Exact runtime gate before any mutation | Yes | Confirmed by code and 5+ fault-injection tests. |
| §3 Explicit mode/source selection, TOML shape validation | Yes (module-level) — but see CRITICAL-1 for the practical consequence | `_validate_source` correctly implements `_CANONICAL_UI = {"accent": "#6FA0AF"}` per design.md — it is the checked-in **source files** that do not match this constant, not the validator. |
| §4 Runtime target resolution precedence | Yes | Matches exactly. |
| §5 Transaction boundaries/atomicity | Yes | Matches exactly, including sibling-file/exclusive-create/fsync sequence. |
| §6 Reload applicability via explicit `reload_requested` only | Yes | No process/socket/PID inspection present. |
| "First slice reviewable below 400 authored lines" | No (explicitly acknowledged) | Slice 2 totals ~1,280 authored lines; `size:exception` was requested and granted by the orchestrator with a documented rationale (dirty-workspace ledger inflation, not padding). Accepted as WARNING, not CRITICAL, given the recorded exception. |

### Issues Found

**CRITICAL**:

1. **`[ui].accent` is palette-driven in the shipped renderer and checked-in 0.7.3 variants, contradicting proposal.md, specs/herdr/spec.md, and design.md, and this breaks the activation feature end-to-end against real repository files.**
   - `proposal.md` Success Criteria #3: "Both variants include `[ui]` with `accent = "#6FA0AF"` exactly." — **violated**. Actual checked-in `config.dark.toml` has `[ui] accent = "#A5B4FC"`; `config.light.toml` has `[ui] accent = "#824f16"`.
   - `proposal.md` Success Criteria #5: "`[ui]` and `[keys]` are identical between Light and Dark and are not derived from Dreamcoder palette tokens." — **violated**; `[ui].accent` differs between the two variants and is derived from the Dreamcoder `accent` token (confirmed: dark value equals the Dreamcoder Dark palette accent, light value equals the Dreamcoder Cocoa/Lúcuma palette accent).
   - `specs/herdr/spec.md` Requirement "Complete bounded variants" / Scenario "Light and Dark preserve canonical non-theme values": "both variants MUST contain the canonical `[ui]` values exactly, including `accent = "#6FA0AF"`" — **violated**.
   - `design.md` Decision 1 explicitly states `[ui]` and `[keys]` "are renderer constants copied from the approved upstream configuration and are not represented as palette tokens," with the exact example `accent = "#6FA0AF"`. The shipped `renderers_herdr.py` instead treats `accent` in `_PALETTE_UI_FIELDS` as a palette-token-mapped field, inherited unchanged from the older PR1 `herdr_contract.py`/`HERDR_073_EVIDENCE` architecture (`allowed_ui_fields=("accent",)`) that predates this change's design.md.
   - **Reproduced independently, not from apply-progress.md claims**: `herdr_activation.py`'s own `_validate_source()` (which correctly implements the design.md canonical constant `_CANONICAL_UI = {"accent": "#6FA0AF"}`) rejects **both** checked-in 0.7.3 source files as non-conformant. A live call to `activate_herdr("dark", reload_requested=False, ...)` against the real repository source root, with the version gate mocked to pass, returns `status='precondition-failed', stage='source', message='checked-in Herdr dark source is missing or does not match the canonical shape'` — confirmed for both `dark` and `light`.
   - **Root cause of the undetected gap**: every test in `test_herdr_activation.py` overrides `source_root` with a synthetic fixture built to match `_CANONICAL_UI`/`_CANONICAL_KEYS`; none exercises the default `_SOURCE_ROOT` pointing at the actual checked-in `DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3/*.toml` files. `test_herdr_theme_generation.py` independently asserts the *opposite* contract (`parsed["ui"] == {"accent": VARIANTS[mode]["accent"]}`, i.e. palette-driven), so neither test suite ever cross-checks the two slices against each other.
   - **Impact**: the managed activation feature — the entire subject of this change and Slice 2 — cannot successfully activate either variant against the repository's own shipped configuration files. It is not a theoretical edge case; it is the default, only-supported code path.
   - This blocks archive. It requires either (a) rewriting `renderers_herdr.py`'s 0.7.3 output to emit the fixed canonical `[ui]` constant (as design.md specifies) and regenerating the two checked-in files, or (b) a design amendment if palette-driven `[ui].accent` is actually the intended contract — in which case proposal.md, specs/herdr/spec.md, and design.md all require correction, and `herdr_activation.py`'s `_CANONICAL_UI` must be updated to match, plus a new integration test must exercise the real `_SOURCE_ROOT` end-to-end. Task rows Slice 1 RED #2 and GREEN #1 in `tasks.md` are marked complete but do not reflect this actual code state.

**WARNING**:

1. Slice 2's review-line budget (400 authored lines) was not met (~1,280 authored lines for the module + full fault-injection matrix, plus a ~15-line cross-change fix to `cli_handlers.py`). A `size:exception` was requested and granted by the orchestrator with a documented rationale (native ledger inflated by ~50 unrelated pre-existing dirty files, not by this slice's own surface). Recorded here for traceability; not a re-blocking issue given the explicit grant.
2. `renderers_herdr.py`'s `herdr_content()` accepts `mode in {"dark", "light", "night"}`, and `REGISTRATIONS` declares `modes=frozenset({"dark", "light", "night"})`, whereas design.md Decision 1 states the renderer "accepts only `dark` or `light`." In practice no `night` 0.7.3 artifact is generated or shipped by this change (only 0.7.3 dark/light exist), so this is a latent boundary looseness rather than an observed non-goal violation; recommend tightening the accepted-mode set for the 0.7.3 profile specifically, or documenting why `night` remains structurally accepted at the shared-renderer level.
3. `apply-progress.md`'s Slice 1 claim "Updated the renderer ... with canonical upstream `[ui]` and `[keys]` values" and the corresponding checked task rows do not match the actual shipped code (see CRITICAL-1). Future apply-progress entries should be verified against a real activation call against the checked-in source root, not only against unit tests using synthetic fixtures.
4. Two full-suite warnings persist (`test_dreamcoder_sync.py` palette-divergence UserWarning, `test_renderer_contract.py` pytest fixture-deprecation warning). Both are independently confirmed pre-existing and unrelated to this change (in-flight lowercase-hex CSS refactor and an upstream pytest deprecation, respectively); not a regression introduced by this change.

**SUGGESTION**:

1. Add one integration test that calls `activate_herdr()` with `source_root` defaulted (i.e., pointed at the real `DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3/` tree) and a mocked `run` for the version/reload commands, asserting `status == "applied"`. This is the single test that would have caught CRITICAL-1 before it reached verify.
2. Consider a small cross-slice consistency test that renders each variant via `renderers_herdr.py` and asserts the byte-for-byte result is accepted by `herdr_activation._validate_source()`, so the two independently developed slices cannot silently diverge again.

### Protected Paths and Scope Verification

Independently confirmed via `git status --porcelain` and `git diff --stat`, scoped to this change:

- No changes to Hyprland renderers/config beyond what is present as unrelated pre-existing dirty-workspace state (`DreamcoderThemes/dreamcoder/hyprland*.conf`, confirmed hex-color-only diffs from a separate in-flight lowercase-hex CSS refactor, not touched by this change's task list).
- No changes to `DreamcoderGhostty/` beyond the same unrelated pre-existing dirty-workspace state (confirmed hex-color-only diffs).
- No changes to `DreamcoderThemes/dreamcoder/tokens.json` by this change (confirmed hex-color-only diff from the same unrelated refactor; this change's tasks.md explicitly forbids touching this file and it was not touched by Herdr-scoped work).
- No changes to Fish/shell startup scripts by this change (one untracked `DreamcoderShell/.config/fish/completions/copilot.fish` exists in the workspace but is unrelated to this change and not listed among this change's files-changed).
- No changes to `openspec/changes/repair-dreamcoder-theme-rollout/` or any other OpenSpec change's artifacts (not present in `git status --porcelain` at all).
- Files actually changed by this change, confirmed by `git status --porcelain`: `DreamcoderHerdr/.config/herdr/dreamcoder/0.7.3/config.{dark,light}.toml`, `src/dreamcoder_theme/{herdr_activation.py (new),cli_handlers.py,herdr_contract.py,renderers_herdr.py}`, `tests/{test_herdr_activation.py (new),test_herdr_contract.py,test_herdr_theme_generation.py,test_cli_theme_activation.py}`, `pyproject.toml`, and this change's own `tasks.md`/`apply-progress.md`. `DreamcoderHerdr/.config/herdr/dreamcoder/0.8.0/config.*.toml` are also modified in the working tree but are confirmed unrelated (different Herdr version profile, out of this change's declared scope, and not listed in this change's files-changed records).

### Verdict

**FAIL**

One CRITICAL finding blocks archive: the shipped `[ui].accent` value is palette-driven in both the renderer and the checked-in 0.7.3 static variants, directly contradicting proposal.md Success Criteria #3/#5, specs/herdr/spec.md's "Complete bounded variants" requirement, and design.md Decision 1 — and this is not a paper-only gap: a live `activate_herdr()` call against the real checked-in source root fails source validation for both `dark` and `light`, meaning the managed activation feature this change exists to deliver does not work against the repository's own shipped files. All other requirements/scenarios (11/12), the full pytest suite (609 passed), the focused suite (95 passed), ruff, and `verify-theme-health.py` are independently confirmed clean. Recommend routing back to `sdd-apply` to reconcile the renderer's `[ui]` output with the canonical constant (or amend the design/spec if palette-driven `[ui]` is actually intended, with the activation module's `_CANONICAL_UI` and its documentation updated to match) and add the missing default-`source_root` integration test before re-verifying.

## Key Learnings

1. Independent reproduction found that `activate_herdr` rejects both checked-in Herdr 0.7.3 source files at runtime.
2. Every activation test overrides `source_root` with a synthetic fixture, so no test exercises the real checked-in files.
3. The renderer's `[ui].accent` field is still palette-driven, contradicting the design's fixed-constant contract.
4. Full pytest suite passing does not prove spec compliance when the covering test asserts the wrong expected value.
5. Unrelated pre-existing workspace dirt (Ghostty, Hyprland, tokens.json) was confirmed out of this change's scope via git diff.
