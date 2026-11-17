---
name: flowchart-bpmn
description: Draw flowcharts (top-down) and BPMN-style swimlane processes (lanes per actor, start/end events, tasks, exclusive gateways, sub-processes, data stores, retry loops) as editable draw.io files plus an SVG preview, generated from a JSON spec; includes how to turn an SRS workflow table (Actor / Condition / Action) into a diagram. Use for SRS section 1.2 "Main Workflows", screen/process flows, "vẽ flowchart", "vẽ BPMN", "sơ đồ quy trình có swimlane", "lưu đồ". Not for use case diagrams (use usecase-diagram) or ERD/architecture/charts (use diagramming).
---

# Flowchart and BPMN

Generates `.drawio` and optional `.svg` from a JSON spec. Notation follows the SRS workflow tables: each step has an **actor** (becomes the lane), a **condition** (becomes the gateway or flow label) and an **action** (becomes the task).

## Choose the type

| Need | `type` |
|---|---|
| Logic/decisions of one actor or one system, top-down | `flowchart` |
| Process across actors/systems with responsibilities, handoffs, retries | `bpmn` (lanes, left-to-right) |

## Workflow

1. **Collect the steps** (from the SRS workflow table or the UC Normal/Alternative Flow): actor, action, condition, next step.
2. **Write the spec** (copy `templates/spec-bpmn-example.json` or `spec-flowchart-example.json`):
   - `lanes`: one per actor (Teacher, System, AI/LLM); the order shown is the order drawn.
   - `nodes`: `start`, `end`, `end-error`, `task`, `subprocess`, `gateway`, `datastore`, `document`; each with `id`, `name`, `lane` (bpmn).
   - `flows`: `from`, `to`, optional `label`, optional `"style": "dashed"`.
3. **Build**: `python scripts/build_flow.py spec.json out.drawio --svg out.svg`
4. **Validate**: `python scripts/validate-drawio.py out.drawio`; the builder also warns about missing start/end, dead ends, nodes without input, gateway branches without a label, and more than 25 nodes.
5. **Review** the SVG against the source steps, then deliver both files with the SRS section (for example 1.2.3).

## Mapping the SRS workflow table

| Table cell | Diagram |
|---|---|
| `Actor` | lane of the task |
| `Action` | task name (short verb phrase; keep the full sentence in the table) |
| `Condition` = `None` | plain sequence flow |
| `Condition` = outcome ("Generated successfully" / "Not generated successfully") | gateway after the previous task, one labeled flow per outcome |
| Step `4a` (actor retries) | flow back to the earlier step labeled `Retry` |
| Final steps | `end` (success) and `end-error` (failure path that stops) |

The table stays the source of truth for wording; the diagram carries branching. Every branch in the table must appear as a flow, and every flow must come from the table.

## Notation rules

- One **start**; at least one **end**; failures that stop the process end in `end-error`.
- Gateways (exclusive, `X`) ask a question in the name ("Generated?") and every outgoing flow has a condition label.
- Tasks are verb phrases of one actor; a step done by another actor goes into that actor's lane.
- Draw error and retry paths where behavior differs from the happy path.
- Above about 20 tasks, split into sub-processes (`subprocess` node pointing to a detail diagram).
- Participants are systems, roles and modules, never classes or methods (see `diagramming/references/process-governance.md`).

## Limits

Automatic layout: lanes in order, one column per rank, back edges routed below. Crossing flows in dense diagrams may need manual tidying in draw.io. The SVG preview routes edges slightly differently from draw.io.
