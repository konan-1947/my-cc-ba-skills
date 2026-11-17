# Process diagram governance

Rules for diagrams of business processes, workflows, lifecycles and system interactions.
They apply on top of whichever engine draws the diagram (`engines/html-svg`, `engines/drawio` or `engines/excalidraw`).

## Core principle

A diagram is a set of claims drawn instead of written; every box and arrow must be true.
Diagram the **behavior** (processes, lifecycles, interactions). The prose owns the reasoning; the diagram carries what prose serializes badly: branching, concurrency, state.

## Do not draw when

- A linear flow of 3-4 steps: write a numbered list.
- The diagram only restates adjacent prose.
- The content is data-driven charts (use the html-svg engine's chart types) or code structure (class/package layouts belong to the IDE).

## Pick the kind from the reader's question (one question per diagram)

| The reader asks | Draw | Engine type |
|---|---|---|
| How does this process run across the organization | Business process / swimlane view | html-svg `swimlane`, drawio swimlane/BPMN, excalidraw business flow |
| Where does data come from, how is it transformed, where is it stored | Data flow (arrows show data movement, never process order) | html-svg `data-flow`, excalidraw DFD |
| What happens, in what order, with which decisions | Activity / flowchart | `flowchart` |
| Which states can this thing be in, what moves it | State machine | `state` |
| Who talks to whom, in what order | Sequence | `sequence` |
| What exists in this domain and how it relates | Concept / ER at business-object level | `er` |

A diagram answering two questions answers neither: split it. A diagram needing a legend of invented symbols is answering too much.

## Behavior, never implementation

- Participants are systems, roles, modules, business objects. Never classes/methods.
- Edges carry the event or condition in domain language ("payment confirmed"), not a callback name.
- Titles name the process, never a spec, phase, or plan.
- Draw error/exception paths where behavior differs, visibly distinct. A happy-path-only diagram of a process with real failure branches overstates.
- Draw quirks: the state nothing can leave, the flow that skips a step for one input. The surprising branch is why the diagram exists.

## Source, not pictures

- Keep an editable source in version control: `.drawio` (drawio engine), `.excalidraw` (excalidraw engine) or HTML/SVG (html-svg engine); PlantUML/Mermaid when the repo already uses them.
- One diagram per file, named for the process, all in one `diagrams/` directory beside the docs.
- A screenshot or exported image with no source is a defect: nobody can diff or maintain it.
- Exported PNG/SVG are derived; delete stale exports when the source changes.

## Index (more than 5 diagrams)

One index document beside them: what each diagram shows, source file, export if committed, the module it describes (drift anchor), status.

## Maintenance and verification

- A change that alters a flow updates the matching diagram in the same change.
- Verify every box, arrow and guard against the real behavior (code, spec, SME) before drawing. If inferred rather than confirmed, say so beside the diagram.
- Review the source, not just the picture.
- Prose says why the process exists and what to watch for; the diagram shows the flow; neither restates the other step by step.
