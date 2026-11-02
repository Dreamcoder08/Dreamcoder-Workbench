// Auto-verify decisions of the Herdr `verify` mod. Run: node --test tests/herdr_mods
import { test } from "node:test";
import assert from "node:assert/strict";
import { finishedAgents, shouldAutoVerify } from "../../DreamcoderHerdr/.config/herdr-app/mods/verify/detect.js";

const agent = (address, space, status) => ({ address, space, status });

test("finishedAgents reports agents that went from working to done or idle", () => {
  const prev = { t1: "working", t2: "working", t3: "idle", t4: "working" };
  const now = [agent("t1", "s1", "done"), agent("t2", "s2", "idle"), agent("t3", "s1", "done"), agent("t4", "s1", "working"), agent("t5", "s3", "done")];
  assert.deepEqual(finishedAgents(prev, now), [agent("t1", "s1", "done"), agent("t2", "s2", "idle")]);
});

test("finishedAgents ignores a blocked agent: it needs you, it did not finish", () => {
  assert.deepEqual(finishedAgents({ t1: "working" }, [agent("t1", "s1", "blocked")]), []);
});

const NOW = 1_000_000;
test("shouldAutoVerify needs an opted-in space", () => {
  assert.equal(shouldAutoVerify("s1", new Set(), undefined, NOW), false);
  assert.equal(shouldAutoVerify("s1", new Set(["s1"]), undefined, NOW), true);
});

test("shouldAutoVerify skips a running verify and a run started under 60 s ago", () => {
  const on = new Set(["s1"]);
  assert.equal(shouldAutoVerify("s1", on, { state: "running", started: NOW - 120_000 }, NOW), false);
  assert.equal(shouldAutoVerify("s1", on, { state: "pass", started: NOW - 30_000 }, NOW), false);
  assert.equal(shouldAutoVerify("s1", on, { state: "fail", started: NOW - 61_000 }, NOW), true);
});
