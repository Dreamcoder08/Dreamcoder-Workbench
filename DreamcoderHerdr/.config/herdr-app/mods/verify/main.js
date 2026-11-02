// One-key verify: runs the focused repo's lint+test command in herdr-core
// (`hc run --bg`, so it is not bound by exec's 30 s limit) and shows the
// result per space in the status bar. Key: `verify.run`. Click a finished
// result to read its log. `verify.auto` opts the focused space in or out of
// auto-verify: it then runs by itself whenever one of its agents finishes.
import { View, div } from "gpui-kit";
import { h_flex } from "gpui-base";
import { spaces, panes, focused, exec, readTextFile, theme, notify, run, nextCommand, agents } from "herdr";
import { detectVerify, elapsed, finishedAgents, parseMakeTargets, shouldAutoVerify } from "./detect.js";

const ANSI = /\u001b\[[0-9;]*m/g;
const POLL_MS = 1000;

function location() {
  const space = spaces().find((s) => s.active), f = focused();
  const pane = f?.pane ? panes().find((p) => p.pane === f.pane) : null;
  return { space, cwd: pane?.cwd || f?.cwd || space?.folder };
}

const termName = (spaceId) => "dcv-" + spaceId.replace(/[^a-z0-9]/g, "").slice(-12);
const readOr = async (path, fallback) => { try { return await readTextFile(path); } catch { return fallback; } };

async function planFor(root) {
  const ls = await exec("ls", ["-1A"], { cwd: root });
  const files = new Set(ls.code === 0 ? ls.stdout.split("\n").filter(Boolean) : []);
  const makefile = files.has("Makefile") ? await readOr(`${root}/Makefile`, "") : "";
  let scripts = {};
  if (files.has("package.json")) { try { scripts = JSON.parse(await readOr(`${root}/package.json`, "{}")).scripts || {}; } catch { /* invalid package.json */ } }
  const custom = await readOr(`${root}/.herdr/verify`, null);
  return detectVerify({ files, makeTargets: parseMakeTargets(makefile), scripts, custom });
}

export default class Verify extends View {
  init(_props, cx) {
    try { this.runs = JSON.parse(localStorage.getItem("runs") ?? "{}"); } catch { this.runs = {}; }
    for (const r of Object.values(this.runs)) if (r.state === "fail" && r.code == null) r.state = "stopped";
    try { this.auto = new Set(JSON.parse(localStorage.getItem("auto") ?? "[]")); } catch { this.auto = new Set(); }
    this.statuses = Object.fromEntries(agents().map((a) => [a.address, a.status]));
    cx.timer.every(POLL_MS, (cx) => this.poll(cx));
    cx.spawn(async (cx) => {
      for (;;) {
        const command = await nextCommand();
        if (command === "run") this.start(cx);
        else if (command === "auto") this.toggleAuto(cx);
      }
    });
  }

  save() { localStorage.setItem("runs", JSON.stringify(this.runs)); }

  toggleAuto(cx) {
    const { space } = location();
    if (!space) return;
    const on = !this.auto.has(space.id);
    on ? this.auto.add(space.id) : this.auto.delete(space.id);
    localStorage.setItem("auto", JSON.stringify([...this.auto]));
    notify({ title: `Auto-verify ${on ? "on" : "off"} · ${space.name}`, body: on ? "Runs when an agent in this space finishes." : undefined, level: "info", timeout: 2500 });
    cx.notify();
  }

  // Starts auto-verify for spaces whose agents just finished.
  watchAgents(cx) {
    const now = agents();
    for (const a of finishedAgents(this.statuses, now)) {
      if (!shouldAutoVerify(a.space, this.auto, this.runs[a.space], Date.now())) continue;
      const space = spaces().find((s) => s.id === a.space);
      const cwd = panes().find((p) => p.pane === a.pane)?.cwd || space?.folder;
      if (space && cwd) this.start(cx, { space, cwd, auto: true });
    }
    this.statuses = Object.fromEntries(now.map((a) => [a.address, a.status]));
  }

  start(cx, target = null) {
    const { space, cwd } = target ?? location();
    if (!space || !cwd) return notify({ title: "Verify: no folder", level: "warning" });
    if (space.machine) return notify({ title: "Verify runs on this computer only", body: space.name, level: "warning" });
    if (this.runs[space.id]?.state === "running") return notify({ title: "Verify already running", body: this.runs[space.id].label, level: "info", timeout: 2000 });
    cx.spawn(async (cx) => {
      try {
        const top = await exec("git", ["rev-parse", "--show-toplevel"], { cwd });
        const root = top.code === 0 ? top.stdout.trim() : cwd;
        const found = await planFor(root);
        if (!found) return notify({ title: "Verify: nothing to run", body: "Add a .herdr/verify file with the command.", level: "warning" });
        const name = termName(space.id);
        await exec("hc", ["rm", name]).catch(() => {});
        const r = await exec("hc", ["run", "--bg", "--json", "--no-parent", "--no-notify", "--name", name,
          "--label", "dreamcoder=verify", "--cwd", root, "--", "bash", "-c", found.command]);
        if (r.code !== 0) throw new Error(r.stderr.trim().split("\n")[0] || `hc run exited ${r.code}`);
        this.runs[space.id] = { state: "running", name, root, label: found.label, space: space.name, started: Date.now(), auto: Boolean(target?.auto) };
        this.save();
        if (target?.auto) notify({ title: `Auto-verify · ${space.name}`, body: `An agent finished: ${found.label}`, level: "info", timeout: 2500 });
      } catch (e) {
        notify({ title: "Verify failed to start", body: String(e?.message || e), level: "error" });
      } finally { cx.notify(); }
    });
  }

  poll(cx) {
    this.watchAgents(cx);
    const running = Object.entries(this.runs).filter(([, r]) => r.state === "running");
    if (!running.length) return;
    if (this.polling) return;
    this.polling = true;
    cx.spawn(async (cx) => {
      try {
        for (const [id, r] of running) {
          const g = await exec("hc", ["get", r.name, "--json"]).catch(() => null);
          if (!g || g.code !== 0) { Object.assign(r, { state: "error", finished: Date.now() }); continue; }
          const t = JSON.parse(g.stdout.replace(ANSI, ""));
          if (t.state !== "finished") continue;
          // A killed run has no exit code: report it as stopped, not as a failure.
          const state = t.exit_code === 0 ? "pass" : t.exit_code == null ? "stopped" : "fail";
          Object.assign(r, { state, code: t.exit_code, finished: t.finished_ms || Date.now() });
          notify({ title: `Verify ${{ pass: "passed", fail: "failed", stopped: "stopped" }[state]} · ${r.space}`,
            body: `${r.label} (${elapsed(r.finished - r.started)})`, level: { pass: "success", fail: "error", stopped: "warning" }[state] });
          this.runs[id] = r;
        }
        this.save();
      } finally { this.polling = false; cx.notify(); }
    });
  }

  showLog(r) {
    if (!r?.name) return;
    // No pager: `less` is not always installed, and tab.new keeps the shell open
    // after the command, so the log stays in the terminal's scrollback.
    run("tab.new", { name: "verify log", folder: r.root, argv: ["hc", "read", r.name] });
  }

  render() {
    const t = theme();
    const { space } = location();
    const r = space ? this.runs[space.id] : null;
    const look = {
      running: ["◌", t.working, `verify ${elapsed(Date.now() - (r?.started ?? Date.now()))}`],
      pass: ["✓", t.done, "verify passed"],
      fail: ["✗", t.blocked, `verify failed (exit ${r?.code})`],
      stopped: ["■", t.dim, "verify stopped"],
      error: ["?", t.blocked, "verify lost"],
    }[r?.state] ?? ["▶", t.dim, "verify  alt-t"];
    const auto = Boolean(space && this.auto.has(space.id));
    return h_flex().id("verify").size_full().px(10).gap(6).items_center().justify_end().text_size(12)
      .when(auto, (el) => el.child(div().flex_none().px(5).rounded(4).text_size(10.5).bg(t.accent + "26").text_color(t.accent)
        .tooltip("Auto-verify on: runs when an agent here finishes (alt-shift-t)").child("auto")))
      .when(Boolean(r) && r.state !== "running", (el) => el.cursor_pointer().hover((s) => s.bg(t.hover)))
      .tooltip(r ? `${r.label}\n${r.root}` : "Run lint and tests (alt-t)")
      .on_click(() => (r && r.state !== "running" ? this.showLog(r) : null))
      .child(div().flex_none().text_color(look[1]).child(look[0]))
      .child(div().flex_none().text_color(r ? t.foreground : t.dim).child(look[2]));
  }
}
