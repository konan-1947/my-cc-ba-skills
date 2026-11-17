#!/usr/bin/env python3
"""Validate UC specifications written in the FPT template (Markdown tables).

Usage: python validate-uc-fpt.py <file.md|dir> [--registry reg1.md [reg2.md ...]] [--strict]
  <file.md|dir>  one Markdown file, or a directory of .md files (registry files are skipped)
  --registry     one or more files containing the registered BR-xx / MSGnn ids (any layout);
                 cited ids that are not in them are errors
  --actors       Markdown file with the actors table (1.3.1); the Primary Actor must be one of its actors
  Checks that come from analysis rules (see references/field-analysis-guide.md): every flow step starts with its subject; one primary actor; secondary actors are
  external objects, not human roles, and appear in a flow; Description = As a <role>, I want to <goal>, so that <benefit>.
  --skip-resume  do not warn when an Alternative Flow block fails to say where the flow resumes or that the UC ends (default: warn)
  --strict    treat warnings as failures
Each UC block starts at a row beginning with `| **Primary Actors**`; its title is
the nearest heading above. Exit 0 = pass, 1 = errors.
"""
import os
import re
import sys

HUMAN_ROLE = r"\b(teacher|student|moderator|principal|admin|administrator|manager|staff|user|users|visitor|guest|parent|learner|mentor|supporter|employee|member|owner|reviewer|approver)\b"
HUMAN_SAFE = r"\b(service|system|api|gateway|provider|server|storage|platform|google|oauth|llm|ai|email|sms|bot|scheduler|database|cloud|engine|broker|queue|printer|device|sensor|scanner|camera|lms|sso|idp|library)\b"

END_RE = re.compile(r"(?i)(returns? to|resum\w*|continu\w*|retry from|retries from|back to step|use case (ends|stops|terminates)|flow (ends|stops)|(ends|stops) (here|the use case)|does not continue|is complete|completes)")
FAIL_RE = re.compile(r"(?i)\b(fails?|failed|failure|cannot|can not|unable|error|invalid|unavailable|timeout|timed out|denied|not permitted|not allowed|rejected|expired|missing|empty)\b")
TITLE_RE = re.compile(r"^\**\s*Step\s*(\d+)\s*[_\u2013\u2014:-]\s*(.*?)\**\s*$")

PRE_ACTION_RE = re.compile(r"(?i)^(the\s+)?[\w/ -]{1,40}?\s+(opens|clicks|selects|enters|submits|navigates|presses|types|chooses|taps|logs in|signs in to)\b")
PRE_VAGUE_RE = re.compile(r"(?i)\b(is ready|are ready|everything is|properly configured|is working|motivated|has everything|all set)\b")
PRE_CHECKED_RE = re.compile(r"(?i)\b(the system (checks|verifies|validates)|is validated|is verified)\b")
POST_STATE_RE = re.compile(r"(?i)\b(is|are|has been|have been|was|were|remains?|exists?)\b|\b(saved|stored|created|updated|deleted|removed|displayed|shown|sent|recorded|terminated|published|submitted|approved|rejected|assigned|generated|logged|exported|redirected|issued|listed|available)\b")
POST_HEDGE_RE = re.compile(r"(?i)\b(might|maybe|perhaps|probably|hopefully|possibly|try to|tries to|should|ideally|as much as possible|if possible)\b")
POST_IMPERATIVE_RE = re.compile(r"(?i)^(save|create|update|delete|send|display|show|store|record|open|close|submit)\b")
POST_FAIL_RE = re.compile(r"(?i)\b(fails?|failure|error|if the .{0,40}(fails|is not|cannot))\b")
WRITE_VERBS = {"create", "add", "update", "edit", "delete", "remove", "submit", "approve", "reject", "publish", "unpublish", "assign", "upload", "post", "save", "send", "set", "reset", "change", "generate", "register", "replace", "deactivate", "reactivate", "comment", "hide", "unsubmit", "customize", "record", "enable", "disable", "log", "logout"}
READ_VERBS = {"view", "search", "filter", "browse", "list", "open", "show", "display", "download", "present", "preview"}
WRITE_RE = re.compile(r"(?i)\b(exists?|established|authenticated|signed in|saved|stored|created|updated|deleted|removed|changed|published|submitted|recorded|assigned|approved|rejected|status|added|deactivated|reactivated|hidden|sent|set|generated|exported|uploaded|posted|replaced|terminated|cleared|issued|applied|written|withdrawn|reverted|restored|reset|enabled|disabled|no longer|again|marked|moved|linked|attached|copied|duplicated|retains?|keeps?|has|have)\b")
READ_RE = re.compile(r"(?i)\b(displays?|displayed|shows?|shown|lists?|listed|returns?|returned|available|downloads?|downloaded|presents?|presented|opens?|opened|visible|appears?|retrieved|unchanged|does not change)\b")

