# Pi CLI-first integrations

## Objective
Remove all 20 current Pi MCP registrations and use verified CLI replacements, retaining native non-MCP memory and web research.

## Authorization and scope
User selected remove_all_mcp_registrations after explicit capability-loss disclosure. Remove registrations only, not installed/shared packages. Global registration mutations must use native pi mcp remove; no direct edit of credentials or global settings. Clean exactly eight local enabled-only overrides before removing their global bases. Preserve .pi/mcp.json and unrelated/new edits, stored credentials, auth.json, mcp-auth.json, ~/.engram storage, .codegraph indexes, caches, other clients and inactive legacy adapter configuration. No process termination, installs, publication or commits without specific authorization.

## Capability decisions
Use gh exclusively for GitHub; authenticated by read-only scout. CodeGraph CLI verified. Engram authoritative native tools use HTTP, not MCP. Keep native pi-web-access non-MCP research. Context7, desktop, browser and Sentry capabilities without verified replacements are intentionally retired/deferred. Do not equate an MCP-server executable with a standalone CLI, or GNU Parallel with the research provider.

## Tasks
- [x] C1 — Map CLI replacements, native removal semantics and exact capability scope. Route: delegated gentle-ai-verify, command-verification trigger. Evidence: mustftcw-2-oy29 read-only map; gh authenticated, global20/local8; user selected full removal. Commit not authorized.
- [x] C2 — Remove exactly eight local overrides then all 20 global registrations through native CLI; verify preservation. Route: delegated gentle-ai-worker, environment configuration and multi-file write trigger. Status: executed and self-verified; parent zero-count spot check passed. Commit not authorized.
- [x] C3 — Independently verify empty registration sets, preserved native capabilities and CLI functionality; report activation and performance limits. Route: delegated gentle-ai-verify per native assessment plan. Status: passed within authorized scope; loader gap, metadata-only preservation and normal restart requirement documented. Commit not authorized.

## Exact allowed surfaces
Repository .pi/mcp.json: only the eight existing override entries computer-use, docker, kubernetes, obscura, persyst, postgres, redis, screenpipe.
Operational scope: ~/.pi/agent/mcp.json registration entries only via native CLI pi mcp remove. No other environment edits.
Parent-only bookkeeping: odd/tasks/pi-cli-first-integrations.md and full Engram mirror odd/pi-cli-first-integrations/tasks.

## Removal labels
Global: github, codegraph, engram, context7, parallel-search, docker, kubernetes, postgres, redis, computer-use, obscura, persyst, screenpipe, sentry, seq-thinking, time, filesystem, git, playwright, chrome-devtools.
Local cleanup: computer-use, docker, kubernetes, obscura, persyst, postgres, redis, screenpipe.

## Acceptance and checks
Before changes: validate global/local registration JSON and privately hash non-sensitive pre-existing dirty source paths where permitted; retain only in process memory, never expose secrets or create backup files. User approved METADATA-ONLY preservation for auth.json, mcp-auth.json, settings.json and mcp-adapter.json: stat/lstat existence, mode, size, inode and timestamps, without reading protected contents or hashes. Explicitly report no byte/content-hash guarantee for those files. Reject unknown/new registrations rather than remove beyond scope.
Observed RED: same read-only assertion requires no MCP entries and valid non-orphan local overrides; expected failure against baseline20global/8local. GREEN: rerun exact assertion after native removals, empty mcpServers globally/locally, valid JSON and unchanged unrelated parsed fields.
Preservation: protected auth/settings/legacy-adapter metadata unchanged where accessible; content unread and unverified by approved contract. Do not claim complete byte preservation. Global/local registration JSON changes intentional; credentials/server values must never be dumped.
CLI: pi --version, gh auth status sanitized, one public gh api read, codegraph status/query bound to this repository, engram stats if safe. No MCP calls or pi mcp list; no extra Pi sessions or forced server startup. Native memory read and non-MCP web fetch parent checks after worker.
Functional checks/diff/markdown validator pass or reported exact failures. Existing processes are not stopped by registration removal; current-session tool declarations may persist until normal user restart. Do not claim RAM savings from registration count.

## Delivery and continuity
Strategy ask-on-risk; forecast approximately60-150authored diff lines, no source changes. Commits not authorized. Existing odd/tasks/pi-workbench-memory-performance.md remains untouched: prior T4partial, no totalPSSsaving. This feature replaces GitHubMCPverification with ghverification, not fixing MCPcredentials.

## Progress and next step
C1-C3 complete within the authorized registration-cleanup scope. Initial writer musttphz-3-buo6 stopped before commands or mutations because protected-file hashes conflicted with its safety rules. User approved metadata-only coverage. Continuation mustwvpt-4-o4nw executed all 28 native removal commands successfully, local overrides first. Observed RED: global 20/local 8; GREEN: global 0/local 0, valid JSON, no orphans, unrelated parsed fields retained. Parent readback and count spot check passed. Do not replay removals.

Worker verification passed Pi 1.0.1, authenticated gh and public API read, CodeGraph repository status/query, Engram stats, diff and Markdown checks. Worker preservation evidence: 74 unrelated dirty paths retained metadata/status, 58 non-sensitive content hashes unchanged, 16 metadata-only paths. Protected files were not read or hashed; no byte-exact guarantee. This evidence is not an independent baseline comparison.

Independent verifier musu3ii2-5-lf8w passed global/local empty JSON and zero orphans; Pi version, gh auth/API, CodeGraph status/query, Engram stats, diff and Markdown checks. Protected metadata snapshots covered eight candidates (five existing), unchanged across verification. Original hashes/bytes were not supplied, so worker content-preservation claims were not independently re-proven. Native no-startup loader was skipped because its safe API was unknown; no MCP clients were started and no protected settings read. All three owned task/profile files remain untracked; commits were not authorized.

Parent native HTTP memory search and non-MCP web fetch passed after removal. Accepted gaps remain for Context7, desktop, browser and Sentry without verified replacements. Shared packages, credentials, data, indexes and legacy adapter were not removed. Other clients were not changed.

Activation: configured registrations are removed now, but already-open MCP processes and tool declarations may persist until the user exits Pi normally and resumes with pi --continue. No process was terminated or session restarted by tools. No RAM-savings claim: the old performance T4 remains partial and untouched. Next step is a normal restart; any subsequent performance evaluation must use comparable workload evidence rather than registry counts.
