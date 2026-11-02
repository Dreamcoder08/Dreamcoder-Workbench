// Pure verify-command detection of the Herdr `verify` mod. Run: node --test tests/herdr_mods
import { test } from "node:test";
import assert from "node:assert/strict";
import { detectVerify, elapsed, parseMakeTargets } from "../../DreamcoderHerdr/.config/herdr-app/mods/verify/detect.js";

const repo = (over = {}) => ({ files: new Set(), makeTargets: [], scripts: {}, custom: null, ...over });

test("a custom .herdr/verify command wins over everything", () => {
  const plan = detectVerify(repo({ custom: "  just ci  \n", files: new Set(["Makefile"]), makeTargets: ["verify"] }));
  assert.deepEqual(plan, { label: "just ci", command: "just ci" });
});

test("make verify, then make check, then make lint test", () => {
  const make = (targets) => detectVerify(repo({ files: new Set(["Makefile"]), makeTargets: targets })).command;
  assert.equal(make(["test", "verify", "check"]), "make verify");
  assert.equal(make(["test", "check"]), "make check");
  assert.equal(make(["test", "lint"]), "make lint test");
  assert.equal(make(["test"]), "make test");
});

test("package.json scripts: verify, check, lint and test, test", () => {
  const npm = (scripts) => detectVerify(repo({ files: new Set(["package.json"]), scripts })).command;
  assert.equal(npm({ verify: "x", test: "y" }), "npm run verify");
  assert.equal(npm({ check: "x" }), "npm run check");
  assert.equal(npm({ lint: "x", test: "y" }), "npm run lint && npm test");
  assert.equal(npm({ test: "y" }), "npm test");
});

test("language defaults for Python, Go and Rust", () => {
  assert.equal(detectVerify(repo({ files: new Set(["pyproject.toml"]) })).command, "python3 -m pytest -q");
  assert.equal(detectVerify(repo({ files: new Set(["go.mod"]) })).command, "go vet ./... && go test ./...");
  assert.equal(detectVerify(repo({ files: new Set(["Cargo.toml"]) })).command, "cargo test");
});

test("no known project gives null", () => {
  assert.equal(detectVerify(repo({ files: new Set(["README.md"]) })), null);
});

test("parseMakeTargets reads rule names and skips variables and specials", () => {
  const text = "CC := gcc\n.PHONY: test\ntest:\n\tpytest\nlint: python-lint shell-lint\npython-lint:\n\truff\n%.o: %.c\n";
  assert.deepEqual(parseMakeTargets(text), ["test", "lint", "python-lint"]);
});

test("elapsed formats seconds and minutes", () => {
  assert.equal(elapsed(0), "0s");
  assert.equal(elapsed(12_400), "12s");
  assert.equal(elapsed(125_000), "2m05s");
});