REQ = ["Primary Actors", "Description", "Preconditions", "Postconditions",
       "Normal Flow", "Alternative Flow"]


def rows(lines):
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"\|\s*\*\*([^*|]+?)\*\*\s*\|(.*)\|\s*$", line)
        if m:
            out.append((i, m.group(1).strip().rstrip(":"), m.group(2)))
    return out


def step_text(step):
    return re.sub(r"^\s*\d+\.\s*", "", step).strip()


def subject_of(text, names):
    """Return (kind, subject): kind is 'known' (actor or system), 'other' (some other noun phrase) or 'none' (no subject)."""
    low = text.lower()
    if "," in text[:70] and not any(low.startswith(("the " + n + " ", n + " ")) for n in names):
        kind, subj = subject_of(text.split(",", 1)[1].strip(), names)      # "For each item, the system displays ..."
        if kind == "known":
            return kind, subj
    for n in sorted(names, key=len, reverse=True):
        if low.startswith("the " + n + " ") or low.startswith(n + " ") or low == n:
            return "known", n
    m = re.match(r"(?i)(the|an?)\s+(.+?)\s+(is|are|was|were|has|have|can|may|will|shall|[a-z]+s)\b", text)
    if m:
        return "other", m.group(2)
    toks = text.split(" ")
    first = toks[0]
    if first.lower() in ("the", "a", "an"):
        return "other", " ".join(toks[:3])
    # a proper-noun subject ("Google Identity Services returns ...", "AI/LLM Service ..."): it names something, just not a declared actor
    caps_inside = any(c.isupper() for c in first[1:])
    second_cap = len(toks) > 1 and toks[1][:1].isupper()
    if caps_inside or second_cap:
        return "other", " ".join(toks[:3])
    return "none", first


def parse_alt(cell):
    """Alternative Flow cell -> blocks [{k, name, lines}]; a block starts at a 'Step N_<condition>' title line."""
    blocks, cur = [], None
    for ln in re.split(r"<br\s*/?>", cell):
        ln = ln.strip()
        if not ln:
            continue
        m = TITLE_RE.match(ln)
        if m:
            cur = {"k": int(m.group(1)), "name": m.group(2).strip(), "lines": []}
            blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(ln)
    return blocks


def steps(cell):
    parts = re.split(r"<br\s*/?>", cell)
    return [p.strip() for p in parts if re.match(r"\s*\d+\.\s", p)]


