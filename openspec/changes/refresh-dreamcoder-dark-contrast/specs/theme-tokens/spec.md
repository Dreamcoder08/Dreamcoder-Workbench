# Theme Tokens Specification

## Purpose

Define the canonical `modes.dark` token values in `DreamcoderThemes/dreamcoder/tokens.json`, their lockstep literal mirrors, and the WCAG/APCA guardrails that MUST hold across Dark, its derived Night profile, and every regenerated consumer target.

## Requirements

### Requirement: Dark text and mirror literals are updated

`modes.dark.text` MUST equal `#CBD5E1`, mirrored identically by `prompt_text`, `on_surface`, and `selection_fg`. `modes.dark.text_heading` MUST equal `#E2E8F0`. No mirror key MAY diverge from its source, since `tokens.json` stores plain literals with no in-file references.

#### Scenario: Text and heading tokens match their mirrors

- GIVEN the updated `modes.dark` block
- WHEN `text`, `prompt_text`, `on_surface`, `selection_fg` are compared
- THEN all four equal `#CBD5E1`, and `text_heading` equals `#E2E8F0`
- AND any divergence between a mirror and its source is treated as a defect blocking regeneration

### Requirement: Accent hue separation widens via accent_2

`modes.dark.accent` MUST remain `#A5B4FC` (unchanged). `modes.dark.accent_2` MUST equal `#D4B5FD`, mirrored identically by `prompt_accent_2`, `lavender`, and `link_hover`. The HSL hue separation between `accent` and `accent_2` MUST be at least 32 degrees.

#### Scenario: accent_2 and its mirrors widen without touching accent

- GIVEN `accent` (`#A5B4FC`) and updated `accent_2` (`#D4B5FD`)
- WHEN `accent_2`, `prompt_accent_2`, `lavender`, `link_hover` are compared and hue separation is computed
- THEN all four equal `#D4B5FD`, separation is at least 32 degrees (predicted ≈36.1°), and both colors stay in the indigo/violet family

### Requirement: WCAG contrast floor and preferred band

Every touched Dark text token MUST clear `guardrails.minimum_text_contrast` (4.5:1) against its paired background and SHOULD clear `guardrails.preferred_main_text_contrast` (7.0:1). `selection_fg` MUST clear `guardrails.minimum_terminal_selection_contrast` (7.0:1) against `selection_bg`.

#### Scenario: Body, heading, and selection text clear their floors

- GIVEN `text`/`text_heading` against `#000000` and `selection_fg` against `selection_bg`
- WHEN WCAG 2.2 contrast is computed
- THEN each MUST be at least its MUST floor, and `text`/`text_heading` SHOULD also clear 7.0:1

### Requirement: APCA dual gate remains independently blocking

`scripts/verify-theme-health.py` MUST validate every touched Dark pair against its APCA floor from `tokens.json.guardrails` — `minimum_apca_body_dark`, `minimum_apca_quiet`, `minimum_apca_ui_dark`, `minimum_apca_heading_dark`, `minimum_apca_on_accent` — as a required, non-optional gate. An APCA failure MUST block regardless of WCAG result.

#### Scenario: Health check enforces APCA after the value change

- GIVEN the updated `modes.dark` tokens
- WHEN `scripts/verify-theme-health.py` runs
- THEN every touched pair MUST meet or exceed its named APCA floor, and any below-floor pair MUST fail the command non-zero

### Requirement: Unaffected modes and surface policy stay untouched

`modes.light`, `modes.dusk`, and `modes.dark.surface_policy` MUST remain byte-identical to their pre-change state.

#### Scenario: Other modes and surface policy are unchanged

- GIVEN `tokens.json` before and after this change
- WHEN `modes.light`, `modes.dusk`, and `modes.dark.surface_policy` are diffed
- THEN there is zero difference, and no new theme identity or OLED policy is introduced

### Requirement: Night profile re-derives automatically

`src/dreamcoder_theme/palette.py::night_palette()` MUST derive its output from the corrected `modes.dark` values with no manual edits, and the derived Night profile MUST still clear the WCAG/APCA dual gate.

#### Scenario: Night regenerates from the new Dark base

- GIVEN the updated `modes.dark` tokens and an unmodified `night_palette()`
- WHEN Night is regenerated
- THEN its output reflects the new values and clears the dual gate with no hand-authored override

### Requirement: Consumer regeneration and test suite

Running `./scripts/dreamcoder sync` MUST regenerate `palette_tokens.py` and all 33 declared consumer targets with diffs limited to the nine changed keys' hex substitutions. The full `pytest` suite MUST pass afterward with zero WCAG/APCA errors.

#### Scenario: Sync and tests confirm a scoped, valid change

- GIVEN the updated `modes.dark` tokens
- WHEN `./scripts/dreamcoder sync` runs and `pytest` is run afterward
- THEN every changed file's diff contains only expected hex substitutions with no structural or schema change, and the full test suite passes
