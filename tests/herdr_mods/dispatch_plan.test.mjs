// Pure dispatch planning of the Herdr `dispatch` mod. Run: node --test tests/herdr_mods
import { test } from "node:test";
import assert from "node:assert/strict";
import { branchFor, ceilingWarning, launchFor } from "../../DreamcoderHerdr/.config/herdr-app/mods/dispatch/plan.js";

test("branchFor uses a leading conventional type and slugs the rest", () => {
  assert.equal(branchFor("fix login redirect loop"), "fix/login-redirect-loop");
  assert.equal(branchFor("Docs: explain the verify key"), "docs/explain-the-verify-key");
  assert.equal(branchFor("refactor(theme) sync writers"), "refactor/theme-sync-writers");
});

test("branchFor defaults to feat and keeps names short and safe", () => {
  assert.equal(branchFor("Añadir panel de métricas!"), "feat/anadir-panel-de-metricas");
  const long = branchFor("a ".repeat(80) + "end");
  assert.ok(long.length <= 45, long);
  assert.match(long, /^feat\/[a-z0-9-]+[a-z0-9]$/);
  assert.equal(branchFor("   "), "feat/task");
});

const TEMPLATE = "---\nname: reviewer\ndescription: Read-only review.\ncommand: gentle-shell\n---\nYou are a read-only reviewer.\n\nReport findings.\n";

test("launchFor builds a role agent from its template", () => {
  assert.deepEqual(launchFor("reviewer", TEMPLATE, "review src/x.rs"), {
    argv: ["gentle-shell"],
    task: "You are a read-only reviewer.\n\nReport findings.\n\nTask: review src/x.rs",
  });
});

test("launchFor runs Claude Code with the task as-is", () => {
  assert.deepEqual(launchFor("claude", null, "fix the flaky test"), { argv: ["claude"], task: "fix the flaky test" });
});

test("launchFor rejects a role template without a command", () => {
  assert.throws(() => launchFor("explorer", "---\nname: explorer\n---\nbody", "map it"), /command/);
});

test("ceilingWarning only fires from the fourth working agent", () => {
  assert.equal(ceilingWarning(3), null);
  assert.match(ceilingWarning(4), /4 agents are working/);
});
