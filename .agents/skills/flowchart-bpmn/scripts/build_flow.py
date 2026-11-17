#!/usr/bin/env python3
"""Build a flowchart or a BPMN-style swimlane process (.drawio and optional .svg) from JSON.

Usage: python build_flow.py spec.json out.drawio [--svg out.svg]

Spec:
{
  "title": "Create lesson plan",
  "type": "bpmn",                      # "bpmn" (lanes, left-to-right) or "flowchart" (top-down)
  "lanes": [{"id": "teacher", "name": "Teacher"}, {"id": "system", "name": "System"}],
  "nodes": [
    {"id": "s",  "type": "start",   "name": "Start",          "lane": "teacher"},
    {"id": "t1", "type": "task",    "name": "Select lesson",  "lane": "teacher"},
    {"id": "g1", "type": "gateway", "name": "Generated?",     "lane": "system"},
    {"id": "e",  "type": "end",     "name": "Done",           "lane": "system"}
  ],
  "flows": [{"from": "s", "to": "t1"}, {"from": "g1", "to": "e", "label": "Yes"}]
}
Node types: start, end, end-error, task, subprocess, gateway, datastore, document.
Loops (retry) are allowed: flows pointing back to an earlier node are drawn as back edges.
"""
import json
import sys
from xml.sax.saxutils import escape

SIZE = {"start": (36, 36), "end": (36, 36), "end-error": (36, 36), "task": (150, 60), "subprocess": (150, 60),
        "gateway": (50, 50), "datastore": (110, 60), "document": (130, 60)}
STYLE = {
    "start": "ellipse;aspect=fixed;html=1;fillColor=#d5e8d4;strokeColor=#82b366;verticalLabelPosition=bottom;verticalAlign=top;",
    "end": "ellipse;aspect=fixed;html=1;strokeWidth=3;fillColor=#f5f5f5;strokeColor=#333333;verticalLabelPosition=bottom;verticalAlign=top;",
    "end-error": "ellipse;aspect=fixed;html=1;strokeWidth=3;fillColor=#f8cecc;strokeColor=#b85450;verticalLabelPosition=bottom;verticalAlign=top;",
    "task": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;arcSize=12;",
    "subprocess": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;arcSize=12;strokeWidth=2;dashed=0;",
    "gateway": "rhombus;html=1;fillColor=#fff2cc;strokeColor=#d6b656;verticalLabelPosition=top;verticalAlign=bottom;",
    "datastore": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=12;fillColor=#e1d5e7;strokeColor=#9673a6;",
    "document": "shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#f5f5f5;strokeColor=#666666;",
}
GAP_X, GAP_Y, LANE_HEAD, MARGIN = 70, 40, 30, 40


def validate(spec):
    nodes = spec["nodes"]
    ids = [n["id"] for n in nodes]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit("duplicate node ids: %s" % sorted(dup))
    for n in nodes:
        if n["type"] not in SIZE:
            raise SystemExit("unknown node type %r (allowed: %s)" % (n["type"], ", ".join(SIZE)))
    idset = set(ids)
    for f in spec["flows"]:
        if f["from"] not in idset or f["to"] not in idset:
            raise SystemExit("flow references unknown node: %s -> %s" % (f["from"], f["to"]))
    if spec.get("type", "bpmn") == "bpmn":
        lanes = {l["id"] for l in spec.get("lanes", [])}
        if not lanes:
            raise SystemExit("bpmn needs lanes (or use type flowchart)")
        for n in nodes:
            if n.get("lane") not in lanes:
                raise SystemExit("node %s has missing/unknown lane" % n["id"])
    starts = [n for n in nodes if n["type"] == "start"]
    ends = [n for n in nodes if n["type"] in ("end", "end-error")]
    if len(starts) != 1:
        print("WARN expected exactly one start event, found %d" % len(starts))
    if not ends:
        print("WARN no end event")
    out_deg = {i: 0 for i in ids}
    in_deg = {i: 0 for i in ids}
    for f in spec["flows"]:
        out_deg[f["from"]] += 1
        in_deg[f["to"]] += 1
    for n in nodes:
        if n["type"] == "gateway" and out_deg[n["id"]] >= 2:
            unl = [f for f in spec["flows"] if f["from"] == n["id"] and not f.get("label")]
            if unl:
                print("WARN gateway %s has outgoing flows without a condition label" % n["id"])
        if n["type"] not in ("start", "datastore", "document") and in_deg[n["id"]] == 0:
            print("WARN node %s has no incoming flow" % n["id"])
        if n["type"] not in ("end", "end-error", "datastore", "document") and out_deg[n["id"]] == 0:
            print("WARN node %s has no outgoing flow (dead end)" % n["id"])
    if len(nodes) > 25:
        print("WARN %d nodes: split into sub-processes" % len(nodes))


