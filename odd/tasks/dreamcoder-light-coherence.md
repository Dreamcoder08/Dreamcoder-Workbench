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
| T1 | S2,S6 | Baseline: screenshot every Light target, contrast/ΔE report, full hex-literal inventory (uncapped) | inline | 49620af |
| T2 | S2,S3 | Token v2: DTCG three-tier `tokens.json`, OKLCH primitives; generate `palette_tokens.py` from it; parity test (Risk 3: config format) | inline, own commit | cb62884 |
| T3 | S3,S4 | Material model: paper neutrals + pigment accents + ANSI-16 in tokens, all guarded (APCA/WCAG/ΔE) | inline | 94ff703 |
| T4 | S3,S6 | Light & elevation: key/ambient shadow tokens, radius, border scale, translucency floor over wallpaper | inline | 2dc9292 |
| T5 | S2 | Type, spacing (4 pt), motion tokens → Hyprland, Waybar, rofi, Herdr, GTK/Qt | writer A (parallel with T6) | dd38a84 |
| T6 | S1,S3,S7 | Wallpapers via Codex CLI image generation from a token-derived brief (paper, pigment washes, single key light, bar safe zones); Light set + paired Dark companions; post-process (≥1920×1080, blue-noise dither) and gate on T7 | inline + Codex CLI | — |
| T7 | S1,S2 | Wallpaper↔UI contract: OKLab L band, chroma cap, hue window around accent, APCA test of panels over worst wallpaper region; clamp matugen adaptive mode | inline | eab3706 |
| T8 | S2 | Migrate offenders: generate nvim `dreamcoder-light.lua`, tmux colors, renderer literals; audit Waybar/Herdr/Pi/ml4w_assets | inline | 7d5500e |
| T9 | S6 | Semantic chrome: badges, status icons, focus ring, window borders unified across Herdr/Waybar/Gentle Shell | inline | dff0e7e |
| T10 | S4 | Visual regression: specimen board, perceptual diff (ΔE2000), `make theme-check`, CI hook (Risk 5) | inline, own commit | 3850a78 |
| T11 | S2,S6 | Live verification on Hyprland: reload, GTK/Qt, screenshots vs T1; close open items of `light-theme-delivery.md` | inline | — |
| T12 | S2 | Docs: rewrite `docs/DREAMCODER_DESIGN_SYSTEM.md`, fix `WALLPAPER_SETUP.md`, update both skills | inline | eb2081f |
| T13 | S5 | Cleanup (gated by D2/D3): dusk, duplicate token source, checked-in generated files, old wallpapers, "Dreamcoder OS", archived `docs/superpowers` (Risk 1/3: each deletion proven unused) | inline, own commit | — |
| T15 | S2,S4 | DTCG 2025.10 interop export: generated `docs/generated/dreamcoder.tokens.json` validated against the vendored official schema | worker | cc12e99 |
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
- L9 — T4 design (one light model, first component tier):
  - Key light: overhead, slightly in front of the screen (no lateral offset), so every shadow falls straight
    down; the T6 wallpaper brief uses the same light. Two-term shadow (Lambert key + sky ambient):
    key = `0 {0.5z}px {z}px` and ambient = `0 0 {2z}px`, z per level e1=1, e2=3, e3=8, e4=16 (×~2.5 geometric).
  - Shadow colour is warm ink, never black: light shadows use the `ink.215` primitive (interreflection off warm
    paper keeps umbra warm); alphas key .10/.12/.14/.16 and ambient .05/.06/.07/.08 for e1..e4.
  - Elevation ladder: canvas bg e0; surface1/module e1; surface0 cards e2; popovers/menus/rofi e3; modal/
    notification e4. Radius scale r1 4, r2 8, r3 12 px; windows use r3; hairline border 1px `border`.
  - Tokens: new top-level `components` (tier 3) with `elevation`, `radius`, `border` geometry; per-mode colour
    comes from a primitive name, resolved like bindings. Light only; Dark output must stay byte-identical.
- L10 — T4 result: `components` tier (elevation e1–e4, radius r1–r3, hairline border) resolved by
  `src/dreamcoder_theme/elevation.py`, merged into Light palettes by `load_variants`. Wired: Hyprland shadow/scrim
  warm ink instead of black, Waybar modules r2 + e1, rofi radii r3/r2. Dark byte-identical (dark sync no diff).
  Left for T8/T9: Herdr, GTK/Qt, Gentle Shell/Pi, OpenCode shadow literal, hairline border consumers, Waybar e2–e4.
