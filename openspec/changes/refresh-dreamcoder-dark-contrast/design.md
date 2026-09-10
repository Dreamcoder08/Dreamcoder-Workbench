# Design: Refresh Dreamcoder Dark Contrast and Legibility

## Technical Approach

A values-only edit of 9 literal keys inside `DreamcoderThemes/dreamcoder/tokens.json` → `modes.dark`, propagated through the existing, unmodified regeneration pipeline (`./scripts/dreamcoder sync`), then confirmed by the existing health/test gates. No schema, renderer, or writer code changes. `tokens.json` stores plain literals with no in-file references, so every duplicate of `text`/`accent_2` must be hand-edited in the same commit — the pipeline cannot infer mirrors it does not model.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| Where to encode the new colors | Literal edits in `tokens.json` only | Add a "ceiling" guardrail key; add token references/aliasing to `tokens.json` | Proposal is explicitly values-only; a new guardrail or reference mechanism is a schema change, out of scope, and unnecessary for a one-time authored correction |
| How `on_surface` gets its new value | Explicit literal edit in `tokens.json` | Rely on `generate-palette-tokens.py`'s `c.setdefault("on_surface", text)` | Confirmed by reading `scripts/generate-palette-tokens.py:140` — `setdefault` only fills a *missing* key; `on_surface` already exists as a literal in `tokens.json` (line 50), so it will not auto-follow a `text` edit. It is edited explicitly and is already in the 9-key list. |
| How Night is updated | No edit — re-derive via `night_palette()` | Hand-patch Night TOML/JSON outputs | `night_palette()` is a deterministic transform of the `dark` base (ADR-003, `palette.py:689`); hand-patching would create a second source of truth and violate the non-goal "no manual edits to Night" |
| Divergence detection for the 9 mirrors | Manual diff review of the edit, backed by the existing `check_generated()` drift gate | New automated base-mode equality assertion (e.g. `tokens.json["text"] == tokens.json["prompt_text"]`) | In scope for this change is regeneration + verification, not new tooling; `scripts/generate-palette-tokens.py --check` already fails the build if `palette_tokens.py` drifts from any hand-edit mistake in the 9 keys, which is the binding safety net. Adding a bespoke equality test is a reasonable spec/task follow-up but not required to implement the color values themselves. |
| Failure response if the dual gate rejects a candidate | Nudge the specific failing hex 1–2 steps darker/lighter within the same OKLCH lightness band, re-run the full gate | Accept an out-of-band lower floor; abandon the comfort-band target | Keeps the floor-preserving business rule intact while still allowing the comfort-band intent to succeed on a corrected candidate |

## Data Flow

```
DreamcoderThemes/dreamcoder/tokens.json (modes.dark)
  [9 literal edits: text, text_heading, prompt_text, on_surface,
   selection_fg, accent_2, prompt_accent_2, lavender, link_hover]
        │
        ▼
./scripts/dreamcoder sync
        │
        ├──▶ scripts/generate-palette-tokens.py
        │      enrich_mode(modes.dark)             (setdefault: does NOT
        │        │                                   touch on_surface —
        │        ▼                                   already a literal)
        │      src/dreamcoder_theme/palette_tokens.py  (VARIANTS["dark"] regenerated)
        │
        ▼
src/dreamcoder_theme/sync.py
        │
        ├──▶ load_variants(DEFAULT_VARIANTS, tokens_file)
        │
        ├──▶ src/dreamcoder_theme/palette.py::night_palette(base=dark, ...)
        │      deterministic HSL transform + corrective pass
        │      → Night palette re-derived automatically, no hand edits
        │
        ├──▶ sync_active_targets() / sync_repo_snippets()
        │      → 24 renderers_*.py modules render dark/night payloads
        │        (renderers_kitty, renderers_starship, renderers_tmux,
        │         renderers_ghostty_warp, renderers_opencode, ...)
        │
        ▼
src/dreamcoder_theme/writers.py::write_if_changed()
        → 33 consumer target files updated only where bytes differ
```

### Sequence Diagram — Edit to Verified Regeneration

