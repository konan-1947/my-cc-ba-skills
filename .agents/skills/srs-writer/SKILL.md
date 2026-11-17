---
name: srs-writer
description: Single entry point for SRS work, in the FPT University capstone (EDUA Report 3) structure, directly on a Word file - import an existing SRS .docx into Markdown parts, audit the whole document (UC specs, screens, NFR, BR/MSG references, catalog vs section 2, authorization matrix, empty headings) with one report, edit the .docx in place (replace text, delete empty headings, add a UC by cloning the document's own UC table), write new parts from scratch, and rebuild/export Word and PDF. Use for "kiểm tra file SRS này", "audit SRS Report 3", "sửa trực tiếp file Word SRS", "thêm use case vào file Word", "đọc file docx SRS", "viết SRS", "SRS đã đủ chưa", "record of changes", or when the user sends a Word SRS and asks what is wrong or to continue it. Delegates to uc-fpt, srs-overall, srs-screen-spec, srs-nfr, srs-br-msg, usecase-diagram, flowchart-bpmn, diagramming, srs-docx-builder.
---

# SRS writer: one entry point, works on the Word file

Structure taken from `EDUA Report 3 - SRS v1.2` (110 UC tables, 52 screen specs, 5 workflows, 18 business rules, 220 messages). The Word file the user sends is always read-only input: every write goes to a new file.

## Choose the mode

| The user says / has | Mode | Command |
|---|---|---|
| Sends a Word SRS: "what is wrong", "check it", "continue it" | **Audit** | `python scripts/audit_srs.py in.docx [workdir]` |
| Wants it as editable text parts | **Import** | `python scripts/import_docx.py in.docx outdir` |
| Wants a fix inside the Word file | **Edit in place** | `python scripts/docx_edit.py <replace\|fix-empty-headings\|add-uc> in.docx out.docx ...` |
| Starts a new SRS or a new part | **Write** | route each part with the table below |
| Wants the final Word / PDF | **Build** | `srs-docx-builder` (`build_srs_docx.py`, then `finalize-docx.ps1`) |

Scripts live in `scripts/` of this skill; sibling skills must be installed beside it (the audit calls their validators).

## Audit (start here for any existing file)

`audit_srs.py` imports the document, runs every validator and cross-check, and writes `audit-report.md` plus the imported Markdown parts:

| Check | What it finds |
|---|---|
| UC specs (`uc-fpt`) | missing rows, Primary Actor not in the actors table (1.3.1), Normal Flow too short or over 12 steps, Alternative Flow without `Step N_` blocks, BR/MSG ids not registered |
| BR/MSG references (`srs-br-msg`) | cited but unregistered ids, registered but never cited, duplicates, numbering gaps, invalid message types |
| Screen specs (`srs-screen-spec`) | missing purpose / Mapped Use Case(s) / capability list / Field Description, unknown UC ids, catalog UCs mapped by no screen (group headings without body are skipped) |
| Overall tables (`srs-overall`) | actor and UC id problems, workflow step numbering, authorization columns not actors, screens missing from section 3 (or the reverse) |
| NFR (`srs-nfr`) | id format, `shall`, measurability, vague words |
| Catalog vs section 2 | UCs in the catalog without a spec (and the reverse), name mismatches |
| Word structure | empty heading paragraphs (blank entries in the navigation pane) |

Read the report, separate **real defects** from **convention differences** (for example the authorization matrix names screens differently from section 3 headings: a naming inconsistency to confirm with the author, not necessarily an error), and tell the user which findings you would fix first. Never "fix" a finding by editing the document without the user's decision, except mechanical ones the user asked for.

## Edit in place (`docx_edit.py`)

- `replace --find X --replace Y [--regex]`: works across Word's split runs; keeps the first run's formatting. Use for renames (an actor name, an id); re-run the audit afterwards.
- `fix-empty-headings`: deletes heading paragraphs without text.
- `add-uc --after "2.2.3 Export Lesson Plan" --from uc.md`: inserts a new UC after the named one, cloning that UC's heading and 4-column table so fonts, borders, shading and spacing match; each cloned list gets its own numbering that restarts at 1. `uc.md` is the `uc-fpt` format. Afterwards: add the catalog row (1.3.2), register any new `BR-??` / `MSG??` (`srs-br-msg`), map a screen (section 3), update Record of Changes, and refresh the table of contents.
- Everything else in the file (images, styles, header/footer, numbering) is copied unchanged; the output is checked for well-formed XML. Still open the result in Word (or run `finalize-docx.ps1`) before sending it on.

## Write (part to skill map)

| SRS part | Skill | Validator |
|---|---|---|
| Record of Changes | this skill (below) | none |
| 1 Overall Requirements | `srs-overall` | `check-overall.py` |
| 1.2 workflow diagrams, 1.4.1 screen flows | `flowchart-bpmn` | `validate-drawio.py` |
| 1.3.3 use case diagrams | `usecase-diagram` | `validate-drawio.py` |
| 1.1 context, 1.5 ERD diagrams | `diagramming` | engine validators |
| 2 Use Case Specifications | `uc-fpt` (company format: `uc-company`) | `validate-uc-fpt.py` |
| 3 Functional Requirements (screens) | `srs-screen-spec` | `validate-screen-spec.py` |
| 4 Non-Functional Requirements | `srs-nfr` | `validate-nfr.py` |
| 5.1 Business Rules, 5.2 System Messages | `srs-br-msg` | `check-refs.py` |
| Word file and PDF | `srs-docx-builder` | Word finalize + page review |
| Discovery, user stories, AC (upstream) | `ba`, `user-story-ac-writer` | their checklists |

Writing order: scope -> actors (1.3.1) -> workflows and UC catalog -> section 2 UCs (placeholders `BR-??` / `MSG??`) -> register them (5) -> screens (3) -> authorization matrix and flows (1.4) -> NFR (4) -> diagrams -> Record of Changes -> `audit_srs.py` on the built file -> deliver.

## Record of Changes

| Date | A*M, D | In charge | Change Description |
|---|---|---|---|
| dd/mm/yyyy | A | <name> | Added section 1. Overall Requirements (Context Diagram, Main Workflows) |

`A` added, `M` modified, `D` deleted. One row per change batch, dated, naming the section and what changed. Append a row for every section added or reviewed section changed.

## Principles

- The user's Word file is evidence: read it, report on it, change only a copy, and only what was asked.
- Names and ids are shared across parts (actors 1.3.1, UC ids 1.3.2, screen names section 3, BR/MSG ids section 5); fix the source first, then the citing parts.
- Write behavior once (UC step in section 2, field meaning in section 3, rule in 5.1, message text in 5.2) and cite ids elsewhere.
- Never invent requirements, thresholds, actors, services or ids; ask, or mark `??` and list under "to register / to confirm".
- **A sample document is evidence, not the standard.** Never answer a field by copying how the sample wrote it. Derive each field by analysis of the function (who starts it, what outside the product it touches, what the actor wants and why, what must be true before and after) using `uc-fpt/references/field-analysis-guide.md`. Example: Secondary Actors are the external systems/services/devices a function touches, not extra human users; Description is `As a <role>, I want to <goal>, so that <benefit>` built from the analysis.
- Separate **standards** (traceability, one primary actor, measurable NFR, unique ids) from **conventions** (table layout, id prefixes, message vocabulary inferred from one file). Report standards as defects; report conventions only as differences for the author to decide. The audit report's Basis column says which is which.
- Validators encode both; where the user's document follows a different but consistent convention, say so instead of reporting hundreds of errors.
- Language: English text; UI message content may stay in the product language (as in the sample).

## Limits

- Import and audit read the structure the EDUA file uses (Heading styles, a 4-column UC table starting with "Primary Actors", register tables with the header names `ID | Rule Definition` and `# | Message code | ...`). A different layout may need adjusted headers.
- `add-uc` requires an existing UC table in the document to clone; it does not create the first one.
- Tested on the EDUA v1.2 file (110 UC tables, 177 tables, 75 images); other SRS documents may expose different conventions.
- Remaining gaps and statistics: [references/skill-gap.md](references/skill-gap.md).