- L11 — Order change: T7 (contract) runs before T6 so Codex-generated wallpapers are gated by a test, not by eye.
  Codex CLI 0.172 has `image_generation` (stable); output ≤ ~1536×1024, so T6 finishes images by Lanczos upscale
  to 3840×2160 plus native-resolution paper grain and TPDF dither (low-frequency art needs no source resolution;
  fine texture is synthesized at output size). No PIL/numpy in the project: tools use ImageMagick via
  `command -v magick`, no new Python dependency (avoids Risk 5).
  T7 contract (`components.wallpaper.<mode>` in tokens.json, measured in OKLab on a downsample):
  - size ≥ 3840×2160, aspect 16:9 ± 1%.
  - light: mean L in [0.86, 0.97]; dark: mean L in [0.08, 0.22].
  - chroma: p95 C ≤ 0.060 and mean C ≤ 0.035 (the T1 wallpaper was too saturated against the UI paper).
  - hue: chroma-weighted circular mean hue within ±25° of 70° (paper/clay/umber axis) when mean C ≥ 0.01.
  - bar safe zone (top 6% and bottom 6%): std L ≤ 0.035; light mean L ≥ 0.88.
  - readability: Waybar `module_rgba` composited over the darkest 1% of the top band keeps `text` ≥ 7:1 WCAG and
    `muted` ≥ 4.5:1; `panel_rgba` over the image's darkest 1% keeps `text` ≥ 7:1.
- L12 — T7 result: `components.wallpaper.{light,dark}` + `wallpaper_contract.py` + `scripts/check-wallpaper.py`
  (51 tests). All 8 current wallpapers fail: both light ones on size/chroma (p95 0.103–0.110)/safe zone; dark
  ones on size, lightness (0.26–0.35 > 0.22), safe zone, bar readability 1.9–3.0:1, and three on hue (258–267°).
  Light readability can only fail with a weaker palette (module/panel alphas hold 7:1 over black): a guard.
- L13 — T6 blocker: Codex CLI 0.172 runs on a ChatGPT account; its built-in `image_gen` returns 403 Forbidden
  (model gpt-5.6-terra); gpt-6-sol is not allowed on ChatGPT accounts; no `OPENAI_API_KEY` for the API path.
  Needs a human decision. Done meanwhile: `scripts/finish-wallpaper.sh` (16:9 crop, linear-light Lanczos to
  3840×2160, additive paper grain ~1.4 code values RMS, ordered dither to 8-bit, byte-deterministic) with
  `tests/test_finish_wallpaper.py`. ImageMagick 7.1.2-36 `SoftLight` composite returns white (bug), so the grain
  is additive `Mathematics`; ordered dither replaces TPDF for reproducible builds.
- L14 — User decision on the T6 blocker, verbatim: "Habilito Codex y te aviso". T6 waits; T9, T8, T5 continue.
  T9 design (S6 defects from the screenshot, Light only, Dark byte-identical):
  - Pigment wash rule (Kubelka–Munk thin layer): any coloured chip/badge/tile = pigment at ~12–16% over paper as
    fill, the same pigment as text/icon. No saturated solid fills in Light chrome.
  - Waybar count badges (e.g. updates `102`): neutral clay chip (`selection` fill, `accent` text); only real
    error/critical states use the madder wash. ML4W/settings tile (teal `ml.`): umber wash tile.
  - Hyprland active border: solid `accent` (no accent→paper gradient); inactive: `inactive_border`.
  - Gentle Shell / Pi Light: no dark fills inside Light (the violet "Delegating" block); tool/delegation blocks
    use `surface1`/`surface0` with a pigment left rule and ink text.
- L15 — T9 result (partial by design): Light Waybar updates badge = clay chip with umber text, only `.critical` a
  madder wash; live override `style-custom.css` washes ML4W's `.red/.yellow` badge (GTK CSS cannot tell modes
  apart, so Dark live badges become washes too — flagged to the user); Hyprland Light border solid accent in
  `hyprland-light.conf`. Open, moved to T11: (a) ML4W Lua `conf/windows/default.lua:7` still draws the live
  `primary→on_primary` gradient — needs a wired override; (b) the teal `ml.` tile is an ML4W SVG, kept as is
  (blanking it lost the launcher glyph) — needs a recoloured glyph. Upstream (gentle-pi, not this repo): the
  violet "Delegating" card is `extensions/gentle-agents.ts:584` `IRIS_TINT_BG #1a1526` with no theme hook.
