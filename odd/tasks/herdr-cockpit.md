# Herdr engineering cockpit

Objective: customize the Herdr app (0.1.12) for a faster software-engineering flow: PRs/CI, one-key verify, agent coordination and work-mode layouts.
Branch: `feat/herdr-cockpit` (based on `feat/herdr-app-config`, which is not yet on `main`). Delivery: one work-unit commit per task; PR target decided at close. Test runner: `herdr-app check <mod>` + live app (`herdr-app status`, `*.error` files), `python3 -m pytest` for repo regressions.

## Specs

- **S1 — PRs y CI.** "Ver PRs, checks y logs de CI de cada repo sin salir de Herdr." Panel mod for the focused space's repo: open PRs with check rollup and review state; click opens the PR; failing checks reachable in one step; refreshes on its own and on demand.
- **S2 — Verificar cambios.** "Correr lint y tests con una tecla y ver el resultado por space, sin abrir una terminal." One key runs the repo's checks in the background (`hc run --bg`, since mod `exec` stops at 30 s) and shows pass/fail per space.
- **S3 — Coordinar agentes.** "Squads, ver qué agente terminó o está bloqueado, y repartir tareas en worktrees más rápido." Board of agents grouped by status (blocked, done, working, idle) with one-click focus, reusing the existing `worktree` / `needs-you` flows for distribution.
- **S4 — Layouts por modo.** "Cambiar de un atajo entre deep work, review y squad, cada uno con sus paneles." Named layouts switchable by key, each showing the panels that mode needs.
- Shared constraint (from L3 research): squad mode is designed for 3–4 parallel agents, the practical ceiling when one person integrates (assumption based on cited 2026 sources, not a hard limit).

## Tasks

| ID | Specs | Route | Status | Evidence |
|----|-------|-------|--------|----------|
| T1 | S1 | inline | done | `7af771e`; 5 node tests; real gh data for #60-#62 parsed (8 checks each) |
| T2 | S2 | inline | done | `7de5854`, `1318d86`; 7 node tests; live run detected `make lint test`, exit 2 (mypy missing on PATH) |
| T3 | S3 | inline | done | `b58f161`; 6 node tests; hwt -n in scratch repo; real templates parsed; popup opens/closes |
| T4 | S4 | inline | done | `cc612e7`; each layout switched live with no errors; screenshots reviewed |
| T5 | L6 | inline | done | `a2a9f74`; layout renamed gentleman -> dreamcoder, app switched before removal |

Route declaration: all inline. The units have disjoint mod folders, but they share `keys.json`, `layouts/*.json` and `.gitignore`, and every unit must be exercised in the single live app (the app config is the repo working tree via symlink), so parallel writers would collide on files and on the live app.

## Log

- **L1 (2026-11-02, user):** "hey bro quisiera personalizar mas y al maximo herdr app inspirate en gentleman + los mejores del mundo , creativos , objetivo mejor productividad , avanza para el flujo de ingeneria de softwart , que opinas ? es necesario hacerme preguntas y mas"
- **L2 (2026-11-02, user):** asked which area first (PRs y CI / Coordinar agentes / Verificar cambios / Layouts por modo), answered "todo".
- **L3 (2026-11-02, user):** "ademas cuestiona con la informacion actualizada de la web , de esta semana , mes 2026"
- **L4 (research):** No dated Herdr changelog for Nov 2026 on the web; the app's own `herdr.d.ts` / `gpui-kit.d.ts` (rewritten each start) are the API truth. Herdr ships OSC 7501 status and `hc run --bg`; reuse them instead of new runners. 2026 sources: ~3–4 parallel agents is the practical ceiling with one integrator; worktrees isolate code but not processes/services.
- **L5 (API facts):** mod `exec` = argv, no shell, 30 s, 8 MiB; `hc run --bg --json` returns an address and `hc get <t> --json` gives `state`, `exit_code`, `finished_ms`. Side panels live in stack `panel-body` of `layouts/dreamcoder.json`, shown with `layout.select` + `layout.show {id:"panel"}`. Free keys include `alt-b c e f i o p q r s t u w y`.
- **L6 (2026-11-02, user):** "hey porque el layout se llama gentleman , debe llamarse dreamcoder , por mi"
- **L7 (decision):** S3 already had native coverage (sidebar agents grouped by status with timers, `alt-n` needs-you, `alt-a` squad), so T3 adds only the missing piece: dispatching a task to a role in a fresh worktree, reusing `hwt` and the herdr-core templates.
- **L8 (discovery):** writing `main.js` before `mod.json` makes Herdr dock the mod into the shown layout on first sight; it happened for verify and dispatch and the stray blocks were removed. Create `mod.json` first.
- **L9 (user report, 2026-11-02):** "bash: line 1: less: command not found ... failed printing to stdout: Broken pipe" when opening the verify log; fixed by running `hc read` without a pager (`1318d86`).
- **L10 (verification):** full suite 1120 passed on this branch (base `feat/herdr-app-config`, which lacks the 12 tests merged to main via #61/#62); `node --test tests/herdr_mods/*.test.mjs` 18 passed; `herdr-app check` passes for prs, verify, dispatch, dc-tabs; `herdr-app status` errors empty.
- **L11 (open):** `make lint` fails on this machine because `mypy` is not on PATH (pre-commit runs it in its own env). Delivery: branch `feat/herdr-cockpit` sits on unmerged `feat/herdr-app-config`; push/PR not done.
