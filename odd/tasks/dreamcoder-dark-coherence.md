# Dreamcoder Dark — Holistic Design-System Coherence

Bring Dreamcoder Dark to the same measurable model Light now has (primitives → semantic → components, material
laws pinned by tests), keeping the Dark decisions already made. Status: in progress.
Branch `feat/dark-coherence` (stacked on `feat/light-coherence`) in worktree `.local-backups/worktrees/dark-coherence`.

## Specs

- S1 — Scope, verbatim (L1): "perfect continuemos asi como mejoramos dreamcoder light ahora meoremos dreamcoder dark".
  Same method as `odd/tasks/dreamcoder-light-coherence.md` (its S2–S5 apply to Dark: one token source, grounded
  and measurable decisions, benchmark by metrics, legacy cleanup).
- S2 — Canvas, verbatim (L2): "Mantener #000 OLED (Recomendado)". `bg` stays `#000000`.
- S3 — Identity, verbatim (L2): "Índigo + familias de Light (Recomendado)". Dark keeps the indigo accent; its
  semantic roles use the same eight pigment families as Light (same hue order) at night density.
- S4 — Neutrals, verbatim (L2): "Neutros puros (Recomendado)". Dark surfaces and text greys have chroma 0.
- S5 — Prior decisions stay binding: OLED canvas and near-black scroll/functional surfaces
  (`dark-design-benchmark.md:13`), indigo identity, Dark ANSI slots 6/14 semantics, only Dark and Light modes.

## Evidence baseline (explore + repo math, 2026-11-27)

- Accents (OKLab L / WCAG on bg): error .748/8.80, warning .837/12.58, success .773/10.92, info .828/12.60,
  accent .785/10.53, accent_2 .825/11.83, mauve .827/11.88, focus .623/5.71 (3.09 on selection). L spread .214.
- ΔE2000 < 12: mauve ↔ lavender/accent_2 1.0 (indistinct), accent ↔ accent_2 11.9; implicit duplicates
  info = diagnostic, accent_2 = lavender (0.0).
- Text hierarchy inverted: comment 13.62:1 is louder than muted 12.42:1; subtle = disabled (`#A7A7A7`).
- Surfaces: bg_soft = surface0 (`#0B0B0B`), surface1 ΔL .010 above it; ladder L 0, .150, .160, .239, .301, .348.
- No Dark primitives/bindings; Dark gets no elevation/radius/rhythm (`elevation.adopts_components`); black
  shadows on black (hypr/rofi/opencode); `_math.py:68` falls back to `#100f0d`.
- Hand-written Dark files on the old `#100f0d` palette: Alacritty, WezTerm, tmux, Zellij `config-dark.kdl`.
- Dark wallpaper contract hue window 70°±25 contradicts the indigo identity; all Dark wallpapers fail it.
- Tests pinning Dark bytes: `test_dark_neutral_palette.py:83`, `test_dark_ansi_semantics.py`, `test_dark_cross_app_states.py`,
  `test_light_elevation.py:213`, `test_light_rhythm.py:307,326`, `test_herdr_app_theme.py:16`, others — re-pin deliberately.

## Design principles (grounding)

1. **Light from the screen, not on it.** On OLED black a shadow is invisible; elevation is luminance: each level
   lifts the surface by a perceptually even OKLab ΔL (emissive model), with no drop shadows in Dark.
2. **Night density.** Pigments share one OKLab L (isoluminance) high enough for ≥ 7:1 on bg and ≥ 4.5:1 on the
   highest text surface; chroma tamed for halation on black (bright saturated text blooms on OLED).
3. **Recede, don't shout.** Text ramp strictly ordered: heading > text > muted > comment > subtle > disabled.
4. **Neutral greys** (chroma 0), indigo only where meaning lives.

## Tasks

| ID | Specs | Task | Route | Commit |
| --- | --- | --- | --- | --- |
| T1 | S1 | Baseline: live Dark screenshot, Dark specimen, measurements recorded | inline | 96dd168 |
| T2 | S1-S5 | Dark primitives + bindings (neutral ramp, 8 pigment families at night density, indigo brand), material laws in `tests/test_dark_material.py`, deliberate re-pins | worker | ae28a10 |
| T3 | S1,S2 | Dark components: tonal elevation (no shadows), radius/rhythm adopted for Dark, renderer literals | worker | — |
| T4 | S1 | Generate the stale hand-written Dark files; guard test like `test_light_color_files.py` | worker | — |
| T5 | S1,S3 | Dark wallpaper contract: hue rule follows identity (neutral or indigo), not warm | inline | — |
| T6 | S1 | Live verification at night; specimen + DTCG export include Dark primitives | inline | — |
| T7 | S1 | Docs, skills, changelog | worker | — |
| T8 | S1 | Benchmark vs reference dark themes; close | inline | — |

## Log

- L1 — User request (2026-11-27), verbatim: "perfect continuemos asi como mejoramos dreamcoder light ahora meoremos
  dreamcoder dark".
- L2 — User decisions (2026-11-27), verbatim: canvas "Mantener #000 OLED (Recomendado)"; identity "Índigo + familias
  de Light (Recomendado)"; neutrals "Neutros puros (Recomendado)".