- L16 — T8 design: every Light colour file is either generated from tokens (preferred: renderer + registry,
  Dark output byte-identical) or, when a renderer is disproportionate, uses only exact current Light token
  values. Guard test: no tracked Light colour file outside the generated set contains a hex that is not a
  current `modes.light` value (allowlist only with a written reason). Inventory: T1 baseline list in
  `odd/evidence/light-coherence/t1-baseline.md` (Light entries), `scripts/apply-theme-mode.sh` tmux literals,
  renderer literals (`renderers_herdr.py:13`, `renderers_opencode.py:170` shadow).
- L17 — T8 result: 7 Light files now generated (`renderers_light_files.py`, `sync_light_files`): Alacritty,
  WezTerm, Nushell, Tmux blocks + base, Yazi, Zellij theme block (spliced in place); `apply-theme-mode.sh` Light
  sources generated `tmux-ukiyo-light.conf`; OpenCode Light shadow is warm ink. Guard `tests/test_light_color_files.py`
  (every non-generated Light file uses only current Light tokens). Dark unchanged. Pre-existing, not T8:
  `shell-tests/test_doctor.bats` #1 fails and `test_repair.bats` hangs at #4 on base 82b1bc2 too. For T13: orphan
  mode-less mirrors (`btop/bat/cava/delta/dunst/firefox/fzf/ls-colors/obsidian-dreamcoder.*`, `tmux-dreamcoder.conf`,
  `zsh-syntax-highlighting-dreamcoder.zsh`) with old-palette hex; hand-written Dark Alacritty/WezTerm/Nushell/Tmux
  still on old `#100f0d` (out of Light scope, report only).
- L18 — Order change: T13 (cleanup, minus wallpapers which wait for T6) runs before T5/T10 to shrink their
  surface. Scope: (1) remove `dusk` everywhere (D2): tokens, schema, generator, palette, targets, renderer
  contract, health gate, preview, installer, profiles schema, tests, skills, docs; (2) delete tracked Zellij
  `*.bak.*` and foreign-theme layouts (`work_everforest|kanagawa|oldWorld|sakura`) if unreferenced; (3) delete
  orphan mode-less mirrors listed in L17 if nothing reads them; (4) `.p10k.zsh` only if no shell config sources
  it; (5) identity "Dreamcoder OS" → "Dreamcoder Workbench" in tokens + schema. Every deletion needs grep evidence
  of non-use (scripts, installer, lib, stow layout, docs links). Dark/Light outputs unchanged.
- L19 — T13 result (cleanup part 1, −3492 lines): `dusk` removed from tokens, schema, design-system contract,
  targets (`dusk-runtime` target dropped, 37→36), generator, palette, renderer contract, health gate, preview,
  installer help, profile schema, nvim, skills, CLAUDE/AGENTS, docs; `light_hours_default` now 07:00-18:00 (matches
  the systemd timer). Deleted with non-use evidence: 4 Zellij `.bak`, 4 foreign-theme layouts, 9 mode-less mirrors.
  Identity "Dreamcoder Workbench" in tokens/schema. Kept (live references): `btop-dreamcoder.theme` (CI +
  doctor hint), `dunst-dreamcoder.conf` (apply-theme-mode link migration), `.p10k.zsh` (zshrc fallback).
  Pending for T13 part 2: old wallpapers (after T6), tracked `installer/installer` binary still says dusk,
  "Dreamcoder OS" in installer UI / goreleaser / .github templates, `docs/superpowers` archive. Pre-existing on
  main: `tests/shell/test_pi_theme.bats` #2–3 expect `#824f16` (main light accent was `#8b440c`).
- L20 — T5 design (non-colour tokens in `components`, mode-independent values):
  - spacing: 4 px base grid, scale s1 4, s2 8, s3 12, s4 16, s6 24, s8 32; every Light padding/margin/gap the
    renderers emit must be on the grid.
  - typography: Light gets the same `typography` contract Dark has (body 400, emphasis 500, heading 600,
    letter-spacing 0 / uppercase .04em) so both modes share one type system; mono/ui font families recorded once.
  - motion (physics): durations quick 120 ms, base 200 ms, slow 320 ms (≈1.6× steps, perceptual JND);
    curves are critically damped spring approximations — enter `cubic-bezier(0.22, 1, 0.36, 1)`, exit
    `cubic-bezier(0.4, 0, 1, 1)`, move `cubic-bezier(0.33, 0, 0.2, 1)`; no overshoot/bounce on chrome.
  - Wiring: Light artifacts only (Dark byte-identical, consistent with the feature scope); where a current Light
    value is off-grid, snap it to the nearest grid step; record each change. Dark adoption is a follow-up.
