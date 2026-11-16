# DeepSeek Harness uninstall, keep data
Remove the Bun-installed DSH CLI and DSH-exclusive direct global packages using Bun.
Preserve ~/.dsh, the existing upgrade backup and unrelated tools. No process kills, data removal, script trust, blanket cleanup or rollback.

## Specs
- **S1:** "hay errores con deepseek harnes , mejor elimina todo de deepseek"
- **S2:** Explicit destructive scope choice: "Desinstalar y conservar mis datos (recomendado)" — remove DSH and its exclusive packages, retain ~/.dsh and upgrade backup; selected token uninstall_keep_data.

## Tasks
- T1 | S1-S2 | parent maintenance | done | .tmp/dsh-uninstall/before.json records exact 20 DSH package names, 11 unrelated package manifests/resolutions, 13497 user data metadata entries and backup presence; commit: none.
- T2 | S1-S2 | parent maintenance | dropped | User changed objective to installing official DSH before any remove command ran; commit: none.
- T3 | S1-S2 | independent verifier | dropped | No removal occurred; superseded by install request; commit: none.

## Log
- L1: "hay errores con deepseek harnes , mejor elimina todo de deepseek"
- L2: User selected "Desinstalar y conservar mis datos (recomendado)" (uninstall_keep_data). No deletion of ~/.dsh or .tmp/dsh-update-20261109T010312 allowed.
- L3: Current launcher ~/.bun/bin/dsh -> ~/.bun/install/global/node_modules/@deepseek-ai/dsh/lib/bin.js. Global manifest has @deepseek-ai/dsh plus 19 @deepseek-ai/dsh-* direct dependencies, distinct from unrelated Pi, Open Pencil, codegraph, TypeScript and other tools. Confirmed 20 from manifest. Risk item 5: package-manager environment removal. Previous update verifier limitations remain historical, not reset or passed; uninstall is a newly authorized objective.
- L4: User: "instala deepseek harnes , https://github.com/deepseek-ai/deepseek-harness". Supersedes pending uninstall before any removal command. DSH remains installed 0.2.2-rc.1, all user data and upgrade backup retained. Official README supports npm package launch and source clone/build; clarify source checkout versus repair isolated package installation before changes.
