---
name: diagramming
description: Unified skill for creating, importing, editing and reviewing diagrams of any kind - business process, workflow, flowchart, swimlane, DFD, sequence, state machine, ER/database schema, UML class, architecture, deployment, BPMN, network topology, mind map, org chart, timeline, Gantt, roadmap and 50+ chart/diagram types. Routes between three engines - presentation-grade HTML/SVG/PNG (with import from .drawio, Mermaid, Excalidraw, PlantUML), editable draw.io files (.drawio, .drawio.svg, .drawio.png), and hand-drawn Excalidraw files (.excalidraw) - and applies process-diagram governance rules. Use whenever a request says draw, diagram, visualise, flow, sơ đồ, vẽ sơ đồ, lưu đồ, mind map, or when a document needs a graph rather than more paragraphs.
---

# Diagramming

One entry point for all diagram work: decide, choose engine, choose type, draw, validate, deliver.

## Step 1 - Decide whether to draw

If a table, list, or 3-4 numbered steps says the same thing, do not draw. Full rules (one question per diagram, behavior not implementation, error paths, source-not-pictures, same-change maintenance): [references/process-governance.md](references/process-governance.md). Apply them whichever engine is used.

## Step 2 - Dedicated skills first

For SRS-style **use case diagrams** use the `usecase-diagram` skill; for **flowcharts and BPMN swimlane processes** use `flowchart-bpmn` (both generate `.drawio` plus SVG from a JSON spec with clean layout). Use the engines below for everything else (ERD, context, architecture, deployment, charts, mind maps, hand-drawn sketches, import/export).

## Step 2b - Choose the engine

| The user needs | Engine | Load |
|---|---|---|
| Polished, branded, read-only visual (docs, slides, reports); charts; any of the 50 types; PNG/SVG export | **html-svg** | [engines/html-svg/ENGINE.md](engines/html-svg/ENGINE.md) |
| A file others keep editing in draw.io (`.drawio`, `.drawio.svg`, `.drawio.png`); BPMN, network topology; edit an existing `.drawio` | **drawio** | [engines/drawio/ENGINE.md](engines/drawio/ENGINE.md) |
| Hand-drawn, workshop / brainstorm style, quick sketch editable on excalidraw.com; DFD; mind map; cloud icons from `.excalidrawlib` | **excalidraw** | [engines/excalidraw/ENGINE.md](engines/excalidraw/ENGINE.md) |
| Redraw / beautify an existing `.drawio`, Mermaid, Excalidraw or PlantUML diagram | **html-svg** (import, ENGINE.md section 11) | |
| A presentable picture AND an editable source | Draw the editable source first (drawio or excalidraw), then redraw in **html-svg** | both |

If unclear, ask one question: "Does it need to stay editable (draw.io / Excalidraw) or is it a finished visual?" If the user cannot be asked: **drawio** for maintained process/BA artifacts, **excalidraw** for brainstorm sketches, **html-svg** for presentation visuals.

## Step 3 - Choose the type

| Need | html-svg | drawio | excalidraw |
|---|---|---|---|
| Decisions and branches | flowchart | Flowchart | Flowchart |
| Handoffs between roles/teams | swimlane, process | swimlane / BPMN | Business flow (swimlane) |
| Data moving between sources, processes, stores | data-flow | flowchart + cylinders | Data flow (DFD) |
| Message order between actors | sequence | Sequence | Sequence |
| Lifecycle / statuses | state | flowchart with states | Flowchart |
| Data model | er, db-schema | ER Diagram | ER |
| Classes | uml-class | UML Class | Class |
| System structure | architecture, deployment, layers | Architecture | Relationship / Architecture |
| Concept hierarchy | tree, nested | Mind Map | Mind map |
| Charts, Gantt, Sankey, Wardley, roadmap, ... | 50-type guide in ENGINE.md | shape libraries | not supported |

## Step 4 - Draw and validate

Follow the loaded engine's workflow and use its validator before delivering:

| Engine | Validator |
|---|---|
| html-svg | `python scripts/self_check.py <file>` and `python scripts/verify_geometry.py <file>` |
| drawio | `python scripts/validate-drawio.py <file>` |
| excalidraw | `python scripts/validate-excalidraw.py <file>` |

Engine paths are relative to the engine directory. Common limits: about 9 nodes for html-svg, about 40 cells for drawio, about 20 elements for excalidraw; above that split into overview plus detail.

## Step 5 - Deliver

Give the file path, one sentence on what it shows, how to open it, the validator result, and anything inferred rather than confirmed. Keep the editable source; export PNG/SVG only when asked (PNG export needs `playwright`).

## Layout

```
diagramming/
  SKILL.md                           router (this file)
  references/process-governance.md   when/what to draw, behavior-level rules, maintenance
  engines/html-svg/                  HTML/SVG/PNG: 50 types, templates, import + export scripts
  engines/drawio/                    draw.io XML: recipes, templates, validator
  engines/excalidraw/                Excalidraw JSON: 8 templates, validator, icon + arrow scripts
```
