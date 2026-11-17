#!/usr/bin/env python3
"""Edit an existing SRS Word file in place (always writes a new file; the original is never touched).

Usage:
  python docx_edit.py replace  in.docx out.docx --find "IT Supporter" --replace "IT Support Staff" [--regex]
  python docx_edit.py fix-empty-headings in.docx out.docx
  python docx_edit.py add-uc   in.docx out.docx --after "2.2.3 Export Lesson Plan" --from uc.md

replace              text replacement that works across Word's split runs; keeps the formatting of the first affected run
fix-empty-headings   deletes Heading paragraphs that have no text (blank entries in the navigation pane)
add-uc               inserts a new UC (heading + 4-column table) after the UC named by --after, cloning that UC's own
                     heading and table so fonts, borders, shading and numbering match the document exactly.
                     uc.md uses the FPT format: a heading line (any # level, e.g. "#### 2.2.4 Duplicate Lesson Plan")
                     followed by the table rows of the uc-fpt template.
Other parts of the file (images, styles, headers, footers) are copied byte for byte. Update the table of contents
afterwards (srs-docx-builder/scripts/finalize-docx.ps1 or F9 in Word).
Pure standard library; the XML is edited as text, never re-serialized, so Word-specific attributes survive.
"""
import re
import sys
import zipfile
from xml.sax.saxutils import escape, unescape

P_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)
T_RE = re.compile(r"(<w:t(?: [^>]*)?>)(.*?)(</w:t>)", re.S)


def load(path):
    z = zipfile.ZipFile(path)
    return z, z.read("word/document.xml").decode("utf-8")


def save(src, out, doc, extra=None):
    extra = extra or {}
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.is_dir():
                continue
            if item.filename == "word/document.xml":
                data = doc.encode("utf-8")
            elif item.filename in extra:
                data = extra[item.filename].encode("utf-8")
            else:
                data = zin.read(item.filename)
            zout.writestr(item.filename, data)


def ptext(p):
    return "".join(unescape(m.group(2)) for m in T_RE.finditer(p))


def style_of(p):
    m = re.search(r'<w:pStyle w:val="([^"]+)"', p)
    return m.group(1) if m else ""


# ------------------------------------------------------------------ replace
def replace_in_paragraph(p, pattern, repl, regex):
    nodes = list(T_RE.finditer(p))
    if not nodes:
        return p, 0
    texts = [unescape(m.group(2)) for m in nodes]
    full = "".join(texts)
    pat = re.compile(pattern if regex else re.escape(pattern))
    matches = list(pat.finditer(full))
    if not matches:
        return p, 0
    starts, pos = [], 0
    for t in texts:
        starts.append(pos)
        pos += len(t)
    new = list(texts)
    for m in reversed(matches):
        a, b = m.start(), m.end()
        rep = m.expand(repl) if regex else repl
        if b <= a:
            continue
        first = next(i for i in range(len(starts) - 1, -1, -1) if starts[i] <= a)
        last = next(i for i in range(len(starts) - 1, -1, -1) if starts[i] <= b - 1)
        last = max(last, first)
        la, lb = a - starts[first], b - starts[last]
        if first == last:
            new[first] = new[first][:la] + rep + new[first][lb:]
        else:
            new[first] = new[first][:la] + rep
            for k in range(first + 1, last):
                new[k] = ""
            new[last] = new[last][lb:]
    out, last_end = [], 0
    for m, t in zip(nodes, new):
        out.append(p[last_end:m.start()])
        open_tag = m.group(1)
        if 'xml:space' not in open_tag:
            open_tag = open_tag[:-1] + ' xml:space="preserve">'
        out.append(open_tag + escape(t) + m.group(3))
        last_end = m.end()
    out.append(p[last_end:])
    return "".join(out), len(matches)


def op_replace(doc, find, repl, regex):
    total = 0

    def sub(m):
        nonlocal total
        p, n = replace_in_paragraph(m.group(0), find, repl, regex)
        total += n
        return p

    return P_RE.sub(sub, doc), total


