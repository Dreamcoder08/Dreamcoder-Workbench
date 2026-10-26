# ML4W 2.16.1 Dreamcoder integration

Historical recovery record. Current delivery status is tracked in [main delivery](readme-main-delivery.md); implementation notes below are preserved.
Objective: modernize the repository overlay and apply Dreamcoder Light/Dark to supported ML4W surfaces; never mutate the live desktop.
Branch: `feat/ml4w-2.16.1-dreamcoder`; delivery: ask-on-risk; initial forecast: 300–400 authored lines, reassess after upstream interface evidence; runners: Bats, pytest, repository verifiers.

## Specs

- S1: "ayudame a actualizar todo ml4w en la vanguardia bien configurado 10/10 eliminar legacy"
- S2: "y que el system desing de dreamcoder light + dreamcoder dark se apliquen bien sobre esas configuraciones"
- S3: "Repositorio primero (recomendado)" — selected option description: "Actualizar y probar Dreamcoder Workbench contra ML4W estable; retirar solo lo demostrado obsoleto, sin tocar tu instalación activa."

## Tasks

- T1 [S1,S3] in_progress; route: delegated worker (runtime context backstop); verify official 2.16.1 interfaces, update upstream provenance and obsolete integration commands with focused tests/docs; commit: pending.
- T2 [S2,S3] pending; route: delegated worker (runtime context backstop); cover supported ML4W desktop color interfaces using canonical tokens and isolated dark/light tests; commit: pending.
- T3 [S1,S2,S3] pending; route: parent checks and independent verifier only for named high risk; run applicable suites, assess changes, record limitations and close work units; commit: pending.

## Log

L1 — Original user request, verbatim:

ayudame a actualizar todo ml4w en la vanguardia bien configurado 10/10 eliminar legacy , y que el system desing de dreamcoder light + dreamcoder dark se apliquen bien sobre esas configuraciones , La última versión de los dotfiles de ML4W (My Linux for Work) es la versión 2.16.1, publicada en octubre de 2026. [1] (https://github.com/mylinuxforwork/dotfiles/releases)
Poco antes, la versión mayor 2.16 se había lanzado a principios del mismo mes, introduciendo características destacadas como el interruptor de filtro de luz azul en la barra lateral y un nuevo script de instalación rápido para ventanas Quickshell. La revisión menor 2.16.1 llegó días después para mover el menú de apagado (power menu) a su propio repositorio independiente. [1] (https://github.com/mylinuxforwork/dotfiles/releases)
Si estás pensando en actualizar o realizar una nueva instalación, puedes hacerlo directamente de las siguientes maneras:
• Instalación limpia/actualización estándar: Ejecutando el instalador script oficial desde la terminal mediante el comando bash <(curl -s https://ml4w.com/os/stable).
• Mediante repositorio: Revisando el código directamente desde el repositorio oficial de GitHub en mylinuxforwork/dotfiles. [1] (https://ml4w.com/os/getting-started/update), [2] (https://github.com/mylinuxforwork/dotfiles/releases)
¿Te gustaría saber qué dependencias necesitas preparar en tu distribución antes de actualizar, o prefieres asistencia para respaldar tus configuraciones personalizadas actuales y que no se sobrescriban?

L2 — Scope choice: "Repositorio primero (recomendado)". No host installation, package changes, remote installer, publishing or deletion of unverified legacy targets.

L3 — Parent verified GitHub latest release API: stable tag 2.16.1, published 2026-10-04. Explorer did not verify upstream source contracts and incorrectly looked for manifest at repository root; actual manifest is docs/upstream-manifest.json. Existing 2.16 fixtures are not proof of incompatibility. Waybar remains supported and is not automatically obsolete.

L4 — Baseline ed186df4ae80abe93588686228a0b3e5f5135324. Pre-existing untracked odd/tasks/durable-terminal-integration.md belongs to other work; preserve and never stage it. New feature branch created from fix/light-tui-coherence without modifying other work. Worker must return evidence before selecting removals; no speculative deletion or replacement of user tokens.