def ranks(spec):
    """Longest-path rank, ignoring back edges found by DFS."""
    adj = {n["id"]: [] for n in spec["nodes"]}
    for f in spec["flows"]:
        adj[f["from"]].append(f["to"])
    back = set()
    state = {}

    def dfs(u):
        state[u] = 1
        for v in adj[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2

    roots = [n["id"] for n in spec["nodes"] if n["type"] == "start"] + [n["id"] for n in spec["nodes"]]
    for r in roots:
        if r not in state:
            dfs(r)
    rank = {n["id"]: 0 for n in spec["nodes"]}
    for _ in range(len(rank) + 1):
        changed = False
        for f in spec["flows"]:
            if (f["from"], f["to"]) in back:
                continue
            if rank[f["to"]] < rank[f["from"]] + 1:
                rank[f["to"]] = rank[f["from"]] + 1
                changed = True
        if not changed:
            break
    return rank, back


def layout(spec):
    rank, back = ranks(spec)
    nodes = spec["nodes"]
    pos = {}
    if spec.get("type", "bpmn") == "bpmn":
        lanes = spec["lanes"]
        maxr = max(rank.values())
        colw = max(SIZE[n["type"]][0] for n in nodes) + GAP_X
        # per lane: stacking of nodes sharing a rank
        lane_rows = {}
        slot = {}
        for l in lanes:
            counts = {}
            for n in nodes:
                if n["lane"] == l["id"]:
                    r = rank[n["id"]]
                    slot[n["id"]] = counts.get(r, 0)
                    counts[r] = counts.get(r, 0) + 1
            lane_rows[l["id"]] = max(counts.values()) if counts else 1
        y = MARGIN + 30
        lane_box = {}
        for l in lanes:
            h = lane_rows[l["id"]] * (80 + GAP_Y) + 20
            lane_box[l["id"]] = (MARGIN, y, LANE_HEAD + (maxr + 1) * colw + MARGIN, h)
            y += h
        for n in nodes:
            w, h = SIZE[n["type"]]
            lx, ly, lw, lh = lane_box[n["lane"]]
            cx = lx + LANE_HEAD + MARGIN / 2 + rank[n["id"]] * colw + (colw - GAP_X) / 2
            cy = ly + 20 + slot[n["id"]] * (80 + GAP_Y) + 40
            pos[n["id"]] = (cx - w / 2, cy - h / 2, w, h)
        total = (lane_box[lanes[0]["id"]][2] + 2 * MARGIN, y + MARGIN)
        return pos, lane_box, total, back
    # flowchart: top-down
    rowh = 60 + GAP_Y + 30
    byrank = {}
    for n in nodes:
        byrank.setdefault(rank[n["id"]], []).append(n)
    maxcount = max(len(v) for v in byrank.values())
    colw = 150 + GAP_X + 20
    width = maxcount * colw + 2 * MARGIN
    for r, group in byrank.items():
        for i, n in enumerate(group):
            w, h = SIZE[n["type"]] if n["type"] != "gateway" else (150, 70)
            cx = MARGIN + (width - 2 * MARGIN) / 2 + (i - (len(group) - 1) / 2) * colw
            pos[n["id"]] = (cx - w / 2, MARGIN + 30 + r * rowh, w, h)
    return pos, {}, (width, MARGIN * 2 + 30 + (max(byrank) + 1) * rowh), back


def to_drawio(spec, pos, lane_box, total, back):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>',
             '<mxCell id="title" value="%s" style="text;html=1;fontSize=18;fontStyle=1;align=left;" vertex="1" parent="1"><mxGeometry x="40" y="8" width="700" height="30" as="geometry"/></mxCell>' % escape(spec.get("title", ""))]
    for l in spec.get("lanes", []) if lane_box else []:
        x, y, w, h = lane_box[l["id"]]
        cells.append('<mxCell id="lane_%s" value="%s" style="swimlane;horizontal=0;startSize=%d;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;html=1;" vertex="1" parent="1"><mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>' % (l["id"], escape(l["name"]), LANE_HEAD, x, y, w, h))
    for n in spec["nodes"]:
        x, y, w, h = pos[n["id"]]
        label = escape(n.get("name", ""))
        cells.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1"><mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>' % (n["id"], label, STYLE[n["type"]], x, y, w, h))
    for i, f in enumerate(spec["flows"]):
        dashed = "dashed=1;" if f.get("style") == "dashed" else ""
        cells.append('<mxCell id="f%d" value="%s" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;%s" edge="1" source="%s" target="%s" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>' % (i + 1, escape(f.get("label", "")), dashed, f["from"], f["to"]))
    w, h = total
    return ('<mxfile host="Electron" version="26.0.0"><diagram id="flow" name="%s"><mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0"><root>%s</root></mxGraphModel></diagram></mxfile>'
            % (escape(spec.get("title", "Flow")), max(int(w), 827), max(int(h), 600), "".join(cells)))