- L21 — T5 result: `components.spacing` (4 px grid), `components.motion` (120/200/320 ms; enter/exit/move
  curves with no overshoot), `components.typography.font_family`, Light `typography` = Dark's; resolver
  `rhythm.py`. Light Hyprland conf gains gaps 4/16 and a dc_enter/exit/move animation block; Waybar module padding,
  margin, weights; rofi entry/element/listview rhythm. No off-grid value existed. Dark unchanged. For T11: ML4W Lua
  may override gaps/animations live; font families recorded but not emitted (ML4W owns fonts).
- L22 — T10 design: (1) `make theme-check` = repo-only sync dark+light then `git diff --exit-code` on tracked
  generated outputs, `verify-theme-health.py`, the theme test subset, and `check-wallpaper.py` over the canonical
  wallpaper set when present; (2) `scripts/theme-diff.py [REF]`: perceptual regression report — ΔE2000 and
  WCAG/APCA deltas per semantic role between a git ref (default `origin/main`) and the working tree, flagging
  roles with ΔE ≥ 2 (just-noticeable) and any contrast floor crossed; (3) `scripts/generate-specimen.py` →
  `docs/generated/dreamcoder-light-specimen.svg` (pure Python SVG: primitive ramps, roles on every surface with
  contrast numbers, elevation e0–e4, pigment ΔE matrix), regenerated by the preview hook path. CI wiring
  (Risk 5) is a separate decision, not part of this worker.
- L23 — T10 result: `make theme-check` (syncs, generated-drift, health, theme tests, wallpaper contract on
  `DreamcoderWallpapers/dreamcoder-*.png`), `scripts/theme-diff.py` (ΔE2000/WCAG/APCA per role vs a ref) and
  `scripts/generate-specimen.py` → `docs/generated/dreamcoder-light-specimen.svg` (grouped paper → ink → clay →
  pigments by hue; surface3 labelled non-text). Preview hook now really diffs (bash -c). theme-diff vs origin/main:
  38/90 roles changed, all Light; 15 visible (ΔE ≥ 2), max 11.39 accent_2, 0 floors crossed, 1 recovered
  (accent_2 on surface1, APCA 68.2 → 78.7). Dark: no change. CI wiring deferred (Risk 5, separate decision).
- L24 — Incident during the T10 commit: the pre-commit pytest hook exports `GIT_INDEX_FILE`; the new
  theme-diff test built a scratch git repo that inherited it and overwrote the real index (1284 staged
  deletions, files intact on disk). Recovered with `git reset` (index = HEAD, working tree untouched).
  Reproduced on an index copy, fixed by scrubbing `GIT_*` from the test's subprocess env; the other three
  git-spawning tests were checked the same way and leave the index unchanged.
- L25 — Second effect of the L24 incident: the scratch `git init` also inherited the hook's `GIT_DIR`, which set
  `core.bare = true` in the shared `.git/config`, so the user's main checkout stopped working as a work tree.
  Restored `core.bare = false`; the main checkout's branch and uncommitted changes are as at session start.
  The L24 fix (scrub all `GIT_*`) was replayed with `GIT_DIR` + `GIT_INDEX_FILE` against a disposable clone:
  core.bare stays false.
- L26 — T12 result: `docs/DREAMCODER_DESIGN_SYSTEM.md` is the single design-system page (tiers, material laws,
  elevation, rhythm, wash rule, wallpaper contract, tooling, embedded specimen); `scripts/WALLPAPER_SETUP.md`
  describes the real adaptive flow; both skills updated (fixed a wrong `guard()` reference); theme-system and
  docs index updated. Revisit the wallpaper paragraph when T6 lands.
