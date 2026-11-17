#!/usr/bin/env python3
"""Validate screen specifications (SRS section 3) written in Markdown.

Usage: python validate-screen-spec.py <file-or-dir> [--catalog catalog.md] [--strict]
Each screen starts at a heading whose text begins with a number `3.x` (any heading level).
Required per screen: purpose paragraph, `Mapped Use Case(s)` with UC-nn items (or "Non-UI"),
a line "The <name> screen allows the <role> to:" followed by bullets, and a
`Field Description` table (Field Name | Description) with a non-empty description per row.
--catalog  Markdown/text file listing the UC catalog ids (UC-nn); unknown ids are errors and
           catalog UCs that no screen maps are reported as warnings.
"""
import os
import re
import sys


def md_files(p):
    if os.path.isdir(p):
        return sorted(os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs if f.lower().endswith(".md"))
    return [p]


def screens(lines):
    idx = [i for i, l in enumerate(lines) if re.match(r"#{2,6}\s+3\.\d", l)]
    for n, i in enumerate(idx):
        yield lines[i].lstrip("# ").strip(), lines[i:(idx[n + 1] if n + 1 < len(idx) else len(lines))]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    catalog = None
    if "--catalog" in argv:
        catalog = set(re.findall(r"\bUC-\d+\b", open(argv[argv.index("--catalog") + 1], encoding="utf-8").read()))
    errors = warns = 0
    mapped = set()
    count = 0
    containers = 0
    for f in md_files(argv[1]):
        for title, block in screens(open(f, encoding="utf-8").read().split("\n")):
            body_lines = [x for x in block[1:] if x.strip()]
            if not body_lines:
                containers += 1            # group heading with sub-screens only
                continue
            count += 1
            text = "\n".join(block)
            errs, wrns = [], []
            body = [l for l in block[1:] if l.strip()]
            if not body or re.match(r"(\*\*|#|-|\|)", body[0]):
                errs.append("missing purpose paragraph right after the heading")
            m = re.search(r"Mapped Use Case\(s\)[^\n]*\n((?:\s*[-*][^\n]*\n?)+)|Mapped Use Case\(s\):\**\s*([^\n]+)", text)
            ids = set(re.findall(r"\bUC-\d+\b", m.group(0))) if m else set()
            if not m:
                errs.append("missing 'Mapped Use Case(s)'")
            elif not ids and "non-ui" not in m.group(0).lower():
                errs.append("'Mapped Use Case(s)' lists no UC-nn (write Non-UI if none)")
            mapped |= ids
            if catalog is not None:
                for u in sorted(ids - catalog):
                    errs.append("%s is not in the UC catalog" % u)
            if not re.search(r"allows the [^\n]+? to:\s*\n(?:\s*[-*][^\n]+\n?)+", text, re.I):
                errs.append("missing 'The <screen> screen allows the <role> to:' with bullet list")
            fd = re.search(r"Field Description[^\n]*\n+((?:\|[^\n]*\n?)+)", text)
            if not fd:
                errs.append("missing 'Field Description' table")
            else:
                rows = [r for r in fd.group(1).strip().split("\n") if r.strip().startswith("|")]
                data = [r for r in rows[2:]] if len(rows) > 2 else []
                if not data:
                    errs.append("Field Description table has no rows")
                for r in data:
                    cells = [c.strip() for c in r.strip().strip("|").split("|")]
                    if len(cells) < 2 or not cells[0] or not cells[1]:
                        errs.append("Field Description row incomplete: %s" % r.strip()[:50])
                    elif not re.match(r"[A-Z][a-z]+(s|es)\b", cells[1]) or re.match(r"(This|The|Its|Is|Has|Was|Does|Yes|Default)\b", cells[1]):
                        wrns.append("description of '%s' should start with a verb (Allows/Displays/Submits...)" % cells[0])
            if re.search(r"#[0-9a-fA-F]{6}\b|\b\d+\s?px\b", text):
                wrns.append("layout detail (color/pixel) found; a screen spec describes behavior, not styling")
            print(title)
            for e in errs:
                print("  ERROR", e)
            for w in wrns:
                print("  WARN ", w)
            errors += len(errs)
            warns += len(wrns)
    if count == 0:
        print("ERROR no screen found (heading starting with 3.x expected)")
        return 1
    if catalog is not None:
        print("Catalog coverage")
        for u in sorted(catalog - mapped):
            print("WARN  %s in catalog is mapped by no screen (mark Non-UI in the UC if intended)" % u)
            warns += 1
    bad = errors or ("--strict" in argv and warns)
    print("FAIL" if bad else "PASS", "- %d screen(s) (%d group headings skipped), %d error(s), %d warning(s)" % (count, containers, errors, warns))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
