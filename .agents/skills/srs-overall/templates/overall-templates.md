# Templates for SRS section 1 "Overall Requirements"

## 1.1 Context Diagram (narrative under the diagram)

Paragraphs, in order:
1. Purpose: "The context diagram below illustrates the external entities (system actors and connected services) that interface with <System> and the data flows between them."
2. Human actors outside the boundary: "<N> human actors sit outside the system boundary: <A>, <B>, ... <A> submits ... ; <B> reviews ..."
3. External systems: "<K> external systems complete the boundary. <Service>, the <role>, receives <labeled flow> and returns <labeled flow>."
4. Flow convention: "Each connection is a labeled, directional data flow crossing the system boundary, for example "<flow name>" from <X> to <Y>."

Diagram: context diagram (one process = the system, external entities, labeled flows). Draw with `diagramming` (data-flow / architecture type).

## 1.2 Main Workflows

### 1.2.<n> <Process name>

Description: <one or two sentences: goal, actors, trigger, result>

| # | Actor | Condition | Action |
|---|---|---|---|
| 1 | <role/system> | None | <what the actor does or the system does; one action> |
| 2 | System | None | <...> |
| 3 | AI/LLM | None | <...> |
| 4 | System | Not generated successfully | <error handling with Retry option> |
| 4a | Teacher | Not generated successfully | Selects Retry; the workflow returns to Step 2. |
| 5 | System | Generated successfully | <next step> |

Rules: `Actor` is a lane (role, System, or external service); `Condition` is `None` or the outcome that selects this row; branch rows reuse the step number with a letter suffix; the last rows state the final saved state. Then draw the process with `flowchart-bpmn`.

## 1.3.1 Actors

| # | Actor | Description |
|---|---|---|
| 1 | <Actor> | <Who they are, scope (subject/grade), what they may do.> |
| 2 | <Specialization> | <Role description. Inherits all capabilities of <Parent>.> |

Rules: human roles and external systems both listed; specializations state inheritance; names are used verbatim in every later section.

## 1.3.2 Use Cases (UC catalog)

| ID | Use Case | Feature | Use Case Description |
|---|---|---|---|
| UC-01 | <Verb + Object> | <Feature group> | <2-3 sentences: actor does X, system does Y, outcome> |

Rules: ids sequential and global; `Feature` = the section 2 group; wording summarizes the UC spec (`uc-fpt`).

## 1.3.3 Use Case Diagrams

One heading per role or group: `1.3.3.1 UCs for User`, `1.3.3.2 UCs for IT Support Staff`, ... one diagram each, built with `usecase-diagram`.

## 1.4.1 Screens Flow

One heading per role: `1.4.1.<n> Screens Flow for <Role>`, one navigation flow diagram each (screens as nodes, user actions as labeled transitions), built with `flowchart-bpmn` (type flowchart) or `diagramming`.

## 1.4.2 Screen Authorization

| Screen | <Role 1> | <Role 2> | <Role 3> | ... |
|---|---|---|---|---|
| Landing Page | X | X | X | X |
| <Screen> | X |  |  |  |

Rules: one row per screen of section 3 (same names); `X` = the role may open the screen; blank = not allowed; role columns equal the actors of 1.3.1 that sign in.

## 1.4.3 Non-UI Functions

| # | Feature | System Function | Description |
|---|---|---|---|
| 1 | <Feature> | <Function name> | <What the system does without a screen: integration, scheduled job, authorization resolution, notification dispatch.> |

## 1.5 Entity Relationship Diagram

ERD drawn with `diagramming` (er / db-schema type) plus:

| # | Entity | Description |
|---|---|---|
| 1 | <table_name> | <What it stores; key fields.> |
