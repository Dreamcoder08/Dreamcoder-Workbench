// Dreamcoder cockpit panels inside the gentle-shell layout. The right column is
// a stack (`panel-body`) whose default child is the Gentle inspector; Files, PRs
// and Flow share it. A button (or `dc-panels.panel-<id>`) shows that panel, and
// using it again returns to the inspector, so the column is never empty.
import { View, svg } from "gpui-kit";
import { h_flex } from "gpui-base";
import { layout, nextCommand, run, theme } from "herdr";

const HOME = "inspector";
const PANELS = [
  { id: "files", label: "Files", icon: "mods/files/file.svg" },
  { id: "prs", label: "PRs", icon: "mods/prs/prs.svg" },
  { id: "flow", label: "Flow", icon: "mods/flow/flow.svg" },
];

function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

function toggle(id) {
  const body = find(layout(), "panel-body");
  if (!body?.children?.some((c) => c.id === id)) return;
  run("layout.select", { stack: "panel-body", child: body.active === id ? HOME : id });
  run("layout.show", { id: "panel" });
}

export default class Panels extends View {
  init(_props, cx) {
    cx.spawn(async () => {
      for (;;) {
        const command = await nextCommand();
        if (typeof command === "string" && command.startsWith("panel-")) toggle(command.slice(6));
      }
    });
  }

  render() {
    const t = theme();
    const body = find(layout(), "panel-body");
    const button = ({ id, label, icon }) => {
      const on = body?.active === id;
      return h_flex().id(`panel-${id}`).h(22).px(7).gap(5).flex_none().items_center().rounded(5)
        .text_size(11.8).bg(on ? t.selected : t.chrome).text_color(on ? t.foreground : t.muted)
        .hover((s) => s.bg(t.hover))
        .on_click(() => toggle(id))
        .child(svg(icon).size(13)).child(label);
    };
    return h_flex().size_full().px(6).gap(3).items_center().justify_end().bg(t.chrome).border_t(1).border_color(t.border)
      .children(PANELS.filter((p) => body?.children?.some((c) => c.id === p.id)).map(button));
  }
}
