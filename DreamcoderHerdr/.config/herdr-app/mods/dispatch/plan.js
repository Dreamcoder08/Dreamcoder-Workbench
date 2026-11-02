// Pure helpers for the dispatch mod: no Herdr imports, so they run under `node --test`.

const TYPES = new Set(["feat", "fix", "docs", "refactor", "test", "chore", "perf", "style", "build", "ci"]);
const MAX_BRANCH = 45;
// With one person integrating, 3-4 parallel agents is the practical ceiling.
const CEILING = 4;

// Conventional branch name from a task: "fix login loop" -> "fix/login-loop".
export function branchFor(task) {
  const words = task.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().match(/[a-z0-9]+/g) ?? [];
  const type = TYPES.has(words[0]) ? words.shift() : "feat";
  const slug = words.join("-").slice(0, MAX_BRANCH - type.length - 1).replace(/-+$/, "");
  return `${type}/${slug || "task"}`;
}

// What to run for a role: Claude Code takes the task as-is; a herdr-core
// template supplies its command and instructions, followed by the task.
export function launchFor(role, templateText, task) {
  if (role === "claude") return { argv: ["claude"], task };
  const match = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/.exec(templateText ?? "");
  const command = match && /^command:\s*(.+)$/m.exec(match[1])?.[1].trim();
  if (!command) throw new Error(`template "${role}" has no command`);
  return { argv: [command], task: `${match[2].trim()}\n\nTask: ${task}` };
}

export function ceilingWarning(working) {
  return working >= CEILING
    ? `${working} agents are working. With one person integrating, 3-4 in parallel is the practical ceiling.`
    : null;
}