# ------------------------------------------------------------------ empty headings
def op_fix_empty_headings(doc):
    removed = 0

    def sub(m):
        nonlocal removed
        p = m.group(0)
        if re.fullmatch(r"Heading\d", style_of(p)) and not ptext(p).strip() and "<w:drawing" not in p and 'w:type="page"' not in p:
            removed += 1
            return ""
        return p

    new = P_RE.sub(sub, doc)
    for tc in re.finditer(r"<w:tc>.*?</w:tc>", new, re.S):
        if "<w:p" not in tc.group(0):
            raise SystemExit("aborted: removing an empty heading would leave a table cell without a paragraph")
    return new, removed


# ------------------------------------------------------------------ add UC
def strip_ids(x):
    return re.sub(r'\s+w14:(paraId|textId)="[^"]*"', "", x)


class NumAlloc:
    """Gives each cloned list its own numId (restarting at 1) by appending <w:num> overrides to numbering.xml."""

    def __init__(self, xml):
        self.xml = xml
        self.next = max([int(x) for x in re.findall(r'<w:num w:numId="(\d+)"', xml)] + [0]) + 1
        self.added = []

    def fresh(self, proto):
        m = re.search(r'<w:ilvl w:val="(\d+)"/>\s*<w:numId w:val="(\d+)"/>', proto) or re.search(r'<w:numId w:val="(\d+)"/>', proto)
        if not m:
            return None
        old = m.group(m.lastindex)
        lvl = m.group(1) if m.lastindex == 2 else "0"
        a = re.search(r'<w:num w:numId="%s"[^>]*>\s*<w:abstractNumId w:val="(\d+)"/>' % old, self.xml)
        if not a:
            return None
        nid = self.next
        self.next += 1
        self.added.append('<w:num w:numId="%d"><w:abstractNumId w:val="%s"/><w:lvlOverride w:ilvl="%s"><w:startOverride w:val="1"/></w:lvlOverride></w:num>' % (nid, a.group(1), lvl))
        return nid

    def result(self):
        if not self.added:
            return self.xml
        block = "".join(self.added)
        i = self.xml.find("<w:numIdMacAtCleanup")
        if i < 0:
            i = self.xml.rfind("</w:numbering>")
        return self.xml[:i] + block + self.xml[i:]


def make_para(proto, text, numid=None):
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", proto, re.S)
    if ppr and numid is not None:
        ppr = re.match(r"(?s)(.*)", re.sub(r'(<w:numId w:val=")\d+(")', r"\g<1>%d\2" % numid, ppr.group(0)))
    rpr = re.search(r"<w:r(?: [^>]*)?>\s*(<w:rPr>.*?</w:rPr>)", proto, re.S)
    return "<w:p>%s<w:r>%s<w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % (ppr.group(0) if ppr else "", rpr.group(1) if rpr else "", escape(text))


def cell_parts(tc):
    m = re.match(r"(<w:tc>)(<w:tcPr>.*?</w:tcPr>)?(.*)(</w:tc>)$", tc, re.S)
    return m.group(2) or "", P_RE.findall(m.group(3))


