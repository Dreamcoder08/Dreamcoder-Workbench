// Pure flow metrics of the Herdr `flow` mod. Run: node --test tests/herdr_mods
import { test } from "node:test";
import assert from "node:assert/strict";
import { parseGhJson as prsParse } from "../../DreamcoderHerdr/.config/herdr-app/mods/prs/ci.js";
import { duration, flowStats, parseGhJson } from "../../DreamcoderHerdr/.config/herdr-app/mods/flow/stats.js";

const NOW = Date.parse("2026-11-02T18:00:00Z");
const H = 3600_000;
const pr = (openedHoursAgo, leadHours, lines = 100) => ({
  createdAt: new Date(NOW - openedHoursAgo * H).toISOString(),
  mergedAt: new Date(NOW - openedHoursAgo * H + leadHours * H).toISOString(),
  additions: lines, deletions: 0,
});

test("flowStats counts merges in the window and per week", () => {
  const s = flowStats([pr(10, 1), pr(50, 2), pr(200, 3), pr(500, 4)], NOW, 14);
  assert.equal(s.merged, 3);
  assert.equal(s.perWeek, 1.5);
});

test("flowStats gives median and p90 open-to-merge lead time in hours", () => {
  const s = flowStats([pr(10, 1), pr(20, 2), pr(30, 3), pr(40, 4), pr(50, 10)], NOW, 14);
  assert.equal(s.leadMedianH, 3);
  assert.equal(s.leadP90H, 10);
});

test("flowStats reports median size and the share over 400 lines", () => {
  const s = flowStats([pr(10, 1, 50), pr(20, 1, 300), pr(30, 1, 900), pr(40, 1, 1600)], NOW, 14);
  assert.equal(s.sizeMedian, 600);
  assert.equal(s.overShare, 0.5);
});

test("flowStats is empty-safe", () => {
  assert.deepEqual(flowStats([], NOW, 14), { merged: 0, perWeek: 0, leadMedianH: null, leadP90H: null, sizeMedian: null, overShare: 0 });
});

test("duration formats minutes, hours and days", () => {
  assert.equal(duration(null), "—");
  assert.equal(duration(0.5), "30m");
  assert.equal(duration(3.25), "3.3h");
  assert.equal(duration(50), "2.1d");
});

test("parseGhJson matches the prs mod copy on colored and plain gh output", () => {
  for (const text of ['\u001b[1;37m[\u001b[m{"number":64}\u001b[1;37m]\u001b[m', '[{"number":1}]']) {
    assert.deepEqual(parseGhJson(text), prsParse(text));
  }
});