- L27 — User decisions (verbatim): T11 "Sí, aplicar ahora"; CI "Sí, añadir al CI" (`make theme-check`, own commit).
- L28 — T11 live pass (20:00–20:15): repo-only and live sync from the worktree applied Light to 37 targets; the
  live bat step wrote through the stow link into the main checkout's tracked `Dreamcoder-Light.tmTheme`
  (restored with `git checkout`; finding: `sync_bat_theme_variants` follows stow links, unlike Warp). Window
  variant `~/.config/hypr/conf/windows/dreamcoder.lua` (solid `primary`, `outline` hairline, gaps 4/16) selected in
  ML4W `window.lua` (backup /tmp) — live and verified via hyprctl. Found and fixed: `lib/waybar.sh` could never
  install the override on ML4W 2.17 (selector saved without trailing newline → `read` returns 1); T9 had left
  5 `tests/ml4w/waybar_override.bats` red (oracle) — oracle updated, new no-newline test, all 15 pass; stale
  `tests/shell/test_pi_theme.bats` #2–3 now read the accent from tokens. Override installed live, Waybar
  relaunched. At 20:13 a wallpaper change fired wallpaper-hook → theme-auto, which applied Dark per the user's
  schedule (Light 07:00–18:00); the Light screenshot was not taken at night to avoid fighting the schedule.
  `t11-desktop-after.png` shows Dark with the mode-agnostic border variant and badge wash live. Light visual
  check pending for daylight hours.
- L29 — Before CI: two latent T10 defects fixed in 3cd98d8 — `theme-check` called `check-wallpaper.py` without
  `--mode` (canonical set renamed `dreamcoder-light-*.png` / `dreamcoder-dark-*.png`, one call per mode) and the
  checker required IM7 `magick` while CI runners ship IM6 (`convert`/`identify` fallback, tested with PATH
  shims). CI: new `theme-check` job in `.github/workflows/theme-validation.yml` (Python 3.12, ImageMagick +
  GTK fixtures, HOME in runner temp, `make theme-check`), own commit, simulated on a fresh clone first.
- L30 — CI job committed after a fresh-clone simulation (Python 3.12, HOME in temp): `make theme-check` exit 0,
  343 theme tests, no drift. T14 benchmark in `odd/evidence/light-coherence/t14-benchmark.md`: leads on weakest
  accent (6.44:1), muted text (6.82:1) and isoluminance (L spread 0.002); behind Catppuccin Latte / GitHub
  Primer on min ΔE (15.1 vs 16.4/16.1, umber↔ochre) and GitHub on APCA body (99 vs 103, warm paper by design).
- L31 — CI independent verify: PASS (S4) with advisories. Fixed A1: wallpaper tests build images with IM6
  `convert` when `magick` is absent, so CI exercises the checker's IM6 path (IM6-only PATH: 52 passed, 1
  skipped); added the probe that a failing wallpaper step stops `make` before the next mode (the suggested file
  name missed the glob; corrected). Unverified until CI runs on GitHub: real-IM6 run, drift probe on a
  non-worktree clone (U1–U3).
- L32 — Draft PR #85: GitHub CI green except commitlint (subject-case: acronyms/proper nouns in 13 titles).
  Titles rewritten to lower-case with an identical tree; hashes in this document remapped (T1 was
  already stale after an amend). Codex image_gen still 403 on the ChatGPT account (retry 01:35Z).
- L33 — User request (2026-11-27), verbatim: "usa la funcion hc de herdr app y mas cuestiona con informacion
  actualizada de la web y mejorate a ti mismo y mas". Findings: (1) `hc` (persistent agent terminals) ran
  interactive Codex; `/status` shows a single *Monthly limit* (Free-plan signature) and published plan pages say
  Codex image generation is not available on Free → T6 403 root cause is the plan (`codex doctor`: auth ok, no proxy).
  `hc send` wraps text as an agent message; slash commands need `hc keys`. (2) WCAG 3 draft (2026-09-10) leaves
  the contrast algorithm undetermined; APCA stays a second, blocking opinion over the WCAG 2.2 floor — docs
  already say so; add a dated note. (3) DTCG Format/Color 2025.10 is stable (2025-10-28) with oklch colour
  objects, dimension/duration/cubicBezier/shadow types; our `oklch(L C H)` strings are not interoperable →
  T15: generated DTCG export validated against the vendored official schema (`tests/fixtures/dtcg/`).
- L34 — T15 result: `scripts/export-dtcg.py` + `dtcg_export.py` → `docs/generated/dreamcoder.tokens.json` (26 Light
  OKLCH primitives with hex fallback, 102 semantic tokens with Light aliases `{primitive.light.<family>.<step>}`,
  23 components: dimension, duration, cubicBezier, shadow), validated offline against the vendored official
  2025.10 schema; regenerated by `make theme-check` and the preview hook; 14 tests. Dated WCAG 3 / APCA note in
  the design-system page.
