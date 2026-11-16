// Pure helpers for the work-unit budget: the authored changed lines on the
// focused branch, additions plus deletions, measured against its base.
// No `herdr` imports, so `node --test` runs this file directly.

// The reviewable size one work unit aims for. `prs/ci.js` uses the same rule
// for pull requests; this mod shows it while the unit is still being built.
export const REVIEWABLE_LINES = 400;

// Git must not write under .git: the folder watch would see it and every
// refresh would start the next one.
export const READ = [
  "--no-optional-locks",
  "-c",
  "core.fsmonitor=false",
  "-c",
  "diff.autoRefreshIndex=false",
];

// The branch bases this cockpit treats as "the work starts here", in order:
// the local integration branch first, then the remote's own default branch,
// then the usual remote-tracking names for a clone whose `origin/HEAD` was
// never set (`git remote set-head` unfixed).
export const BASES = ["main", "master", "origin/HEAD", "origin/main", "origin/master"];

export const countLines = (text) =>
  text ? text.split("\n").length - Number(text.endsWith("\n")) : 0;

// `git diff --numstat -z`: "<add>\t<del>\t<path>\0", "-" for a binary file.
export function parseNumstat(stdout) {
  let add = 0;
  let del = 0;
  for (const entry of String(stdout ?? "").split("\0")) {
    const parts = entry.split("\t");
    if (parts.length < 3) continue;
    add += Number(parts[0]) || 0;
    del += Number(parts[1]) || 0;
  }
  return { add, del };
}

// `git status --porcelain=v1 -z`: "XY <path>\0".
export function parseStatus(stdout) {
  return String(stdout ?? "")
    .split("\0")
    .filter(Boolean)
    .map((entry) => ({ xy: entry.slice(0, 2), path: entry.slice(3) }));
}

// `git log --numstat --format=__C__%h %s`: a header line opens a commit and the
// numstat lines after it belong to that commit.
export function parseLog(stdout) {
  const commits = [];
  let current = null;
  for (const line of String(stdout ?? "").split("\n")) {
    if (line.startsWith("__C__")) {
      current = { short: line.slice(5).trim(), add: 0, del: 0 };
      commits.push(current);
      continue;
    }
    if (!current || !line) continue;
    const parts = line.split("\t");
    if (parts.length < 3) continue;
    current.add += Number(parts[0]) || 0;
    current.del += Number(parts[1]) || 0;
  }
  return commits;
}

export const total = (parts) =>
  parts.reduce(
    (acc, part) => ({ add: acc.add + (part?.add ?? 0), del: acc.del + (part?.del ?? 0) }),
    { add: 0, del: 0 },
  );

export function budget(parts) {
  const { add, del } = total(parts);
  const lines = add + del;
  return { add, del, lines, over: lines > REVIEWABLE_LINES };
}

export const label = ({ add, del }) => `+${add} \u2212${del}`;
