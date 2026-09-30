# Upstream bump 2026-09-30 (Gentleman.Dots pin, pin check, Herdr 0.9.3)

## Objective

Keep the pinned upstreams and the installed tools current ("vanguardia") without breaking the
Dreamcoder overlay: verify what changed upstream before bumping, and record the evidence.

## Findings (checked 2026-09-30)

- ML4W: latest tag `2.16` (pinned). Remote `HEAD` is now `328351d`, ahead of the tag with
  unreleased commits; the project pins releases, so this is reported as drift only.
- Gentleman.Dots: one new commit `5b13e07` (`fix(nvim): use valid snacks.picker name for
  obsidian`, 2 lines in `GentlemanNvim/nvim/lua/plugins/obsidian.lua`). `DreamcoderNvim` does
  `dofile` of Gentleman's `init.lua`, so the fix reaches Neovim once the local checkout moves.
- Herdr: latest `v0.9.3` (2026-09-29), installed `0.9.1`. The official release asset validates
  the repo's 0.9.1 dark and light variants with `herdr config check` (`config: ok`).
- `scripts/upstream-diff.py --check-pins` could not verify any pin that was no longer the remote
  `HEAD`: it ran `git ls-remote <url> <sha>`, which matches ref names, never hashes, so it always
  exited 2. It went unnoticed while every pin equalled `HEAD`.

## Constraints

- Never install or restart herdr while the user's server has open panes; use a scratch copy of
  the release asset for evidence.
- Commit messages: lowercase subject, body lines <= 100 (commitlint). One PR per work unit.
- TDD: off (no project configuration); each behaviour change has a test that fails without it.

## Tasks

- [x] U1 — Pin Gentleman.Dots to `5b13e07` (manifest, sources table, test fixture) and fast-forward
  the local `~/Gentleman.Dots` checkout. Route: inline.
- [x] U2 — `--check-pins` verifies reachability by fetching the pinned hash into a throwaway bare
  repo (the mechanism `_diff_upstream` already uses); tests forbid the ref-name lookup. Live
  result: Gentleman.Dots current, ML4W stale (drift, pin reachable). Route: inline.
- [ ] U3 — Herdr 0.9.3 profile and evidence, generated variants, docs. Route: delegated writer
  (separate PR).

## Acceptance criteria

- `python3 scripts/upstream-diff.py --check-pins` exits 0 against the real remotes and reports
  Gentleman.Dots current and ML4W stale-but-reachable.
- pytest, bats, ruff, mypy green; `verify-repo-sync.py` ok.

## Progress

- U1 and U2 verified: pytest exit 0, bats 192 ok, ruff and mypy clean.

## Next step

U3 (agent running in its own worktree), then record its evidence here.
