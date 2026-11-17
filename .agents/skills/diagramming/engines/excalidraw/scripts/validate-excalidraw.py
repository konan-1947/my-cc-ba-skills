#!/usr/bin/env python3
"""Validate a .excalidraw file: JSON shape, unique ids, Excalifont, bindings, overlaps.

Usage: python validate-excalidraw.py <file.excalidraw> [--strict]
Exit code 0 = no errors (warnings allowed unless --strict), 1 = errors.
"""
import json, sys

def main(path, strict=False):
    errors, warns = [], []
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as ex:
        print(f"ERROR invalid JSON: {ex}"); return 1
    if d.get("type") != "excalidraw": errors.append('top-level "type" must be "excalidraw"')
    els = d.get("elements")
    if not isinstance(els, list): print("ERROR missing elements array"); return 1
    ids = [e.get("id") for e in els]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: errors.append(f"duplicate ids: {sorted(dup)}")
    idset = set(ids)
    live = [e for e in els if not e.get("isDeleted")]
    for e in live:
        t, i = e.get("type"), e.get("id")
        for k in ("x", "y"):
            if not isinstance(e.get(k), (int, float)): errors.append(f"{i}: missing numeric {k}")
        if t == "text":
            if e.get("fontFamily") != 5: errors.append(f"{i}: text must use fontFamily 5 (Excalifont)")
            if (e.get("fontSize") or 0) < 16: warns.append(f"{i}: fontSize < 16 hurts readability")
            if e.get("containerId") and e["containerId"] not in idset: errors.append(f"{i}: containerId not found")
        if t in ("arrow", "line") and not e.get("points"): errors.append(f"{i}: {t} without points")
        if t == "arrow":
            for side in ("startBinding", "endBinding"):
                b = e.get(side)
                if b and b.get("elementId") not in idset: errors.append(f"{i}: {side} points to missing element")
            if not e.get("startBinding") and not e.get("endBinding"):
                warns.append(f"{i}: arrow not bound to any shape (will not follow when shapes move)")
        for gid in e.get("boundElements") or []:
            if gid.get("id") not in idset: errors.append(f"{i}: boundElements references missing id {gid.get('id')}")
    # overlap between top-level shapes (not nested in a frame/container, not text/arrow)
    shapes = [e for e in live if e["type"] in ("rectangle", "ellipse", "diamond") and not e.get("frameId")]
    def box(e): return e["x"], e["y"], e["x"] + e.get("width", 0), e["y"] + e.get("height", 0)
    def inside(a, b): return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]
    for n, a in enumerate(shapes):
        for b in shapes[n + 1:]:
            A, B = box(a), box(b)
            if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3] and not inside(A, B) and not inside(B, A):
                warns.append(f"{a['id']} overlaps {b['id']} (partial overlap)")
    if len(live) > 20: warns.append(f"{len(live)} elements: consider splitting the diagram (guideline <= 20)")
    for m in errors: print("ERROR", m)
    for m in warns: print("WARN ", m)
    bad = errors or (strict and warns)
    print(("FAIL" if bad else "PASS"), f"- {len(live)} elements, {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if bad else 0

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1], "--strict" in sys.argv))
