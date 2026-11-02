// Pure helpers for the verify mod: no Herdr imports, so they run under `node --test`.

// Picks the repo's lint+test command. Order: custom file, make, npm, language defaults.
// repo = { files: Set<rootFileName>, makeTargets: string[], scripts: object, custom: string|null }
export function detectVerify(repo) {
  const custom = repo.custom?.trim();
  if (custom) return plan(custom);
  if (repo.files.has("Makefile")) {
    const t = new Set(repo.makeTargets);
    if (t.has("verify")) return plan("make verify");
    if (t.has("check")) return plan("make check");
    if (t.has("lint") && t.has("test")) return plan("make lint test");
    if (t.has("test")) return plan("make test");
  }
  if (repo.files.has("package.json")) {
    const s = repo.scripts || {};
    if (s.verify) return plan("npm run verify");
    if (s.check) return plan("npm run check");
    if (s.lint && s.test) return plan("npm run lint && npm test");
    if (s.test) return plan("npm test");
  }
  if (["pyproject.toml", "pytest.ini", "setup.cfg"].some((f) => repo.files.has(f))) return plan("python3 -m pytest -q");
  if (repo.files.has("go.mod")) return plan("go vet ./... && go test ./...");
  if (repo.files.has("Cargo.toml")) return plan("cargo test");
  return null;
}

const plan = (command) => ({ label: command, command });

// Rule names from a Makefile, skipping variables (:=), specials (.PHONY) and patterns (%).
export function parseMakeTargets(text) {
  const targets = [];
  for (const line of text.split("\n")) {
    const m = /^([A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?!=)/.exec(line);
    if (m && !targets.includes(m[1])) targets.push(m[1]);
  }
  return targets;
}

export function elapsed(ms) {
  const s = Math.floor(ms / 1000);
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m${String(s % 60).padStart(2, "0")}s`;
}
