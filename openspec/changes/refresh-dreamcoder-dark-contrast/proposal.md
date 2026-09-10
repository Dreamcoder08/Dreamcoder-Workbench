# Proposal: Refresh Dreamcoder Dark Contrast and Legibility

## Intent

Soften Dreamcoder Dark's primary text and widen the accent/accent_2 hue separation so the canonical dark identity sits inside a comfortable OLED reading band instead of at its outer edge, without weakening any existing accessibility floor.

`DreamcoderThemes/dreamcoder/tokens.json` → `modes.dark` is the single source of truth for the dark identity, regenerated across 24 renderer modules and 33 declared consumer targets by `./scripts/dreamcoder sync`. The "Dark Contract Normalization" (commit `e6ffec0`) already retired a separate `dark-black-oled` identity: OLED behavior now lives only in `modes.dark.surface_policy.pure_black_policy`. This proposal changes nothing about that contract. It is a **values-only** correction inside `modes.dark`: body/heading text currently reads far brighter against `#000000` than comfort-oriented OLED guidance recommends, and `accent`/`accent_2` sit close enough in hue that they read as near-duplicates in low-differentiation UI states (borders, links, diagnostics).

Now is the right time because the contract normalization already stabilized the schema and guardrail shape this change must respect, and no other in-flight change touches `modes.dark` values.

## Current-State Gap

Verified directly against `DreamcoderThemes/dreamcoder/tokens.json` and the repository's own WCAG math in `src/dreamcoder_theme/_math.py` (`rel_luminance()`/`contrast()` — standard WCAG 2.2 relative-luminance formula, hand-computed and cross-checked below):

| Token | Current hex | Contrast vs `#000000` |
|---|---|---|
| `text` | `#E2E8F0` (Tailwind slate-200) | **17.03:1** |
| `text_heading` | `#F1F5F9` (Tailwind slate-100) | **19.17:1** |

Both sit well above `guardrails.preferred_main_text_contrast` (7.0) and far outside the ~13–15:1 comfort band commonly recommended for OLED body text (near-white on true black causes halation/glow that is most noticeable in text-dense terminal/editor use).

**Correction to the exploration's cited reference**: the exploration cited "`#000000` + `#D1D5DB` ≈ 15.3:1" as the comfort-band anchor. Hand-computing the same WCAG formula gives **14.25:1**, not 15.3:1. The proposal below does not depend on the wrong number — it targets the general 13–15:1 band and verifies its own candidate independently.

`accent` (`#A5B4FC`) and `accent_2` (`#C4B5FD`) were verified at hue ≈229.7° / ≈252.5° (HSL, ≈22.8° apart), lightness ≈0.818 / ≈0.851 — confirming the exploration's estimates. That separation is narrower than reference dual-accent dark themes (e.g. Tokyo Night blue/magenta ≈48° apart, Catppuccin Mocha blue/mauve ≈51° apart), so `accent` and `accent_2` under-differentiate in low-saturation UI states.

`tokens.json.guardrails` only defines WCAG/APCA **floors** (`minimum_text_contrast=4.5`, `preferred_main_text_contrast=7.0`, plus the APCA `_dark` classes in `src/dreamcoder_theme/palette.py`); no ceiling exists. This proposal does not add one — it is a one-time value correction, not a new enforced policy.

Because `tokens.json` stores plain literals (no in-file references), several keys duplicate `text` and `accent_2` by value today: `prompt_text`, `on_surface`, `selection_fg` mirror `text`; `prompt_accent_2`, `lavender`, `link_hover` mirror `accent_2`. `scripts/generate-palette-tokens.py` only defaults `on_surface` to `text` via `setdefault()` — since `on_surface` is already present in `tokens.json`, it will **not** auto-follow a `text` edit. Every mirrored key must be edited in lockstep or the regenerated `src/dreamcoder_theme/palette_tokens.py` and downstream renderers will silently diverge.

## Product Outcome

