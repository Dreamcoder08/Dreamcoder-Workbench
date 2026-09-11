# Superseded: audit-opencode-sdd-orchestration

Status: **superseded** (2026-09-11). Verification proved the change's target
implementation is not present in the repository.

## Why

`tasks.md` reports 30/30 complete, but `verify-report.md` (2026-09-11, verdict
`fail`, 3/11 requirements) found that checked is not true:

- The spec's orchestrator model `openai/gpt-5.6-terra` and the ten SDD agents'
  `openai/gpt-5.6-luna` do not exist anywhere in the repository outside this
  change's own planning artifacts; the shipped values are `openai/gpt-5.4` and
  `openai/gpt-5.4-mini`.
- No `provider` block is present in
  `DreamcoderOpenCode/.config/opencode/opencode.json`.
- `apply-progress.md` is absent from the artifact store.
- `git grep -e gpt-5.6-terra -e gpt-5.6-luna` matches only this change's own
  documents.

The applied state survives at most as a deleted blob, and a later commit
(`e43cbf6`, 2026-07-20) committed the target file in a different migration state.

## Surviving sub-outcomes (delivered, recorded here)

Only these sub-outcomes of the original intent survived into the shipped
configuration:

- `sdd-onboard.hidden = false`
- the `sdd-archive` field removals
- `cursor-acp` is gone

## Disposition

- **Not delivered**: the `gpt-5.6-*` per-phase model routing, the `provider`
  block, and the shared managed block across scopes.
- **Superseded** rather than amended: the aspirational model IDs are not a plan
  of record, and no later change re-attempted them.
- If OpenAI-native per-phase routing is wanted later, open a fresh change with
  the model IDs that actually exist.

The original proposal, design, spec, and tasks are kept for their audit value.
