// Pure helpers for the Engram recall overlay: where the focused space lives,
// which Engram project owns that folder, and how the answers are drawn. No
// `herdr` imports, so `node --test` runs this file directly.

const BASE = "http://127.0.0.1:7437";

// The folder the overlay reads memory for, or null when there is none to use:
// a remote space, a relative path, or the filesystem root.
export function localFolder(space, cwd) {
  if (!space || space.machine) return null;
  const folder = space.folder || cwd;
  if (!folder || !folder.startsWith("/")) return null;
  const clean = folder.replace(/\/+$/, "");
  return clean || null;
}

// Engram files a project under the directories it has seen, so the folder is
// the only reliable key: a checkout can be renamed after Engram first indexed
// it and its basename then points at no project at all. The longest matching
// directory wins, so `/home/me` does not shadow `/home/me/work` inside it.
export function resolveProject(folder, projects) {
  if (!folder || !Array.isArray(projects)) return null;
  const target = String(folder).replace(/\/+$/, "");
  let best = null;
  let bestLength = -1;
  for (const entry of projects) {
    const name = typeof entry === "string" ? entry : entry?.name;
    const dirs = Array.isArray(entry?.directories) ? entry.directories : [];
    if (!name) continue;
    for (const raw of dirs) {
      const dir = String(raw ?? "").replace(/\/+$/, "");
      if (!dir) continue;
      if (target !== dir && !target.startsWith(`${dir}/`)) continue;
      if (dir.length > bestLength) {
        bestLength = dir.length;
        best = name;
      }
    }
  }
  return best;
}

// `/projects` names every project and the folders each one covers.
export function projectsRequest() {
  return ["--fail", "--silent", "--show-error", "--max-time", "3", `${BASE}/projects`];
}

export function parseProjects(response) {
  if (response?.code !== 0) return [];
  try {
    const data = JSON.parse(response.stdout);
    if (Array.isArray(data)) return data;
    return Array.isArray(data?.projects) ? data.projects : [];
  } catch {
    return [];
  }
}

export function requestFor(project, query) {
  project = project?.trim();
  if (!project) throw new Error("Missing project");
  const q = query.trim();
  const path = q ? `search?q=${encodeURIComponent(q)}&` : "context?";
  return ["--fail", "--silent", "--show-error", "--max-time", "3",
    `${BASE}/${path}project=${encodeURIComponent(project)}&limit=10`];
}

// curl's exit code says why a request failed; "offline" for all of them hides
// a stopped server behind a wrong project name, which is fixed by a different
// action.
const CURL_ERRORS = {
  6: `Engram's host does not resolve (${BASE}).`,
  7: `Engram is not running on ${BASE}. Start it with \`engram serve\`.`,
  22: "Engram rejected the request.",
  28: "Engram did not answer within 3 seconds.",
};

export function resultFor(query, response) {
  if (response?.code !== 0) return CURL_ERRORS[response?.code] || "Engram is offline or the request failed.";
  try {
    const data = JSON.parse(response.stdout);
    if (!query.trim()) {
      if (typeof data?.context !== "string") throw new Error();
      return data.context.trim() || "No context for this project.";
    }
    if (!Array.isArray(data)) throw new Error();
    if (!data.length) return "No results for this project.";
    return data.map((item) => `### ${String(item.title || "Untitled").replace(/[\r\n]/g, " ")}\n\n${item.content || ""}`).join("\n\n---\n\n");
  } catch { return "Error: invalid Engram response."; }
}

// A search answer as rows the overlay can list one per line. Null means the
// answer was not a list at all, so the caller reports the failure instead.
export function rowsFor(response) {
  if (response?.code !== 0) return null;
  try {
    const data = JSON.parse(response.stdout);
    if (!Array.isArray(data)) return null;
    return data
      .filter((row) => row && typeof row.title === "string" && row.title.trim())
      .map((row) => ({
        id: String(row.id ?? row.title),
        type: String(row.type ?? ""),
        title: row.title.trim(),
        content: String(row.content ?? ""),
        created: String(row.created_at ?? ""),
      }));
  } catch { return null; }
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// Engram stamps are "2026-11-04 22:19:18"; a row wants "Nov 4".
export function shortDate(stamp) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(stamp ?? ""));
  if (!m) return "";
  const month = MONTHS[Number(m[2]) - 1];
  return month ? `${month} ${Number(m[3])}` : "";
}

// Which theme color draws a memory type. Unknown types read as plain text.
const TONES = {
  bugfix: "blocked",
  decision: "accent",
  architecture: "working",
  discovery: "done",
  pattern: "done",
  config: "muted",
  preference: "muted",
  manual: "muted",
  passive: "dim",
  session_summary: "dim",
};

export const typeTone = (type) => TONES[String(type ?? "").toLowerCase()] ?? "muted";

// The one-line preview under a title: markdown flattened, whitespace collapsed.
export function snippet(text, max = 140) {
  const flat = String(text ?? "")
    .replace(/[*_`#>]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (flat.length <= max) return flat;
  return `${flat.slice(0, max - 1).trimEnd()}\u2026`;
}
