# Pi and Workbench memory performance

## Objective
Update Pi safely and reduce evidenced startup overhead, using measurements rather than speculative tuning.

## Current scope and constraints
CLI-first; no MCP calls. GitHub uses gh, CodeGraph uses CLI, and native non-MCP memory/web remain available. All 20 global MCP registrations and eight local overrides were removed in the completed [CLI-first feature](pi-cli-first-integrations.md). Credentials, shared packages, data and indexes were not deleted. Protected-file preservation was metadata-only by explicit user choice, not a byte-exact guarantee.

Preserve existing dirty work. One verifier at a time, exclude its entire process tree from parent measurements. No process termination, kernel tuning, forced GC, inspector attachment, heap dumps, package disabling, installation, publication or commits without specific authorization. Do not expose credentials, environment values or raw process arguments.

## Tasks
- [x] T1 — Verify updater safety and initial memory baseline. Delegated gentle-ai-verify; Bun-preserving native updater confirmed. Initial ~903 MiB parent-tree PSS snapshot was observational, not proof of a leak.
- [x] T2 — Update Pi and independently verify installation. Native update ran once, 1.0.0 to 1.0.1; extensions skipped, Bun path retained. Version/help, Node requirement, brace-expansion 5.0.12 and structural checks passed. Subsequent restart corroborated by process ancestry/start time.
- [x] T3 — Apply narrowly scoped startup changes. Delegated worker created eight local overrides; independently verified. Later superseded by user-authorized removal of all registrations, with verified gh, CodeGraph and Engram CLI functionality. No source refactor or shared-package uninstall.
- [ ] T4 — Verify performance under comparable workloads. Partial: qualified observational measurements complete, but matched A/B and parent model-generation measurements remain unperformed. No causal savings or 10/10 claim.
  - [x] T4.1 — Confirm post-removal startup and collect corrected quiet/CLI-load measurements. Delegated verifier musucjwa-1-owd3 completed; no immediate tuning justified.
  - [ ] T4.2 — Measure a defined parent review/generation workload with verified sampler overlap. Coordination attempt failed: the sampler ran only after the workload ended. Do not check off or automatically retry.

## Historical evidence
| Stage | Parent-tree PSS | Processes | Interpretation |
| --- | --- | --- | --- |
| Pre-profile | ~902.4–903.0 MiB | 27 | Direct Pi ~327 MiB; descendants ~575 MiB |
| Eight-server profile | ~940.6–947.5 MiB | 15 | Direct ~425–428 MiB; descendants ~516–520 MiB; no observed total reduction |
| Full registration removal and restart | 511.165 MiB | 3 | Direct 363.036 MiB; descendants 148.129 MiB; qualified observation |

Historical snapshots differ in runtime age, context, workload and shared-memory allocations. They are not matched A/B evidence. The old GitHub MCP credential blocker is obsolete: registrations were removed and authenticated gh public API reads passed. Do not repair or invoke GitHub MCP.

Official Pi 1.0.1 notes document a codemode output-loop OOM limit and brace-expansion security pin, not a general idle-RAM reduction guarantee: https://pi.dev/changelog/releases/1.0.1.

## Diagnostic-method incident
The baseline verifier initially classified diagnostic Bash as Pi because its inline source contained the word pi. ALL initial SAMPLE/TEMP_CLI attribution and workload results were discarded. Corrected identity requires Node executable class plus exact comm=pi and stable ancestry, never arbitrary argument/source substrings.

Corrected orchestrator PID 2097940 and verifier PID 2142462 were confirmed twice. Old parent PIDs were absent and the orchestrator start postdated registration-removal mtimes. The entire verifier subtree was excluded. Only corrected results below are accepted.

## Corrected measurements
Three quiet samples five seconds apart were identical, kernel kB:
- Direct parent PSS: 371749; RSS: 434788.
- Included children PSS: 151684; RSS: 213496.
- Total PSS: 523433 (511.165 MiB); RSS: 648284.
- Included tree: Pi, pyright-langserver and marksman, three processes.

Known inspected MCP markers were absent. Marker matching cannot exclude every unusual embedded implementation. Global/local registration dictionaries were valid and empty. All included/excluded memory reads succeeded; five transient failures for unrelated disappearing PIDs were reported, not counted as zero.

Direct RssAnon was 365040 kB and RssFile 69748 kB. Kernel anonymous/file buckets do not identify JavaScript heap size or individual extension ownership. Installed package inventory does not establish activation or attribution.

