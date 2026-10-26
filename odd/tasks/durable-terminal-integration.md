# Durable terminal integration

Historical recovery record. Current delivery status is tracked in [main delivery](readme-main-delivery.md); implementation notes below are preserved.
Objective: persist the approved ML4W/nmtui and bat repairs, inspect secondary TUI states, and deliver reviewable PRs without merge or release.
Baseline: ed186df4ae80abe93588686228a0b3e5f5135324; branch: fix/light-tui-coherence; delivery: auto-chain / feature-branch-chain; checks: pytest, Bats, Ruff, mypy, ShellCheck, markdown links, isolated PTY probes.

## Specs

1. **S1 — Durable repairs and verification.** User: "yes continua con todo , te autorizo todo y avanza de forma autonoma". This approves the immediately preceding four-item proposal: make the installed ML4W nmtui route reproducible through repository installation; rebuild bat's cache after theme installation/update; inspect secondary nmtui screens; prepare a PR and inspect CI. Preserve the existing terminal and networking behavior, process-local styling, explicit style overrides, and Light/Dark switching. Do not change network connections or global ANSI colors. No merge or release is authorized.
2. **S2 — Remote issue and labels.** User selected: "Sí, crear issue y esas etiquetas". Approved target: github.com/Dreamcoder08/Dreamcoder-Workbench; create an issue for this scope, create/apply `status:approved` to that issue, create/apply `type:bug` to PRs, and use nonclosing `Refs #N`. Default branch `main` and current actor admin/maintain permissions were read from the target. No issue, labels or PR has yet been created.
3. **S3 — Reviewable delivery.** User selected: "Cadena sobre rama de integración (recomendado)". Use `chain_strategy=feature-branch-chain`; the existing published work and new repairs must have clearly identified review slices rather than one oversized PR. Generated theme snapshots are distinguished from authored changes. Pushes and PR creation are authorized; no force push, merge, or release.
4. **S4 — Critical visual inspection.** User: "se critico obsesivo". The user approved the current main-menu appearance with "muy bien ya esta bien". Inspect secondary states without modifying network data; report missing visual proof honestly rather than equating mocks or emitted SGR sequences with a screenshot.

## Tasks

- T1 | S1 | delegated parallel writer | in_progress | commit: — | Make the ML4W nmtui route reproducible through existing setup; test preview, recognized legacy/already-patched inputs, repeat application, and preservation of unrelated content. Risk: item 5 (installer/environment).
- T2 | S1 | delegated parallel writer | in_progress | commit: — | Rebuild bat cache after relevant theme writes across sync/activation lifecycle; test fresh/stale/unchanged cache, missing optional binary, failures and rollback interactions. Risk: item 5 (environment/cache lifecycle).
- T3 | S1,S4 | inline parent | in_progress | commit: — | Inspect secondary nmtui states using isolated harmless fixtures or public probes, never real connection edits; explicitly record any unavailable graphical proof.
- T4 | S1 | independent verifier then parent seam check | pending | commit: — | Verify both high-risk units once against isolated state, run the combined suite and applicable lint/type/shell/docs checks, and reconcile failures before delivery.
- T5 | S1,S3 | inline parent | pending | commit: — | Commit reviewable units with evidence and apply only the already authorized local installation/cache changes after verification.
- T6 | S2,S3 | inline parent / background remote CI | pending | commit: — | Create approved scope issue, prepare feature-branch-chain PR slices with target policy labels/templates, push normally, and follow required CI; no merge.

## Log

- L1 | User request verbatim: "yes continua con todo , te autorizo todo y avanza de forma autonoma".
- L2 | Accepted referenced proposal: "Hacer reproducible la corrección de ML4W", "Evitar que reaparezca el problema de bat", "Abrir un PR hacia main y revisar CI", and "Comprobar pantallas secundarias de nmtui". Implementation has not started for these follow-ups.
- L3 | Read-only map: active ML4W fix exists only in installed `~/.config/ml4w/scripts/ml4w-network`, replacing two direct calls with `${HOME}/.local/bin/dreamcoder-nmtui`. Repository setup is `scripts/setup-hyprland.sh`; existing Bats are `tests/ml4w/setup_hyprland.bats`. Bat writes occur in `sync_active_targets` and `sync_bat_theme_variants`; activation and rollback call these from `cli_handlers.py`. Current doctor checks theme files, not compiled cache.
- L4 | User explicitly approved creating/applying `status:approved` on the scope issue and `type:bug` on PRs, using `Refs #N`, no merge. Target has no open issues or PR on the current branch and only default GitHub labels at inspection time.
- L5 | User selected feature-branch-chain. Existing branch already carries approximately 400+ authored lines plus generated Light assets; forecast for the follow-up is roughly 200–400 additional authored lines, subject to evidence. Protect review scope; do not omit tests or compress code to fit a budget.
- L6 | Prior completed evidence: all changes on `fix/light-tui-coherence` were pushed to ed186df; user approved main-menu screenshot. Existing nmtui default is native inverse-video selection. Newt treats every present `NEWT_MONO` value, including `0`/empty, as monochrome. RGB/indexed color support was not demonstrated; do not retry those probes or assume it.