```
Author        tokens.json      generate-palette-   sync.py /        verify-theme-  pytest
              (modes.dark)     tokens.py           renderers_*.py   health.py
  │                │                  │                  │                │           │
  │ edit 9 keys    │                  │                  │                │           │
  ├───────────────▶│                  │                  │                │           │
  │                │                  │                  │                │           │
  │ run            │                  │                  │                │           │
  │ ./scripts/     │                  │                  │                │           │
  │ dreamcoder sync│                  │                  │                │           │
  ├────────────────┼─────────────────▶│                  │                │           │
  │                │  load_tokens()   │                  │                │           │
  │                │◀─────────────────┤                  │                │           │
  │                │  enrich_mode()   │                  │                │           │
  │                │  (setdefault:    │                  │                │           │
  │                │   on_surface     │                  │                │           │
  │                │   NOT touched —  │                  │                │           │
  │                │   already set)   │                  │                │           │
  │                │                  │ write             │                │           │
  │                │                  │ palette_tokens.py │                │           │
  │                │                  ├─────────────────▶│                │           │
  │                │                  │                  │ load VARIANTS  │           │
  │                │                  │                  │ night_palette()│           │
  │                │                  │                  │ (auto-derive)  │           │
  │                │                  │                  │ render 24      │           │
  │                │                  │                  │ renderers_*.py │           │
  │                │                  │                  │ write_if_changed│          │
  │                │                  │                  │ (33 targets)   │           │
  │                │                  │                  │                │           │
  │ run verify-theme-health.py ───────┼──────────────────┼───────────────▶│           │
  │                │                  │                  │  WCAG contrast()│          │
  │                │                  │                  │  APCA apca_lc() │          │
  │                │                  │                  │  Light/Dark/    │          │
  │                │                  │                  │  Dusk/Night     │          │
  │◀───────────────┼──────────────────┼──────────────────┼── pass/fail ────┤           │
  │ run pytest ────┼──────────────────┼──────────────────┼─────────────────┼──────────▶│
  │◀───────────────┼──────────────────┼──────────────────┼─────────────────┼── pass/fail┤
  │ manual visual diff review (Kitty colors-dreamcoder.conf, Starship toml, ...)        │
  │  → expect ONLY hex substitutions, no structural diff                                │
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `DreamcoderThemes/dreamcoder/tokens.json` | Modify | Edit exactly 9 literal keys inside `modes.dark` (list below) |
| `CLAUDE.md` | Modify | Update Dark palette snippet: `text` and `accent_2` documented values |
| `src/dreamcoder_theme/palette_tokens.py` | Regenerate | Via `scripts/generate-palette-tokens.py`; not hand-edited |
| 33 consumer target files across active `renderers_*.py` outputs | Regenerate | Via `./scripts/dreamcoder sync`; `write_if_changed` limits writes to files whose rendered bytes actually differ |

### Exact 9-key edit set (`modes.dark`)

| Key | Current | New | Source of new value |
|---|---|---|---|
| `text` | `#E2E8F0` | `#CBD5E1` | Semantic — Tailwind slate-300, 14.14:1 vs `#000000` |
| `text_heading` | `#F1F5F9` | `#E2E8F0` | Semantic — today's `text` value, 17.03:1 |
| `prompt_text` | `#E2E8F0` | `#CBD5E1` | Mirror of `text` |
| `on_surface` | `#E2E8F0` | `#CBD5E1` | Mirror of `text` — **must be edited explicitly**; `enrich_mode`'s `setdefault("on_surface", text)` only fills a missing key and `on_surface` is already a literal |
| `selection_fg` | `#E2E8F0` | `#CBD5E1` | Mirror of `text` (gated against `selection_bg` `#16161D`, not `#000000`; predicted ≈12.13:1) |
| `accent_2` | `#C4B5FD` | `#D4B5FD` | Semantic — hue ≈252.5°→≈265.8°, ≈36.1° separation from unchanged `accent` |
| `prompt_accent_2` | `#C4B5FD` | `#D4B5FD` | Mirror of `accent_2` |
| `lavender` | `#C4B5FD` | `#D4B5FD` | Mirror of `accent_2` |
| `link_hover` | `#C4B5FD` | `#D4B5FD` | Mirror of `accent_2` |

`accent` (`#A5B4FC`), `bg` (`#000000`), `surface_policy`, `guardrails`, `tokens.schema.json`, `modes.light`, and `modes.dusk` are untouched.

## Interfaces / Contracts