- L3 — T1 baseline: live Dark at 21:49 (`odd/evidence/dark-coherence/t1-desktop-before.png`). Already improved by the
  Light branch: Waybar `133` badge is an indigo wash, window edge solid. Still off: teal `ml.` launcher tile, cold
  blue photographic wallpaper unrelated to the system, card/code greys not on a measured ladder. Measurements in
  "Evidence baseline" verified with the repo's `_math` / `color_space` (not the explorer's JS port).
- L4 — T2 design (laws to pin in `tests/test_dark_material.py`; values are the worker's to tune within them):
  - graphite (neutral, C < 0.002): bg `#000000` (S2); tonal ladder surface0 < surface1 < surface2 < surface3 <
    selection with even ΔL ≥ 0.04 (OLED emissive elevation; surface0 stays near-black ≈ L .15 per S5). bg_soft is an
    explicit alias of surface0; hover/pressed alias selection/surface2.
  - text ramp strictly ordered by L: text_heading > text > muted > comment > subtle > disabled (comment recedes
    below muted), each step ΔL ≥ 0.04; muted ≥ 7:1 on bg; comment and subtle ≥ 4.5:1 on bg…surface2 and selection.
    border < border_ui < border_hi stay ≥ 3:1 on bg where they are UI boundaries (border_ui, border_hi).
  - pigments at one night density: OKLab L spread ≤ 0.01 across error, warning, success, info, accent, lavender,
    mauve, focus; every one ≥ 7:1 on bg and ≥ 4.5:1 on selection; chroma ≤ 0.13 (halation on OLED black).
    Families follow Light's hue order around the wheel: madder (error) < ochre (warning) < malachite (success) <
    verdigris (focus) < indigo (info) < iris (accent, Dark brand ≈ H 275, S3) < violet (lavender) < cochineal (mauve).
    Pairwise ΔE2000 ≥ 12 among those eight roles.
  - hover: accent_2 / link_hover in the iris family (|ΔH| ≤ 6° from accent), lighter than accent (emission), ΔE ≥ 12
    from lavender and mauve.
  - explicit aliases: diagnostic = info, sage = success, link = accent, prompt_accent = accent.
  - focus ring ≥ 3:1 on every surface including selection.
  - Preserve S5: ANSI slots 6/14 semantic assertions in `test_dark_ansi_semantics.py` keep holding (re-pin only byte
    baselines, never the semantic checks); `aliases.brand` (filled indigo) and `on_accent` contrast floors still pass.
- L5 — T2 result: `primitives.dark` (graphite chroma 0 + madder, ochre, malachite, verdigris, indigo, iris, violet,
  cochineal at L .790; iris.865 hover) and `bindings.dark` for all 46 hex roles; `tests/test_dark_material.py`
  (29 laws, RED 16/29 before). Metrics: pigment L spread 0.000, min ΔE 14.24 (was 1.0), pigments ≥ 10.31:1 on bg
  and ≥ 6.48:1 on selection, focus ≥ 7.05:1 everywhere, ladder ΔL 0.042, strict text ramp. Deviations forced by
  existing guards: surface0 L .142, subtle L .720, border_ui L .570, pigment L .790. Focus moved blue → verdigris
  (ΔE 32.7, S3). DTCG export emits `primitive.dark`; pi-theme bats reads the dark accent from tokens. Light
  byte-identical (tokens light/primitives/components equal HEAD; theme-diff: 40 roles changed, all dark, 0 floors
  crossed). `effects.glow_focus` still blue → T3.
- L6 — T3 design (Dark components; Light output byte-identical):
  - Elevation is tonal on OLED: levels e1–e4 resolve to graphite surfaces (e1 surface1, e2 surface2, e3 surface3,
    e4 selection), lighter as they rise (emission). Shadows keep the Light geometry (one overhead key + ambient) with
    ink `graphite.000`: invisible on the black canvas, visible only where a window floats over the lit wallpaper —
    the physically correct reading. e3/e4 also get a top-edge hairline one ladder step lighter (the overhead key
    catching the top edge).
  - Dark adopts the mode-independent geometry: radius r1–r3, hairline, spacing grid, motion curves and durations,
    type contract — Hyprland gaps/animations, Waybar module rhythm and rofi radii match Light.
  - Effects derive from tokens: `glow_focus` from `focus`, `glow_brand` from `aliases.brand`, `glow_error` from
    `error` (same blur/alpha as today).
  - Remove Dark literals: `_math.py:68` `#100f0d` fallback → the mode's own bg; `renderers_herdr.py:13` `#6FA0AF` →
    the semantic token it stands for (name it); OpenCode Dark shadow and hypr/rofi `#000000` → the elevation ink.
- L7 — T3 result: Dark adopts the component tier. Tonal elevation (e1–e4 → graphite 184/226/268/310, top-edge
  hairline for e3/e4 via new `graphite.352`), shadow ink graphite.000 resolved from primitives; radius, spacing,
  motion, type equal Light's (Hyprland gaps/animations, Waybar rhythm, rofi radii). `effects.py` derives
  glow_focus (verdigris), glow_brand, glow_error (now `error`) with an EFFECTS_DRIFT health check. Literals gone:
  `#100f0d` fallback → mode canvas, Herdr `#6FA0AF` → `accent` (both modes). Light artifacts unchanged
  (`theme-diff HEAD`: no perceptual change). Tests encoding "Dark unchanged" from the Light feature updated to the
  new intended Dark behaviour (listed in the worker report); no contrast/ΔE assertion weakened.
