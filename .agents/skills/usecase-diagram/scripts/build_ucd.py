#!/usr/bin/env python3
"""Build a UML use case diagram (.drawio and optional .svg) from a JSON spec.

Usage: python build_ucd.py spec.json out.drawio [--svg out.svg]

Spec:
{
  "title": "UCs for Teacher",
  "system": "EDUA",
  "actors":   [{"id": "teacher", "name": "Teacher", "side": "left", "parent": null}],
  "usecases": [{"id": "uc05", "name": "Create Lesson Plan"}],
  "links":    [{"actor": "teacher", "uc": "uc05"}],
  "includes": [{"from": "uc05", "to": "uc02"}],      # <<include>>: base -> included
  "extends":  [{"from": "uc07", "to": "uc05"}]       # <<extend>>: extension -> base
}
`parent` on an actor draws a generalization (child -> parent, hollow triangle).
`side` is "left" or "right" (default: alternate). Use cases keep the given order.
"""
import json
import math
import sys
from xml.sax.saxutils import escape

UC_W, UC_H, GAP_X, GAP_Y = 200, 60, 50, 30
PAD, HEAD = 40, 50
ACT_W, ACT_H, ACT_GAP = 40, 70, 40


def layout(spec):
    ucs, actors = spec["usecases"], spec["actors"]
    n = len(ucs)
    cols = 1 if n <= 8 else 2 if n <= 16 else 3
    sides = {}
    for i, a in enumerate(actors):
        sides[a["id"]] = a.get("side") or ("left" if i % 2 == 0 else "right")
    # column assignment: with 2 columns, use cases linked mostly to right-side actors go right
    colof = {}
    if cols == 2:
        for i, u in enumerate(ucs):
            score = 0
            for l in spec.get("links", []):
                if l["uc"] == u["id"] and l["actor"] in sides:
                    score += 1 if sides[l["actor"]] == "left" else -1
            colof[u["id"]] = 0 if score > 0 else 1 if score < 0 else None
        for i, u in enumerate([u for u in ucs if colof[u["id"]] is None]):
            colof[u["id"]] = i % 2
    else:
        for i, u in enumerate(ucs):
            colof[u["id"]] = i % cols
    columns = [[u for u in ucs if colof[u["id"]] == c] for c in range(cols)]
    rows = max(len(c) for c in columns)
    sys_w = PAD * 2 + cols * UC_W + (cols - 1) * GAP_X
    sys_h = HEAD + PAD + rows * UC_H + (rows - 1) * GAP_Y
    left_x = 40
    sys_x = left_x + ACT_W + 140
    sys_y = 60
    pos = {}
    for c, col in enumerate(columns):
        for r, u in enumerate(col):
            pos[u["id"]] = (sys_x + PAD + c * (UC_W + GAP_X), sys_y + HEAD + r * (UC_H + GAP_Y), UC_W, UC_H)
    right_x = sys_x + sys_w + 140
    apos = {}
    for side in ("left", "right"):
        group = [a for a in actors if sides[a["id"]] == side]
        want = []
        for a in group:
            ys = [pos[l["uc"]][1] + UC_H / 2 for l in spec.get("links", []) if l["actor"] == a["id"] and l["uc"] in pos]
            want.append((sum(ys) / len(ys) if ys else sys_y + sys_h / 2, a))
        want.sort(key=lambda t: t[0])
        last = None
        for cy, a in want:
            y = cy - ACT_H / 2
            if last is not None and y < last + ACT_H + ACT_GAP + 30:
                y = last + ACT_H + ACT_GAP + 30
            last = y
            apos[a["id"]] = ((left_x if side == "left" else right_x), y, ACT_W, ACT_H)
    total_w = right_x + ACT_W + 120
    total_h = max(sys_y + sys_h, max((p[1] + ACT_H for p in apos.values()), default=0)) + 70
    return pos, apos, (sys_x, sys_y, sys_w, sys_h), (total_w, total_h)


def edges(spec):
    out = []
    for l in spec.get("links", []):
        out.append(("assoc", l["actor"], l["uc"], ""))
    for e in spec.get("includes", []):
        out.append(("include", e["from"], e["to"], "«include»"))
    for e in spec.get("extends", []):
        out.append(("extend", e["from"], e["to"], "«extend»"))
    for a in spec["actors"]:
        if a.get("parent"):
            out.append(("general", a["id"], a["parent"], ""))
    return out


def check(spec):
    ids = [x["id"] for x in spec["actors"]] + [x["id"] for x in spec["usecases"]]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit("duplicate ids: %s" % sorted(dup))
    idset = set(ids)
    for kind, a, b, _ in edges(spec):
        for r in (a, b):
            if r not in idset:
                raise SystemExit("%s references unknown id %s" % (kind, r))
    linked = {l["uc"] for l in spec.get("links", [])} | {e["to"] for e in spec.get("includes", [])} | {e["from"] for e in spec.get("extends", [])}
    orphans = [u["id"] for u in spec["usecases"] if u["id"] not in linked]
    if orphans:
        print("WARN use cases with no actor link and not included/extending:", orphans)
    if len(spec["usecases"]) > 20:
        print("WARN more than 20 use cases: split the diagram (per role or per feature group)")


EDGE_STYLE = {
    "assoc": "endArrow=none;html=1;rounded=0;",
    "include": "endArrow=open;endFill=0;dashed=1;html=1;rounded=0;",
    "extend": "endArrow=open;endFill=0;dashed=1;html=1;rounded=0;",
    "general": "endArrow=block;endFill=0;html=1;rounded=0;",
}


