// Pure helpers for the prs mod: no Herdr imports, so they run under `node --test`.

const FAILED = new Set(["FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR"]);
const PENDING = new Set(["PENDING", "EXPECTED"]);
const SKIPPED = new Set(["SKIPPED", "NEUTRAL"]);
// Raw ESC never occurs inside valid JSON strings (it would be \u001b), so
// stripping SGR sequences only removes color that CLICOLOR_FORCE injects.
const ANSI = /\u001b\[[0-9;]*m/g;

export function parseGhJson(text) {
  return JSON.parse(text.replace(ANSI, ""));
}

// Normalizes CheckRun and StatusContext entries to { name, state, url }.
export function checkState(c) {
  const name = c.name || c.context || "check";
  const url = c.detailsUrl || c.targetUrl || null;
  const result = c.conclusion || c.state || "";
  if (FAILED.has(result)) return { name, state: "fail", url };
  if ((c.status && c.status !== "COMPLETED") || PENDING.has(result)) return { name, state: "pending", url };
  if (SKIPPED.has(result)) return { name, state: "skip", url };
  return { name, state: "pass", url };
}

export function rollup(checks) {
  if (!checks.length) return "none";
  if (checks.some((c) => c.state === "fail")) return "fail";
  if (checks.some((c) => c.state === "pending")) return "pending";
  return "pass";
}