def to_svg(spec, pos, lane_box, total, back):
    w, h = total
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" font-family="Arial, sans-serif" font-size="12">' % (w, h, w, h),
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>',
         '<title>%s</title><rect width="100%%" height="100%%" fill="#fff"/><text x="40" y="26" font-size="18" font-weight="bold">%s</text>' % (escape(spec.get("title", "")), escape(spec.get("title", "")))]
    for l in spec.get("lanes", []) if lane_box else []:
        x, y, lw, lh = lane_box[l["id"]]
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#f5f5f5" stroke="#666"/><rect x="%d" y="%d" width="%d" height="%d" fill="#e8e8e8" stroke="#666"/><text transform="translate(%d,%d) rotate(-90)" text-anchor="middle" font-weight="bold">%s</text>'
                 % (x, y, lw, lh, x, y, LANE_HEAD, lh, x + 19, y + lh / 2, escape(l["name"])))

    rank, backset = ranks(spec)
    bpmn = spec.get("type", "bpmn") == "bpmn"
    floor_y = max(p[1] + p[3] for p in pos.values())
    right_x = max(p[0] + p[2] for p in pos.values())
    for f in spec["flows"]:
        a, b2 = f["from"], f["to"]
        ax, ay, aw, ah = pos[a]
        bx, by, bw, bh = pos[b2]
        acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        isback = (a, b2) in backset
        gw = next(n for n in spec["nodes"] if n["id"] == a)["type"] == "gateway"
        if bpmn and not isback and rank[b2] > rank[a] and gw and abs(bcy - acy) > 1:
            p1 = (acx, ay + ah) if bcy > acy else (acx, ay)
            p2 = (bx, bcy)
            pts = [p1, (acx, bcy), p2]
        elif bpmn and not isback and rank[b2] > rank[a]:
            p1, p2 = (ax + aw, acy), (bx, bcy)
            mx = (p1[0] + p2[0]) / 2
            pts = [p1, (mx, p1[1]), (mx, p2[1]), p2]
        elif bpmn and isback:
            yb = max(ay + ah, by + bh) + 22
            p1, p2 = (acx, ay + ah), (bcx, by + bh)
            pts = [p1, (acx, yb), (bcx, yb), p2]
        elif bpmn:
            if bcy >= acy:
                p1, p2 = (acx, ay + ah), (bcx, by)
            else:
                p1, p2 = (acx, ay), (bcx, by + bh)
            pts = [p1, p2]
        elif not isback:
            p1, p2 = (acx, ay + ah), (bcx, by)
            my = (p1[1] + p2[1]) / 2
            pts = [p1, (p1[0], my), (p2[0], my), p2]
        else:
            xr = right_x + 20
            p1, p2 = (ax + aw, acy), (bx + bw, bcy)
            pts = [p1, (xr, p1[1]), (xr, p2[1]), p2]
        dedup = [pts[0]]
        for q in pts[1:]:
            if abs(q[0] - dedup[-1][0]) > 0.5 or abs(q[1] - dedup[-1][1]) > 0.5:
                dedup.append(q)
        d = "M" + " L".join("%.1f,%.1f" % q for q in dedup)
        o.append('<path d="%s" fill="none" stroke="#333" marker-end="url(#ar)"/>' % d)
        if f.get("label"):
            segs = list(zip(dedup, dedup[1:])) or [(dedup[0], dedup[0])]
            q1, q2 = max(segs, key=lambda sg: abs(sg[0][0] - sg[1][0]) + abs(sg[0][1] - sg[1][1]))
            vertical = abs(q1[0] - q2[0]) < 1
            o.append('<text x="%.1f" y="%.1f" text-anchor="%s" font-size="11" stroke="#fff" stroke-width="4" paint-order="stroke">%s</text>' % ((q1[0] + q2[0]) / 2 + (6 if vertical else 0), (q1[1] + q2[1]) / 2 - (0 if vertical else 5), "start" if vertical else "middle", escape(f["label"])))
    for n in spec["nodes"]:
        x, y, ww, hh = pos[n["id"]]
        cx, cy = x + ww / 2, y + hh / 2
        t = n["type"]
        name = escape(n.get("name", ""))
        if t == "task" or t == "subprocess":
            o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="8" fill="#dae8fc" stroke="#6c8ebf" stroke-width="%d"/>' % (x, y, ww, hh, 2 if t == "subprocess" else 1))
            words, lines, cur = n.get("name", "").split(), [], ""
            for wd in words:
                if len(cur) + len(wd) + 1 > 22 and cur:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            lines.append(cur)
            y0 = cy + 4 - (len(lines) - 1) * 7
            o.append('<text text-anchor="middle">%s</text>' % "".join('<tspan x="%.1f" y="%.1f">%s</tspan>' % (cx, y0 + i * 14, escape(ln)) for i, ln in enumerate(lines)))
        elif t == "gateway":
            o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fff2cc" stroke="#d6b656"/>' % (cx, y, x + ww, cy, cx, y + hh, x, cy))
            if spec.get("type", "bpmn") == "bpmn":
                o.append('<text x="%.1f" y="%.1f" text-anchor="middle">%s</text><text x="%.1f" y="%.1f" text-anchor="middle" font-weight="bold">X</text>' % (cx, y - 8, name, cx, cy + 5))
            else:
                o.append('<text x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (cx, cy + 4, name))
        elif t in ("start", "end", "end-error"):
            fill = {"start": "#d5e8d4", "end": "#f5f5f5", "end-error": "#f8cecc"}[t]
            stroke = {"start": "#82b366", "end": "#333", "end-error": "#b85450"}[t]
            o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" stroke="%s" stroke-width="%d"/><text x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (cx, cy, ww / 2, fill, stroke, 1 if t == "start" else 3, cx, y + hh + 14, name))
        else:
            o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="#e1d5e7" stroke="#9673a6"/><text x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (x, y, ww, hh, cx, cy + 4, name))
    o.append("</svg>")
    return "\n".join(o)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    spec = json.load(open(argv[1], encoding="utf-8"))
    validate(spec)
    pos, lane_box, total, back = layout(spec)
    open(argv[2], "w", encoding="utf-8").write(to_drawio(spec, pos, lane_box, total, back))
    print("wrote", argv[2])
    if "--svg" in argv:
        p = argv[argv.index("--svg") + 1]
        open(p, "w", encoding="utf-8").write(to_svg(spec, pos, lane_box, total, back))
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
