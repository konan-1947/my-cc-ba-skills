# Use Case Template - FPT (EDUA SRS style)

Layout (heading + 4-column table with six rows) inferred from the EDUA capstone SRS. That file shows one team's layout only; the field rules below come from standard use case practice (Cockburn, IIBA/Wiegers), and every field is derived by analysis (see `references/field-analysis-guide.md`), not copied from a sample.
Use for FPT University capstone SRS deliverables. In Word, each UC is a heading plus one table.

Language: English. Style: short sentences, one action per step, alternate Actor / System.

---

## 1. UC catalog row (SRS section 1.3.2, one table for all UCs)

| ID | Use Case | Feature | Use Case Description |
|---|---|---|---|
| UC-NN | <Verb + Object> | <Feature group, same as section 2.x> | <2-3 sentences: actor does X, system does Y, outcome> |

- IDs are sequential and global (UC-01, UC-02, ...), never reused.
- `Feature` equals the section 2.x group name (User Identity, Lesson Plan, Blog, Class, ...).

## 2. UC specification (SRS section 2.x.y)

Heading: `2.<group>.<n> <Verb + Object>` (heading level 4). The UC-NN id appears in the catalog and in screen specs ("Mapped Use Case(s): UC-NN: <name>").

| **Primary Actors** | <one role that starts the UC> | **Secondary Actors** | <external systems/services/devices the function touches, or "None"> |
|---|---|---|---|
| **Description** | As a <role>, I want to <goal>, so that <benefit>. |
| **Preconditions** | <state that must already be true before step 1: prerequisite done / actor state / data state / environment; cite rule (BR-xx)><br><next state> |
| **Postconditions** | <outcome the actor obtains><br><state change: object created/updated/deleted, where, status, owner><br><side effect: notification, log, update> |
| **Trigger** (optional) | <event that starts the UC; omit if Step 1 already states it> |
| **Normal Flow** | **<UC name>**<br>1. The <actor> <action>.<br>2. The system <response> (BR-xx).<br>3. ...<br>N. The system <final state / result>, and displays MSGnn when applicable. |
| **Alternative Flow** | **Step <N>_<Condition as a state>**<br>The system <detects it, shows MSGnn, keeps or discards data>.<br>The <actor> may <retry / correct>.<br>The use case continues at Step <M> of the Normal Flow. (or: The use case ends.)<br><br>**Step <N>_<Next condition>**<br>... |

### Field rules

- **Primary Actors**: exactly one role that starts the UC (never "A or B"). **Secondary Actors**: objects **outside the product** that take part in this function (identity provider, AI/LLM service, storage, email/SMS, payment, other systems, devices). They are not additional human users: another person who acts later is the primary actor of a different UC. Write `None` when the function touches nothing external. Derive both by analysis: `references/field-analysis-guide.md`.
- **Description**: `As a <primary actor>, I want to <goal: verb + object, no UI mechanics>, so that <benefit that adds information>`. One goal per UC; the role equals the Primary Actor.
- **Preconditions**: facts that must already be true before step 1, written as states ("is", "has", "exists"), never as actions. Kinds: a prerequisite UC/setup completed (name it, for example the account was registered), actor state (authenticated, authorized, owner), data state (the object exists in an allowed status), environment (a service or catalog is available). Assumed by this UC; anything the UC checks itself and reacts to belongs to the flows. `None` only when nothing must be true first.
- **Postconditions**: what is true after **success**, verifiable by a tester: the outcome the actor obtains, the state change (object, place, status, owner) for write UCs, side effects (notification, log, balance). Each item is produced by a Normal Flow step; together they express the goal. Failure outcomes belong to Alternative Flow. The postcondition of this UC feeds the preconditions of the UCs that follow.
- **Trigger** (optional row): the starting event; keep the Normal Flow to 7-12 steps (split or extract a shared UC beyond that; see references/uc-writing-guide.md).
- **Normal Flow**: first line is the UC name in bold. Every numbered step starts with its subject (`The <actor> ...`, `The system ...`, or the secondary actor); never a bare verb ("Displays the menu") and never passive ("The menu is displayed"). Step 1 is the primary actor's action. Steps alternate actor and system. Every validation step cites its business rule `(BR-xx)`. Messages are cited by code (`MSG02`), never by text.
- **Alternative Flow**: this template has **no separate Exceptions field**; variants, failures and cancellations are all blocks here. Derive them by walking every Normal Flow step (`references/field-analysis-guide.md` section 5). Block = title `Step N_<condition>` (N = the step where the condition is detected; the condition is a state, not a question) + behavior lines, each with a subject (what the user sees: cite `MSGnn`; what happens to data: kept or not stored) + exactly one ending line: `The use case continues at Step M of the Normal Flow.` or `The use case ends.` Blocks in ascending N, 1-8 lines each. Every secondary actor has a failure block; every violable business rule has a violation block.

### Cross-reference ledger (keep updated, check before delivery)

- Every `BR-xx` used exists in SRS section 5.1.
- Every `MSGnn` used exists in SRS section 5.2 with type, context and content.
- Every UC-NN appears in the catalog and in at least one screen spec ("Mapped Use Case(s)") or is marked Non-UI.
- Step numbers in Alternative Flow headings exist in the Normal Flow.

### Quality checklist (FPT)

- [ ] Heading numbering matches the group and sequence
- [ ] Description is "As a ..., I want ..., so that ..."
- [ ] Primary actor is one role; secondary actors are external objects (no human roles) or "None"; each appears in a flow step
- [ ] Steps alternate actor / system, one action each
- [ ] Every rule and message cited by ID
- [ ] Every Alternative Flow header names a real Normal Flow step and ends with where the flow resumes
- [ ] Failure paths leave a defined data state (kept or not stored)
- [ ] No UI layout detail (that belongs to the screen spec, section 3)
