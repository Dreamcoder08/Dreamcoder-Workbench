# Eye-Comfort Specification

## Purpose

Define the eye-comfort contract for Dreamcoder OS: one canonical APCA contrast implementation, independent blocking WCAG 2.2 + APCA gates, exactly two user-facing modes (Dreamcoder Light and Dreamcoder Dark) activated through the Dreamcoder CLI, declared coverage of every active color consumer, and fail-closed validation before any write — without medical claims, palette redesign, or renderer-interface changes.

## Requirements

### Requirement: Canonical APCA contrast implementation

The system MUST provide a single canonical package implementation of APCA luminance and polarity-aware `apca_lc(foreground, background)` in `src/dreamcoder_theme/_math.py`, preserving the currently cross-validated SAPC/APCA 0.0.98G-4g behavior. The three locations that currently copy an independent SAPC/APCA implementation — `scripts/verify-theme-health.py`, `scripts/generate-theme-preview.py`, and `tests/test_dreamcoder_global_design_system.py` — MUST import `apca_lc()` (and `contrast()` for the WCAG path) from the package and MUST NOT contain a copied production formula. `tests/test_apca_implementation.py` MUST remain cross-validation evidence against known vectors and MUST NOT become a fourth production implementation. `validate_palette()` in `src/dreamcoder_theme/palette.py` MUST return both WCAG and APCA validation errors so a palette failing either metric never reaches a renderer or writer.

#### Scenario: Single source of truth for APCA

- GIVEN `_math.py` exposes the canonical `apca_lc()` implementation
- WHEN any consumer (health script, preview generator, or test) computes APCA contrast
- THEN it imports the package function and yields results consistent with the cross-validated 0.0.98G-4g known vectors

#### Scenario: A duplicated SAPC formula is detected

- GIVEN a consumer file still contains a copied SAPC/APCA formula instead of importing from the package
- WHEN health validation or the focused test suite runs
- THEN validation MUST fail, naming the consumer and the duplicated formula location

#### Scenario: validate_palette reports both metrics

- GIVEN a palette where a pair passes WCAG but fails APCA, or passes APCA but fails WCAG
- WHEN `validate_palette()` runs
- THEN it MUST return an error for the failing metric and MUST NOT clear or waive the other metric's failure

### Requirement: Independent blocking WCAG and APCA dual gate

All enforced text and affordance pairs MUST satisfy BOTH the WCAG 2.2 minimum contrast floor and the mode-aware APCA Lc floors. WCAG MUST remain the legal accessibility floor, including at least 4.5:1 for semantic text and the preserved 7.0:1 preferred main-text and terminal selection rules. APCA MUST be independently blocking: passing WCAG MUST NOT waive an APCA failure, and passing APCA MUST NOT waive a WCAG failure. The blocking APCA floors MUST be read from the canonical guardrails in `DreamcoderThemes/dreamcoder/tokens.json` — `minimum_apca_body` (Lc 75), `minimum_apca_body_dark` (Lc 50), `minimum_apca_quiet` (Lc 44), `minimum_apca_ui` (Lc 60), `minimum_apca_ui_dark` (Lc 28), `minimum_apca_on_accent` (Lc 60), `minimum_apca_heading_light` (Lc 60), and `minimum_apca_heading_dark` (Lc 45) — and MUST NOT be duplicated as policy literals. Existing terminal ANSI, cursor, and selection WCAG floors MUST remain independently blocking.

#### Scenario: WCAG pass with APCA fail is blocking

- GIVEN a body-text pair that measures 5.0:1 WCAG but Lc 48 against the dark-background floor of 50
- WHEN validation runs
- THEN the gate MUST fail on APCA with the pair, measured Lc, and required threshold, and the WCAG pass MUST NOT excuse it

#### Scenario: APCA pass with WCAG fail is blocking

- GIVEN a pair that measures Lc 80 but 4.2:1 WCAG
- WHEN validation runs
- THEN the gate MUST fail on WCAG, and the APCA pass MUST NOT excuse it

#### Scenario: Thresholds come from canonical guardrails

- GIVEN `tokens.json` defines the mode-aware APCA floors
- WHEN validation computes a below-floor verdict
- THEN the threshold in the diagnostic MUST equal the value read from the canonical guardrails, not a hardcoded literal in code

#### Scenario: Class floors apply per content and mode

- GIVEN heading (Lc 60 light / Lc 45 dark), quiet (Lc 44), UI (Lc 60 light / Lc 28 dark), and on-accent (Lc 60) pairs across Light, Dark, and Dusk
- WHEN health validation runs
- THEN each pair MUST be measured against its declared class and mode floor, and any below-floor pair MUST block

### Requirement: Pre-write validation and fail-closed write behavior

The final Light or Dark palette MUST be validated by `validate_palette()` before the first writer runs, and validation MUST finish before `sync_active_targets()` and `sync_repo_snippets()` perform any write. If any WCAG or APCA pair misses its floor, generation MUST stop before writes, the command MUST exit non-zero, and no partial cross-target state MAY be left applied. `write_if_changed()` semantics MUST be preserved.

#### Scenario: A failed gate blocks all writes

- GIVEN a palette that misses one APCA floor
- WHEN the validated sync runs
- THEN no target or active output is written or selected, the command exits non-zero, and the prior mode remains active

### Requirement: Declared coverage of every active color consumer

Every consumer output in the union of `sync_active_targets()` and `sync_repo_snippets()` MUST be declared in the sync coverage table and rendered in memory during preparation; an undeclared or unrendered consumer MUST fail the command before any write. `targets.json` render modes MUST be exactly `dark` and `light`; `dusk-runtime` MUST remain excluded.

#### Scenario: An undeclared consumer blocks preparation

