// Pure CI helpers of the Herdr `prs` mod. Run: node --test tests/herdr_mods
import { test } from "node:test";
import assert from "node:assert/strict";
import { checkState, parseGhJson, rollup } from "../../DreamcoderHerdr/.config/herdr-app/mods/prs/ci.js";

test("parseGhJson strips forced ANSI colors before parsing", () => {
  const colored = '\u001b[1;37m[\u001b[m\n  \u001b[1;37m{\u001b[m\u001b[1;34m"number"\u001b[m\u001b[1;37m:\u001b[m 62\u001b[1;37m}\u001b[m\u001b[1;37m]\u001b[m';
  assert.deepEqual(parseGhJson(colored), [{ number: 62 }]);
});

test("parseGhJson keeps plain JSON unchanged", () => {
  assert.deepEqual(parseGhJson('[{"number":1,"title":"a \\u001b b"}]'), [{ number: 1, title: "a \u001b b" }]);
});

test("checkState normalizes CheckRun results", () => {
  const run = (status, conclusion) => checkState({ name: "test", status, conclusion, detailsUrl: "https://ci/1" });
  assert.deepEqual(run("COMPLETED", "SUCCESS"), { name: "test", state: "pass", url: "https://ci/1" });
  assert.equal(run("COMPLETED", "FAILURE").state, "fail");
  assert.equal(run("COMPLETED", "TIMED_OUT").state, "fail");
  assert.equal(run("COMPLETED", "CANCELLED").state, "fail");
  assert.equal(run("IN_PROGRESS", "").state, "pending");
  assert.equal(run("QUEUED", "").state, "pending");
  assert.equal(run("COMPLETED", "SKIPPED").state, "skip");
  assert.equal(run("COMPLETED", "NEUTRAL").state, "skip");
});

test("checkState normalizes StatusContext results", () => {
  const ctx = (state) => checkState({ context: "ci/legacy", state, targetUrl: "https://ci/2" });
  assert.deepEqual(ctx("SUCCESS"), { name: "ci/legacy", state: "pass", url: "https://ci/2" });
  assert.equal(ctx("ERROR").state, "fail");
  assert.equal(ctx("FAILURE").state, "fail");
  assert.equal(ctx("PENDING").state, "pending");
});

test("rollup ranks fail over pending over pass, and none when empty", () => {
  const s = (state) => ({ name: "x", state, url: null });
  assert.equal(rollup([]), "none");
  assert.equal(rollup([s("pass"), s("skip")]), "pass");
  assert.equal(rollup([s("pass"), s("pending")]), "pending");
  assert.equal(rollup([s("pending"), s("fail"), s("pass")]), "fail");
});
