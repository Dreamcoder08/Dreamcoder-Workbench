# Dreamcoder Dark visual-quality benchmark

## Objective and status

**Authorized for autonomous local implementation.** On 2026-10-23 the user approved advancing autonomously after the proposed black/near-black/indigo direction. Improve Dreamcoder Dark's legibility and visual hierarchy using measured comparisons with current dark interfaces, without copying a vendor palette or assuming that newer means better. Local scoped implementation, verification and attributable work-unit commits are authorized; publication and live activation remain excluded.

The problem is not a proven palette failure: token-level tests exist, but rendered role contrast, interaction states, terminal color distinctions, and cross-target visual parity still need dated evidence. Better contrast must improve actual reading and state recognition, not just pass a single ratio.

This is a **follow-on visual-quality benchmark**, not a restart or completion of [OLED Black with controlled glass](oled-black-glass.md). That separate feature's delivery and live-activation tasks remain open. Reuse its verified black-canvas and surface-policy work; do not attribute its dirty-tree changes, unfinished verification, or historical push authorization to this feature.

## Scope and constraints

- Approved direction: preserve the `#000000` Dark canvas and existing near-black scroll/functional surfaces in `modes.dark.surface_policy`; prefer a calm neutral hierarchy and retain the indigo identity. Specific token changes still require measured justification.
- Preserve Light/Dusk source and output behavior. Add no canonical mode. Avoid automatic palette churn when current values pass and no measurable improvement is demonstrated. Never hand-edit `docs/generated/dreamcoder-theme-preview.md`.
- Compare actual rendered foreground/background pairs, accounting for alpha and backdrop where relevant; token-only checks are insufficient. Include selection, focus, hover, disabled, diagnostics, terminal ANSI, and syntax distinctions.
- Acceptance floors: WCAG 2.2 contrast at least 4.5:1 for normal text, 3:1 for large text, and 3:1 for applicable UI component/state boundaries. Aim for 7:1 on primary reading text; that target is not a universal requirement. Existing mode-specific APCA floors are supplementary project guardrails, **not** W3C conformity. Document exceptions and role applicability rather than treating every token as text.
- Glare and OLED smear require visual/device assessment; neither ratios nor static previews prove comfort on every display. No absolute “world best,” hardware-proof, live-pixel, or activated-mode claim.
- Derive exact source edit surfaces before each writer. This documentation update changes no renderer, token, generated output, installed setting, credential, mode, or running process. No remote work.

## Tasks and route

All tasks are open. Earlier exploration is input evidence, not completion or commit proof. Each task uses the **delegated** route: research/mapping, preparation for writing, multi-file behavior changes, or command verification exceed the inline route. The parent performs a structural spot check; a bounded writer/verifier reports observed results. Approximately 400 authored changed lines per task is advisory, never a reason to omit tests or split coherent behavior.

- [ ] **DB1 — Measure baseline and benchmark dated references.** Record the contrast/distinction matrix below and adversarial finding: vendor imitation is not justified by current contrast evidence. Date-windowed official-source checks found no new dated official palette specification; publication evidence is unavailable, not assumed from access dates. Read-only research is drafted, but task closure and commit evidence are pending.
- [ ] **DB2 — Improve Dark ANSI semantics only where justified.** Approved local direction retains canonical tokens, black/near-black surfaces, and non-ANSI lavender/indigo roles. In `src/dreamcoder_theme/palette.py`, change only the Dark `ansi` derivation: slot 6 to `mix(success, info, .5)` cyan and slot 14 to `mix(cyan, text, .15)`, through the existing guard pipeline; all other slots unchanged. Add `tests/test_dark_ansi_semantics.py`. Observe deterministic RED on current bytes, then GREEN for normal/bright cyan hue, magenta/cyan separation (a project criterion, not a WCAG standard), 4.5:1 contrast floors, fixed Light/Dusk output snapshots, and cross-terminal parity. No token churn is authorized by this finding.
- [ ] **DB3 — Resolve renderer parity/state-legibility evidence.** Map exact terminal output surfaces before assigning a writer. If DB2 propagates through existing renderers and states remain legible, record a no-change disposition rather than rewrite them. Correct only independently proven renderer gaps with observed RED/GREEN where deterministic; keep selection/focus/hover/disabled/diagnostics and syntax distinction in the evidence matrix.
- [ ] **DB4 — Produce reproducible visual evidence.** Use existing preview tooling and a static contrast/distinction report; do not hand-edit generated artifacts. Compare target outputs and alpha/backdrop conditions, preserve Light output, and disclose missing live screenshots, device glare/smear, and runtime proof.
- [ ] **DB5 — Verify and prepare work-unit delivery.** Have the writer run applicable checks and an independent verifier validate high/unassessable risk while RDD is off. Inspect attribution against the inherited dirty tree, commit only feature work units on the dedicated branch, and record exact command results and commit identities. No push, PR, merge, reload, activation, or old-rollout delivery is authorized.

## Preliminary evidence and freshness gaps

- `DreamcoderThemes/dreamcoder/tokens.json:7-13,80-88` defines Dark values/surface policy; `tests/test_dark_neutral_palette.py:84-108,128-154`, `tests/test_nvim_readability.py:127-139`, and `tests/test_terminal_readability.py:22-35` cover existing token/renderer expectations. These are explorer observations, **not** tests rerun for this document.
- [OpenAI appearance guidance](https://help.openai.com/en/articles/11958281-updating-your-visual-experience-on-chatgpt), accessed 2026-10-23, establishes appearance controls but no verified publication date or canonical hex palette. [Anthropic appearance guidance](https://support.anthropic.com/en/articles/8887527-how-do-i-switch-to-dark-mode-on-claude-ai), accessed 2026-10-23, establishes appearance settings only; a fetched localized version showed 2026-03-16, not a verified full color system.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and its [non-text contrast explanation](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) ground the contrast checks. The [WCAG 3.0 draft dated 2026-03-03](https://www.w3.org/TR/2026/WD-wcag-3.0-20260303/) leaves its algorithm unsettled; it is not a conformance claim.
- The earlier 365-day vendor search and undated week/month anecdotes **did not establish** a new official palette. The bounded dated checks below close that research gap only as a documented absence of verified publication evidence. Do not invent release dates, screenshots, color values, or device proof.

### DB1 read-only findings (2026-10-23; not yet task closure)

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

## Delivery and recovery

Feature branch: `feat/dark-design-benchmark`, created from `d499b13aa52437b63b10ccf27cdc0331cd690052` without altering inherited dirty bytes. Stage only new feature files or attributable hunks; never stage inherited implementation. Historical authorization recorded in the older OLED task document does not authorize publication here. RDD reports off, decided by clone-local preference; keep it off and use ordinary functional/independent verification.

Delivery strategy: `ask-on-risk`. Revised authored forecast is 250–380 lines for targeted code/tests, static evidence, and documentation; generated files excluded. Re-evaluate before commits without cosmetic line shaving. If forecast or running authored count exceeds about 400 before a later commit, ask once for `stacked-to-main` versus `feature-branch-chain`; record slice boundaries and commit identities then. No commit evidence exists yet. RDD is off; assess an actual writer diff for proportional independent verification, treating failed assessment as unassessable/high. A passive planning document has no meaningful test-first RED; structural and Markdown checks are appropriate.

**Progress:** 0/5 tasks complete; DB1 research and the Dark-only decision are recorded, but DB1 closure/commit is pending. **Next step:** parent mirrors and commits this documentation unit, then delegates DB2 with the exact source/test surfaces above and mapped terminal outputs. Record failed, skipped, unavailable, and pending checks explicitly as work proceeds.