def parse_uc_md(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    title = next((re.sub(r"^#+\s*", "", l).strip() for l in lines if l.startswith("#")), None)
    rows = []
    for l in lines:
        m = re.match(r"\|\s*\*\*([^*|]+?)\*\*\s*\|(.*)\|\s*$", l)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            rows.append((m.group(1).strip(), cells))
    if not title or not rows or rows[0][0] != "Primary Actors":
        raise SystemExit("uc.md must start with a heading and a row beginning | **Primary Actors**")
    return title, rows


def lines_of(label, cell):
    parts = [p for p in re.split(r"<br\s*/?>", cell)]
    out = []
    if label == "Normal Flow":
        for i, p in enumerate(parts):
            p = p.strip()
            if not p:
                continue
            if i == 0 and p.startswith("**"):
                out.append((0, p.strip("*")))
            else:
                out.append((1, re.sub(r"^\d+\.\s*", "", p)))
    elif label == "Alternative Flow":
        for p in parts:
            p = p.strip()
            if not p:
                continue
            if p.startswith("**") and p.endswith("**"):
                out.append((0, p.strip("*")))
            else:
                out.append((1, p))
    else:
        out = [(0, p.strip()) for p in parts if p.strip()]
    return out


def op_add_uc(doc, after, md, nums):
    title, new_rows = parse_uc_md(md)
    paras = list(P_RE.finditer(doc))
    h = next((m for m in paras if style_of(m.group(0)).startswith("Heading") and ptext(m.group(0)).strip().startswith(after)), None)
    if not h:
        raise SystemExit("heading not found: " + after)
    t0 = doc.find("<w:tbl>", h.end())
    if t0 < 0:
        raise SystemExit("no table after heading: " + after)
    t1 = doc.find("</w:tbl>", t0) + len("</w:tbl>")
    tbl = doc[t0:t1]
    if "Primary Actors" not in ptext(tbl)[:40]:
        raise SystemExit("the table after '%s' is not a UC table" % after)
    # new table from the template
    row_xml = re.findall(r"<w:tr[ >].*?</w:tr>", tbl, re.S)
    head = tbl[:tbl.find(row_xml[0])]
    new_row_xml = []
    for r in row_xml:
        tcs = re.findall(r"<w:tc>.*?</w:tc>", r, re.S)
        label = ptext(tcs[0]).strip()
        src = next((cells for lab, cells in new_rows if lab == label), None)
        if src is None:
            raise SystemExit("uc.md has no row '%s'" % label)
        trpr = re.search(r"<w:trPr>.*?</w:trPr>", r, re.S)
        built = []
        if label == "Primary Actors":
            vals = {1: src[0], 3: src[2] if len(src) > 2 else "None"}
            for i, tc in enumerate(tcs):
                if i in vals:
                    tcpr, ps = cell_parts(tc)
                    built.append("<w:tc>%s%s</w:tc>" % (tcpr, make_para(ps[0], vals[i])))
                else:
                    built.append(strip_ids(tc))
        else:
            built.append(strip_ids(tcs[0]))
            tcpr, ps = cell_parts(tcs[1])
            p0 = ps[0]
            p1 = ps[1] if len(ps) > 1 else ps[0]
            content, cur = [], None
            for kind, text in lines_of(label, src[0]):
                proto = p0 if kind == 0 else p1
                if label in ("Normal Flow", "Alternative Flow"):
                    if kind == 0:
                        cur = None                       # a title: the next list restarts at 1
                    elif cur is None:
                        cur = nums.fresh(proto)
                    nid = cur if kind == 1 else None
                else:
                    if cur is None:
                        cur = nums.fresh(proto)
                    nid = cur
                content.append(make_para(proto, text, nid))
            content = "".join(content)
            built.append("<w:tc>%s%s</w:tc>" % (tcpr, content or make_para(p0, "")))
            built += [strip_ids(tc) for tc in tcs[2:]]
        new_row_xml.append("<w:tr>%s%s</w:tr>" % (trpr.group(0) if trpr else "", "".join(built)))
    new_tbl = head + "".join(new_row_xml) + "</w:tbl>"
    heading = make_para(h.group(0), title)
    insert = heading + new_tbl
    nxt = P_RE.match(doc, t1)
    if nxt and not ptext(nxt.group(0)).strip() and not style_of(nxt.group(0)).startswith("Heading"):
        insert = strip_ids(nxt.group(0)) + insert      # keep the document's spacer paragraph pattern
    return doc[:t1] + insert + doc[t1:], title


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    cmd, src, out = argv[1], argv[2], argv[3]
    opt = lambda f: argv[argv.index(f) + 1] if f in argv else None
    z, doc = load(src)
    extra = None
    if cmd == "replace":
        find, repl = opt("--find"), opt("--replace")
        if find is None or repl is None:
            raise SystemExit("replace needs --find and --replace")
        doc, n = op_replace(doc, find, repl, "--regex" in argv)
        print("replaced %d occurrence(s)" % n)
    elif cmd == "fix-empty-headings":
        doc, n = op_fix_empty_headings(doc)
        print("removed %d empty heading paragraph(s)" % n)
    elif cmd == "add-uc":
        nums = NumAlloc(z.read("word/numbering.xml").decode("utf-8"))
        doc, title = op_add_uc(doc, opt("--after"), opt("--from"), nums)
        extra = {"word/numbering.xml": nums.result()}
        print("added UC '%s' after '%s' (%d new list(s) numbered from 1)" % (title, opt("--after"), len(nums.added)))
    else:
        print(__doc__)
        return 2
    save(src, out, doc, extra)
    import xml.dom.minidom as md
    with zipfile.ZipFile(out) as zz:
        md.parseString(zz.read("word/document.xml"))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
