# Dreamcoder Light — Holistic Design-System Coherence

Raise Dreamcoder Light (tokens, every app target, and the wallpapers) to one physically grounded,
measurable visual language, then remove legacy and redundant parts. Status: in progress.
Branch `feat/light-coherence` off `origin/main` in worktree `.local-backups/worktrees/light-coherence`.

## Specs

- S1 — Scope, verbatim: "mejorar aun mas el system desing de dreamcoder light inclutendo sus walppaper".
- S2 — Coherence, verbatim: "todo debe tener coherencia visual , de diseño". Every Light surface
  (terminals, editors, shells, Herdr, Waybar, rofi, GTK/Qt, Gentle Shell/Pi, wallpapers) derives from
  one token source; no hand-copied hex values outside generated artifacts.
- S3 — Method, verbatim: "se critico eres genio holisitico interdiciplinario , la fisica , la quimica ,
  e ingenerias , fundamentos , patrones y mas debes aplicar para mejorar todo". Each design decision
  records its grounding (color science, optics, pigment chemistry, engineering pattern) and a measurable check.
- S4 — Ambition, verbatim: "ser mejor que los mejores del mundo y en la vanguardia". Benchmark is by
  measured metrics against reference systems, never by copying their palettes or assets.
- S5 — Cleanup, verbatim: "has limpieza al final elimina lo legacy redundante y mas". Last phase removes
  redundant sources, stale docs and dead assets, with proof of non-use for every deletion.
- S6 — Reference screenshot (L1 image): Herdr + Gentle Shell + Waybar over a peach/cream wallpaper.
  Observed defects to fix: wallpaper is more saturated/orange than the UI paper; saturated red `102`
  badge and teal `ml.` icon break the palette; orange window border competes with the accent; mixed
  elevation cues (borders, flat cards, left rules) with no single light model.

- S7 — Wallpaper source, verbatim (L3): "pide a codex cli que las genere".

## Evidence baseline (explore handoff, 2026-11-26)

- Tokens: `DreamcoderThemes/dreamcoder/tokens.json` (light ~L113–175, `dusk` still present, `:4` says
  "Dreamcoder OS"). Duplicate source: `src/dreamcoder_theme/palette_tokens.py:12–130`.
- No ANSI-16 in tokens; derived in `palette.py`. Adaptive accents via matugen `palette.py:91–122`.
- Hardcoded offenders: `DreamcoderNvim/.config/nvim/colors/dreamcoder-light.lua` (~200+ hex),
  `scripts/apply-theme-mode.sh:142–171` (22 tmux literals), renderer literals
  (`renderers_hypr_waybar_rofi.py:334–335`, `renderers_herdr.py:13`, `renderers_opencode.py:170`).
- Wallpapers: 8 ChatGPT exports, 1672×941 / 1536×1024 (below 1080p → upscaled blur on 1920×1080).
  Only 2 are light (mean luminance 0.84, 0.77; average `#F0D7BF`, `#DFC8B0`); 1 mid, 5 dark.
  No generator; `scripts/WALLPAPER_SETUP.md` claims a fixed palette that contradicts adaptive matugen.
- Gates: `scripts/verify-theme-health.py`, `tests/test_light_*`, `test_apca_implementation.py`,
  `test_token_parity.py`; no Makefile theme target.

## Design principles (grounding for S3)

1. **One light, one material.** A single key light (top-left, ~30° elevation) plus ambient sky term
   drives every shadow, wallpaper shading and elevation token (Lambert + soft-shadow penumbra model).
2. **Paper chemistry.** Neutrals sit on one warm hue axis modelled on aged cellulose paper (lignin
   yellowing → warm white point near D50); chroma rises monotonically as lightness falls.
3. **Pigment accents.** Accent family mapped to historical mineral pigments (burnt umber/sienna = iron
   oxide for `accent`, ochre for warning, verdigris for focus/success, ultramarine/indigo for info,
   cochineal/madder for error). Mixing and washes use Kubelka–Munk, not RGB lerp.
