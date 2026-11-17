---
name: srs-overall
description: Write SRS section 1 "Overall Requirements" - context diagram narrative, main workflow tables (Actor / Condition / Action), actors, UC catalog, use case diagram and screen-flow headings, screen authorization matrix, non-UI functions, entity table for the ERD - and check the tables for consistency with a script. Use for "viết phần Overall Requirements", "bảng workflow", "danh sách actor", "UC catalog", "bảng phân quyền màn hình", "Non-UI functions", "context diagram mô tả", SRS section 1.1-1.5. Delegates diagrams to usecase-diagram, flowchart-bpmn and diagramming.
---

# SRS section 1: Overall Requirements

Section 1 frames the whole document: who the actors are, what the main flows are, which UCs exist, which screens each role can open, which functions have no UI, and the data model. Everything later (UC specs, screens, rules) refers back to its names and ids.

## Files

- [templates/overall-templates.md](templates/overall-templates.md): templates and rules for 1.1 to 1.5.
- `scripts/check-overall.py`: consistency checker for the tables.

## Sub-sections and who does what

| Part | Content | Produced with |
|---|---|---|
| 1.1 Context Diagram | narrative + diagram | text from the template; diagram with `diagramming` (data-flow / architecture) |
| 1.2 Main Workflows | description + Actor/Condition/Action table per workflow | table from the template; diagram with `flowchart-bpmn` |
| 1.3.1 Actors | `# / Actor / Description` | template |
| 1.3.2 UC catalog | `ID / Use Case / Feature / Description` | template; wording summarizes `uc-fpt` specs |
| 1.3.3 Use Case Diagrams | one diagram per role/group | `usecase-diagram` |
| 1.4.1 Screens Flow | one diagram per role | `flowchart-bpmn` (flowchart) |
| 1.4.2 Screen Authorization | Screen x Role matrix of `X` | template |
| 1.4.3 Non-UI Functions | `# / Feature / System Function / Description` | template |
| 1.5 ERD | diagram + entity table | `diagramming` (er / db-schema) |

## Workflow

1. Ask for the product scope, roles, external services and the main business flows. Do not invent actors or services.
2. Write in this order, because later parts depend on earlier names: 1.3.1 Actors -> 1.2 Workflows -> 1.3.2 UC catalog -> 1.1 Context narrative -> 1.4.3 Non-UI -> 1.5 entities -> then, after section 3 exists, 1.4.2 Authorization and 1.4.1 flows.
3. Draw the diagrams with the delegated skills; keep captions as the section headings.
4. Check: `python scripts/check-overall.py section1.md [--screens screens-dir]`
   - ERROR: duplicate actor or UC id, workflow step numbering broken or branch not following its step, incomplete rows, authorization column that is not an actor.
   - WARN: UC id gaps or order, UC name not Verb + Object (single-word names such as Login are usually fine), screen allowed for no role, screen missing from or extra in the authorization matrix versus section 3.

## Basis of these rules

The table layouts come from the EDUA capstone SRS and are conventions, not standards; adjust them to the project's template. What is universal: names and ids are used identically everywhere, every UC is traceable to a screen or a non-UI function, actors are roles or external systems, workflow steps are one action by one actor.

## Rules

- Names are used verbatim everywhere: actors (1.3.1) in workflows, authorization columns, UC specs and screen specs; screens (section 3 headings) in the matrix and flows.
- A workflow table row is one action by one actor; outcomes are in `Condition`; retries are lettered rows.
- The catalog row is a summary; the UC spec (`uc-fpt`) holds the behavior.
- The authorization matrix lists screens, not UCs; backend-only capabilities go to 1.4.3.
- Every UC-nn in the catalog is either mapped by a screen (section 3) or has a row in 1.4.3.