- GIVEN a consumer written by sync but missing from the coverage declaration
- WHEN preparation runs
- THEN the command fails closed before any write and names the consumer

### Requirement: Dreamcoder CLI Light/Dark activation

`dreamcoder light` and `dreamcoder dark` MUST persist `terminal.default_mode`, run the validated sync, and return non-zero without changing active outputs when validation fails. `night` MUST be rejected as an unknown command, and `dreamcoder theme apply` MUST accept only `light` and `dark`. A settings file that still carries the retired `theme.render_profile` key MUST load without error: the key is reported as an unknown setting, preserved, and never read. `scripts/theme-auto.sh` MUST keep the Light/Dark schedule.

#### Scenario: Light or Dark activation succeeds

- GIVEN either mode is active
- WHEN the user runs `dreamcoder light` or `dreamcoder dark`
- THEN the mode is persisted, the palette is validated, and every declared consumer receives that mode's output

#### Scenario: A failing gate changes nothing

- GIVEN a palette that fails a floor
- WHEN the user runs `dreamcoder light` or `dreamcoder dark`
- THEN the command exits non-zero, no active output is changed, and the prior setting remains in effect

#### Scenario: Night is not a mode

- GIVEN the Night render profile was removed
- WHEN the user runs `dreamcoder night` or `dreamcoder theme apply night`
- THEN the command is rejected as unknown, exits non-zero, and changes nothing

#### Scenario: Legacy render profile setting is tolerated

- GIVEN a persisted `theme.render_profile` from an older version
- WHEN settings are loaded, validated, or updated
- THEN loading succeeds with an unknown-setting warning and the key is preserved without affecting the mode

### Requirement: Blocking health verification

`scripts/verify-theme-health.py` MUST import canonical `contrast()` and `apca_lc()` from the package and MUST remove the `check_apca_or_warn()` advisory path for declared guardrail pairs. Every below-floor pair MUST terminate the command non-zero and report mode, token or state pair, measured WCAG/APCA value, and required threshold. The command MUST validate Light, Dark, and design-system Dusk deterministically. It MUST declare generation/selection coverage for every active consumer, and any consumer without declared coverage MUST block. `scripts/generate-theme-preview.py` MUST use the same canonical math without creating screenshot baselines.

#### Scenario: Below-floor pair blocks with actionable diagnostics

- GIVEN a quiet-text pair measuring below Lc 44 in Dark
- WHEN `verify-theme-health.py` runs
- THEN the command exits non-zero and reports mode dark, the pair, the measured Lc value, and the required threshold

#### Scenario: All canonical palettes are validated

- GIVEN the Light, Dark, and design-system Dusk palettes
- WHEN health validation runs
- THEN each palette is measured deterministically, and any below-floor pair in any palette blocks the command

#### Scenario: Advisory warnings become blocking

- GIVEN a declared guardrail pair that previously produced a warning through `check_apca_or_warn()`
- WHEN health validation runs
- THEN the pair MUST block the command non-zero and MUST NOT be downgraded to an advisory warning

#### Scenario: All-target coverage is declared

- GIVEN the sync coverage declaration
- WHEN health validation runs
- THEN it declares generation/selection coverage for every active consumer, and any consumer without declared coverage blocks the command

### Requirement: Focused regression coverage for the eye-comfort contract

The automated test suite MUST cover APCA known vectors, threshold boundaries, polarity, failed-gate no-write behavior, legacy `theme.render_profile` tolerance, Light/Dark CLI activation, and all-target coverage. Advisory assertions and comments in `tests/test_dreamcoder_global_design_system.py` MUST be replaced with blocking checks. `tests/test_apca_implementation.py` MUST cross-validate the package `apca_lc()` against known vectors. Local and CI behavior MUST align around `python scripts/verify-theme-health.py` and the existing pytest suite.

#### Scenario: Known vectors cross-validate the package implementation

- GIVEN the known APCA vectors and the package `apca_lc()`
- WHEN `tests/test_apca_implementation.py` runs
- THEN every vector matches within the established tolerance and the test exercises the package implementation, not a copied formula

#### Scenario: Boundary and polarity cases are covered

- GIVEN pairs at and just below each class floor, and both light-on-dark and dark-on-light polarity
- WHEN the focused tests run
- THEN at-floor pairs pass and below-floor pairs fail with the correct metric and polarity-aware measurement

#### Scenario: Failed gate performs no writes

- GIVEN a test that forces the dual gate to fail
- WHEN the sync path runs under test
- THEN no writes occur and the failure is asserted

### Requirement: Evidence and claims boundaries

The Light/Dark modes MUST be documented as display modes, not a medical treatment. The system MUST NOT make blue-light-treatment, disease-prevention, eye-strain-cure, or sleep-improvement claims, MUST NOT add automatic warmth/color-temperature filtering, and MUST NOT replace the existing Hyprland 4000K keybindings, which remain a separate external display filter. `docs/DREAMCODER_DESIGN_SYSTEM.md` and generated preview policy MUST document WCAG 2.2 and APCA as independent blocking gates, and previously documented APCA exceptions MUST be corrected or explicitly removed rather than remaining accepted warnings.

#### Scenario: Modes are documented without treatment claims

- GIVEN the Light/Dark documentation
- WHEN the documentation and generated preview policy are inspected
- THEN the modes are described without medical-treatment, blue-light-filtering, or sleep claims, and no automatic warmth is introduced

#### Scenario: Advisory APCA exceptions are removed

- GIVEN documentation that previously recorded below-threshold APCA pairs as accepted warnings
- WHEN the documentation is reviewed
- THEN those exceptions are corrected or removed, and the documentation states that WCAG 2.2 and APCA are independent blocking gates
