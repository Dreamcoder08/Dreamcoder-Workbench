# Dreamcoder Light: Lúcuma paper

Objective: rebuild the Dreamcoder Light system design so every surface and text level is legible and clearly ranked, in line with the best 2026 light themes, while keeping the Cocoa/Lúcuma identity (direction A).
Branch: `feat/dreamcoder-light-paper` from `feat/herdr-gentle-shell-layout`. Delivery: ask-on-risk; one work-unit commit per task. Test runner: `python3 -m pytest -q`, `scripts/verify-theme-health.py`, live screenshots (`herdr-app shot`).

## Specs

- **S1 — Mejorar el system design de Dreamcoder Light.** "ahora el gran objetivo para flujo ODD es mejorar el system desing de dreamcoder light". Light tokens form a real elevation ladder (recessed chrome < canvas < cards), selection and hover are visible on every surface, and the renderers map each token to the role it was designed for.
- **S2 — Legibilidad, crítico obsesivo.** "tambien theme dreamcoder light ser critico obsesivo con la legibilidad". Every text token (text, muted, subtle, comment, border_ui, accents, semantics) reaches ≥ 4.5:1 on every resting surface (bg, bg_soft, surface0, surface1, surface2, selection); the three text levels stay distinct; component borders reach ≥ 3:1 on resting surfaces; warning is not confusable with the accent.
- **S3 — Referentes 2026.** "y mas inspirarte en los mejores themes lights del mundo o mas modernos de esta 2026". Neutrals stay near paper (OKLCH chroma ≤ 0.02) with colour reserved for accent and semantics, as GitHub Primer, Vercel Geist, Linear and Flexoki do; semantics share one lightness so none shouts.
- **S4 — Identidad.** Direction A, "Lúcuma paper", chosen by the user ("quiero lo mejor de lo mejor te autorizo todo"): warm paper hue, cocoa accent, rust accent_2, peach selection; visible name stays `Dreamcoder`.

## Tasks

| ID | Specs | Route | Status | Evidence |
|----|-------|-------|--------|----------|
| T1 | S2, S3, S4 | inline | done | `tokens.json` light rebuilt; `tests/test_light_paper_system.py` RED on the old palette (10 of 18 fail), GREEN on the new; full suite 1146 + 18 pass; `verify-theme-health.py` clean |
| T2 | S1, S2 | inline | done | light role fixes: herdr-app chrome/selected, herdr TUI sidebar/active row, gentle-shell selected/hover, Pi selectedBg, Antigravity selection/hover/line, GTK sidebar, OpenCode diff tint, Codex line highlight + gutter; Dark bytes unchanged |
| T3 | S1, S2 | inline | done | live `herdr-app shot`: active rows visible (peach selection), recessed sidebar, no sepia; health gate covers every generated light file |
| T4 | S1-S4 | inline | done | `CLAUDE.md` light block + system rules, palette skill row, regenerated theme preview |

Route declaration: all inline; every unit shares `tokens.json` and the generated files, so no parallel writers.

## Log

- **L1 (2026-11-16, user):** "ahora el gran objetivo para flujo ODD es mejorar el system desing de dreamcoder light , tambien theme dreamcoder light ser critico obsesivo con la legibilidad , y mas inspirarte en los mejores themes lights del mundo o mas modernos de esta 2026" (with two screenshots of the gentle-shell layout in Light).
- **L2 (diagnosis, measured):** surface1 (L 0.90) and bg_soft (0.91) are darker than bg (0.95), so elevation reads inverted; selection on the sidebar is 1.02:1 (invisible active project); neutral chroma 0.017-0.046 at hue 72 tints everything sepia; muted 10.4:1 vs text 15.4:1 collapses hierarchy; comment 4.01:1 on surface1 fails AA; warning (h72) and accent (h60) share a hue; border 2.70:1 below the 3:1 component minimum.
- **L3 (user decision):** "quiero lo mejor de lo mejor te autorizo todo has lo que sea necesario" → direction A, Lúcuma paper.
- **L4 (design):** neutrals at hue 78, chroma 0.004-0.017: bg L0.975, bg_soft (recessed chrome) 0.952, surface0 (cards) 0.993, surface1 (hover) 0.935, surface2 (pressed) 0.900, surface3 0.855. Text ladder 0.215 / 0.405 / 0.46 / 0.485. Accent cocoa L0.47 C0.115 h52, rust h38, warning amber h84; semantics at L 0.47-0.48. Audit: every text token ≥ 4.5:1 on all six resting surfaces; border ≥ 3:1 on bg, bg_soft, surface0, surface1.
- **L5 (tests as reviewers):** the suite caught real issues the first palette had: diff bands vanished on paper (1.01:1, fixed with a 10% hue tint, ink >= 5.04:1); comment vs muted 1.40 < 2.0 in nvim (muted moved to L0.31, #352f29); Codex line highlight 1.10 < 1.15 and gutter < 1.45 (light uses surface2 / surface3 #d3ccc1); disabled 4.31 < 4.5 (now #726e68). Pins of old hex values were replaced with design properties (elevation, selection visible on bg_soft) or canonical token references.
- **L6 (role audit):** old tests pinned #eadcc9 which was both surface1 and selection, hiding that Pi, herdr and Antigravity used the hover/card tone for selection. Light now maps selected rows to `selection`, hover to `surface1`, sidebars to `bg_soft`.
- **L7 (open, not ours):** Claude Code's own `light` theme paints saturated green/pink diff bands in the terminal; they come from Claude Code, not the palette.
- **L8 (delivery):** T1-T3 in `8922ca6` (palette, roles, generated light files, tests); T4 in the docs commit that carries this line. Active-mode mirrors (generated files currently showing Light because the system is in Light) stay uncommitted on purpose.
