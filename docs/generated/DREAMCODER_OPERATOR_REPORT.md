# Dreamcoder Operator Report

Generated from current machine state and Control Center contracts.

## Visual Dashboard

```text
┌──────────────────────── Dreamcoder Health ────────────────────────┐
│ Theme: unknown  Profile: unknown            │
│ Motion: unknown Health: 6 ok / 8 warn / 6 fail       │
│ Installer conflicts: 0   Repair actions: 14          │
└───────────────────────────────────────────────────────────────────┘
```

## Terminal Settings TUI Preview

```text
╭──────────── Dreamcoder Settings ────────────╮
│ Theme: unknown  Profile: unknown          │
│ Motion: unknown Health: 6 ok / 8 warn / 6 fail │
├─────────────────────────────────────────────┤
│ terminal.default_mode    = light      │
│   Default terminal theme mode. (light, dark│
│ profile.active           = default    │
│   Active machine profile name.             │
│ motion.active            = balanced   │
│   Active motion preset. (battery, balanced,│
├─────────────────────────────────────────────┤
│ Apply: dreamcoder tui set <key> <value>     │
│ Safe: add --dry-run --json before applying  │
╰─────────────────────────────────────────────╯
```

## Safety Model

- Inspect before mutating: doctor, dashboard, installer plan, and TUI render are read-only.
- Preview before writing: TUI set, profile apply, motion apply, repair apply, and backup restore support dry-run flows.
- Back up before mutation: apply flows create `dreamcoder.backup.v1` manifests.
- Keep risky operations manual: installer conflicts and system service changes require operator review.

## Quality Gates

```bash
./scripts/verify.sh
./scripts/dreamcoder doctor-json
./scripts/dreamcoder dashboard --json
./scripts/dreamcoder tui render --json
./scripts/dreamcoder settings validate --json
./scripts/dreamcoder repair plan --json
```

## Contracts

- `dreamcoder.dashboard.v1`
- `dreamcoder.tui.v1`
- `dreamcoder.settings-schema.v1`
- `dreamcoder.repair-plan.v1`
- `dreamcoder.install-plan.v1`
- `dreamcoder.backup.v1`

## Competitive Checklist

| Capability | Dreamcoder | ML4W/GentlemanDots baseline |
| --- | --- | --- |
| Machine-readable health | `dreamcoder.doctor.v1` | Usually human shell output |
| Safe repair planning | `dreamcoder.repair-plan.v1` | Mostly manual reapply |
| Settings UI contract | `dreamcoder.tui.v1` + schema | Often hardcoded UI/settings |
| Rollback | Manifest backups | Ad-hoc backups/manual restore |
| Visual docs | Generated operator report | Static docs/screenshots |

## Commands

- Doctor: `./scripts/dreamcoder doctor-json`
- Repair plan: `./scripts/dreamcoder repair plan --json`
- Profile preview: `./scripts/dreamcoder profile apply asus-vivobook15 --dry-run --json`
- Motion preview: `./scripts/dreamcoder motion apply fluid --dry-run --json`
- Installer plan: `./scripts/dreamcoder installer plan --json`
- Verify: `./scripts/verify.sh`
