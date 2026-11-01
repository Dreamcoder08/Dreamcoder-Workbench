// A quiet drawer of the agents that need you: blocked first, then done.
// Empty when nobody does, so it hides itself.

import { View, div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { agents, placement, run, theme } from "herdr";

const WIDTH = 240;
const ROW = 30;
const RANK = { blocked: 0, done: 1 };

// The agent's icon from the app's program table: a one-color glyph or a picture.
function icon(p, size, color) {
  if (!p?.icon) return null;
  return p.tint ? svg(p.icon).size(size).flex_none().text_color(color) : image(p.icon).w(size).h(size).flex_none();
}

export default class NeedsYou extends View {
  render() {
    const waiting = agents()
      .filter((a) => a.status in RANK)
      .sort((a, b) => RANK[a.status] - RANK[b.status] || b.seq - a.seq);
    if (waiting.length === 0) return div();

    const t = theme();
    // On the right edge the status sits on the edge side, so the row is mirrored.
    const mirror = placement()?.edge === "right";

    return v_flex()
      .id("needs-you")
      .w(WIDTH)
      .py(4)
      .children(waiting.map((a) => {
        const color = a.status === "blocked" ? t.blocked : t.done;
        const dot = div().w(8).h(8).rounded(4).flex_none().bg(color);
        const glyph = icon(a.program, 14, t.muted);
        const label = div()
          .flex_1()
          .truncate()
          .text_size(12.5)
          .text_color(t.foreground)
          .child(a.space_name === a.tab_name ? a.space_name : `${a.space_name} · ${a.tab_name}`);
        const parts = [dot, glyph, label].filter(Boolean);
        return h_flex()
          .id(`needs-${a.address}`)
          .h(ROW)
          .px(12)
          .gap(10)
          .items_center()
          .hover((el) => el.bg(t.hover))
          .on_click(() => run("agent.focus", { terminal: a.address }))
          .children(mirror ? parts.reverse() : parts);
      }));
  }
}
