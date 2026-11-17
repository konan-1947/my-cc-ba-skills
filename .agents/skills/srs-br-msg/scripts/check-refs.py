#!/usr/bin/env python3
"""Cross-check BR-xx and MSGnn ids between the registers (SRS 5.1 / 5.2) and the documents that cite them.

Usage:
  python check-refs.py --registry br-registry.md msg-registry.md --scan uc/ screens/ nfr.md [--strict]

--registry  one or more Markdown files holding the register tables
              BR rows : | BR-01 | Rule definition |
              MSG rows: | 1 | MSG01 | Inline | Context | Content |
--scan      files or directories (*.md) that cite ids; registry files are excluded automatically
Reports: cited but unregistered (error), duplicate registry ids (error), invalid message type (error),
registered but never cited (warning), numbering gaps (warning), placeholders MSG?? / BR-?? still to register (info).
Exit 0 = no errors (warnings allowed unless --strict).
"""
import os
import re
import sys

MSG_TYPES = ("Inline", "Toast", "Popup", "Confirmation popup", "Dialog", "Banner", "Button state", "Status label", "Email", "Notification")


def md_files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                out += [os.path.join(root, f) for f in files if f.lower().endswith(".md")]
        else:
            out.append(p)
    return out


def parse_registry(files):
    br, msg, errors = {}, {}, []
    for f in files:
        for line in open(f, encoding="utf-8"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            if re.fullmatch(r"BR-\d+", cells[0]):
                if cells[0] in br:
                    errors.append("duplicate registry id %s" % cells[0])
                br[cells[0]] = cells[1]
            else:
                code = next((c for c in cells[:2] if re.fullmatch(r"MSG\d+", c)), None)
                if code:
                    if code in msg:
                        errors.append("duplicate registry id %s" % code)
                    typ = cells[cells.index(code) + 1] if cells.index(code) + 1 < len(cells) else ""
                    if not typ.startswith(MSG_TYPES):
                        errors.append("%s has invalid or missing message type %r (allowed prefixes: %s)" % (code, typ, ", ".join(MSG_TYPES)))
                    msg[code] = typ
    return br, msg, errors


def ranges(ids):
    """['MSG03','MSG04','MSG05','MSG09'] -> 'MSG03-MSG05, MSG09' (runs of consecutive numbers collapsed)."""
    import re as _re
    items = sorted(((int(_re.sub(r"\D", "", i)), i) for i in ids))
    out, run = [], []
    for n, i in items:
        if run and n == run[-1][0] + 1:
            run.append((n, i))
        else:
            if run:
                out.append(run)
            run = [(n, i)]
    if run:
        out.append(run)
    return ", ".join(r[0][1] if len(r) == 1 else "%s-%s (%d ids)" % (r[0][1], r[-1][1], len(r)) for r in out)


def gaps(ids, prefix):
    nums = sorted(int(re.sub(r"\D", "", i)) for i in ids)
    if not nums:
        return []
    have = set(nums)
    return ["%s%02d" % (prefix, n) for n in range(nums[0], nums[-1] + 1) if n not in have]


def main(argv):
    if "--registry" not in argv or "--scan" not in argv:
        print(__doc__)
        return 2
    def opt(flag):
        i = argv.index(flag) + 1
        out = []
        while i < len(argv) and not argv[i].startswith("--"):
            out.append(argv[i])
            i += 1
        return out

    reg_args, scan_args = opt("--registry"), opt("--scan")
    reg_files = md_files(reg_args)
    reg_abs = {os.path.abspath(f) for f in reg_files}
    scan_files = [f for f in md_files(scan_args) if os.path.abspath(f) not in reg_abs]
    br, msg, errors = parse_registry(reg_files)
    cited_br, cited_msg, placeholders = {}, {}, []
    for f in scan_files:
        text = open(f, encoding="utf-8").read()
        for m in re.finditer(r"\b(BR-\d+|MSG\d+)\b", text):
            (cited_br if m.group(1).startswith("BR") else cited_msg).setdefault(m.group(1), set()).add(os.path.basename(f))
        for m in re.finditer(r"\b(BR-\?\?|MSG\?\?)", text):
            placeholders.append("%s in %s" % (m.group(1), os.path.basename(f)))
    warns = []
    for i in sorted(set(cited_br) - set(br)):
        errors.append("%s cited in %s but not registered" % (i, sorted(cited_br[i])))
    for i in sorted(set(cited_msg) - set(msg)):
        errors.append("%s cited in %s but not registered" % (i, sorted(cited_msg[i])))
    for i in sorted(set(br) - set(cited_br)):
        warns.append("%s registered but never cited" % i)
    for i in sorted(set(msg) - set(cited_msg)):
        warns.append("%s registered but never cited" % i)
    g = gaps(br, "BR-") + gaps(msg, "MSG")
    if g:
        warns.append("numbering gaps: %s" % ranges(g))
    print("registry: %d BR, %d MSG | scanned %d file(s): cites %d BR, %d MSG" % (len(br), len(msg), len(scan_files), len(cited_br), len(cited_msg)))
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    for p in placeholders:
        print("TODO  to register:", p)
    bad = errors or ("--strict" in argv and warns)
    print("FAIL" if bad else "PASS", "- %d error(s), %d warning(s), %d placeholder(s)" % (len(errors), len(warns), len(placeholders)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
