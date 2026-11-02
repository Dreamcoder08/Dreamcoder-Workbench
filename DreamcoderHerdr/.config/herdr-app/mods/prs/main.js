// Pull requests and CI for the focused space's repository, via the gh CLI.
// Click a PR to expand its checks; click a check to open its CI logs.
import { View, div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { spaces, panes, focused, exec, theme, notify, nextCommand, home } from "herdr";
import { checkState, parseGhJson, prSize, REVIEWABLE_LINES, rollup } from "./ci.js";

const FIELDS = "number,title,url,isDraft,headRefName,author,reviewDecision,statusCheckRollup,additions,deletions";
const REFRESH_MS = 60000;

function location() {
  const space = spaces().find((s) => s.active), f = focused();
  const pane = f?.pane ? panes().find((p) => p.pane === f.pane) : null;
  return { cwd: pane?.cwd || f?.cwd || space?.folder, on: space?.machine ?? null };
}

const REVIEW = { APPROVED: ["Approved", "done"], CHANGES_REQUESTED: ["Changes", "blocked"], REVIEW_REQUIRED: ["Review", "dim"] };

export default class Prs extends View {
  init(_props, cx) {
    this.prs = []; this.open = new Set(); this.error = null; this.repo = null;
    this.refresh(cx);
    cx.timer.every(REFRESH_MS, (cx) => this.refresh(cx));
    cx.spawn(async (cx) => {
      for (;;) if ((await nextCommand()) === "refresh") this.refresh(cx, true);
    });
  }

  refresh(cx, manual = false) {
    if (this.busy) return;
    const { cwd, on } = location();
    if (!cwd) return;
    const context = JSON.stringify({ cwd, on });
    if (context !== this.context) { this.context = context; this.prs = []; this.open.clear(); this.error = null; }
    this.busy = true; cx.notify();
    cx.spawn(async (cx) => {
      try {
        const top = await exec("git", ["rev-parse", "--show-toplevel"], { cwd, on });
        if (top.code !== 0) { this.repo = null; this.prs = []; this.error = `Not a git repository: ${cwd.replace(home(), "~")}`; return; }
        const root = top.stdout.trim();
        this.repo = root.split("/").pop();
        const r = await exec("gh", ["pr", "list", "--state", "open", "--limit", "30", "--json", FIELDS], { cwd: root, on });
        if (r.code !== 0) { this.error = r.stderr.trim().split("\n")[0] || "gh pr list failed"; return; }
        const previous = new Map(this.prs.map((p) => [p.number, p.ci]));
        this.prs = parseGhJson(r.stdout).map((p) => {
          const checks = (p.statusCheckRollup || []).map(checkState);
          return { ...p, checks, ci: rollup(checks), size: prSize(p) };
        });
        this.error = null;
        for (const p of this.prs) {
          const before = previous.get(p.number);
          if (before === "pending" && (p.ci === "fail" || p.ci === "pass")) {
            notify({ title: `#${p.number} CI ${p.ci === "pass" ? "passed" : "failed"}`, body: p.title, level: p.ci === "pass" ? "success" : "error" });
          }
        }
        if (manual) notify({ title: `${this.prs.length} open PR(s)`, body: this.repo, level: "info", timeout: 2000 });
      } catch (e) {
        this.error = String(e?.message || e);
      } finally {
        this.busy = false; cx.notify();
      }
    });
  }

  openUrl(url, cx) {
    if (!url) return;
    try { cx.open_url(url); } catch { exec("xdg-open", [url]).catch(() => {}); }
  }

  dot(state, t) {
    const color = { pass: t.done, fail: t.blocked, pending: t.working, skip: t.dim, none: t.dim }[state];
    return div().size(8).flex_none().rounded(4).bg(color);
  }

  row(p, t) {
    const expanded = this.open.has(p.number);
    const [reviewLabel, reviewColor] = REVIEW[p.reviewDecision] || [null, null];
    const head = h_flex().id(`pr-${p.number}`).gap(8).px(8).h(30).items_center().rounded(6).cursor_pointer()
      .hover((s) => s.bg(t.hover))
      .on_click((_e, cx) => { expanded ? this.open.delete(p.number) : this.open.add(p.number); cx.notify(); })
      .child(this.dot(p.ci, t))
      .child(div().flex_none().text_color(t.dim).child(`#${p.number}`))
      .child(div().flex_1().min_w(0).truncate().text_color(p.isDraft ? t.muted : t.foreground).child(p.title))
      .when(p.isDraft, (el) => el.child(div().flex_none().text_size(10.5).text_color(t.dim).child("draft")))
      .child(div().id(`pr-size-${p.number}`).flex_none().px(5).rounded(4).text_size(10.5)
        .when(p.size.over, (el) => el.bg(t.blocked + "26").font_semibold())
        .text_color(p.size.over ? t.blocked : t.dim)
        .tooltip(p.size.over ? `${p.size.lines} changed lines: over ${REVIEWABLE_LINES}, consider splitting` : `${p.size.lines} changed lines`)
        .child(`±${p.size.label}`))
      .when(Boolean(reviewLabel), (el) => el.child(div().flex_none().text_size(10.5).text_color(t[reviewColor]).child(reviewLabel)))
      .child(div().id(`pr-open-${p.number}`).flex_none().px(4).text_color(t.accent).cursor_pointer()
        .tooltip("Open PR")
        .on_click((e, cx) => { e.stop_propagation?.(); this.openUrl(p.url, cx); })
        .child("↗"));
    if (!expanded) return head;
    const checks = [...p.checks].sort((a, b) => ["fail", "pending", "pass", "skip"].indexOf(a.state) - ["fail", "pending", "pass", "skip"].indexOf(b.state));
    return v_flex().gap(1).child(head)
      .child(div().pl(24).text_size(11).text_color(t.dim).child(`${p.headRefName} · ${p.author?.login ?? ""}`))
      .when(!checks.length, (el) => el.child(div().pl(24).text_size(11.5).text_color(t.dim).child("No checks")))
      .children(checks.map((c, i) => h_flex().id(`check-${p.number}-${i}`).gap(8).pl(24).pr(8).h(24).items_center().rounded(5)
        .when(Boolean(c.url), (el) => el.cursor_pointer().hover((s) => s.bg(t.hover)).on_click((_e, cx) => this.openUrl(c.url, cx)))
        .child(this.dot(c.state, t))
        .child(div().flex_1().min_w(0).truncate().text_size(11.5).text_color(c.state === "fail" ? t.blocked : t.muted).child(c.name))));
  }

  render() {
    const t = theme();
    const failing = this.prs.filter((p) => p.ci === "fail").length;
    const header = h_flex().gap(8).px(10).h(36).flex_none().items_center().border_b(1).border_color(t.border)
      .child(div().font_semibold().text_color(t.foreground).child("Pull requests"))
      .child(div().flex_1().min_w(0).truncate().text_color(t.dim).child(this.repo ?? ""))
      .when(failing > 0, (el) => el.child(div().flex_none().text_size(11).text_color(t.blocked).child(`${failing} failing`)))
      .child(div().id("prs-refresh").flex_none().px(6).rounded(5).cursor_pointer().text_color(this.busy ? t.dim : t.accent)
        .hover((s) => s.bg(t.hover)).tooltip("Refresh")
        .on_click((_e, cx) => this.refresh(cx, true))
        .child(this.busy ? "…" : "⟳"));
    const body = v_flex().id("prs-list").flex_1().min_h(0).p(6).gap(2).overflow_y_scrollbar()
      .when(Boolean(this.error), (el) => el.child(div().px(8).py(6).text_color(t.blocked).child(this.error)))
      .when(!this.error && !this.busy && !this.prs.length, (el) => el.child(div().px(8).py(6).text_color(t.dim).child("No open pull requests")))
      .children(this.prs.map((p) => this.row(p, t)));
    return v_flex().id("prs").size_full().bg(t.surface).text_size(12.5).child(header).child(body);
  }
}
