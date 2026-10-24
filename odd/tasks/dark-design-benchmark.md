# Dreamcoder Dark visual-quality benchmark

## Objective and status

**Authorized for autonomous local implementation.** On 2026-10-23 the user approved advancing autonomously after the proposed black/near-black/indigo direction. Improve Dreamcoder Dark's legibility and visual hierarchy using measured comparisons with current dark interfaces, without copying a vendor palette or assuming that newer means better. Local scoped implementation, verification and attributable work-unit commits are authorized; publication and live activation remain excluded.

The problem is not a proven palette failure: token-level tests exist, but rendered role contrast, interaction states, terminal color distinctions, and cross-target visual parity still need dated evidence. Better contrast must improve actual reading and state recognition, not just pass a single ratio.

This is a **follow-on visual-quality benchmark**, not a restart or completion of `odd/tasks/oled-black-glass.md` (the pre-existing untracked local rollout record). That separate feature's delivery and live-activation tasks remain open. Reuse its verified black-canvas and surface-policy work; do not attribute its dirty-tree changes, unfinished verification, or historical push authorization to this feature.

## Scope and constraints

- Approved direction: preserve the `#000000` Dark canvas and existing near-black scroll/functional surfaces in `modes.dark.surface_policy`; prefer a calm neutral hierarchy and retain the indigo identity. Specific token changes still require measured justification.
- Preserve Light/Dusk source and output behavior. Add no canonical mode. Avoid automatic palette churn when current values pass and no measurable improvement is demonstrated. Never hand-edit `docs/generated/dreamcoder-theme-preview.md`.
- Compare actual rendered foreground/background pairs, accounting for alpha and backdrop where relevant; token-only checks are insufficient. Include selection, focus, hover, disabled, diagnostics, terminal ANSI, and syntax distinctions.
- Acceptance floors: WCAG 2.2 contrast at least 4.5:1 for normal text, 3:1 for large text, and 3:1 for applicable UI component/state boundaries. Aim for 7:1 on primary reading text; that target is not a universal requirement. Existing mode-specific APCA floors are supplementary project guardrails, **not** W3C conformity. Document exceptions and role applicability rather than treating every token as text.
- Glare and OLED smear require visual/device assessment; neither ratios nor static previews prove comfort on every display. No absolute “world best,” hardware-proof, live-pixel, or activated-mode claim.
- Derive exact source edit surfaces before each writer. This documentation update changes no renderer, token, generated output, installed setting, credential, mode, or running process. No remote work.

## Tasks and route

DB1 is closed; DB2–DB5 remain open until their work-unit commit and independent verification. Each task uses the **delegated** route: research/mapping, preparation for writing, multi-file behavior changes, or command verification exceed the inline route. The parent performs a structural spot check; a bounded writer/verifier reports observed results. Approximately 400 authored changed lines per task is advisory, never a reason to omit tests or split coherent behavior.

- [x] **DB1 — Measure baseline and benchmark dated references.** Contrast/distinction matrix and scoped premise check recorded below. Date-windowed official-source checks found no new dated official palette specification; publication evidence is unavailable, not assumed from access dates. Markdown validation passed; work-unit commit `66725236e0a54e650ef46f770c105181f77ff34d` contains only this document.
- [ ] **DB2 — Improve Dark ANSI semantics only where justified.** Approved local direction retains canonical tokens, black/near-black surfaces, and non-ANSI lavender/indigo roles. In `src/dreamcoder_theme/palette.py`, change only the Dark `ansi` derivation: slot 6 to `mix(success, info, .5)` cyan and slot 14 to `mix(cyan, text, .15)`, through the existing guard pipeline; all other slots unchanged. Add `tests/test_dark_ansi_semantics.py`. Observe deterministic RED on current bytes, then GREEN for normal/bright cyan hue, magenta/cyan separation (a project criterion, not a WCAG standard), 4.5:1 contrast floors, fixed Light/Dusk output snapshots, and cross-terminal parity. No token churn is authorized by this finding.
- [ ] **DB3 — Resolve renderer parity/state-legibility evidence.** Map exact terminal output surfaces before assigning a writer. If DB2 propagates through existing renderers and states remain legible, record a no-change disposition rather than rewrite them. Correct only independently proven renderer gaps with observed RED/GREEN where deterministic; keep selection/focus/hover/disabled/diagnostics and syntax distinction in the evidence matrix.
- [ ] **DB4 — Produce reproducible visual evidence.** Use existing preview tooling and a static contrast/distinction report; do not hand-edit generated artifacts. Compare target outputs and alpha/backdrop conditions, preserve Light output, and disclose missing live screenshots, device glare/smear, and runtime proof.
- [ ] **DB5 — Verify and prepare work-unit delivery.** Have the writer run applicable checks and an independent verifier validate high/unassessable risk while RDD is off. Inspect attribution against the inherited dirty tree, commit only feature work units on the dedicated branch, and record exact command results and commit identities. No push, PR, merge, reload, activation, or old-rollout delivery is authorized.

