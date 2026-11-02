# Herdr flow: review-first cockpit

Objective: attack the 2026 review bottleneck in the Herdr cockpit: PR size guard, flow metrics, auto-verify when an agent finishes.
Branch: `feat/herdr-flow` from `main`. Delivery: one work-unit commit per task, one PR to `main`. Test runner: `node --test tests/herdr_mods/*.test.mjs` (via `tests/test_herdr_mods_node.py`), `herdr-app check`, live app.

## Specs

- **S1 — Guardia de tamaño.** "Que cada PR muestre sus líneas cambiadas y se ponga en rojo si pasa de las ~400 (la regla de Gentleman de PRs revisables)." The PRs panel shows each PR's changed lines (additions + deletions) and marks it red above 400.
- **S2 — Métricas de flujo.** "El tiempo real desde que abrís una PR hasta que la mergeás, y cuántas PRs mergeás por semana, sacado de `gh` de tus últimas dos semanas." Panel with merged PRs per week and open-to-merge lead time over the last 14 days.
- **S3 — Verify automático.** "Cuando un agente pasa a "done", se dispara solo el verify de su space [...] se podría limitar a los spaces que vos marques." Auto-verify a space when one of its agents finishes, only for spaces the user opts in.

## Tasks

| ID | Specs | Route | Status | Evidence |
|----|-------|-------|--------|----------|
| T1 | S1 | inline | done | `d71e6f4`; 1 node test (4 cases); real PRs: #64 1.6k and #63 748 flagged over 400 |
| T2 | S2 | inline | done | `a802acd`; 6 node tests; real 14 days: 28 merged, 14/week, lead median 7m, p90 32m, 46% over 400 |
| T3 | S3 | inline | done | `185aaf3`; 4 node tests; toggle verified live (badge + toast), left off |

Route declaration: all inline; units share `keys.json`, `layouts/*.json` and the live app.

## Log

- **L1 (2026-11-02, user):** "ummm y que mas me reocmiendas personalizar ?? objetivo estar en la vanguardia , productividad y mas , en base a la informacion de la web de esta semana , mes"
- **L2 (research):** 2026 sources: review is the bottleneck (Faros: PR size +51%, bugs/PR +28%, review time 5x in high-adoption teams; METR: experienced devs 19% slower on large unfamiliar codebases). Installed tools already current: Claude Code 2.1.316, Ghostty 1.4.0, gentle-ai 4.2.0.
- **L3 (2026-11-02, user):** "te autorizo todo" — all three recommendations.
- **L4 (discovery):** Herdr rejects imports outside a mod's folder (`module ... resolves outside the application directory`), so `parseGhJson` is repeated in `flow/stats.js` with a parity test against `prs/ci.js`.
- **L5 (finding for the user):** lead median 7 minutes means PRs merge as soon as CI passes, without human review; 46% exceed 400 lines. The panel makes that visible.
- **L6 (verification):** full suite 1133 passed; `node --test` 29 passed; `herdr-app check` passes for prs, flow, verify, dc-tabs; `herdr-app status` errors empty. Not exercised live: an actual agent finishing with auto-verify on (needs a real agent run); covered by `finishedAgents`/`shouldAutoVerify` tests.