def main(path, registry=None, strict=False, actors=None, check_resume=True):
    registry = registry or []
    if os.path.isdir(path):
        reg_abs = {os.path.abspath(r) for r in registry}
        files = sorted(os.path.join(r, f) for r, _, fs in os.walk(path) for f in fs
                       if f.lower().endswith(".md") and os.path.abspath(os.path.join(r, f)) not in reg_abs)
        if not files:
            print("ERROR no .md files in", path)
            return 1
        worst = 0
        for f in files:
            print("== " + f)
            if "**Primary Actors**" not in open(f, encoding="utf-8").read():
                continue
            worst = max(worst, main(f, registry, strict, actors, check_resume))
        return worst
    lines = open(path, encoding="utf-8").read().split("\n")
    known = None
    if registry:
        known = set()
        for r in registry:
            known |= set(re.findall(r"\b(?:BR-\d+|MSG\d+)\b", open(r, encoding="utf-8").read()))
    rs = rows(lines)
    starts = [i for (i, lab, _) in rs if lab == "Primary Actors"]
    if not starts:
        print("ERROR no UC block found (expected a row starting `| **Primary Actors**`)")
        return 1
    errors = warns = 0
    for n, st in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        title = next((lines[j].lstrip("# ").strip() for j in range(st, -1, -1)
                      if lines[j].startswith("#")), "UC block %d" % (n + 1))
        block = {lab: cell for (i, lab, cell) in rs if st <= i < end}
        first = lines[st]
        errs, wrns = [], []
        for lab in REQ:
            if lab not in block:
                errs.append("missing row: " + lab)
        cells = first.split("|")
        actor = cells[2].strip() if len(cells) > 2 else ""
        secondary = cells[4].strip() if len(cells) > 4 else ""
        # --- primary actor: exactly one role
        parts = [x.strip() for x in re.split(r",|;| and | or |(?<=[a-z])/(?=[A-Z])", actor) if x.strip()]
        if not parts:
            errs.append("Primary Actor is empty")
        elif len(parts) > 1:
            errs.append("Primary Actor '%s' names several actors: one UC has one primary actor (split the UC, or use a generalized actor)" % actor)
        elif actors is not None and actors and actor.lower() not in actors:
            errs.append("Primary Actor '%s' is not in the actors table (1.3.1)" % actor)
        elif actor.lower() in ("user", "users") and not actors:
            wrns.append("Primary Actor 'User' is generic: name the role, or define 'User' in the actors table")
        # --- secondary actors: external objects, never people
        if "Secondary Actors" not in first:
            wrns.append("Secondary Actors missing in first row (write None if absent)")
        sec_list = [x.strip() for x in re.split(r",|;| and |(?<=[a-z])/(?=[A-Z])", secondary) if x.strip() and x.strip().lower() not in ("none", "n/a", "-")]
        for sec in sec_list:
            low = sec.lower()
            looks_system = re.search(HUMAN_SAFE, low)
            if (re.search(HUMAN_ROLE, low) and not looks_system) or (actors and low in actors and not looks_system and re.search(HUMAN_ROLE, low)):
                wrns.append("Secondary Actor '%s' looks like a human role: secondary actors are external systems/services/devices; a person who acts later is the primary actor of another UC" % sec)
        flow_text = " ".join([block.get("Normal Flow", ""), block.get("Alternative Flow", "")]).lower()
        for sec in sec_list:
            tokens = [t for t in re.findall(r"[a-z0-9]{3,}", sec.lower()) if t not in ("service", "system", "the")]
            if tokens and not any(t in flow_text for t in tokens):
                wrns.append("Secondary Actor '%s' is never mentioned in the Normal or Alternative Flow (list it only if the function really depends on it)" % sec)
        # --- description: As a <role>, I want to <goal>, so that <benefit>
        desc = block.get("Description", "").strip()
        m = re.match(r"(?is)\s*as an? (?P<role>.+?),?\s+i want(?: to)? (?P<goal>.+?),?\s+so that (?P<benefit>.+)$", desc)
        if not m:
            errs.append("Description must be 'As a <role>, I want to <goal>, so that <benefit>'")
        else:
            role = re.sub(r"^(the|a|an)\s+", "", m.group("role").strip().lower())
            act = re.sub(r"^(the|a|an)\s+", "", actor.lower())
            if act and role != act and role not in act and act not in role:
                wrns.append("Description role '%s' differs from the Primary Actor '%s'" % (m.group("role").strip(), actor))
            goal, benefit = m.group("goal").strip(), m.group("benefit").strip()
            if re.match(r"(?i)(be able|have the ability|use the system)", goal):
                wrns.append("Description goal '%s...' is vague: state the action (verb + object)" % goal[:30])
            gw = {w for w in re.findall(r"[a-z]{4,}", goal.lower())}
            bw = {w for w in re.findall(r"[a-z]{4,}", benefit.lower())}
            if gw and len(gw & bw) / float(len(gw)) > 0.7:
                wrns.append("Description benefit mostly repeats the goal: say what the actor gets or decides because of it")
        # --- preconditions and postconditions
        def items_of(label):
            cell = block.get(label, "")
            return [re.sub(r"^[-\u2022*]\s*", "", x).strip() for x in re.split(r"<br\s*/?>", cell) if x.strip()]

        pre, post = items_of("Preconditions"), items_of("Postconditions")
        if "Preconditions" in block and not pre:
            errs.append("Preconditions is empty: list what must already be true, or write None")
        for it in pre:
            if it.lower().strip(". ") in ("none", "n/a", "-"):
                continue
            if PRE_ACTION_RE.search(it):
                wrns.append("Precondition reads like an action ('%s...'): state what must already be true (a state, not a step)" % it[:45])
            if PRE_VAGUE_RE.search(it):
                wrns.append("Precondition is vague ('%s...'): make it verifiable (which state, of which object or actor)" % it[:45])
            if PRE_CHECKED_RE.search(it):
                wrns.append("Precondition '%s...' is checked by the system: a fact the UC verifies belongs to the flow and an Alternative Flow, not to the preconditions" % it[:40])
            if re.search(r"(?i)\bwill\b", it):
                wrns.append("Precondition uses the future ('%s...'): write the state that is already true" % it[:40])
        if "Postconditions" in block and not post:
            errs.append("Postconditions is empty: state the verifiable result of success")
        for it in post:
            if POST_HEDGE_RE.search(it) or len(it.split()) < 3:
                wrns.append("Postcondition '%s...' is hedged or too short to verify: state what exists, changed or is displayed" % it[:40])
            elif POST_IMPERATIVE_RE.match(it):
                wrns.append("Postcondition '%s...' reads like an instruction: state the result, not the step" % it[:40])
            if POST_FAIL_RE.search(it):
                wrns.append("Postcondition '%s...' describes a failure: failure outcomes belong to an Alternative Flow" % it[:40])
        if pre and post and {x.lower() for x in pre} & {x.lower() for x in post}:
            wrns.append("A postcondition repeats a precondition: nothing changed, state the new result")
        uc_name = re.sub(r"^\d+(\.\d+)*\s*", "", title.split(":")[0]).strip().lower()
        verb = uc_name.split(" ")[0] if uc_name else ""
        post_text = " ".join(post)
        if post:
            if verb in WRITE_VERBS and not WRITE_RE.search(post_text):
                wrns.append("'%s' changes data, but no postcondition states the state change (object, where, status, owner)" % uc_name)
            elif verb in READ_VERBS and not READ_RE.search(post_text):
                wrns.append("'%s' is a read use case, but no postcondition states what is displayed or returned" % uc_name)
        ns = steps(block.get("Normal Flow", ""))
        if "Normal Flow" in block:
            if len(ns) < 3:
                errs.append("Normal Flow has %d numbered steps (expected >= 3)" % len(ns))
            if len(ns) > 12:
                wrns.append("Normal Flow has %d steps (> 12): consider splitting" % len(ns))
            if re.search(r"\b(if|otherwise|else)\b", " ".join(ns), re.I):
                wrns.append("possible embedded if/else in Normal Flow; move to Alternative Flow")
            # every step starts with its subject: the actor, a secondary actor, or the system
            names = {"system"}
            for nm in [actor] + sec_list:
                nm = re.sub(r"^(the|a|an)\s+", "", nm.strip().lower())
                if nm:
                    names.add(nm)
            for k, st in enumerate(ns, 1):
                kind, subj = subject_of(step_text(st), names)
                if kind == "none":
                    errs.append("Normal Flow step %d has no subject: write 'The <actor> ...' or 'The system ...' (found '%s ...')" % (k, subj))
                elif kind == "other":
                    wrns.append("Normal Flow step %d: subject '%s' is not the primary actor, a secondary actor or the system" % (k, subj))
            if ns:
                kind, subj = subject_of(step_text(ns[0]), names)
                if kind == "known" and subj == "system" and not re.search(r"scheduler|timer|cron|system", actor.lower()):
                    wrns.append("Normal Flow starts with the system: the primary actor performs the first action (the trigger)")
        alt = block.get("Alternative Flow", "")
        alt_blocks = parse_alt(alt)
        blocks = alt_blocks
        alt_text = re.sub(r"<br\s*/?>|\*", " ", alt).strip().lower()
        if not alt_text or alt_text in ("none", "n/a", "-", "none."):
            wrns.append("No Alternative Flow: at every step ask what else could happen and what could go wrong (invalid input, cancel, state changed, external failure, save failure)")
        elif not alt_blocks:
            errs.append("Alternative Flow has no `**Step N_<condition>**` block")
        alt_names = {"system", "the use case", "use case", "the flow", "flow"}
        for nm in [actor] + sec_list:
            nm = re.sub(r"^(the|a|an)\s+", "", nm.strip().lower())
            if nm:
                alt_names.add(nm)
        seen, last_k = set(), 0
        for blk in alt_blocks:
            k, name, body = blk["k"], blk["name"], blk["lines"]
            label = "Alternative Flow 'Step %d_%s'" % (k, name)
            if ns and k > len(ns):
                errs.append("%s branches from a step beyond the Normal Flow (%d steps)" % (label, len(ns)))
            if k < last_k:
                wrns.append("%s is out of order: list blocks by ascending step number" % label)
            last_k = max(last_k, k)
            key = (k, re.sub(r"\W+", " ", name.lower()).strip())
            if key in seen:
                wrns.append("%s is repeated" % label)
            seen.add(key)
            if not body:
                errs.append("%s has no behavior lines" % label)
                continue
            if len(body) > 8:
                wrns.append("%s has %d lines: keep a branch short and return to the Normal Flow" % (label, len(body)))
            for ln in body:
                kind, subj = subject_of(step_text(ln), alt_names)
                if kind == "none":
                    wrns.append("%s: line has no actor or system subject: '%s...'" % (label, ln[:40]))
            joined = " ".join(body)
            if check_resume and not END_RE.search(body[-1]):
                wrns.append("%s does not end by saying where the flow resumes or that the use case ends" % label)
            for mm in re.finditer(r"(?i)\bstep\s+(\d+)\b", joined):
                if ns and int(mm.group(1)) > len(ns):
                    errs.append("%s refers to Step %s, beyond the Normal Flow (%d steps)" % (label, mm.group(1), len(ns)))
            if FAIL_RE.search(joined + " " + name) and not re.search(r"\bMSG(\d+|\?\?|nn)\b", joined):
                wrns.append("%s is a failure but cites no message (MSGnn) for what the user sees" % label)
        alt_all = " ".join(" ".join(x["lines"]) + " " + x["name"] for x in alt_blocks).lower()
        for sec in sec_list:
            tokens = [t for t in re.findall(r"[a-z0-9]{3,}", sec.lower()) if t not in ("service", "system", "the")]
            if tokens and alt_blocks and not any(t in alt_all for t in tokens):
                wrns.append("Secondary Actor '%s' never appears in an Alternative Flow: cover its failure (unavailable, timeout, invalid or partial response)" % sec)
        cited = set(re.findall(r"\b(?:BR-\d+|MSG\d+)\b", " ".join(block.values())))
        if known is not None:
            for c in sorted(cited - known):
                errs.append("%s cited but not in registry" % c)
        print("%s: %d steps, %d alt blocks, cites %s" % (title, len(ns), len(blocks), sorted(cited) or "-"))
        for m in errs:
            print("  ERROR", m)
        for m in wrns:
            print("  WARN ", m)
        errors += len(errs)
        warns += len(wrns)
    bad = errors or (strict and warns)
    print(("FAIL" if bad else "PASS"), "- %d UC(s), %d error(s), %d warning(s)" % (len(starts), errors, warns))
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    argv = sys.argv
    reg = []
    if "--registry" in argv:
        i = argv.index("--registry") + 1
        while i < len(argv) and not argv[i].startswith("--"):
            reg.append(argv[i])
            i += 1
    actors = None
    if "--actors" in argv:
        txt = open(argv[argv.index("--actors") + 1], encoding="utf-8").read()
        actors = set()
        for line in txt.split("\n")[2:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[1]:
                actors.add(cells[1].lower())
    sys.exit(main(argv[1], reg, "--strict" in argv, actors, "--skip-resume" not in argv))