def to_drawio(spec, pos, apos, sysbox, size):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    cells.append('<mxCell id="title" value="%s" style="text;html=1;fontSize=18;fontStyle=1;align=left;" vertex="1" parent="1"><mxGeometry x="40" y="10" width="600" height="30" as="geometry"/></mxCell>' % escape(spec.get("title", "")))
    sx, sy, sw, sh = sysbox
    cells.append('<mxCell id="system" value="%s" style="rounded=0;whiteSpace=wrap;html=1;fillColor=none;verticalAlign=top;fontStyle=1;fontSize=14;" vertex="1" parent="1"><mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>' % (escape(spec.get("system", "System")), sx, sy, sw, sh))
    for a in spec["actors"]:
        x, y, w, h = apos[a["id"]]
        cells.append('<mxCell id="%s" value="%s" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;" vertex="1" parent="1"><mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>' % (a["id"], escape(a["name"]), x, y, w, h))
    for u in spec["usecases"]:
        x, y, w, h = pos[u["id"]]
        cells.append('<mxCell id="%s" value="%s" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1"><mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>' % (u["id"], escape(u["name"]), x, y, w, h))
    for i, (kind, a, b, label) in enumerate(edges(spec)):
        cells.append('<mxCell id="e%d" value="%s" style="%s" edge="1" source="%s" target="%s" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>' % (i + 1, escape(label), EDGE_STYLE[kind], a, b))
    w, h = size
    return ('<mxfile host="Electron" version="26.0.0"><diagram id="ucd" name="%s"><mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0"><root>%s</root></mxGraphModel></diagram></mxfile>'
            % (escape(spec.get("title", "UCD")), max(w, 827), max(h, 600), "".join(cells)))


def clip_ellipse(cx, cy, rx, ry, tx, ty):
    dx, dy = tx - cx, ty - cy
    d = math.hypot(dx / rx, dy / ry) or 1
    return cx + dx / d, cy + dy / d


def clip_rect(cx, cy, hw, hh, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    k = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return cx + dx * k, cy + dy * k


def to_svg(spec, pos, apos, sysbox, size):
    w, h = size
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" font-family="Arial, sans-serif" font-size="13">' % (w, h, w, h),
         '<defs><marker id="op" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10" fill="none" stroke="#333"/></marker>'
         '<marker id="tri" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#fff" stroke="#333"/></marker></defs>',
         '<title>%s</title><rect width="100%%" height="100%%" fill="#fff"/>' % escape(spec.get("title", "")),
         '<text x="40" y="30" font-size="18" font-weight="bold">%s</text>' % escape(spec.get("title", ""))]
    sx, sy, sw, sh = sysbox
    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#333"/><text x="%d" y="%d" text-anchor="middle" font-weight="bold" font-size="14">%s</text>' % (sx, sy, sw, sh, sx + sw / 2, sy + 28, escape(spec.get("system", "System"))))
    center = {}
    for u in spec["usecases"]:
        x, y, ww, hh = pos[u["id"]]
        center[u["id"]] = ("e", x + ww / 2, y + hh / 2, ww / 2, hh / 2)
    for a in spec["actors"]:
        x, y, ww, hh = apos[a["id"]]
        center[a["id"]] = ("a", x + ww / 2, y + hh / 2, ww / 2, hh / 2)
    for kind, a, b, label in edges(spec):
        ka, xa, ya, rxa, rya = center[a]
        kb, xb, yb, rxb, ryb = center[b]
        p1 = clip_ellipse(xa, ya, rxa, rya, xb, yb) if ka == "e" else clip_rect(xa, ya, rxa, rya, xb, yb)
        p2 = clip_ellipse(xb, yb, rxb, ryb, xa, ya) if kb == "e" else clip_rect(xb, yb, rxb, ryb, xa, ya)
        dash = ' stroke-dasharray="6,4"' if kind in ("include", "extend") else ""
        mk = ' marker-end="url(#op)"' if dash else (' marker-end="url(#tri)"' if kind == "general" else "")
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#333"%s%s/>' % (p1[0], p1[1], p2[0], p2[1], dash, mk))
        if label:
            o.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11" fill="#333" stroke="#fff" stroke-width="4" paint-order="stroke">%s</text>' % ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 4, escape(label)))
    for u in spec["usecases"]:
        _, cx, cy, rx, ry = center[u["id"]]
        o.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#dae8fc" stroke="#6c8ebf"/><text x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (cx, cy, rx, ry, cx, cy + 4, escape(u["name"])))
    for a in spec["actors"]:
        _, cx, cy, rx, ry = center[a["id"]]
        top = cy - ry
        o.append('<g stroke="#333" fill="none"><circle cx="%.1f" cy="%.1f" r="8" fill="#fff"/><line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/></g><text x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                 % (cx, top + 8, cx, top + 16, cx, top + 42, cx - 16, top + 26, cx + 16, top + 26, cx, top + 42, cx - 14, top + 66, cx, top + 42, cx + 14, top + 66, cx, cy + ry + 16, escape(a["name"])))
    o.append("</svg>")
    return "\n".join(o)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    spec = json.load(open(argv[1], encoding="utf-8"))
    check(spec)
    pos, apos, sysbox, size = layout(spec)
    open(argv[2], "w", encoding="utf-8").write(to_drawio(spec, pos, apos, sysbox, size))
    print("wrote", argv[2])
    if "--svg" in argv:
        p = argv[argv.index("--svg") + 1]
        open(p, "w", encoding="utf-8").write(to_svg(spec, pos, apos, sysbox, size))
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