A user on Dreamcoder Dark sees body and heading text that is still clearly the brightest, most legible content on screen, but without the glow/halation of near-maximum contrast on pure black. `accent` and `accent_2` remain recognizably the same indigo/violet family (per `CLAUDE.md`'s documented identity) but read as two distinguishable roles instead of near-duplicates. Every one of the 33 consumer targets regenerates through the existing `./scripts/dreamcoder sync` pipeline with no manual per-target edits, and the Night render profile (`src/dreamcoder_theme/palette.py::night_palette()`) re-derives automatically and still clears the dual WCAG/APCA gate.

## Scope

### In scope

- Edit exactly these 9 literal values inside `DreamcoderThemes/dreamcoder/tokens.json` → `modes.dark` (2 semantic changes, propagated to their mirrors):
  - `text`: `#E2E8F0` → `#CBD5E1` (Tailwind slate-300) — 14.14:1 vs `#000000`
  - `text_heading`: `#F1F5F9` → `#E2E8F0` (Tailwind slate-200, i.e. today's `text` value) — 17.03:1 vs `#000000`
  - `prompt_text`, `on_surface`, `selection_fg`: → `#CBD5E1` (mirror `text`)
  - `accent_2`: `#C4B5FD` → `#D4B5FD` (hue ≈252.5° → ≈265.8°, ≈36.1° separation from unchanged `accent`)
  - `prompt_accent_2`, `lavender`, `link_hover`: → `#D4B5FD` (mirror `accent_2`)
- Regenerate all derived artifacts via `./scripts/dreamcoder sync` (including `src/dreamcoder_theme/palette_tokens.py` and every active renderer output).
- Update the two literal values documented in this repo's `CLAUDE.md` Dark palette snippet (`text`, `accent_2`) so the doc stays accurate.
- Re-run `scripts/verify-theme-health.py` and the `pytest` suite to confirm both the WCAG and APCA gates still pass for `modes.dark` and the derived Night profile.

### Non-goals

- No new theme identity, mode name, or brand palette — this stays the canonical `Dreamcoder Dark`.
- No changes to `surface_policy` shape, `pure_black_policy`, or any OLED behavior — that contract is untouched.
- No `tokens.schema.json` or guardrail-shape changes; no new "contrast ceiling" guardrail key is introduced.
- No changes to `Light` (Cocoa/Lúcuma) or `Dusk` modes.
- No manual edits to the Night render profile — it must re-derive automatically from the corrected `modes.dark` values.
- No change to `accent`'s own value — only `accent_2` and its mirrors move, to keep the touched-token surface small (`accent` also backs the unrelated `link`, `prompt_accent`, and the `active_rgba`/`glow_brand` family, which carry independent risk if disturbed).
- No compositor/window-transparency change: `background_opacity 0.76` in Kitty/Ghostty is an orthogonal glass-blur product decision, not a color token, and is out of scope here.
- No new renderer code paths — implementation is regeneration plus verification against the existing pipeline.

## Business and Product Rules

- **Identity-first**: colors change only inside the already-adopted indigo/violet Dreamcoder family; no generic theme (Nord, Dracula, Catppuccin, etc.) is substituted.
- **Values-only boundary**: every edit is a literal value inside `modes.dark`; no key is added, removed, or renamed, and no schema field changes shape.
- **Mirror-lockstep rule**: any edit to `text` or `accent_2` must be applied identically to every literal key that currently duplicates that value (`prompt_text`, `on_surface`, `selection_fg` for `text`; `prompt_accent_2`, `lavender`, `link_hover` for `accent_2`), since `tokens.json` has no in-file value references.
- **Floor-preserving, not floor-lowering**: no touched token may drop below its existing WCAG (`minimum_text_contrast`, `preferred_main_text_contrast`, `minimum_terminal_selection_contrast`) or APCA (`minimum_apca_body_dark`, `minimum_apca_heading_dark`) guardrail; the change narrows the ceiling, not the floor.
- **No new enforced ceiling**: the comfort-band target (~13–15:1 body, comfortably reduced heading) is a one-time authored decision, not a new blocking guardrail key.
- **Regeneration is the only implementation mechanism**: no renderer, writer, or consumer target may hand-author a diverging value; `./scripts/dreamcoder sync` is the sole propagation path.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `DreamcoderThemes/dreamcoder/tokens.json` (`modes.dark`) | Modified | 9 literal value edits (`text`, `text_heading`, `prompt_text`, `on_surface`, `selection_fg`, `accent_2`, `prompt_accent_2`, `lavender`, `link_hover`) |
| `src/dreamcoder_theme/palette_tokens.py` | Regenerated | Auto-generated from `tokens.json`; will be regenerated, not hand-edited |
| All active `renderers_*.py` outputs / 33 consumer targets | Regenerated | Any file containing the 9 changed values regenerates with new hex values only |
| `CLAUDE.md` (Dark palette snippet) | Modified | Update documented `text` and `accent_2` lines to match |
| `src/dreamcoder_theme/palette.py::night_palette()` | Verified, not edited | Must re-derive from the corrected `modes.dark` and still clear the dual gate |
| `scripts/verify-theme-health.py`, `pytest` suite | Run, not edited | Confirms WCAG/APCA gates still pass post-change |

### Protected unaffected areas

- `modes.dark.surface_policy` (shape and `pure_black_policy` values).
- `modes.light` (Cocoa/Lúcuma) and `modes.dusk`.
- `DreamcoderThemes/dreamcoder/tokens.schema.json` and `guardrails` keys/thresholds.
- `accent`, `bg`, `bg_soft`, `surface0`–`surface3`, `muted`, `subtle`, `comment`, `border*`, `focus`, `diagnostic`, `error`, `warning`, `success`, `info`, `sage`, `mauve` — every token not explicitly listed as edited.
- Kitty/Ghostty `background_opacity` and any other compositor/window-transparency setting.
- Herdr and any other OpenSpec change's artifacts.

## Edge Cases and Boundaries

- If any mirrored key (`prompt_text`, `on_surface`, `selection_fg`, `prompt_accent_2`, `lavender`, `link_hover`) is edited to a different value than its source (`text`/`accent_2`), that is a defect in this change, not an intentional divergence — the repository has no automated equality check for these base-mode literals today (only `tests/test_night_palette.py` asserts `night["text"] == night["on_surface"]` for the *derived Night profile*, not the base `dark` mode), so a manual diff review of all 9 edits is required before regeneration.
- `selection_fg` is gated against `selection_bg` (`#16161D`), not `#000000`; predicted contrast for the new `#CBD5E1` is ≈12.13:1, comfortably above `minimum_terminal_selection_contrast` (7.0).
- If regenerating `src/dreamcoder_theme/palette_tokens.py` or any renderer produces a diff beyond the expected hex substitutions, that indicates an unrelated drift and must be investigated before merge, not silently accepted.
- Night must re-derive without manual edits; if `night_palette()`'s deterministic transform pushes any changed token below its floor after this base change, that blocks the change — it is not grounds for a Night-specific hand override.
- `accent`, `link`, and `prompt_accent` are explicitly untouched; any renderer output showing those values change is a regression, not an expected side effect.

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| A mirrored literal is missed, leaving `text`/`accent_2` and one of their duplicates inconsistent across targets | Medium | Explicit 9-key edit list in this proposal; diff review before `sync`; spec/task phase should add a lockstep-equality check |
| New `text`/`accent_2` values drop a WCAG or APCA pair below its floor after real (non-hand) `validate_palette()`/`apca_lc()` execution | Low | All hand-computed predictions land with comfortable margin (14.14:1 vs 7.0 floor, 17.03:1 vs 4.5 floor, 12.13:1 vs 7.0 floor); exact APCA Lc must still be confirmed by running the repository's own gate before merge, since APCA is not practical to hand-verify |
| Night profile regression: `night_palette()` derives a value that fails its own gate | Low | Night is deterministic from `dark`; re-run the existing Night-specific test/gate coverage after regeneration, do not hand-patch Night output |
| `CLAUDE.md` doc drifts from the actual token values | Low | Doc-sync of the two documented lines is included in scope |
| Reduced contrast is perceived as a downgrade rather than a comfort improvement | Low | Target band (13–15:1 body, ~17:1 heading) still clears `preferred_main_text_contrast` by a wide margin; this is a ceiling reduction, not a floor reduction |

## Rollback

1. Revert the 9 literal `modes.dark` value edits in `DreamcoderThemes/dreamcoder/tokens.json` to their original hex values (`text` → `#E2E8F0`, `text_heading` → `#F1F5F9`, `prompt_text`/`on_surface`/`selection_fg` → `#E2E8F0`, `accent_2`/`prompt_accent_2`/`lavender`/`link_hover` → `#C4B5FD`).
2. Revert the `CLAUDE.md` Dark palette snippet lines to their original values.
3. Re-run `./scripts/dreamcoder sync` to regenerate `palette_tokens.py` and all consumer targets back to the known-good baseline.
4. Re-run `scripts/verify-theme-health.py` and `pytest` to confirm the restored baseline still passes (it is the pre-change state, already known-good).
5. No runtime/backup/atomic-replace machinery is needed — this is a static token change with no live-process activation step.

## Success Criteria

- [ ] `text` measures in the 13.0–15.5:1 WCAG range against `#000000` (predicted 14.14:1) and still clears `preferred_main_text_contrast` (7.0).
- [ ] `text_heading` measures visibly above `text` and still clears `preferred_main_text_contrast` (predicted 17.03:1).
- [ ] `accent`/`accent_2` hue separation is at least 32° (predicted ≈36.1°), with `accent` unchanged and both remaining in the indigo/violet family.
- [ ] All 9 listed literal keys are updated consistently (no divergence between a source key and its mirror).
- [ ] `scripts/verify-theme-health.py` and the full `pytest` suite pass with zero WCAG/APCA errors for `modes.dark` and the derived Night profile.
- [ ] Regenerating via `./scripts/dreamcoder sync` produces diffs limited to the expected hex substitutions across `palette_tokens.py` and active renderer outputs — no unrelated file changes.
- [ ] `CLAUDE.md`'s documented Dark palette snippet matches the new `text` and `accent_2` values.
- [ ] `modes.light`, `modes.dusk`, `surface_policy`, and `tokens.schema.json` are byte-identical to before this change.