## Preliminary evidence and freshness gaps

- `DreamcoderThemes/dreamcoder/tokens.json:7-13,80-88` defines Dark values/surface policy; `tests/test_dark_neutral_palette.py:84-108,128-154`, `tests/test_nvim_readability.py:127-139`, and `tests/test_terminal_readability.py:22-35` cover existing token/renderer expectations. These are explorer observations, **not** tests rerun for this document.
- [OpenAI appearance guidance](https://help.openai.com/en/articles/11958281-updating-your-visual-experience-on-chatgpt), accessed 2026-10-23, establishes appearance controls but no verified publication date or canonical hex palette. [Anthropic appearance guidance](https://support.anthropic.com/en/articles/8887527-how-do-i-switch-to-dark-mode-on-claude-ai), accessed 2026-10-23, establishes appearance settings only; a fetched localized version showed 2026-03-16, not a verified full color system.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and its [non-text contrast explanation](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) ground the contrast checks. The [WCAG 3.0 draft dated 2026-03-03](https://www.w3.org/TR/2026/WD-wcag-3.0-20260303/) leaves its algorithm unsettled; it is not a conformance claim.
- The earlier 365-day vendor search and undated week/month anecdotes **did not establish** a new official palette. The bounded dated checks below close that research gap only as a documented absence of verified publication evidence. Do not invent release dates, screenshots, color values, or device proof.

### DB1 read-only findings (2026-10-23)

| Measured Dark pair or distinction | Baseline | Interpretation |
| --- | ---: | --- |
| Text / black canvas | 16.83:1 | Above primary 7:1 target. |
| Muted / black canvas | 12.42:1 | No demonstrated text contrast failure. |
| Subtle / black canvas | 8.73:1 | No demonstrated text contrast failure. |
| Text / surface 2 | 13.21:1 | No demonstrated text contrast failure. |
| Selection foreground / selection background | 9.11:1 | Pairwise contrast only; selected-state rendering still needs inspection. |
| Focus / black canvas | 5.71:1 | Pairwise contrast only; focus boundary still needs rendered inspection. |
| Generated ANSI slots | All unique and at least 4.5:1 | Uniqueness/contrast do not ensure hue distinction. |
| Dark ANSI 5 `#D8B4FE` / 6 `#D4B5FD` | RGB distance 4.24 | Nearly identical purple semantic slots; justify targeted cyan derivation, not broad palette replacement. |

Official-source checks covered 2026-10-17–23 (week), 2026-10-01–23 (month), and 2026-01-01–10-23 (year) across public OpenAI, Anthropic, GitHub Primer, and Apple pages. No newly dated official palette specification was established in those windows; accessible guidance and access on 2026-10-23 do not prove publication within a window. [Primer color considerations](https://primer.style/accessibility/design-guidance/color-considerations/) and [Primer color usage](https://primer.style/product/getting-started/foundations/color-usage/) support role/state-oriented design, not vendor hex copying. [WCAG2ICT](https://www.w3.org/TR/wcag2ict-22/) informs non-web applicability. OpenAI/Anthropic guidance above still lacks a verified canonical palette. This is a bounded public-source finding, not proof that no relevant release exists anywhere.

The adversarial premise check rejects a whole-palette refresh: measured text pairs already exceed targets, while the actionable defect is Dark ANSI semantic discrimination. Actual rendered states, backdrop blends, and hardware behavior remain unproven. The approved correction is Dark-only ANSI 6/14; do not claim a WCAG color-distance requirement or universal aesthetic ranking.

### DB2–DB5 candidate evidence (independently verified; pending source commit)

Dark ANSI 6 changed from `#D4B5FD` (violet, 11.83:1 on black) to `#58d3ca` (cyan, 11.59:1); ANSI 14 changed from `#5a94f3` (blue, 6.96:1) to `#6dd6ce` (bright cyan, 12.16:1). The normal cyan and ANSI 5 magenta hues are 175.61° and 269.19° (93.58° apart), and bright cyan is lighter than normal cyan. This hue criterion is project-specific, not WCAG conformance. The other 14 Dark slots and all 16 slots in each Light/Dusk mode match fixed pre-change outputs; canonical palette tokens and non-ANSI roles were not edited.

The existing Kitty, Ghostty, and Warp renderers propagate the two changed slots without renderer code changes. Their named Dark files byte-match renderer output. The Kitty repository alias is an internal symlink to its Dark variant; the Ghostty repository alias was updated in only ANSI 6/14 and now byte-matches its Dark renderer. The Warp repository alias byte-matches **Light** and was preserved. No selector, installed file, reload, or live activation was changed.

| Dark state/role pair | Static ratio | Evidence boundary |
| --- | ---: | --- |
| Text / canvas | 16.83:1 | Primary reading target met. |
| Selection foreground / background | 9.11:1 | Rendered terminal pair is identical across named variants; live selection not inspected. |
| Focus / canvas | 5.71:1 | Static pair only; live outline geometry not inspected. |
| Disabled / canvas | 8.73:1 | Static pair only; disabled behavior not inspected. |
| Diagnostic / canvas | 12.60:1 | Static pair only; diagnostic UI not inspected. |
| Comment / canvas | 13.62:1 | Syntax token distinction is static; editor rendering not inspected. |
| Hover fill / canvas | 1.85:1 | Below a 3:1 sole-boundary target; no claim that fill alone communicates hover. |

TDD: the first isolated pending-state run failed on the intended Dark cyan assertions; after correcting a copied Dusk baseline fixture, the RED run still failed only on the intended Dark cyan/rendered-variant assertions. The new seven-case test then passed. The initial full run found three Ghostty repository active-mirror identity failures and one stale diagnostic expectation; the Ghostty alias and only two exact expected ratios (`ansi6` 11.83→11.59, `ansi14` 5.64→10.52 in its modified-palette fixture) were corrected, not waived.

Final checks used the pending-state snapshot at `/tmp/dark-ansi-tmx0117z/snapshot`, isolated HOME/XDG directories, `PYTHONDONTWRITEBYTECODE=1`, the existing `.venv` interpreter, and pytest cache disabled. `python -m pytest -p no:cacheprovider -q tests/` passed at 100%; the focused ANSI/dual-gate/neutral/terminal/Neovim/GTK-QT suite passed; `scripts/verify-theme-health.py`, `scripts/validate-markdown-links.py`, Ruff lint and check-only formatting all passed. Full command logs are under `/tmp/dark-ansi-tmx0117z/`. An independent snapshot at `/tmp/dark-ansi-verify-guv4pve1/` confirmed 1,073 source files equivalent with no mutation, all 910 Python tests passing, and focused/health/Markdown/Ruff checks exiting 0. Reversing the candidate in a private copy confirmed the other 14 Dark slots and complete Light/Dusk source/render outputs remain unchanged; no code findings were reported.

The existing preview generator ran only in the snapshot and produced an unchanged preview hash because it reads tokens, not derived ANSI. An ANSI-aware static before/after swatch was rendered separately by `/tmp/dark-ansi-verify-guv4pve1/render_dark_ansi_swatch.py` using the standard library and installed `rsvg-convert`: PNG SHA-256 `5664f42a3a319ce9d268cabe6ffac811508b79d78d10dbb822ef8acd44395674`, SVG SHA-256 `90877d8e0ab9814023142c71df346d2da6ac2803be60cc5ffa08a3d9f84e0858`. It is private, static comparison evidence, not a checked-in generated preview or a live screenshot. Display glare/smear, runtime state, and device comfort remain unverified.

## Delivery and recovery

Feature branch: `feat/dark-design-benchmark`, created from `d499b13aa52437b63b10ccf27cdc0331cd690052` without altering inherited dirty bytes. Stage only new feature files or attributable hunks; never stage inherited implementation. Historical authorization recorded in the older OLED task document does not authorize publication here. RDD reports off, decided by clone-local preference; keep it off and use ordinary functional/independent verification.

Delivery strategy: `ask-on-risk`. Revised authored forecast is 250–380 lines for targeted code/tests, static evidence, and documentation; generated files excluded. Re-evaluate before commits without cosmetic line shaving. If forecast or running authored count exceeds about 400 before a later commit, ask once for `stacked-to-main` versus `feature-branch-chain`; record slice boundaries and commit identities then. DB1's documentation commit is recorded above; no source commit exists yet. RDD is off; assess an actual writer diff for proportional independent verification, treating failed assessment as unassessable/high. A passive planning document has no meaningful test-first RED; structural and Markdown checks are appropriate.

**Progress:** 1/5 tasks complete. DB1 commit is recorded above; DB2–DB5 remain open pending their source work-unit commit. Final isolated functional checks passed after source formatting and the four failures were corrected, not waived. Independent verification passed with no code findings. Private source backups and logs are retained at `/tmp/dark-ansi-tmx0117z/`; 41 inherited tracked files were preserved across the DB1 hook. Native assessment returned high/unassessable (untracked inventory); RDD remains off (`disabled/unmanaged`).

**Next step:** stage and commit only attributable source/test/artifact/documentation changes, then record the work-unit identity and final task status. Do not treat repository alias maintenance as permission to touch installed settings or selectors.
