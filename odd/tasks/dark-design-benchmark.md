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

All five tasks are closed by local work-unit evidence. Each task used the **delegated** route: research/mapping, preparation for writing, multi-file behavior changes, or command verification exceeded the inline route. The parent performed a structural spot check; a bounded writer/verifier reported observed results. Approximately 400 authored changed lines per task remained advisory, never a reason to omit tests or split coherent behavior.

- [x] **DB1 — Measure baseline and benchmark dated references.** Contrast/distinction matrix and scoped premise check recorded below. Date-windowed official-source checks found no new dated official palette specification; publication evidence is unavailable, not assumed from access dates. Markdown validation passed; work-unit commit `66725236e0a54e650ef46f770c105181f77ff34d` contains only this document.
- [x] **DB2 — Improve Dark ANSI semantics only where justified.** Dark `ansi` derives slot 6 from `mix(success, info, .5)` and slot 14 from `mix(cyan, text, .15)` through the existing guard. The new test observed meaningful RED then GREEN; other Dark slots, Light/Dusk outputs, canonical tokens, and non-ANSI roles remained unchanged.
- [x] **DB3 — Resolve renderer parity/state-legibility evidence.** Existing Kitty, Ghostty, and Warp renderers propagated the change without renderer code edits. Named Dark variants match renderer output; the Ghostty Dark repository alias was aligned while the Kitty symlink and Light Warp alias were preserved. The static state matrix below records what is and is not proven.
- [x] **DB4 — Produce reproducible visual evidence.** The existing token preview was unchanged; a separate static ANSI-aware SVG/PNG before/after swatch and reproducible script were produced privately. Missing live screenshots, runtime proof, device glare/smear, and hover-only boundary proof remain explicit limitations.
- [x] **DB5 — Verify and prepare work-unit delivery.** Independent high/unassessable-risk verification and clean-tree hooks passed; attributable behavior, tests, artifacts, and documentation were committed locally as `8b86a0eaeb53d2f56e411d9dda84fd4225ef1037`. No push, PR, merge, reload, activation, or old-rollout delivery occurred.

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

### DB2–DB5 evidence (independently verified and locally committed)

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

The clean delivery worktree at `/home/dreamcoder08/Documents/PROYECTOS/dreamcoder-dots-worktrees/dark-design-benchmark` applied the exact eight-path staged candidate; only this document's link to pre-existing untracked `odd/tasks/oled-black-glass.md` was changed to a plain code locator so a clean checkout validates without a fake support file. The clean tree passed all 645 collected Python tests, seven focused ANSI tests, theme health, full Markdown validation, Ruff lint/check-only format, and mypy (56 source files). Its normal, enabled commit hooks all passed with identical source bytes and tree `b24c7b328b73b1bb9c2d428762dfff166a724877`; the source commit was fast-forwarded locally into the feature branch without changing the original checkout's index or working bytes.

Two earlier local commit attempts did not pass and were not waived: the original dirty checkout's pre-commit auto-stash exposed 37 mypy errors in two inherited untracked GTK/Qt files and 76 unrelated pytest failures; a clean-worktree attempt using system Python hit four `jsonschema` collection errors plus theme-health import failure. Using the already installed project `.venv` on `PATH` with private HOME/XDG resolved the dependency discovery issue. The successful hook also reported four incidental pre-commit environment setup messages; no explicit installer command was run, and network/download occurrence was not established. All candidate file hashes remained unchanged across the hooks.

## Delivery and recovery

Feature branch: `feat/dark-design-benchmark`, created from `d499b13aa52437b63b10ccf27cdc0331cd690052` without altering inherited dirty bytes. Stage only new feature files or attributable hunks; never stage inherited implementation. Historical authorization recorded in the older OLED task document does not authorize publication here. RDD reports off, decided by clone-local preference; keep it off and use ordinary functional/independent verification.

Delivery strategy: `ask-on-risk`. Actual authored changed lines were 60 (DB1) + 188 (source work unit) + 22 (this closure document) = **270**, excluding 16 generated terminal-file lines; the approximately 400-line delivery threshold was not reached. DB1's documentation commit is `66725236e0a54e650ef46f770c105181f77ff34d`; the coherent Dark ANSI source work-unit commit is `8b86a0eaeb53d2f56e411d9dda84fd4225ef1037`. RDD was off (`disabled/unmanaged`); native assessment was high/unassessable due to inherited untracked inventory, so independent verification was performed. The passive documentation unit had no meaningful test-first RED; structural and Markdown checks were used.

**Progress:** 5/5 tasks complete locally. The final isolated functional checks and independent verification passed with no code findings; the original dirty-overlay and system-Python hook failures were resolved by exact-tree clean-worktree verification, not waived. Private source backups and logs are retained at `/tmp/dark-ansi-tmx0117z/`; 41 inherited tracked files were preserved across the DB1 hook. Live operation and hardware comfort remain outside the verified scope.

**Next step:** local benchmark delivery is complete. Optional user-led device appraisal, live activation, and publication were not performed; this feature does not close the separate OLED rollout.