4. **Perceptual math.** Ramps authored in OKLCH, verified with APCA Lc and WCAG 2.x, ΔE2000 for
   distinctness, Helmholtz–Kohlrausch correction for saturated small marks (badges, icons).
5. **Signal processing.** Gradients use blue-noise dithering to kill 8-bit banding; wallpapers render
   at native 3840×2160 with downsampled variants (no upscaling).
6. **Engineering.** Three-tier tokens (primitive → semantic → component, W3C DTCG shape), single
   source, generated outputs, golden + perceptual-diff tests, deterministic builds.

## Tasks

| ID | Specs | Task | Route | Commit |
| --- | --- | --- | --- | --- |
| T1 | S2,S6 | Baseline: screenshot every Light target, contrast/ΔE report, full hex-literal inventory (uncapped) | inline | — |
| T2 | S2,S3 | Token v2: DTCG three-tier `tokens.json`, OKLCH primitives; generate `palette_tokens.py` from it; parity test (Risk 3: config format) | inline, own commit | 0979a31 |
| T3 | S3,S4 | Material model: paper neutrals + pigment accents + ANSI-16 in tokens, all guarded (APCA/WCAG/ΔE) | inline | T3 commit |
| T4 | S3,S6 | Light & elevation: key/ambient shadow tokens, radius, border scale, translucency floor over wallpaper | inline | — |
| T5 | S2 | Type, spacing (4 pt), motion tokens → Hyprland, Waybar, rofi, Herdr, GTK/Qt | writer A (parallel with T6) | — |
| T6 | S1,S3,S7 | Wallpapers via Codex CLI image generation from a token-derived brief (paper, pigment washes, single key light, bar safe zones); Light set + paired Dark companions; post-process (≥1920×1080, blue-noise dither) and gate on T7 | inline + Codex CLI | — |
| T7 | S1,S2 | Wallpaper↔UI contract: OKLab L band, chroma cap, hue window around accent, APCA test of panels over worst wallpaper region; clamp matugen adaptive mode | inline | — |
| T8 | S2 | Migrate offenders: generate nvim `dreamcoder-light.lua`, tmux colors, renderer literals; audit Waybar/Herdr/Pi/ml4w_assets | inline | — |
| T9 | S6 | Semantic chrome: badges, status icons, focus ring, window borders unified across Herdr/Waybar/Gentle Shell | inline | — |
| T10 | S4 | Visual regression: specimen board, perceptual diff (ΔE2000), `make theme-check`, CI hook (Risk 5) | inline, own commit | — |
| T11 | S2,S6 | Live verification on Hyprland: reload, GTK/Qt, screenshots vs T1; close open items of `light-theme-delivery.md` | inline | — |
| T12 | S2 | Docs: rewrite `docs/DREAMCODER_DESIGN_SYSTEM.md`, fix `WALLPAPER_SETUP.md`, update both skills | inline | — |
| T13 | S5 | Cleanup (gated by D2/D3): dusk, duplicate token source, checked-in generated files, old wallpapers, "Dreamcoder OS", archived `docs/superpowers` (Risk 1/3: each deletion proven unused) | inline, own commit | — |
| T14 | S4 | Benchmark vs reference systems by metrics (contrast margins, ramp uniformity, ΔE spacing, banding); close feature | verify | — |

## Decisions (human)

- D1 — Decided (L3): Codex CLI generates the wallpapers, validated against the T7 contract.
- D2 — Decided (L3): remove `dusk` entirely.
- D3 — Decided (L3): delete the 8 ChatGPT wallpapers once replacements land.

## Log

