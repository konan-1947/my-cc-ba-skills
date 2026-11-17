#!/usr/bin/env python3
"""Import an existing SRS Word file (.docx) into the Markdown part formats used by the SRS skills.

Usage: python import_docx.py in.docx outdir

Writes:
  outdir/00-record.md            I. Record of Changes
  outdir/01-overall.md           section 1 (tables and headings)
  outdir/02-usecases/<group>.md  one file per section 2.x group, UC tables in the FPT format
  outdir/03-screens.md           section 3
  outdir/04-nfr.md               section 4
  outdir/05-appendix.md          section 5
  outdir/registers/br.md, msg.md the 5.1 and 5.2 tables
  outdir/catalog.md              the 1.3.2 UC catalog table
  outdir/media/                  images extracted from the document
Pure standard library. The Word file is only read, never modified.
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
STEP = re.compile(r"^Step\s*\d+\s*[_–—:-]")


def ptext(p):
    out = []
    for el in p.iter():
        if el.tag == W + "t" and el.text:
            out.append(el.text)
        elif el.tag in (W + "tab", W + "br"):
            out.append(" ")
    return re.sub(r"[ \t]+", " ", "".join(out)).strip()


def pinfo(p):
    ppr = p.find(W + "pPr")
    style, num = "", False
    if ppr is not None:
        st = ppr.find(W + "pStyle")
        style = st.get(W + "val", "") if st is not None else ""
        num = ppr.find(W + "numPr") is not None
    rids = [b.get(R + "embed") for b in p.iter(A + "blip") if b.get(R + "embed")]
    return style, num, rids


def table_rows(tbl):
    rows = []
    for tr in tbl.findall(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            paras = [ptext(p) for p in tc.findall(W + "p")]
            paras = [t for t in paras if t]
            cells.append(paras)
        rows.append(cells)
    return rows


def flatten(parent):
    """Body children in reading order, descending into content controls (w:sdt)."""
    for el in parent:
        if el.tag == W + "sdt":
            content = el.find(W + "sdtContent")
            if content is not None:
                yield from flatten(content)
        else:
            yield el


def esc(t):
    return t.replace("|", "\\|")


def md_cell(paras):
    return "<br>".join(esc(p) for p in paras)


def md_table(rows):
    rows = [r for r in rows if any(r)]
    if not rows:
        return []
    n = max(len(r) for r in rows)
    out = []
    for i, r in enumerate(rows):
        r = r + [[]] * (n - len(r))
        out.append("| " + " | ".join(md_cell(c) for c in r) + " |")
        if i == 0:
            out.append("|" + "---|" * n)
    return out + [""]


def uc_table(rows):
    """FPT-format UC table from the 4-column Word layout."""
    out = []
    for i, r in enumerate(rows):
        if not r or not r[0]:
            continue
        label = r[0][0]
        if i == 0 and len(r) >= 4:
            out.append("| **%s** | %s | **%s** | %s |" % (esc(label), md_cell(r[1]) or "None", esc(r[2][0] if r[2] else "Secondary Actors"), md_cell(r[3]) or "None"))
            out.append("|---|---|---|---|")
            continue
        content = [p for c in r[1:] for p in c]
        if label == "Normal Flow":
            lines = []
            if content:
                lines.append("**%s**" % esc(content[0]))
            for k, step in enumerate(content[1:], 1):
                step = re.sub(r"^\d+\s*[.)]\s+", "", step)          # the Word text may already carry "1. "
                lines.append("%d. %s" % (k, esc(step)))
            cell = "<br>".join(lines)
        elif label == "Alternative Flow":
            lines, first = [], True
            for t in content:
                if STEP.match(t):
                    if not first:
                        lines.append("")
                    lines.append("**%s**" % esc(t))
                    first = False
                else:
                    lines.append(esc(t))
            cell = "<br>".join(lines)
        else:
            cell = "<br>".join(esc(t) for t in content)
        out.append("| **%s** | %s |" % (esc(label), cell))
    return out + [""]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, outdir = argv[1], argv[2]
    z = zipfile.ZipFile(src)
    rels = {}
    if "word/_rels/document.xml.rels" in z.namelist():
        for rel in ET.fromstring(z.read("word/_rels/document.xml.rels")):
            rels[rel.get("Id")] = rel.get("Target")
    body = ET.fromstring(z.read("word/document.xml")).find(W + "body")
    os.makedirs(os.path.join(outdir, "registers"), exist_ok=True)
    os.makedirs(os.path.join(outdir, "02-usecases"), exist_ok=True)
    media_dir = os.path.join(outdir, "media")
    saved = {}

    def media(rid):
        target = rels.get(rid)
        if not target or "media/" not in target:
            return None
        name = os.path.basename(target)
        if name not in saved:
            os.makedirs(media_dir, exist_ok=True)
            open(os.path.join(media_dir, name), "wb").write(z.read("word/" + target.lstrip("/").replace("word/", "")))
            saved[name] = True
        return "media/" + name

    files = {}                 # relative path -> list of lines
    cur_section, cur_group = None, None
    in_toc = True
    last_heading = ""
    stats = {"tables": 0, "uc_tables": 0, "images": 0, "paragraphs": 0, "empty_headings": 0}
    empties = []

    def put(line_list, is_list=False):
        key = cur_section
        if key == "usecases":
            key = "02-usecases/%s.md" % (cur_group or "intro")
        buf = files.setdefault(key, [])
        if is_list and len(buf) > 1 and buf[-1] == "" and buf[-2].startswith("- "):
            buf.pop()                       # keep consecutive list items together
        buf.extend(line_list)

    for el in flatten(body):
        if el.tag == W + "p":
            style, num, rids = pinfo(el)
            text = ptext(el)
            m = re.fullmatch(r"Heading(\d)", style)
            if m and not text:
                stats["empty_headings"] = stats.get("empty_headings", 0) + 1
                empties.append("Heading%s after '%s'" % (m.group(1), last_heading))
                continue
            if m:
                lvl = int(m.group(1))
                in_toc = False
                if lvl == 1 and text.startswith("I. Record"):
                    cur_section, cur_group = "00-record.md", None
                elif lvl == 1:
                    cur_section, cur_group = "01-overall.md", None
                elif lvl == 2:
                    sec = re.match(r"(\d+)\.", text)
                    n = int(sec.group(1)) if sec else 0
                    cur_section = {1: "01-overall.md", 2: "usecases", 3: "03-screens.md", 4: "04-nfr.md", 5: "05-appendix.md"}.get(n, cur_section)
                    cur_group = None
                elif lvl == 3 and cur_section == "usecases":
                    cur_group = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()[:50] or "group"
                last_heading = text
                put(["%s %s" % ("#" * lvl, text), ""])
                continue
            if in_toc or cur_section is None:
                continue
            lines = []
            for rid in rids:
                path = media(rid)
                if path:
                    stats["images"] += 1
                    lines += ["![%s](%s)" % (last_heading, path), ""]
            if text:
                stats["paragraphs"] += 1
                lines += [("- " + text) if num else text, ""]
            put(lines, is_list=bool(num and text and not rids))
        elif el.tag == W + "tbl" and cur_section:
            rows = table_rows(el)
            stats["tables"] += 1
            if rows and rows[0] and rows[0][0] and rows[0][0][0] == "Primary Actors":
                stats["uc_tables"] += 1
                put(uc_table(rows))
            else:
                put(md_table(rows))
    for key, lines in files.items():
        path = os.path.join(outdir, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write("\n".join(lines).rstrip() + "\n")

    # registers and catalog: re-extract the specific tables from the written Markdown
    def grab(file, header_start, dest):
        p = os.path.join(outdir, file)
        if not os.path.exists(p):
            return 0
        lines = open(p, encoding="utf-8").read().split("\n")
        out, on, n = [], False, 0
        for ln in lines:
            if ln.startswith("|") and ln.lower().startswith(header_start):
                on = True
            if on:
                if ln.startswith("|"):
                    out.append(ln)
                    n += 1
                else:
                    break
        if out:
            open(os.path.join(outdir, dest), "w", encoding="utf-8").write("\n".join(out) + "\n")
        return max(n - 2, 0)

    nbr = grab("05-appendix.md", "| id | rule", "registers/br.md")
    nmsg = grab("05-appendix.md", "| # | message code", "registers/msg.md")
    ncat = grab("01-overall.md", "| id | use case |", "catalog.md")
    grab("01-overall.md", "| # | actor | description |", "actors.md")
    print("imported %s -> %s" % (src, outdir))
    print("paragraphs %(paragraphs)d | tables %(tables)d (UC tables %(uc_tables)d) | images %(images)d" % stats)
    print("registers: %d BR, %d MSG | catalog: %d UC | files: %d" % (nbr, nmsg, ncat, len(files)))
    if empties:
        open(os.path.join(outdir, "empty-headings.txt"), "w", encoding="utf-8").write("\n".join(empties) + "\n")
        print("empty heading paragraphs: %d (listed in empty-headings.txt)" % len(empties))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
