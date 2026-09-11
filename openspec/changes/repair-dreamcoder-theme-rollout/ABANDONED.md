# Abandoned: repair-dreamcoder-theme-rollout

Status: **abandoned (not resumed)** — decided 2026-09-11.

## Decision

Not resumed. This is a 62-task program of which only **Slice 1A** landed
(`targets.json` + schema + `targets.py` + tests, recorded in `STATUS.md`). The
remaining 57 tasks span Nytherx dark calibration, deterministic terminal/shell
generation, and editor/CLI/desktop/ML4W output parity. It was last touched
2026-07-17 and no later change re-attempted it.

The Light/Dark contract this change set out to unify already exists in practice
(`scripts/apply-theme-mode.sh`, `dreamcoder light|dark`, the active-mirror
identity guard), delivered by other changes rather than by this plan.

## What stays

- The delivered Slice 1A artifacts remain in the repository and are documented
  in `STATUS.md`.
- The proposal, design, spec, and tasks remain for their audit value. Nothing is
  deleted.
- If the remaining rollout work is wanted, open a fresh, focused change; this
  plan is not a plan of record.