- L1 — User request (2026-11-26), verbatim: "Crea gran Plan ODD para mejorar aun mas el system desing de
  dreamcoder light inclutendo sus walppaper todo debe tener coherencia visual , de diseño , [Image#1] , se
  critico eres genio holisitico interdiciplinario , la fisica , la quimica , e ingenerias , fundamentos ,
  patrones y mas debes aplicar para mejorar todo y ser mejor que los mejores del mundo y en la vanguardia
  y has limpieza al final elimina lo legacy redundante y mas"
- L2 — Explore handoff and wallpaper measurements recorded in "Evidence baseline".
- L3 — User decisions (2026-11-26), verbatim: D1 "pide a codex cli que las genere"; D2 "Eliminar (Recomendado)";
  D3 "Borrarlos (Recomendado)"; start "Sí, empezar con T1".
- L5 — T2 implementation: tiers are additive (`primitives.light` 29 OKLCH, `bindings.light` 45 keys); `modes.*`
  stays flat hex so every consumer is unchanged (repo-only sync: 0 output changes). OKLCH math moved to
  `src/dreamcoder_theme/color_space.py`; health gate reports `TIER_DRIFT`/`TIER_UNBOUND`. Component tier lands
  with T4/T5 tokens; dark bindings with T3. T3 findings: ink steps 0.480 (`comment`) and 0.485 (`border_ui`)
  are perceptually indistinct; paper hue drifts 73.7–91.5°, ink hue 55.6–78.2°; accents already near-isoluminant
  (L 0.463–0.501).
- L6 — T2 independent verify: PASS (S2, S3). Advisories fixed test-first: schema hue/chroma ranges now match the
  parser, `format_oklch` wraps hue 360→0, out-of-range primitives raise `TierError`, generator reuses
  `color_space` sRGB helpers.
- L7 — T3 measurements (ΔE2000 validated vs Sharma 2005): info↔diagnostic ΔE 2.1 (indistinct); accent_2↔error
  ΔE 8.7 (hover link reads as error, hues 38°/27°); subtle/comment/border_ui within ΔL 0.024; pigment L wanders
  0.463–0.501; several pigments < 4.5 on surface3. T3 design (laws pinned in `tests/test_light_material.py`):
  - paper: hue 82°→72° as L falls (lignin reddening), C = 0.0035 + 0.089·(1−L); keep L steps
    surface0 .994, bg .974, bg_soft .951, surface1 .936, surface2 .900, surface3 .848 (elevation is T4).
  - ink (iron-gall/sepia): hue 62°, C = 0.010 + 0.020·L; steps .160 heading; .215 text/on_surface/
    prompt_text/selection_fg; .315 muted/prompt_muted/border_hi; .455 subtle/comment/border_ui; .540 disabled;
    .620 border (lower L if a test floor needs it).
  - pigments at one density L_P ≈ 0.455 (lower only if a contrast floor needs it): madder error H25 C.160;
    umber accent/link/prompt_accent H52 C.115; ochre warning H85 C.100; malachite success+sage H148 C.115;
    verdigris focus H200 C.085; indigo info+diagnostic H245 C.110; violet lavender H290 C.120; cochineal mauve
    H340 C.120. Hover accent_2/link_hover/prompt_accent_2 = deeper umber H48 L≈0.40 C≈0.125. Clamp C to gamut.
  - clay (umber wash on paper): hue 62°, C = 0.40·(1−L); keep L of selection/selection_bg, prompt_surface0..2.
  - on_accent/on_error/on_focus stay paper surface0; rgba keys (panel_rgba, module_rgba, active_rgba,
    inactive_border, overlay, scrim) recomputed from their base hex with unchanged alpha.
  - ANSI stays derived from these semantic tokens in `palette.py` (already single source); no ANSI copy in tokens.
- L8 — T3 result: 25 light primitives (paper, ink, clay + 8 pigments at L .455). Deviations from L7, forced by
  existing guards: subtle .400 ≠ comment .455 (health requires comment ≠ subtle; nvim needs comment/muted ≥ 2:1),
  muted .265; `paper.974` tuned to keep bg `#f9f6f2` (Herdr test pin); sRGB gamut clamped umber.400 C .109,
  ochre C .093, verdigris C .077. Metrics: min pigment ΔE2000 15.1 (was 2.1), accent_2↔error 15.5 (was 8.7),
  min WCAG over text surfaces 5.14 (success on surface2), APCA on bg 78–86. Three Light snapshots from the Dark
  features re-pinned to the new palette (ANSI baseline, Starship sha256, adaptive fingerprint); Dark/Dusk pins
  unchanged.
