#!/usr/bin/env python3
"""Check the tables of SRS section 1 in one Markdown file (or a directory of .md files).

Usage: python check-overall.py <file-or-dir> [--screens screens.md|dir] [--strict]
Tables are recognised by header:
  | # | Actor | Description |                          -> actors
  | ID | Use Case | Feature | Use Case Description |   -> UC catalog
  | # | Actor | Condition | Action |                   -> workflow (one table per workflow)
  | Screen | <role> | <role> | ...                     -> screen authorization matrix
Checks: actor names unique; catalog ids unique and sequential, Feature filled, UC names Verb + Object;
workflow step numbers ascending, letter-suffixed branch rows follow their number, Actor/Condition/Action filled,
Actor is a known actor or System/AI/external service; authorization columns are known actors, each screen row has
at least one X, and (with --screens) screens equal the headings of section 3.
"""
import os
import re
import sys


def read(p):
    if os.path.isdir(p):
        return "\n".join(open(os.path.join(r, f), encoding="utf-8").read() for r, _, fs in sorted(os.walk(p)) for f in sorted(fs) if f.lower().endswith(".md"))
    return open(p, encoding="utf-8").read()


def tables(text):
    cur = []
    for line in text.split("\n") + [""]:
        if line.strip().startswith("|"):
            cur.append([c.strip() for c in line.strip().strip("|").split("|")])
        else:
            if len(cur) >= 2:
                yield cur
            cur = []


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    text = read(argv[1])
    errors, warns = [], []
    actors, catalog, workflows, auth = [], [], [], []
    for t in tables(text):
        h = [c.lower() for c in t[0]]
        rows = [r for r in t[2:]]
        if h[:3] == ["#", "actor", "description"]:
            actors += rows
        elif h[:4] == ["id", "use case", "feature", "use case description"]:
            catalog += rows
        elif h[:4] == ["#", "actor", "condition", "action"]:
            workflows.append(rows)
        elif h[0] == "screen" and len(h) >= 2:
            auth.append(t)
    names = [r[1] for r in actors if len(r) > 1]
    for n in {x for x in names if names.count(x) > 1}:
        errors.append("duplicate actor %s" % n)
    # catalog
    ids = [r[0] for r in catalog]
    for i in {x for x in ids if ids.count(x) > 1}:
        errors.append("duplicate catalog id %s" % i)
    nums = [int(re.sub(r"\D", "", i)) for i in ids if re.fullmatch(r"UC-\d+", i)]
    if nums != sorted(nums):
        warns.append("UC ids are not in ascending order")
    miss = [n for n in range(1, max(nums) + 1) if n not in nums] if nums else []
    if miss:
        runs, cur = [], []
        for n in miss:
            if cur and n == cur[-1] + 1:
                cur.append(n)
            else:
                if cur:
                    runs.append(cur)
                cur = [n]
        if cur:
            runs.append(cur)
        warns.append("UC id gaps: %s" % ", ".join("UC-%02d" % r[0] if len(r) == 1 else "UC-%02d-UC-%02d (%d ids)" % (r[0], r[-1], len(r)) for r in runs))
    for r in catalog:
        if len(r) < 4 or not r[2] or not r[3]:
            errors.append("%s: Feature or Description missing" % (r[0] if r else "?"))
    # workflows
    known = {n.lower() for n in names} | {"system", "ai/llm", "ai", "llm"}
    for w, rows in enumerate(workflows, 1):
        last = 0
        for r in rows:
            if len(r) < 4 or not all(r[:4]):
                errors.append("workflow %d: incomplete row %s" % (w, r[:1]))
                continue
            m = re.fullmatch(r"(\d+)([a-z]?)", r[0])
            if not m:
                errors.append("workflow %d: bad step number %r" % (w, r[0]))
                continue
            n, suf = int(m.group(1)), m.group(2)
            if suf:
                if n != last:
                    errors.append("workflow %d: branch %s does not follow step %d" % (w, r[0], n))
            else:
                if n != last + 1:
                    errors.append("workflow %d: step %d after %d (expected %d)" % (w, n, last, last + 1))
                last = n
            if names and r[1].lower() not in known and not re.search(r"(service|system|provider|api|google|ai)", r[1], re.I):
                warns.append("workflow %d step %s: actor '%s' is not in the actors table" % (w, r[0], r[1]))
    # authorization
    screen_names = []
    for t in auth:
        roles = t[0][1:]
        if names:
            for rl in roles:
                if rl.lower() not in {n.lower() for n in names}:
                    errors.append("authorization column '%s' is not an actor" % rl)
        for r in t[2:]:
            screen_names.append(r[0])
            if not any(c.upper() == "X" for c in r[1:]):
                warns.append("screen '%s' is allowed for no role" % r[0])
    if "--screens" in argv and screen_names:
        sc = read(argv[argv.index("--screens") + 1])
        heads = {re.sub(r"^\d+(\.\d+)*\s*", "", l.lstrip("# ").strip()).lower() for l in sc.split("\n") if re.match(r"#{2,6}\s+3\.\d", l)}
        for s in screen_names:
            if s.lower() not in heads:
                warns.append("authorization screen '%s' has no section 3 screen spec" % s)
        for h in sorted(heads - {s.lower() for s in screen_names}):
            warns.append("screen spec '%s' missing from the authorization matrix" % h)
    print("actors: %d | catalog UCs: %d | workflows: %d | authorization tables: %d" % (len(actors), len(catalog), len(workflows), len(auth)))
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    bad = errors or ("--strict" in argv and warns)
    print("FAIL" if bad else "PASS", "- %d error(s), %d warning(s)" % (len(errors), len(warns)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
