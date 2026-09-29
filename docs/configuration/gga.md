# Gentleman Guardian Angel (gga) Model Pin

← Back to [docs/README.md](../README.md)

Every gga review, in every repository, runs on the OpenAI Codex provider with
`gpt-6.1-sol` at `medium` reasoning effort.

## What is pinned and where

| File | Role |
|------|------|
| `~/.config/gga/bin/codex` | Shim (source: `scripts/gga-codex-shim.sh`). Injects `-m <model> -c model_reasoning_effort=<effort>` into `codex exec` only when a `gga` process is an ancestor and no `-m`/`--model` is given. Everything else passes through to the real `codex`. |
| `~/.config/gga/pin.env` | `GGA_PIN_MODEL` and `GGA_PIN_EFFORT`. Created once; never overwritten. |
| `~/.config/gga/config` | Marked block at the end (`# >>> dreamcoder gga pin >>>`): `PROVIDER`/`GGA_PROVIDER="codex"` and the shim dir first on `PATH`. |
| `~/.config/environment.d/50-gga-pin.conf` | Same provider and `PATH` for desktop-launched programs (IDE git hooks). |
| Fish, Zsh, Bash startup | Export `GGA_PROVIDER=codex` and put the shim dir first on `PATH` when it exists. |

## Why a shim

gga runs `codex exec "<prompt>"` without model options, so it would use the model
that `~/.codex/config.toml` selects for interactive work. The shim pins the review
model without touching that file, and interactive `codex` stays unchanged.

`GGA_PROVIDER` is applied by gga after the global config and the project `.gga`,
so it beats a project's own `PROVIDER`.

## Change the model or effort

Edit `~/.config/gga/pin.env`:

```bash
GGA_PIN_MODEL="gpt-6.1-sol"
GGA_PIN_EFFORT="high"
```

The next review uses it; nothing needs re-installing.

## After `gentle-ai sync` or `gentle-ai install`

Both rewrite the whole `~/.config/gga/config` and drop the pin block. The shim,
`pin.env`, the shell exports and `environment.d` survive, so reviews keep the
pinned model; re-apply the config block with either command:

```bash
./scripts/dreamcoder repair        # runs the installer when gga is on PATH
./scripts/install-gga-pin.sh       # idempotent; --dry-run shows pending changes
```
