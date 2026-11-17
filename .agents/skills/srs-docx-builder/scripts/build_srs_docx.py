#!/usr/bin/env python3
"""Build an SRS Word file (.docx) from Markdown parts. Pure standard library (no pip/npm installs).

Usage: python build_srs_docx.py manifest.json out.docx

Manifest (paths relative to the manifest file):
{
  "title": "EDUA PROJECT REPORT",
  "subtitle": "Report 3 - Software Requirement Specification",
  "date_line": "- Hanoi, Jun 2026 -",
  "logo": "logo.png",                       # optional, PNG/JPG
  "footer": "Edua - G20 - Report 3 (SRS Document)",
  "page": "A4",                             # A4 | A3 | Letter
  "font": "Calibri", "font_size": 11,       # points (the EDUA sample uses 13)
  "toc_levels": 4,
  "parts": ["00-record.md", "section1.md", "section2/*.md"]
}

Markdown subset per part: # to ###### headings (typed numbers stay as text, e.g. "## 1. Overall Requirements"),
paragraphs, **bold**, *italic*, `code`, <br> line breaks, - / * bullets and 1. lists (2-space nesting),
pipe tables (first row = header), UC tables (first cell **Primary Actors**), images ![caption](file.png|file.svg),
<!-- pagebreak -->. SVG images are converted to PNG with headless Edge/Chrome when available.
"""
import glob
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

PAGES = {"A4": (11906, 16838), "A3": (16838, 23811), "Letter": (12240, 15840)}
MARGIN = 1440
HEAD_FILL, LABEL_FILL = "FFE8E1", "FBE5D5"
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


# ---------------------------------------------------------------- helpers
def esc(t):
    return escape(t)


def run(text, bold=False, italic=False, code=False, extra=""):
    rpr = ""
    if bold:
        rpr += "<w:b/><w:bCs/>"
    if italic:
        rpr += "<w:i/><w:iCs/>"
    if code:
        rpr += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/><w:sz w:val="20"/>'
    rpr += extra
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % ("<w:rPr>%s</w:rPr>" % rpr if rpr else "", esc(text))


