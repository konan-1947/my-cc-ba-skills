#!/usr/bin/env python3
"""Validate non-functional requirements (quality attributes) written as `CODE-NN: The system shall ...` lines in Markdown.

Usage: python validate-nfr.py <file.md> [--strict]
Codes follow references/quality-attributes.md: AVL INS INT IOP PER REL ROB SAF SEC USE EFF MOD POR REU SCA VER.
Checks: known code (aliases PRF, USR, ITG, SCL are accepted with a note), unique ids, sequential per code,
uses 'shall', one obligation per id, a measurable threshold (error for AVL PER REL ROB SCA SAF, warning for INS EFF USE),
no vague words, no external-interface requirements (not part of this section).
An attribute that does not apply is declared with a line such as `SAF: Not applicable - <reason>`.
The report ends with a NOTE listing attributes that have neither a requirement nor an N/A declaration.
"""
import re
import sys

CATALOG = {
    "AVL": "availability", "INS": "installability", "INT": "integrity", "IOP": "interoperability",
    "PER": "performance", "REL": "reliability", "ROB": "robustness", "SAF": "safety", "SEC": "security",
    "USE": "usability", "EFF": "efficiency", "MOD": "modifiability", "POR": "portability",
    "REU": "reusability", "SCA": "scalability", "VER": "verifiability",
}
ALIASES = {"PRF": "PER", "USR": "USE", "ITG": "INT", "SCL": "SCA", "MNT": "MOD", "CMP": "POR"}
INTERFACE = {"INT-UI", "INT-SW", "INT-HW", "INT-COM"}
MEASURABLE_REQUIRED = {"AVL", "PER", "REL", "ROB", "SCA", "SAF"}          # error without a threshold
MEASURABLE_ADVISED = {"INS", "EFF", "USE"}                                 # warning: usually measurable, but design rules are possible
VAGUE = ["fast", "quickly", "user-friendly", "easy to use", "robust", "reasonable", "adequate", "as soon as possible", "etc.",
         "and/or", "appropriate", "efficient", "flexible", "modern", "seamless", "intuitive", "high performance"]
MEASURE = re.compile(r"\b\d+(\.\d+)?\s?(%|percent|ms|milliseconds?|seconds?|s|minutes?|hours?|days?|weeks?|fps|frames per second|MB|GB|KB|users?|requests?|px|pixels|times|characters|items|concurrent|attempts?|failures?)\b|\b\d+%|\bTLS\s?\d", re.I)
LINE = re.compile(r"\s*(?:[-*]\s*)?\**((?:INT-[A-Z]+)|[A-Z]{3})(?:-(\d+))?\**\s*:\s*(.+)")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    errors, warns, notes = [], [], []
    seen, per_code, declared = {}, {}, set()
    for ln, line in enumerate(open(argv[1], encoding="utf-8"), 1):
        m = LINE.match(line)
        if not m:
            continue
        prefix, num, text = m.group(1), m.group(2), m.group(3).strip()
        code = ALIASES.get(prefix, prefix)
        if num is None:
            if re.match(r"(?i)(not applicable|n/a)\b", text) and code in CATALOG:
                declared.add(code)
                if len(text.split()) < 4:
                    warns.append("%s (line %d): an N/A declaration must give the reason" % (prefix, ln))
            continue
        rid = "%s-%02d" % (prefix, int(num))
        if prefix in INTERFACE:
            warns.append("%s (line %d): external-interface requirements are not part of this section; express the need as Interoperability (IOP), or move it to the functional requirements" % (rid, ln))
            continue
        if code not in CATALOG:
            errors.append("%s (line %d): unknown code %s (catalog: %s)" % (rid, ln, prefix, ", ".join(sorted(CATALOG))))
            continue
        if prefix in ALIASES:
            notes.append("%s uses the alias %s; the catalog code is %s" % (rid, prefix, code))
        if rid in seen:
            errors.append("%s (line %d): duplicate of line %d" % (rid, ln, seen[rid]))
        seen[rid] = ln
        per_code.setdefault(prefix, []).append(int(num))
        declared.discard(code)
        declared.add(code + "*")                      # has at least one requirement
        if not re.search(r"\bshall\b", text, re.I):
            errors.append("%s: must use 'shall'" % rid)
        if len(re.findall(r"\bshall\b", text, re.I)) > 1:
            warns.append("%s: more than one 'shall'; split into separate ids" % rid)
        if code in MEASURABLE_REQUIRED and not MEASURE.search(text):
            errors.append("%s: %s requirement needs a measurable threshold (number + unit)" % (rid, CATALOG[code]))
        elif code in MEASURABLE_ADVISED and not MEASURE.search(text):
            warns.append("%s: %s requirements are usually measurable (number + unit); if this is a design rule, make sure a tester can still verify it" % (rid, CATALOG[code]))
        for w in VAGUE:
            if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(w), text, re.I):
                warns.append("%s: vague wording '%s'" % (rid, w))
    if not seen and not declared:
        print("ERROR no requirement lines found (expected `AVL-01: The system shall ...`)")
        return 1
    for p, nums in per_code.items():
        nums = sorted(nums)
        miss = [n for n in range(1, nums[-1] + 1) if n not in nums]
        if miss:
            warns.append("%s numbering gaps: %s" % (p, ", ".join("%s-%02d" % (p, n) for n in miss)))
    covered = {c.rstrip("*") for c in declared}
    missing = [c for c in CATALOG if c not in covered]
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    for n in notes[:6]:
        print("NOTE ", n)
    if len(notes) > 6:
        print("NOTE  ... %d more alias uses" % (len(notes) - 6))
    if missing:
        print("NOTE  attributes with neither a requirement nor an N/A declaration: %s" % ", ".join(missing))
    bad = errors or ("--strict" in argv and warns)
    print("FAIL" if bad else "PASS", "- %d requirement(s), %d error(s), %d warning(s)" % (len(seen), len(errors), len(warns)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
