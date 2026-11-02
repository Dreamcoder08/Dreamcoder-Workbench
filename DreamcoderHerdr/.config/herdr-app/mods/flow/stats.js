// Pure flow metrics for the flow mod: no Herdr imports, so they run under `node --test`.

const REVIEWABLE_LINES = 400;
const HOUR = 3600_000;
const ANSI = /\u001b\[[0-9;]*m/g;

// Same as prs/ci.js parseGhJson: Herdr refuses imports outside a mod's own
// folder, so the one-liner is repeated here (tested in flow_stats.test.mjs).
export function parseGhJson(text) {
  return JSON.parse(text.replace(ANSI, ""));
}

const median = (xs) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b), mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
};
// Nearest-rank percentile.
const percentile = (xs, p) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.max(0, Math.ceil(p * s.length) - 1)];
};

// Merged PRs ({createdAt, mergedAt, additions, deletions}) within `days` of `now`.
export function flowStats(prs, now, days) {
  const since = now - days * 24 * HOUR;
  const merged = prs.filter((p) => p.mergedAt && Date.parse(p.mergedAt) >= since);
  const leads = merged.map((p) => (Date.parse(p.mergedAt) - Date.parse(p.createdAt)) / HOUR);
  const sizes = merged.map((p) => (p.additions ?? 0) + (p.deletions ?? 0));
  return {
    merged: merged.length,
    perWeek: Math.round((merged.length / (days / 7)) * 10) / 10,
    leadMedianH: median(leads),
    leadP90H: percentile(leads, 0.9),
    sizeMedian: median(sizes),
    overShare: sizes.length ? sizes.filter((n) => n > REVIEWABLE_LINES).length / sizes.length : 0,
  };
}

export function duration(hours) {
  if (hours == null) return "—";
  if (hours < 1) return `${Math.round(hours * 60)}m`;
  if (hours < 24) return `${hours.toFixed(1)}h`;
  return `${(hours / 24).toFixed(1)}d`;
}
