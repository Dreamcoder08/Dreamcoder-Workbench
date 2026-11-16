import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  localFolder,
  parseProjects,
  projectsRequest,
  requestFor,
  resolveProject,
  resultFor,
  rowsFor,
  shortDate,
  snippet,
  typeTone,
} from "../../DreamcoderHerdr/.config/herdr-app/mods/dc-engram/recall.js";

test("popup root reserves height for its scrollable results", () => {
  const source = readFileSync(new URL("../../DreamcoderHerdr/.config/herdr-app/mods/dc-engram/main.js", import.meta.url), "utf8");
  assert.match(source, /\.w_full\(\)\.h\(400\)/);
  assert.match(source, /id\("engram-results"\)\.flex_1\(\)\.min_h\(0\)\.overflow_y_scrollbar\(\)/);
});

test("the folder comes only from a focused local space", () => {
  assert.equal(localFolder({ folder: "/work/my project/" }, "/work/my project/src"), "/work/my project");
  assert.equal(localFolder({ machine: "remote", folder: "/work/repo" }, "/work/repo"), null);
  assert.equal(localFolder(null, "/work/repo"), null);
  assert.equal(localFolder({ folder: "/" }, "/"), null);
});

test("a project owns the folder Engram has seen it in", () => {
  const projects = [
    { name: "home", directories: ["/home/me"] },
    { name: "work", directories: ["/home/me/work"] },
  ];
  assert.equal(resolveProject("/home/me/work/repo", projects), "work");
  assert.equal(resolveProject("/home/me/work", projects), "work");
  assert.equal(resolveProject("/home/me/notes", projects), "home");
  assert.equal(resolveProject("/home/me/worktree", projects), "home");
});

test("a renamed checkout still resolves through the folder Engram recorded", () => {
  const projects = [{ name: "job-hunter", directories: ["/work/job-hunter", "/work/job"] }];
  assert.equal(resolveProject("/work/job", projects), "job-hunter");
});

test("project resolution reports nothing instead of guessing", () => {
  assert.equal(resolveProject("/srv/other", [{ name: "work", directories: ["/home/me/work"] }]), null);
  assert.equal(resolveProject("/home/me/work", null), null);
  assert.equal(resolveProject("/home/me/work", [{ name: "", directories: ["/home/me/work"] }]), null);
  assert.equal(resolveProject("/home/me/work", [{ name: "work" }]), null);
});

test("the projects request is bounded and the answer is a list or nothing", () => {
  assert.deepEqual(projectsRequest(), ["--fail", "--silent", "--show-error", "--max-time", "3", "http://127.0.0.1:7437/projects"]);
  assert.deepEqual(parseProjects({ code: 0, stdout: '{"count":1,"projects":[{"name":"a"}]}' }), [{ name: "a" }]);
  assert.deepEqual(parseProjects({ code: 0, stdout: '[{"name":"a"}]' }), [{ name: "a" }]);
  assert.deepEqual(parseProjects({ code: 7, stdout: "" }), []);
  assert.deepEqual(parseProjects({ code: 0, stdout: "oops" }), []);
});

test("requests are project-scoped, encoded and bounded", () => {
  assert.deepEqual(requestFor("a & b", ""), ["--fail", "--silent", "--show-error", "--max-time", "3", "http://127.0.0.1:7437/context?project=a%20%26%20b&limit=10"]);
  assert.match(requestFor("repo", "x & y").at(-1), /\/search\?q=x%20%26%20y&project=repo&limit=10$/);
  assert.throws(() => requestFor(" ", "x"), /project/i);
});

test("result states distinguish empty, errors and valid content", () => {
  assert.match(resultFor("", { code: 0, stdout: '{"context":"# Context"}' }), /# Context/);
  assert.match(resultFor("", { code: 0, stdout: '{"context":""}' }), /No context/);
  assert.match(resultFor("x", { code: 0, stdout: '[]' }), /No results/);
  assert.match(resultFor("x", { code: 0, stdout: '[{"title":"Found","content":"body"}]' }), /Found[\s\S]*body/);
  assert.match(resultFor("x", { code: 0, stdout: 'oops' }), /error/i);
});

test("curl exit codes name the actual failure", () => {
  assert.match(resultFor("x", { code: 7, stderr: "refused" }), /not running/);
  assert.match(resultFor("x", { code: 28, stderr: "timeout" }), /did not answer/);
  assert.match(resultFor("x", { code: 22, stderr: "404" }), /rejected/);
  assert.match(resultFor("x", { code: 52, stderr: "" }), /offline/i);
});

test("a search answer becomes rows the overlay can list", () => {
  const rows = rowsFor({
    code: 0,
    stdout: JSON.stringify([
      { id: 1, type: "decision", title: " kept ", content: "body", created_at: "2026-11-04 22:19:18" },
      { id: 2, type: "discovery", title: "   ", content: "blank title" },
      { id: 3, type: "bugfix", content: "no title" },
    ]),
  });
  assert.deepEqual(rows, [{ id: "1", type: "decision", title: "kept", content: "body", created: "2026-11-04 22:19:18" }]);
});

test("a failed or malformed answer is not a row list", () => {
  assert.equal(rowsFor({ code: 7, stdout: "" }), null);
  assert.equal(rowsFor({ code: 0, stdout: '{"error":"nope"}' }), null);
  assert.equal(rowsFor({ code: 0, stdout: "oops" }), null);
  assert.equal(rowsFor(null), null);
});

test("an empty answer is a row list of zero rows, which reads as no results", () => {
  assert.deepEqual(rowsFor({ code: 0, stdout: "[]" }), []);
});

test("shortDate renders an Engram stamp as a short month and day", () => {
  assert.equal(shortDate("2026-11-04 22:19:18"), "Nov 4");
  assert.equal(shortDate("2026-01-31 00:00:00"), "Jan 31");
  assert.equal(shortDate(""), "");
  assert.equal(shortDate(undefined), "");
});

test("typeTone maps known memory types and falls back for the rest", () => {
  assert.equal(typeTone("bugfix"), "blocked");
  assert.equal(typeTone("PASSIVE"), "dim");
  assert.equal(typeTone("invented"), "muted");
  assert.equal(typeTone(undefined), "muted");
});

test("snippet flattens markdown and cuts with one ellipsis", () => {
  assert.equal(snippet("**What**: added `x`\n\nWhy: because"), "What : added x Why: because");
  const out = snippet("word ".repeat(80), 40);
  assert.equal(out.length, 40);
  assert.ok(out.endsWith("\u2026"));
});