def inline(text, bold=False):
    out = []
    for tok in re.split(r"(\*\*.+?\*\*|`.+?`|(?<![\w*])\*(?!\s).+?(?<!\s)\*(?![\w*]))", text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            out.append(run(tok[2:-2], bold=True))
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            out.append(run(tok[1:-1], bold=bold, code=True))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            out.append(run(tok[1:-1], bold=bold, italic=True))
        else:
            out.append(run(tok, bold=bold))
    return "".join(out)


def para(text="", style=None, align=None, bold=False, after=None, keep=False, extra_ppr=""):
    ppr = ""
    if style:
        ppr += '<w:pStyle w:val="%s"/>' % style
    if keep:
        ppr += "<w:keepNext/>"
    ppr += extra_ppr
    if after is not None:
        ppr += '<w:spacing w:after="%d"/>' % after
    if align:
        ppr += '<w:jc w:val="%s"/>' % align
    return "<w:p>%s%s</w:p>" % ("<w:pPr>%s</w:pPr>" % ppr if ppr else "", inline(text, bold) if text else "")


def png_size(data):
    return struct.unpack(">II", data[16:24])


def jpg_size(data):
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise ValueError("cannot read JPEG size")


def find_browser():
    cands = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe", "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    return next((c for c in cands if os.path.exists(c)), None)


def svg_to_png(svg_path, png_path):
    exe = find_browser()
    if not exe:
        raise SystemExit("cannot convert %s: no Edge/Chrome found; export a PNG yourself" % svg_path)
    text = open(svg_path, encoding="utf-8").read()
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', text)
    w, h = (int(float(m.group(1))), int(float(m.group(2)))) if m else (1000, 700)
    url = "file:///" + os.path.abspath(svg_path).replace("\\", "/").lstrip("/")
    cmd = [exe, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
           "--screenshot=" + os.path.abspath(png_path), "--window-size=%d,%d" % (w, h), url]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    if not os.path.exists(png_path):
        raise SystemExit("SVG to PNG conversion failed for " + svg_path)
    return png_path


# ---------------------------------------------------------------- document builder
class Doc:
    def __init__(self, manifest, base):
        self.m, self.base = manifest, base
        self.pw, self.ph = PAGES.get(manifest.get("page", "A4"), PAGES["A4"])
        self.text_w = self.pw - 2 * MARGIN
        self.body = []
        self.media = []          # (name, bytes)
        self.rels = []           # (rid, target)
        self.numbered = 0        # number of numbered lists
        self.warnings = []
        self.cache = tempfile.mkdtemp(prefix="srsdocx_")

    # ---- images
    def image(self, alt, path, part_dir):
        full = next((p for p in (os.path.join(part_dir, path), os.path.join(self.base, path), path) if os.path.exists(p)), None)
        if not full:
            self.warnings.append("image not found: " + path)
            self.body.append(para("[missing image: %s]" % path, align="center"))
            return
        if full.lower().endswith(".svg"):
            full = svg_to_png(full, os.path.join(self.cache, os.path.basename(full) + ".png"))
        data = open(full, "rb").read()
        ext = os.path.splitext(full)[1].lower()
        wpx, hpx = (png_size(data) if data[:4] == b"\x89PNG" else jpg_size(data))
        emu_w = wpx * 9525
        if data[:4] == b"\x89PNG" and "@2x" not in full and full.startswith(self.cache):
            emu_w //= 2
        max_w = self.text_w * 635
        scale = min(1.0, max_w / emu_w)
        cx, cy = int(emu_w * scale), int(emu_w * scale * hpx / wpx)
        n = len(self.media) + 1
        name = "image%d%s" % (n, ".png" if data[:4] == b"\x89PNG" else ".jpg")
        self.media.append((name, data))
        rid = "rIdImg%d" % n
        self.rels.append((rid, "image", "media/" + name))   # (Id, Type suffix, Target)
        drawing = ('<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/>'
                   '<wp:docPr id="%d" name="%s" descr="%s"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                   '<pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="%s"/>'
                   '<a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
                   '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
                   % (cx, cy, n, esc(name), esc(alt), n, esc(name), rid, cx, cy))
        self.body.append('<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr>%s</w:p>' % drawing)
        if alt:
            self.body.append(para(alt, style="Caption", align="center"))

    # ---- tables
    def cell(self, width, text, fill=None, bold=False, span=1, style_text=True):
        tcpr = '<w:tcW w:w="%d" w:type="dxa"/>' % width
        if span > 1:
            tcpr += '<w:gridSpan w:val="%d"/>' % span
        if fill:
            tcpr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill
        parts = [p for p in re.split(r"<br\s*/?>", text)]
        paras = "".join('<w:p><w:pPr><w:spacing w:after="40" w:line="259" w:lineRule="auto"/></w:pPr>%s</w:p>' % inline(p.strip(), bold) for p in parts) or "<w:p/>"
        return "<w:tc><w:tcPr>%s</w:tcPr>%s</w:tc>" % (tcpr, paras)

    def table(self, rows):
        rows = [r for r in rows]
        has_header = len(rows) > 1 and re.fullmatch(r"[\s:|-]+", "|".join(rows[1])) is not None
        if has_header:
            rows = [rows[0]] + rows[2:]
        first = re.sub(r"\*", "", rows[0][0]).strip() if rows and rows[0] else ""
        total = self.text_w - 100
        out = []
        if first == "Primary Actors":
            w = [int(total * f) for f in (0.2, 0.3, 0.2, 0.3)]
            grid = "".join('<w:gridCol w:w="%d"/>' % x for x in w)
            for i, r in enumerate(rows):
                if i == 0 and len(r) >= 4:
                    cells = [self.cell(w[0], r[0], LABEL_FILL, True), self.cell(w[1], r[1]), self.cell(w[2], r[2], LABEL_FILL, True), self.cell(w[3], r[3])]
                elif len(r) >= 2:
                    cells = [self.cell(w[0], r[0], LABEL_FILL, True), self.cell(sum(w[1:]), " ".join(r[1:]) if len(r) > 2 else r[1], span=3)]
                else:
                    cells = [self.cell(total, r[0], span=4)]
                out.append("<w:tr><w:trPr><w:cantSplit w:val=\"0\"/></w:trPr>%s</w:tr>" % "".join(cells))
        else:
            ncol = max(len(r) for r in rows)
            plain = lambda t: re.sub(r"<br\s*/?>|\*\*|`", " ", t)
            minw, weights = [], []
            for c in range(ncol):
                texts = [plain(r[c]) if c < len(r) else "" for r in rows]
                longest_word = max((len(wd) for t in texts for wd in t.split()), default=1)
                minw.append(min(longest_word, 24) * 115 + 260)
                weights.append(min(max(max(len(t) for t in texts), 4), 70))
            free = total - sum(minw)
            if free < 0:
                minw = [max(int(m * total / float(sum(minw))), 600) for m in minw]
                free = 0
            s_w = float(sum(weights))
            w = [m + int(free * x / s_w) for m, x in zip(minw, weights)]
            w[-1] += total - sum(w)
            grid = "".join('<w:gridCol w:w="%d"/>' % x for x in w)
            for i, r in enumerate(rows):
                r = r + [""] * (ncol - len(r))
                head = has_header and i == 0
                cells = "".join(self.cell(w[c], r[c], HEAD_FILL if head else None, head) for c in range(ncol))
                trpr = "<w:trPr><w:cantSplit/>%s</w:trPr>" % ("<w:tblHeader/>" if head else "")
                out.append("<w:tr>%s%s</w:tr>" % (trpr, cells))
        borders = "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="000000"/>' % s for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
        self.body.append('<w:tbl><w:tblPr><w:tblStyle w:val="SRSTable"/><w:tblW w:w="%d" w:type="dxa"/><w:tblInd w:w="100" w:type="dxa"/><w:tblBorders>%s</w:tblBorders>'
                         '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
                         '<w:tblGrid>%s</w:tblGrid>%s</w:tbl>' % (total, borders, grid, "".join(out)))
        self.body.append(para("", after=120))

    # ---- markdown part
    def add_markdown(self, text, part_dir):
        lines = text.replace("\r\n", "\n").split("\n")
        i, para_buf, list_state = 0, [], None

        def flush():
            if para_buf:
                self.body.append(para(" ".join(s.strip() for s in para_buf).replace("<br>", " ").strip(), after=120))
                para_buf.clear()

        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if s.startswith("<!--"):
                if "pagebreak" in s:
                    flush()
                    self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
                while "-->" not in lines[i]:
                    i += 1
                i += 1
                continue
            m = re.match(r"(#{1,6})\s+(.*)", s)
            if m:
                flush()
                list_state = None
                self.body.append(para(re.sub(r"\*\*", "", m.group(2)), style="Heading%d" % len(m.group(1))))
                i += 1
                continue
            m = re.fullmatch(r"!\[(.*?)\]\((.+?)\)", s)
            if m:
                flush()
                self.image(m.group(1), m.group(2), part_dir)
                i += 1
                continue
            if s.startswith("|"):
                flush()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    rows.append([c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))])
                    i += 1
                self.table(rows)
                continue
            m = re.match(r"(\s*)([-*]|\d+\.)\s+(.*)", line)
            if m:
                flush()
                lvl = min(len(m.group(1).replace("\t", "  ")) // 2, 2)
                numbered = m.group(2)[0].isdigit()
                if numbered and (list_state is None or list_state[0] != "n"):
                    self.numbered += 1
                    list_state = ("n", self.numbered + 1)
                elif not numbered:
                    list_state = ("b", 1)
                numid = list_state[1]
                self.body.append(para(m.group(3), style="ListParagraph",
                                      extra_ppr='<w:numPr><w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr>' % (lvl, numid), after=60))
                i += 1
                continue
            if not s:
                flush()
                list_state = None
                i += 1
                continue
            para_buf.append(line)      # one source line = one paragraph (templates are not hard-wrapped)
            flush()
            i += 1
        flush()

    # ---- package
    def cover(self):
        m, b = self.m, self.body
        if m.get("logo"):
            lp = os.path.join(self.base, m["logo"])
            if os.path.exists(lp):
                self.image("", m["logo"], self.base)
        for _ in range(3):
            b.append(para(""))
        b.append(para(m.get("title", "REPORT"), style="Title", align="center"))
        if m.get("subtitle"):
            b.append(para(m["subtitle"], align="center", bold=True, extra_ppr=""))
        if m.get("date_line"):
            b.append(para(m["date_line"], align="center"))
        b.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        b.append(para("Table of Contents", style="TOCHeading"))
        levels = int(m.get("toc_levels", 4))
        b.append('<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-%d" \\h \\z \\u </w:instrText></w:r>'
                 '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Right-click and choose Update Field to build the table of contents.</w:t></w:r>'
                 '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>' % levels)
        b.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def styles(self):
        font = esc(self.m.get("font", "Calibri"))
        sz = int(float(self.m.get("font_size", 11)) * 2)

        def h(i, size, color=None, italic=False, before=240):
            c = '<w:color w:val="%s"/>' % color if color else ""
            it = "<w:i/><w:iCs/>" if italic else ""
            return ('<w:style w:type="paragraph" w:styleId="Heading%d"><w:name w:val="heading %d"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/>'
                    '<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="%d" w:after="80"/><w:outlineLvl w:val="%d"/></w:pPr>'
                    '<w:rPr><w:b/><w:bCs/>%s%s<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:style>' % (i, i, before, i - 1, it, c, size, size))

        base = int(self.m.get("font_size", 11) * 2)
        heads = "".join([h(1, base + 8, "C00000"), h(2, base + 6, None, False, 200), h(3, base + 4, "1E4D78", False, 160), h(4, base + 2, None, True, 120),
                         h(5, base + 1, None, True, 100), h(6, base, "595959", True, 80)])
        toc = "".join('<w:style w:type="paragraph" w:styleId="TOC%d"><w:name w:val="toc %d"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="39"/>'
                      '<w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="%d"/></w:tabs><w:spacing w:after="40"/><w:ind w:left="%d"/></w:pPr></w:style>' % (i, i, self.text_w, (i - 1) * 240) for i in range(1, 7))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles %s>'
                '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s" w:eastAsia="%s"/><w:sz w:val="%d"/><w:szCs w:val="%d"/><w:lang w:val="en-US" w:eastAsia="vi-VN"/></w:rPr></w:rPrDefault>'
                '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
                '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
                '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:before="240" w:after="240"/></w:pPr><w:rPr><w:b/><w:bCs/><w:color w:val="C00000"/><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:style>'
                '<w:style w:type="paragraph" w:styleId="TOCHeading"><w:name w:val="TOC Heading"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:spacing w:after="200"/></w:pPr><w:rPr><w:b/><w:bCs/><w:color w:val="C00000"/><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:style>'
                '<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="200"/></w:pPr><w:rPr><w:i/><w:iCs/><w:color w:val="44546A"/><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:style>'
                '<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:ind w:left="720"/><w:contextualSpacing/></w:pPr></w:style>'
                '<w:style w:type="paragraph" w:styleId="Footer"><w:name w:val="footer"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="0"/></w:pPr><w:rPr><w:sz w:val="%d"/></w:rPr></w:style>'
                '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:uiPriority w:val="99"/><w:semiHidden/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>'
                '<w:style w:type="table" w:styleId="SRSTable"><w:name w:val="SRS Table"/><w:basedOn w:val="TableNormal"/><w:uiPriority w:val="59"/></w:style>'
                '%s%s</w:styles>' % (NS, font, font, font, font, sz, sz, base + 22, base + 22, base + 10, base + 10, base - 2, base - 2, base - 2, heads, toc))

    def numbering(self):
        def lvl(i, fmt, text, left):
            return ('<w:lvl w:ilvl="%d"><w:start w:val="1"/><w:numFmt w:val="%s"/><w:lvlText w:val="%s"/><w:lvlJc w:val="left"/>'
                    '<w:pPr><w:ind w:left="%d" w:hanging="360"/></w:pPr></w:lvl>' % (i, fmt, text, left))
        bullets = "".join(lvl(i, "bullet", "\u2022" if i != 1 else "o", 720 + 360 * i) for i in range(3))
        dec = "".join(lvl(i, "decimal" if i == 0 else "lowerLetter", "%%%d." % (i + 1), 720 + 360 * i) for i in range(3))
        nums = '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
        for n in range(self.numbered):
            nums += '<w:num w:numId="%d"><w:abstractNumId w:val="1"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>' % (n + 2)
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering %s><w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>%s</w:abstractNum>'
                '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>%s</w:abstractNum>%s</w:numbering>' % (NS, bullets, dec, nums))

    def footer(self):
        txt = esc(self.m.get("footer", ""))
        f = lambda instr: '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> %s </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>' % instr
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr %s><w:p><w:pPr><w:pStyle w:val="Footer"/><w:pBdr><w:top w:val="single" w:sz="4" w:space="4" w:color="808080"/></w:pBdr>'
                '<w:tabs><w:tab w:val="right" w:pos="%d"/></w:tabs></w:pPr><w:r><w:t xml:space="preserve">%s</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t xml:space="preserve">Page </w:t></w:r>%s<w:r><w:t xml:space="preserve"> / </w:t></w:r>%s</w:p></w:ftr>'
                % (NS, self.text_w, txt, f("PAGE"), f("NUMPAGES")))

    def write(self, out):
        sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/><w:pgSz w:w="%d" w:h="%d"/>'
                '<w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d" w:header="720" w:footer="720" w:gutter="0"/><w:titlePg/></w:sectPr>'
                % (self.pw, self.ph, MARGIN, MARGIN, MARGIN, MARGIN))
        document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document %s><w:body>%s%s</w:body></w:document>' % (NS, "".join(self.body), sect)
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '<Relationship Id="rIdNum" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
                '<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
                '<Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>%s</Relationships>'
                % "".join('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/%s" Target="%s"/>' % r for r in self.rels))
        ctypes = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                  '<Default Extension="png" ContentType="image/png"/><Default Extension="jpg" ContentType="image/jpeg"/>'
                  '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                  '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                  '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
                  '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
                  '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
                  '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>')
        root = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
        core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title></cp:coreProperties>'
                % esc(self.m.get("subtitle") or self.m.get("title", "")))
        settings = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings %s><w:updateFields w:val="true"/></w:settings>' % NS
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", ctypes)
            z.writestr("_rels/.rels", root)
            z.writestr("word/document.xml", document)
            z.writestr("word/_rels/document.xml.rels", rels)
            z.writestr("word/styles.xml", self.styles())
            z.writestr("word/numbering.xml", self.numbering())
            z.writestr("word/settings.xml", settings)
            z.writestr("word/footer1.xml", self.footer())
            z.writestr("docProps/core.xml", core)
            for name, data in self.media:
                z.writestr("word/media/" + name, data)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    mpath = os.path.abspath(argv[1])
    base = os.path.dirname(mpath)
    manifest = json.load(open(mpath, encoding="utf-8"))
    doc = Doc(manifest, base)
    doc.cover()
    parts = []
    for p in manifest.get("parts", []):
        hits = sorted(glob.glob(os.path.join(base, p))) or []
        if not hits:
            raise SystemExit("part not found: " + p)
        parts += hits
    for p in parts:
        doc.add_markdown(open(p, encoding="utf-8").read(), os.path.dirname(p))
    doc.write(argv[2])
    import xml.dom.minidom as md
    with zipfile.ZipFile(argv[2]) as z:
        for n in z.namelist():
            if n.endswith(".xml") or n.endswith(".rels"):
                md.parseString(z.read(n))
    print("wrote %s: %d part(s), %d image(s), %d numbered list(s)" % (argv[2], len(parts), len(doc.media), doc.numbered))
    for w in doc.warnings:
        print("WARN", w)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
