#!/usr/bin/env python3
"""Audit a whole SRS Word file: import it, run every SRS validator, add cross-section checks, write a report.

Usage: python audit_srs.py in.docx [workdir] [--max N]
  workdir  where the imported Markdown parts and audit-report.md are written (default: <docx name>_audit next to the file)
  --max N  findings listed per check in the report (default 15)
The Word file is only read. Needs the sibling skills (uc-fpt, srs-br-msg, srs-screen-spec, srs-overall, srs-nfr)
installed next to srs-writer.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # folder that holds all skills
sys.path.insert(0, HERE)
import import_docx  # noqa: E402


def group_lines(items, mx):
    """Group findings of the same kind: '<count> x <rule> (e.g. unit, unit, unit)'. Singletons keep their full text."""
    groups, order, plain = {}, [], []
    for it in items:
        m = re.match(r"\[(.*?)\]\s*(.*)", it)
        if not m:
            plain.append("- " + it)          # not tied to a unit (UC/screen): keep each line as is
            continue
        unit, msg = m.group(1), m.group(2)
        key = re.sub(r"\d+", "N", re.sub(r"'[^']*'", "'..'", msg))[:110]
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append((unit, msg))
    out = []
    for key in sorted(order, key=lambda k: -len(groups[k])):
        g = groups[key]
        if len(g) == 1:
            unit, msg = g[0]
            out.append("- %s%s" % ("[%s] " % unit if unit else "", msg))
        else:
            units = []
            for u, _ in g:
                if u and u not in units:
                    units.append(u)
            out.append("- **%d x** %s" % (len(g), g[0][1] if "'" not in g[0][1] else re.sub(r"'[^']*'", "'...'", g[0][1])))
            out.append("  - e.g. %s%s" % (", ".join(units[:3]), "" if len(units) <= 3 else ", ... (%d units)" % len(units)))
    return (out[:mx * 2]) + plain[:mx]


def run(script, args):
    path = os.path.join(ROOT, script)
    if not os.path.exists(path):
        return None, "skill not found: " + script
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, "-X", "utf8", path] + args, capture_output=True, text=True, encoding="utf-8", env=env)
    return p.returncode, (p.stdout + p.stderr)


def findings(out):
    """ERROR/WARN lines, each prefixed with the unit (UC or screen title) printed above it."""
    errs, warns, title = [], [], ""
    for line in out.split("\n"):
        if line and not line[0].isspace() and not line.startswith(("ERROR", "WARN", "PASS", "FAIL", "==", "registry", "actors")):
            title = line.split(":")[0].strip()[:70]
        m = re.match(r"\s*(ERROR|WARN)\s+(.*)", line)
        if m:
            item = ("[%s] %s" % (title, m.group(2)) if title else m.group(2)).strip()
            (errs if m.group(1) == "ERROR" else warns).append(item)
    return errs, warns


def norm(t):
    return re.sub(r"\s+", " ", t.strip().lower())


def cross_checks(work):
    errs, warns = [], []
    cat = {}
    p = os.path.join(work, "catalog.md")
    if os.path.exists(p):
        for l in open(p, encoding="utf-8").read().split("\n")[2:]:
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) >= 2 and c[0].startswith("UC-"):
                cat[c[0]] = c[1]
    specs = []
    d = os.path.join(work, "02-usecases")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        for l in open(os.path.join(d, f), encoding="utf-8"):
            m = re.match(r"#{3,6}\s+2\.\d+\.\d+\s+(.*)", l)
            if m:
                specs.append(m.group(1).strip())
    by_name = {}
    for uid, name in cat.items():
        by_name.setdefault(norm(name), []).append(uid)
    spec_names = [norm(s) for s in specs]
    for name, ids in by_name.items():
        if len(ids) > 1:
            warns.append("catalog name used by several UCs: %s (%s)" % (name, ", ".join(ids)))
    for uid, name in cat.items():
        if norm(name) not in spec_names:
            errs.append("%s '%s' is in the catalog but has no section 2 spec with that name" % (uid, name))
    for s in specs:
        if norm(s) not in by_name:
            errs.append("section 2 spec '%s' is not in the UC catalog" % s)
    if len(cat) != len(specs):
        warns.append("catalog has %d UCs, section 2 has %d specs" % (len(cat), len(specs)))
    return errs, warns, len(cat), len(specs)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    src = argv[1]
    pos = [a for a in argv[2:] if not a.startswith("--")]
    mx = int(argv[argv.index("--max") + 1]) if "--max" in argv else 15
    if "--max" in argv and pos and pos[-1] == argv[argv.index("--max") + 1]:
        pos = pos[:-1]
    work = pos[0] if pos else os.path.splitext(os.path.abspath(src))[0] + "_audit"
    os.makedirs(work, exist_ok=True)
    import io
    buf = io.StringIO()
    old, sys.stdout = sys.stdout, buf
    try:
        import_docx.main(["import_docx.py", src, work])
    finally:
        sys.stdout = old
    import_summary = buf.getvalue().strip()
    j = lambda *p: os.path.join(work, *p)
    reg = [j("registers", "br.md"), j("registers", "msg.md")]
    checks = [
        ("UC specs (uc-fpt)", "uc-fpt/scripts/validate-uc-fpt.py", [j("02-usecases"), "--actors", j("actors.md"), "--registry"] + reg),
        ("BR/MSG references (srs-br-msg)", "srs-br-msg/scripts/check-refs.py", ["--registry"] + reg + ["--scan", j("02-usecases"), j("03-screens.md"), j("04-nfr.md"), j("01-overall.md")]),
        ("Screen specs (srs-screen-spec)", "srs-screen-spec/scripts/validate-screen-spec.py", [j("03-screens.md"), "--catalog", j("catalog.md")]),
        ("Overall tables (srs-overall)", "srs-overall/scripts/check-overall.py", [j("01-overall.md"), "--screens", j("03-screens.md")]),
        ("NFR (srs-nfr)", "srs-nfr/scripts/validate-nfr.py", [j("04-nfr.md")]),
    ]
    report = ["# SRS audit report", "", "Source: `%s`" % src, "", "```", import_summary, "```", ""]
    summary = []
    for title, script, args in checks:
        code, out = run(script, args)
        if code is None:
            report += ["## %s" % title, "", out, ""]
            summary.append((title, "n/a", "n/a"))
            continue
        errs, warns = findings(out)
        last = [l for l in out.strip().split("\n") if l.startswith(("PASS", "FAIL"))]
        summary.append((title, len(errs), len(warns)))
        report += ["## %s: %s" % (title, last[-1] if last else "see output"), ""]
        for tag, lst in (("ERROR", errs), ("WARN", warns)):
            if lst:
                report.append("%s (%d, grouped by kind):" % (tag, len(lst)))
                report += group_lines(lst, mx)
                report.append("")
    errs, warns, ncat, nspec = cross_checks(work)
    summary.append(("Catalog vs section 2 (cross-check)", len(errs), len(warns)))
    report += ["## Catalog vs section 2: %d catalog UCs, %d specs" % (ncat, nspec), ""]
    for tag, lst in (("ERROR", errs), ("WARN", warns)):
        if lst:
            report.append("%s (%d):" % (tag, len(lst)))
            report += ["- " + x for x in lst[:mx]]
            report.append("")
    eh = j("empty-headings.txt")
    n_empty = len(open(eh, encoding="utf-8").read().strip().split("\n")) if os.path.exists(eh) else 0
    summary.append(("Word structure: empty heading paragraphs", 0, n_empty))
    if n_empty:
        report += ["## Word structure: %d empty heading paragraphs" % n_empty, "", "Empty headings appear as blank entries in the navigation pane. Delete them in Word.", ""]
        report += ["- " + l for l in open(eh, encoding="utf-8").read().strip().split("\n")[:mx]] + [""]
    basis = {
        "UC specs": "Standards (UC practice: one primary actor, secondary = external objects, Description form, flows); layout is a convention",
        "BR/MSG": "Standards (every cited id registered, unique ids); message-type vocabulary is a convention",
        "Screen specs": "Convention inferred from this document (screen layout); UC mapping is a standard traceability rule",
        "Overall tables": "Standards (consistent names and ids across sections); table layouts are conventions",
        "NFR": "Standards (unique ids, 'shall', measurable); id prefixes are a convention",
        "Catalog vs": "Standards (traceability between catalog and specs)",
        "Word structure": "Document hygiene",
    }
    pick = lambda t: next((v for k, v in basis.items() if t.startswith(k)), "")
    head = (["## Summary", "", "The document under audit is evidence, not the standard: findings marked Standards apply to any SRS; "
             "findings marked Convention only say that the file differs from the layout inferred from it, and the author decides.", "",
             "| Check | Errors | Warnings | Basis |", "|---|---|---|---|"] +
            ["| %s | %s | %s | %s |" % (t, e, w, pick(t)) for t, e, w in summary] + [""])
    report = report[:7] + head + report[7:]
    rp = j("audit-report.md")
    open(rp, "w", encoding="utf-8").write("\n".join(report))
    print(import_summary)
    print("%-45s %7s %9s" % ("Check", "Errors", "Warnings"))
    for t, e, w in summary:
        print("%-45s %7s %9s" % (t, e, w))
    print("report:", rp)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