No new interfaces. No function signature in `generate-palette-tokens.py`, `sync.py`, `palette.py`, or any `renderers_*.py` changes. The only contract this design touches is the *data* the existing pipeline consumes (`modes.dark` literal values).

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Regeneration integrity | `palette_tokens.py` matches `tokens.json` | `python scripts/generate-palette-tokens.py --check` (existing drift gate) |
| Contrast/luminance gate | WCAG floors preserved for touched tokens across Dark and Night | `python scripts/verify-theme-health.py` (dual WCAG/APCA gate, all of Light/Dark/Dusk/Night) — **hard gate, MUST pass before this change is complete**; hand-computed 14.14:1 / 17.03:1 / 12.13:1 predictions are not a substitute |
| Regression suite | Existing palette/night/renderer/writer tests | `python -m pytest tests/ -v` (repo standard, includes `tests/test_night_palette.py`'s `night["text"] == night["on_surface"]` assertion) |
| Manual visual/structural diff | Regenerated artifacts contain only hex substitutions | Inspect `git diff` for at least: `DreamcoderKitty/.config/kitty/colors-dreamcoder-dark.conf`, `DreamcoderShell/.config/starship-dark.toml`, one more active target (e.g. `DreamcoderTmux/.config/tmux/tmux-dreamcoder.conf`); confirm no key added/removed/reordered |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. This is a static JSON literal edit regenerated through an existing, unmodified Python rendering pipeline; `./scripts/dreamcoder sync` and `verify-theme-health.py` are pre-existing repository commands invoked as-is, not new shell integration.

## Migration / Rollout

No migration. Rollout is a single commit:

1. Edit the 9 `modes.dark` literals in `tokens.json` per the table above.
2. Update the two `CLAUDE.md` Dark palette lines (`text`, `accent_2`).
3. Run `./scripts/dreamcoder sync` to regenerate `palette_tokens.py` and all 33 consumer targets.
4. Run `python scripts/verify-theme-health.py` — hard gate. If it fails on any of the 9 changed tokens or the derived Night profile, nudge the failing hex 1–2 OKLCH-lightness steps darker/lighter (staying in the same indigo/violet hue family and inside the 13–15:1 comfort band for `text`), then re-run steps 3–4. Do not lower a WCAG/APCA floor to pass.
5. Run `python -m pytest tests/ -v` — full suite must pass with zero WCAG/APCA errors.
6. Manually diff at least 2–3 regenerated artifacts to confirm the change surface is limited to hex substitutions.

**Rollback**: revert the 9 literal edits in `tokens.json` to their original values (`text`→`#E2E8F0`, `text_heading`→`#F1F5F9`, `prompt_text`/`on_surface`/`selection_fg`→`#E2E8F0`, `accent_2`/`prompt_accent_2`/`lavender`/`link_hover`→`#C4B5FD`) and the `CLAUDE.md` snippet, then re-run `./scripts/dreamcoder sync` and both gates (step 4–5) to confirm the restored baseline is the already-known-good pre-change state. No backup/atomic-replace machinery is needed; this is a static token change with no live-process activation step.

## Risk Callouts

- **Mirror-lockstep risk**: if any of the 9 duplicate literals is missed or set to a different value than its source (`text`/`accent_2`), renderers silently diverge. The repository has **no automated check for base-mode literal equality today** (`tests/test_night_palette.py` only asserts equality on the *derived Night* profile, not on `modes.dark` itself). Mitigation: this design enumerates the exact 9-key table above; the task phase must require a manual diff review of all 9 edits before running `sync`, and `generate-palette-tokens.py --check` catches drift only between `tokens.json` and `palette_tokens.py`, not an internally-inconsistent `tokens.json`.
- **Unverified APCA margins**: the 14.14:1 / 17.03:1 / 12.13:1 WCAG figures and the ≈36.1° hue separation in this design are proposal-predicted by hand computation, not machine-verified against the repository's own `apca_lc()`/`validate_palette()`. **Running `scripts/verify-theme-health.py` is a hard completion gate for this change** — it is not optional polish. If the dual gate fails on any touched token or the re-derived Night profile, the fallback is to nudge the specific candidate hex 1–2 steps darker/lighter within the same OKLCH lightness/hue band (keeping the indigo/violet family and the floor-preserving business rule) and re-verify, rather than accepting a floor regression or abandoning the comfort-band intent.
- **Night regression risk**: `night_palette()` applies a deterministic corrective pass; if it pushes a changed token below its floor after the base `dark` values move, that blocks the change per the proposal's edge cases — it is not grounds for a Night-specific hand override.

## Open Questions

None — the proposal's stated edge cases resolve all decisions needed to implement this design; the only unresolved item (whether `on_surface` needs an explicit edit) was confirmed by reading `generate-palette-tokens.py` directly (see Architecture Decisions above).
