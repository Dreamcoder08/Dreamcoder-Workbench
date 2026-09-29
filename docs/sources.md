# Source Manifest — Dreamcoder Workbench

← Back to [docs/README.md](README.md)

> Repository-owned declaration of the upstream inputs Dreamcoder Workbench builds on, the
> ownership boundary between them and this repository, and the material that may
> never be imported or versioned here.

## Quick path — re-pin an upstream ref

1. Resolve the current remote HEAD: `git ls-remote https://github.com/<upstream>.git HEAD`
2. Update the pinned ref in [`upstream-manifest.json`](upstream-manifest.json) and the table below
3. Confirm everything agrees: `python3 scripts/verify-repo-sync.py`

## Role

**Dreamcoder Workbench is the overlay and source of truth** for every file shipped in this
repository. Upstream projects (ML4W and Gentleman.Dots) provide the base
environment that Dreamcoder Workbench layers profiles, tokens, renderers, and verification
on top of. This repository never vendors upstream trees wholesale, never mutates
upstream-owned files outside its managed overlay surface, and never claims
authorship of upstream content.

## Machine-readable manifest

The authoritative, machine-readable record of every upstream input lives in
[`upstream-manifest.json`](upstream-manifest.json), validated against
[`upstream-manifest.schema.json`](upstream-manifest.schema.json). It carries the
HTTPS-only remote URL, the verified pinned commit, verification provenance, and
the set of repository files declared owned from each upstream (intentionally
empty until a file is confirmed to track an upstream revision). All of the
upstream tooling is read-only: `scripts/upstream-diff.py` fetches pinned refs
into a temporary bare Git repository only, never writes under this repository or
the home directory, rejects unsafe paths and URLs, and fails closed on malformed
manifests, network failures, unresolvable refs, or missing objects.

## Upstream inputs

The verified remotes below are the exact HTTPS endpoints the manifest pins.
ML4W's canonical site is <https://ml4w.com>; its pinned remote is the Git
repository that ships the dotfiles. Gentleman.Dots is hosted at
<https://github.com/Gentleman-Programming/Gentleman.Dots>.

| Upstream | Kind | Verified remote (HTTPS) | Pinned ref | Status |
| --- | --- | --- | --- | --- |
| ML4W (Hyprland desktop dotfiles) | Desktop base environment | <https://github.com/mylinuxforwork/dotfiles.git> | `3960570f47f4f691c424ff46b387d389a8e69bca` (tag `2.16`) | Pinned — verified against tag 2.16 and remote HEAD |
| Gentleman.Dots | Shell / editor / terminal base configuration | <https://github.com/Gentleman-Programming/Gentleman.Dots.git> | `6f44b797b016aea92772d8a6d81a5f1bc53a84bb` | Pinned — verified against remote HEAD |

### Pin mechanism

Each ref above was verified on the date recorded in
[`upstream-manifest.json`](upstream-manifest.json) by resolving the exact
HTTPS remote listed in the table with `git ls-remote <url> HEAD` and recording
the exact returned commit. Pinning is a two-step process:

1. Verify an upstream commit against its canonical repository and record the
   resolved reference in the machine-readable manifest.
2. Keep the reference auditable: `scripts/upstream-diff.py --check-pins` reports
   whether each pinned ref still matches the remote HEAD (drift is report-only),
   and `scripts/verify-repo-sync.py` fails if the manifest and this document
   disagree.

A ref cell is never filled with an unverified value; an upstream that cannot be
verified stays `unpinned` in the manifest with no ref recorded, and this table
keeps its ref cell explicitly `Unpinned — ref to be recorded`.

## Ownership boundary

- **Dreamcoder Workbench owns**: every `Dreamcoder*` prefixed module, the theme engine in
  `src/`, the renderers and writers, canonical tokens in
  `DreamcoderThemes/dreamcoder/tokens.json`, machine and deployment profiles in
  `DreamcoderProfiles/`, generated repository variants (for example Herdr
  versioned variants under `DreamcoderHerdr/`), scripts, tests, and docs.
- **Upstreams own**: the base installs they ship. Dreamcoder Workbench integration points
  (hooks, selectors, profile overlays) are documented and applied through this
  repository's own managed surface only.
- **Generated variants** are repository-owned artifacts derived from Dreamcoder Workbench
  canonical tokens. They are checked in so sync drift is detectable; they are
  never treated as upstream files.

No file in this repository is currently declared owned from an upstream: the
manifest's `owned_paths` is intentionally empty until a file is confirmed to
track an upstream revision.

## Prohibited material

This repository must never import or version **host secrets or runtime state**:

- SSH keys, agent sockets, or any private-key material
- VPN mesh state and peer configuration
- AI-assistant credentials, API tokens, or session settings
- Device addresses, hostnames, usernames, or machine identifiers
- Live `~/.config` content, environment dumps, or process/session state

Deployment profiles in `DreamcoderProfiles/deploy/` describe platforms and
rendering settings only. The synchronization verifier
(`scripts/verify-repo-sync.py`) scans the synchronization surface for this
material and fails the check if any is found.

## Verification

```bash
python3 scripts/verify-repo-sync.py                # offline: schema, refs, HTTPS URLs, confined paths, doc consistency
python3 scripts/upstream-diff.py --check-pins      # network: pinned refs vs remote HEAD, drift is report-only
python3 scripts/upstream-diff.py                   # network: diff declared owned paths against pinned refs
```

The offline verifier confirms generated variants match the renderer, deployment
profiles are valid, the mobile profile selects Dreamcoder Workbench Light with Herdr pane
scrollbars disabled, the upstream manifest validates (schema, 40-hex pinned
refs, HTTPS-only URLs, confined owned paths, sources.md consistency), and no
sensitive material exists in the synchronization surface. Optional host-tool
validation (for example `herdr config check`) runs only when the tool is
installed and fails safe when it is absent.

CI enforces the offline verifier and the synchronization and shell dispatcher
tests on every push and pull request to `main`
(`.github/workflows/sync-enforcement.yml`). It never runs `--check-pins` and
never fetches upstreams: the two `upstream-diff.py` commands above remain
human-only, network-aware checks run outside CI.