Fixed serial read-only CLI workload, all commands successful:
- codegraph query dreamcoder_theme: 0.236 s.
- engram stats: 0.989 s.
- gh public repository API read: 0.784 s.
- Total monotonic duration: 2.010 s.

Concurrent parent total PSS stayed 523428–523433 kB; temporary CLI subtree sampled PSS 4754–49083 kB, not guaranteed peaks. Post samples were 523430/523433/523431 kB total PSS. This measures verifier-owned CLI command overhead, NOT parent model-generation performance, a stress test or matched A/B.

Host MemAvailable was 2692964–2723204 kB; SwapUsed 2045780–2045784 kB. Memory PSI some/full avg10/60/300 were zero. Observed swap-in delta was one page, swap-out zero. Swap occupancy alone does not establish active pressure.

That quiet/CLI baseline is observationally ~392 MiB below the old ~903 MiB snapshot and ~430–436 MiB below the eight-server snapshots. Different conditions prevent causal savings, regression or leak conclusions.

## Parent-workload coordination incident
The parent performed a bounded read-only theme activation review using CodeGraph CLI and tests source, then generated a limited source-backed explanation. No tests or activation were executed. Review/explanation UTC bounds were 2026-10-03 20:44:39.024214–20:45:30.218541. CodeGraph trimmed part of the handler; this was not a full transaction audit.

Initial observer musuy94b-2-scu0 timed out waiting for start authorization and took no samples. Continuation musv1h5i-3-jixa sampled UTC 20:45:43.472230–20:47:43.521313: 120.049 seconds and 121 samples. It started 13.254 seconds after the explanation ended. There was ZERO overlap with the intended workload. Neither a pre-workload quiet phase nor a strictly idle post-workload phase was established. This is a coordination failure, not a successful generation benchmark.

The later interval remains valid as a qualified observation, excluding the entire verifier subtree. Parent PID/startticks remained 2097940/923223; verifier identity was 2397399/1059881. Total PSS min/median/max/start/end kB: 657065/659672/766984/746260/657071 (approximately 642–749 MiB, median 644 MiB, end 642 MiB). Direct parent PSS: 407449/410047/434943/421571/407455; included children: 249614/249616/339294/324689/249616. Included count was 4–5, start/end 4; RSS total min/median/max/start/end: 777824/780428/887756/867016/777824 kB. These are not interchangeable with the earlier three-process baseline.

Observed parent CPU was 22.58 seconds and included children 0.39 seconds; verifier separately used 7.13 CPU seconds with median 306868 kB PSS. Transient process lifetimes not observed are excluded from CPU deltas. Host MemAvailable was 2533316–2714900 kB; swap-in/out 45/0 pages. Memory PSI averages were zero, but some/full cumulative stalls each increased 82 microseconds; do not claim absolutely no stalls. Included/verifier memory reads succeeded. There were 554 transient process-stat enumeration failures, explicitly not counted as zero memory.

Post-observation diff and Markdown checks passed; registrations were 0/0 at preflight. No source/environment writes or prohibited interventions occurred. No matched-workload result, provider latency, causal savings, heap ownership or comprehensive mutation audit was established. Memory ended below the interval start, but that alone proves neither absence nor presence of a leak. Do not relaunch an observer without first establishing a reliable overlap method.

## Verification and delivery
Pi 1.0.1, intended executable, empty registrations, gh authentication/public API, correctly bound CodeGraph CLI and Engram stats passed. Native non-MCP memory/web checks passed in the CLI-first feature. git diff --check and the Markdown link validator passed; structural checks apply to this bookkeeping document, with no meaningful RED phase.

The verifier performed no writes, MCP calls, protected-content reads, installations or process changes. Comprehensive unrelated-byte preservation was not re-proven. Owned files remain untracked; commits were not authorized. RDD is off; previous native assessment was unassessable due unrelated untracked scope and separate verification was performed.

## Next step
The qualified observational diagnosis is complete; the attempted parent-workload measurement FAILED its overlap criterion. T4 and T4.2 remain partial/unverified. Stop automatic observer retries: each adds overhead and neither attempt established a coordinated benchmark. Current evidence does not justify heap, kernel, allocator or extension tuning. If further performance proof is requested, establish a reliable observation window BEFORE beginning a defined repeatable parent workload, excluding verifier trees and accounting for observer overhead. Pre-removal matched A/B and provider latency remain unavailable. Do not create uncontrolled sessions, infer extension ownership from installed manifests, present later sampling as the intended review workload or promise a 10/10 score. No further source or environment changes are planned without new evidence.
