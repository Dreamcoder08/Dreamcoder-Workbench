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
| T3 | S1,S2 | Dark components: tonal elevation (no shadows), radius/rhythm adopted for Dark, renderer literals | worker | dc89418 |
| T4 | S1 | Generate the stale hand-written Dark files; guard test like `test_light_color_files.py` | worker | 61a0611 |
| T5 | S1,S3 | Dark wallpaper contract: hue rule follows identity (neutral or indigo), not warm | inline | aad4099 |
| T6 | S1 | Live verification at night; specimen + DTCG export include Dark primitives | inline | 66243b8 |
| T7 | S1 | Docs, skills, changelog | worker | 66243b8 |
| T9 | S1 | Calm the text ramp for OLED halation: text ≈ 15:1, comment ≈ 7–8:1, AAA kept (L12) | worker | — |
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
- L8 — T4 result: Light-only file renderers generalised into `renderers_mode_files.py` (`MODE_FILES` per mode,
  `sync_mode_files(mode, palette)`); Dark Alacritty, WezTerm, Nushell, tmux blocks and the Zellij theme block are
  generated; `apply-theme-mode.sh` Dark branch sources generated `tmux-ukiyo-dark.conf` (no colour literals left
  in the script). Guard `tests/test_dark_color_files.py` (allowlist: generated `dreamcoder-dark.css`, ARGB
  `qt6ct-dark.conf`, each pinned to its generator). Light byte-identical. For T6/T7: docs and theme-engine skill
  still name `renderers_light_files.py`/`sync_light_files`; `DreamcoderNushell/env.nu` prompt literals (both modes)
  remain; Dark tmux ukiyo notice/highlight now accent_2/focus — check live.
- L9 — T5 result: Dark wallpaper hue window 275° ± 30 (iris accent hue; law test keeps it within 10° of the iris
  primitive), Light unchanged at 70° ± 25. RED 3 → GREEN 55: an indigo night passes in dark mode, a warm night fails
  WALLPAPER_HUE. The four existing blue night wallpapers no longer fail hue; they still fail size, lightness,
  safe zone and readability, as they should.
- L10 — T6 live pass (23:00): live Dark sync from the worktree applied (bridge `primary` #a7b5fd, solid iris
  window edge via hyprctl); the bat step again wrote through stow links into the main checkout's two `.tmTheme`
  files — restored with `git checkout`, main status identical to before. The session was locked (hyprlock), so
  only the lock screen was captured (`t6-lockscreen-after.png`: iris border and clock); the desktop capture waits
  for the user. Next: Dark specimen board + docs (T6/T7), benchmark (T8).
- L11 — T6/T7 result: `generate-specimen.py --mode dark` → `docs/generated/dreamcoder-dark-specimen.svg` (graphite
  text ramp, tonal ladder, pigments in hue order, roles on six surfaces with WCAG + APCA magnitude, tonal elevation
  e0–e4 with top-edge hairlines, ΔE matrix); wired into `make specimen` and the preview hook; Light board
  byte-identical. Docs: "Dark material model" section, stale `sync_light_files` names fixed, both skills and the
  changelog updated. T8 benchmark in `odd/evidence/dark-coherence/t8-benchmark.md`: leads on weakest accent 10.31:1,
  isoluminance 0.002, chroma cap; behind Rosé Pine/Dracula on min ΔE (14.2 vs 19.9/18.2); open weakness: comment
  13.3:1 barely recedes and near-white 17.6:1 text on OLED black risks halation.
- L12 — User decision (2026-11-27), verbatim: "Sí, calmar texto y comentarios (Recomendado)" — text about 15:1,
  comments about 7–8:1, keep AAA. New task T9.
- L13 — T9 conflict (worker, measured): comment 7–8.5:1 (L ≤ .721) and the Qt guard (disabled ≥ 4.5:1 on selection,
  L ≥ .675) leave .046 of lightness, but comment > subtle > disabled needs ≥ .08 under the L4 law. Decision (parent,
  under the user's "te autorizo todo"): option C — keep every law; Qt disabled `HighlightedText` on a selected row
  uses `comment` (readable on selection; WCAG 2.2 exempts inactive controls anyway), so `disabled` can drop to about
  L .64 with the ΔL ≥ .04 ramp intact. Rejected: A/B weaken the ramp law (tail ΔL .02 ≈ JND), D drops L12.
- L14 — T9 second conflict: the existing AAA pin `comment ≥ 7:1 on surface2` (`test_dark_neutral_palette.py:117`)
  needs comment L ≥ .727 (≈ 8.7:1 on bg), above the new 8.5 ceiling. Decision (parent): option 2 — keep the
  existing AAA pin; the L12 comment window becomes [7.0, 9.0] on bg (comment L ≈ .73, ≈ 8.8:1). The "7–8" figure
  was the parent's own approximation; loosening a standing contrast guard to meet it would weaken the system.
  Comments still drop from 13.3:1 to ≈ 8.8:1 and text from 17.6:1 to ≈ 15:1.
- L15 — T9 third conflict: the sync gate keeps `disabled` APCA ≥ 44 on bg (`minimum_apca_quiet`); with the ΔL ≥ .04
  ramp that puts the lowest comment at `#adadad` ≈ 9.36:1. Decision (parent): option A — keep every standing guard
  (AAA on surface2, quiet APCA floor, even ramp); the parent's own comment window becomes [7.0, 9.5]. Outcome vs
  start: text 17.6 → 15.0:1, comment 13.3 → ≈ 9.4:1, text–comment gap 4.3 → 5.7. The Qt disabled-on-selection
  change (L13) stays necessary (`disabled` ≈ L .663 is under 4.5:1 on selection).
- L16 — T9 fourth conflict (worker): with comment ≈ 9.4:1 two standing nvim readability guards fail —
  comment vs subtle contrast ≥ 1.5 (measured 1.165) and string (sage) vs comment distance ≥ 80 (59.3) — plus the
  Claude Code dark `diffAddedWord` band at 6.89:1 (< 7.0). Root cause (parent, measured): with `disabled` held by
  the quiet APCA floor (≈ L .663) and subtle one step above (L .706), the comment/subtle ≥ 1.5 guard needs comment
  ≥ L ≈ .825 (≈ 12.2:1). The earlier bright comment was forced by legitimate guards, not an oversight. Decision:
  keep every standing guard; correct only the parent's own new targets. Ramp: heading L .945, text .905
  (≈ 15.9:1), muted .865, comment .825, subtle .706, disabled .663; own windows: text [14, 16], heading ≤ 18.0,
  comment [7.0, 12.5]. Outcome: halation reduced (text 17.6 → ≈ 15.9:1, heading 20.1 → ≈ 17.9:1); comment
  recession NOT achievable under the distinctness guards (comment/text ratio ≈ unchanged). The Claude Code dark word
  tint is a derived value: tune it (approved). Keep the Qt disabled-on-selection change (still needed).
- L17 — T9 result: ramp heading `#eeeeee` 18.10:1, text `#e0e0e0` 15.91:1, muted `#d2d2d2` 13.89:1, comment `#c5c5c5`
  12.17:1, subtle `#a0a0a0` 8.03:1, disabled `#939393` 6.84:1 (ΔL ≥ .04, comment/subtle ≥ 1.5, quiet APCA ≥ 44);
  own heading ceiling 18.2. Qt disabled `HighlightedText` = comment (function-level Light difference only, no Light
  file ships). Claude Code tint unchanged (passes at the final text). theme-diff: 10 dark roles, max ΔE 2.47,
  0 floors crossed; Light unchanged. Benchmark row updated.
