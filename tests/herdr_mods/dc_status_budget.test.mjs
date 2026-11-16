// Pure helpers of the Herdr `dc-status` mod. Run: node --test tests/herdr_mods
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  BASES,
  REVIEWABLE_LINES,
  budget,
  countLines,
  label,
  parseLog,
  parseNumstat,
  parseStatus,
  total,
} from "../../DreamcoderHerdr/.config/herdr-app/mods/dc-status/budget.js";

test("BASES tries the local integration branch before the remote's", () => {
  assert.deepEqual(BASES, ["main", "master", "origin/HEAD", "origin/main", "origin/master"]);
});

test("parseNumstat adds additions and deletions across entries", () => {
  assert.deepEqual(parseNumstat("12\t3\tsrc/a.py\0" + "1\t0\tsrc/b.py\0"), { add: 13, del: 3 });
});

test("parseNumstat treats a binary file as zero lines, not as NaN", () => {
  assert.deepEqual(parseNumstat("-\t-\tlogo.png\0"), { add: 0, del: 0 });
});

test("parseNumstat ignores an empty or truncated entry", () => {
  assert.deepEqual(parseNumstat(""), { add: 0, del: 0 });
  assert.deepEqual(parseNumstat("12\t3\0"), { add: 0, del: 0 });
});

test("parseStatus reads porcelain v1 -z entries and their two status letters", () => {
  assert.deepEqual(parseStatus("?? new.md\0 M src/a.py\0A  src/b.py\0"), [
    { xy: "??", path: "new.md" },
    { xy: " M", path: "src/a.py" },
    { xy: "A ", path: "src/b.py" },
  ]);
});

test("parseLog groups numstat lines under their commit header", () => {
  const log = ["__C__a1b2c3d feat: one", "10\t2\tsrc/a.py", "", "__C__e4f5g6h fix: two", "1\t1\tsrc/b.py", "3\t0\tsrc/c.py", ""].join("\n");
  assert.deepEqual(parseLog(log), [
    { short: "a1b2c3d feat: one", add: 10, del: 2 },
    { short: "e4f5g6h fix: two", add: 4, del: 1 },
  ]);
});

test("parseLog yields nothing for a branch with no commits over its base", () => {
  assert.deepEqual(parseLog(""), []);
});

test("budget counts additions plus deletions and stops at the budget itself", () => {
  const at = budget([{ add: 300, del: 100 }]);
  assert.equal(at.lines, REVIEWABLE_LINES);
  assert.equal(at.over, false);
});

test("budget flags one line over the reviewable size", () => {
  const over = budget([{ add: 300, del: 101 }]);
  assert.equal(over.lines, REVIEWABLE_LINES + 1);
  assert.equal(over.over, true);
});

test("budget adds committed, uncommitted and untracked parts together", () => {
  const value = budget([{ add: 10, del: 5 }, { add: 2, del: 1 }, { add: 4, del: 0 }]);
  assert.deepEqual(value, { add: 16, del: 6, lines: 22, over: false });
});

test("total tolerates a missing part, as an unreadable status leaves one", () => {
  assert.deepEqual(total([{ add: 1, del: 2 }, null]), { add: 1, del: 2 });
});

test("countLines counts a trailing newline as ending the last line, not starting one", () => {
  assert.equal(countLines("a\nb\nc"), 3);
  assert.equal(countLines("a\nb\nc\n"), 3);
  assert.equal(countLines(""), 0);
});

test("label keeps a real minus sign, not a hyphen", () => {
  assert.equal(label({ add: 412, del: 38 }), "+412 \u221238");
});
