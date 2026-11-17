---
name: uc-fpt
description: Write Use Case specifications in the FPT University capstone SRS style (EDUA Report 3 format) - one table per UC with Primary/Secondary Actors, Description (As a / I want / so that), Preconditions, Postconditions, Normal Flow and Alternative Flow (failures included, titled "Step N_<name>"), rules and messages cited by BR-xx and MSGnn ids, plus the UC catalog row and a cross-reference check. Use for "viết use case theo mẫu FPT", "đặc tả UC cho SRS đồ án", "UC EDUA", "write UC for SRS section 2", "review UC FPT", "check BR/MSG references". Not for the company 13-field template (use uc-company) or user stories.
---

# UC specification - FPT template

Layout inferred from the EDUA capstone SRS; the content rules come from standard UC practice, and each field is derived by analysis of the function, never copied from a sample document. English output, Markdown tables that paste into Word. Company work with the 13-field template belongs to `uc-company`.

## Files

| File | Use |
|---|---|
| [templates/template-fpt.md](templates/template-fpt.md) | Catalog row, UC table, field rules, cross-reference ledger |
| [references/field-analysis-guide.md](references/field-analysis-guide.md) | **How to derive each field**: primary actor, secondary actors (external objects, not extra users), Description `As a / I want to / so that`, conditions, alternatives |
| [references/uc-writing-guide.md](references/uc-writing-guide.md) | UC vs user story, goal level, identification, 7-12 step limit, anti-patterns |
| [references/checklist-fpt.md](references/checklist-fpt.md) | 18-point checklist + cross-reference checks |
| [references/examples.md](references/examples.md) | Good UC in FPT format, same UC in company shape, weak UC |
| `srs-writer` skill | Orchestrates the whole SRS; part-to-skill map and remaining gaps |
| `scripts/validate-uc-fpt.py` | Validation of UC tables; accepts a file or directory and several `--registry` files |

## Workflow

1. **Classify** the request: (A) write new UC from a feature, (B) split a feature into a UC list/catalog, (C) review existing UCs, (D) write one row (for example only the Alternative Flow). If input is one vague line, ask at most 3 questions: who is the primary actor (specific role), what is the goal, which module/feature group.
2. **Scope** (guide sections 2-3): user-goal level, one actor / one goal / one session, coffee-break test. For lists, use goal-driven, event-driven and CRUD-driven identification; in SRS groups such as Blog, Class or Community Hub, View / Create / Edit / Delete are separate UCs. Output a catalog table (`ID | Use Case | Feature | Use Case Description`) and ask which to detail.
3. **Write** with the template. Unlike `uc-company`, do **not** stop after each row group: write one whole UC (or one feature group) per confirmation, because an SRS has about 100 UCs. If the user wants row-by-row, honor it.
4. **Validate**: `python scripts/validate-uc-fpt.py <file.md> [--registry ids.txt]`, then the checklist. `ids.txt` is any text file listing the registered BR-xx and MSGnn ids (for example exported from SRS sections 5.1 and 5.2).
5. **Deliver** a `.md` file named `UC-NN_<kebab-name>.md` (or one file per feature group), plus the list of new rules/messages that still need registering.

## Rules that differ from company work

- Cite rules and messages by id, never by text. **Never invent ids.** When a message or rule does not exist yet, write `MSG??` / `BR-??` with the intended text and list it under "To register".
- No Priority, Frequency, Exceptions, Includes, Special Requirements, Assumptions or Notes rows. Failures and variants both go into Alternative Flow; a reusable sub-flow is referenced as a Normal Flow step. Non-functional needs go to the NFR section, not the UC.
- Every flow step starts with its subject (`The user opens ...`, `The system displays ...`); never a bare verb, never passive; step 1 is the primary actor's action.
- Ids: global `UC-NN` in the catalog, heading `2.<group>.<n>` in the spec.
- UC steps hold behavior only; field lists and layout belong to the screen spec (SRS section 3).

## Convert

FPT -> company (to `uc-company`): Normal Flow becomes Normal Course; Alternative Flow variants become `UC-XX-YY.AC.n`, failures become `UC-XX-YY.EX.n` (Trigger / Response / Final state); `BR-xx` become Special Requirements or Assumptions in words; `MSGnn` become message text or Notes; Priority, Frequency, Includes and Notes must come from the BA, never invented.
Company -> FPT: merge AC and EX into `Step N_<name>` blocks; drop Priority, Frequency, Special Requirements; turn Includes into Normal Flow steps; replace message text by registered `MSGnn`.

## Attribution

Method (scoping rules, identification techniques, writing style) inherited from `uc-company` (BA Zone use-case-writer by Phuc NT); keep attribution when redistributing.
