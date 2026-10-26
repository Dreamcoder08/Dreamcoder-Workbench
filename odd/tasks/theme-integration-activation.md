# Dreamcoder Workbench theme integration and scoped activation

Historical recovery record. Current delivery status is tracked in [main delivery](readme-main-delivery.md); implementation notes below are preserved.
Objective: integrate the verified theme delivery through the selected feature-branch-chain and apply only the explicitly authorized live theme destinations.
Baseline: published delivery `0f27a579450db7b00de177c993437972711fd1a1`; original shared work stays untouched except task records. No global sync, package installation, force push or destructive cleanup.

## Specs

S1. User request, verbatim: "yes te autorizo todo y avanza de forma autonoma". Continue the preceding follow-through: integrate the verified delivery toward the remote default branch and apply its relevant live theme changes. Do not treat autonomy as permission for unrelated work or bypassing required checks.

S2. User selected, verbatim: "Autorizar integración y aplicación delimitada". The approved prompt permits the three named PR/issue skill reads and access only to the listed OpenCode, Starship, Bat cache/theme, and shared Pi/Gentle theme/settings targets, plus read-only persisted mode. Preserve unrelated fields and active mode, make backups inside the project, and do not execute global sync. The exact private destination manifest stays local, not in public issue/PR bodies.

S3. User selected, verbatim: "Autorizar etiquetas, issue aprobado y PR encadenados". Exact approved question: "En github.com/Dreamcoder08/Dreamcoder-Workbench, ¿autorizas crear las etiquetas status:approved, type:bug, type:chore y type:docs, crear un issue de seguimiento con status:approved desde su creación y enlazar los PR mediante Refs, sin cierre automático del issue?" Current target-bound actor has ADMIN permission. Reuse the selected feature-branch-chain; no silent strategy switch or automatic issue closing.

S4. Previously selected strategy, verbatim: "Cadena sobre una rama integradora". Keep a draft/no-merge tracker until child slices are reviewed and integrated. Child one targets the tracker branch; later children target their immediate parent. Preserve repository-required checks and required review; never bypass them with administrator options.

## Tasks

- T1 | S1,S3-S4 | route: parent Git preparation and bounded worker support | in_progress | Prepare non-rewriting review topology, changelog entries, target templates, a bounded local activation dry-run and required verification. Commit: pending.
- T2 | S3-S4 | route: parent remote operations | pending | Create the authorized labels and approved tracking issue, then publish template-compliant tracker/child PRs with nonclosing Refs and exact type labels. Commit: tracking metadata pending.
- T3 | S1-S2 | route: bounded local activation, parent applies | pending | Inspect managed destinations and aliases, preview/backup changes, apply only validated authorized theme deltas while retaining unrelated data. Commit: local evidence only, no private snapshots published.
- T4 | S1,S3-S4 | route: parent CI and merge orchestration | pending | Observe required checks and review; merge the chosen chain into tracker then default branch only when policy permits, without force or bypass. Commit: resulting merge commits pending.
- T5 | S1-S4 | route: independent environment verification and parent closure | pending | Read back merged remote state and scoped live targets, report visual/ownership limits and any unavailable proof, record actual outcomes. Risk: item 5 (live environment activation); independent verification required. Commit: closing record pending.

## Log

L1. Original user request, verbatim: "yes te autorizo todo y avanza de forma autonoma".

L2. User selected "Autorizar integración y aplicación delimitada" after receiving explicit external destination and resource lists. User then selected "Autorizar etiquetas, issue aprobado y PR encadenados" with the exact label/reference question quoted in S3. No generic authorization is substituted for those selections.

L3. Read-only initial evidence: delivery worktree clean at 0f27a57; no open integrator PR; remote default main; actor ADMIN; only default GitHub labels and no matching theme/Bat/OpenCode issue. CONTRIBUTING requires focused PRs, make lint/test/coverage, changelog and passing hooks; it does not independently require the skill-specific labels. Main-bound workflows cover theme lint/tests/coverage and conventional commits. Existing integrator already contains its child ancestors, so using it directly as the first-child base would create an empty/polluted review. Prepare a plan-only tracker and merge forward metadata into each child without rewriting published history.

L4. Authorized live inspection: persisted mode dark. Pi and Gentle resolve the same agent directory and already select dreamcoder-light/dreamcoder-dark. Their three managed theme names/appearances are correct. Starship already has the Dark diag alias. Starship and Bat paths resolve into the original dirty tree; a blanket sync would risk foreign changes. OpenCode TUI already selects dreamcoder; an absent explicit agent color is not itself a new requirement. No live writes, issue, PR or merge occurred during exploration.

L5. T1 preparation uses two disjoint bounded workers: issue/PR draft artifacts and a one-off local activation dry-run/helper, both under ignored local directories in the verified delivery worktree. Parent retains branch, remote, apply and merge authority. Local activation is not yet started by this preparation step; no new production installer or command is requested. Parent will inspect the proposed managed-field changes before applying. Required Makefile targets only run existing ruff/mypy/shellcheck/pytest; no install target is authorized.
