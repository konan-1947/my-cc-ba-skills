> Engine file of the `diagramming` skill. Paths below are relative to this directory (`engines/excalidraw/`).

# Excalidraw engine

Generates `.excalidraw` JSON (hand-drawn look) from a description. Open at https://excalidraw.com (Open / drag-drop) or in the Excalidraw VS Code extension. Best for workshops, brainstorming, quick shared sketches, DFDs and swimlanes people will keep editing in Excalidraw.

## Types and templates

| Intent | Type | Template |
|---|---|---|
| Steps, procedure, decisions | Flowchart | `templates/flowchart-template.excalidraw` |
| Entities and links, dependencies | Relationship | `templates/relationship-template.excalidraw` |
| Concept hierarchy, brainstorm | Mind map | `templates/mindmap-template.excalidraw` |
| Data movement between sources, processes, stores | Data flow (DFD) | `templates/data-flow-diagram-template.excalidraw` |
| Cross-functional process, actor responsibilities | Business flow (swimlane) | `templates/business-flow-swimlane-template.excalidraw` |
| Object model | Class | `templates/class-diagram-template.excalidraw` |
| Messages over time | Sequence | `templates/sequence-diagram-template.excalidraw` |
| Database model | ER | `templates/er-diagram-template.excalidraw` |
| System components | Architecture | start from relationship / flowchart template |

Not covered here (use another engine): charts, Gantt, Sankey, 50-type catalog (html-svg); BPMN, network topology (drawio).

## What to extract per type

- **Flowchart**: ordered steps, decision points, start/end.
- **Relationship**: entities (name, optional description); relations (from, to, label).
- **Mind map**: central topic; 3-6 branches; 2-4 sub-topics each.
- **DFD**: external entities, processes (transformations), data stores, data flows. Arrows show data movement only, never process order; lay out left-to-right or top-left to bottom-right.
- **Swimlane**: actors as header columns, one lane each, activity boxes inside lanes, arrows including cross-lane handoffs.
- **Class**: names, attributes and methods with visibility (+ - #), relations (inheritance: solid + hollow triangle; implementation: dashed + hollow triangle; association: solid; dependency: dashed; aggregation: hollow diamond; composition: filled diamond), multiplicity (1, 0..1, 1..*, *).
- **Sequence**: actors across the top, lifelines, sync (solid) / async and return (dashed) messages, activation boxes, time top to bottom.
- **ER**: entities, attributes with PK/FK, cardinality 1:1 / 1:N / N:M, junction entities (dashed) for N:M.

## Workflow

1. Apply the governance rules (`../../references/process-governance.md`): one question per diagram, behavior level, error paths drawn.
2. Pick type, extract elements, copy the closest template.
3. Write elements (see `references/excalidraw-schema.md`, `references/element-types.md`). Use types `rectangle`, `ellipse`, `diamond`, `arrow`, `line`, `text`.
4. File skeleton:
   ```json
   { "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
     "elements": [], "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }, "files": {} }
   ```
5. **Validate**: `python scripts/validate-excalidraw.py <file> [--strict]`. Fix every ERROR; fix WARNs unless justified.
6. Save as `<descriptive-kebab-name>.excalidraw` and tell the user how to open it (see Output).

## Rules

- **Every text element: `fontFamily: 5` (Excalifont)**, `fontSize >= 16` (16-24).
- **Bind arrows to shapes** (`startBinding` / `endBinding` with the shape's `elementId`, and list the arrow in the shape's `boundElements`), so they follow when shapes move. Unbound arrows are acceptable only for decorative lines.
- Unique ids on every element.
- Spacing: 200-300 px horizontal, 100-150 px vertical; use a grid (columns = ceil(sqrt(n))) for relationship diagrams, radial (angle = 2*pi*i/n) for mind maps.
- Palette, used consistently: primary `#a5d8ff`, secondary `#b2f2bb`, central/important `#ffd43b`, alert `#ffc9c9`. Focal color on 1-2 elements only.
- Size budget: flowchart 3-10 steps (max 15), relationship 3-8 entities (max 12), mind map 4-6 branches (max 8), at most about 20 elements per diagram. Above that, propose an overview plus detail diagrams instead of one crowded one.
- Remove test: delete any node or arrow whose removal does not change what the reader understands.
- Troubleshooting: overlap, so increase spacing; text overflow, so widen the box or lower font size; unclear layout, so use grid or radial.

## Icons (optional: AWS / GCP / Azure / K8s etc.)

Icon libraries are not bundled. If the user wants real icons:
1. Check `libraries/<name>/reference.md` exists. If not, tell the user: download the `.excalidrawlib` from https://libraries.excalidraw.com/, put it in `engines/excalidraw/libraries/<name>/<name>.excalidrawlib`, then run
   `python scripts/split-excalidraw-library.py libraries/<name>/`
   (offer to continue with plain shapes meanwhile).
2. Build the base diagram, then add icons with scripts (icon JSON never enters context, ids and coordinates are handled for you):
   ```bash
   python scripts/add-icon-to-diagram.py <diagram> <icon-name> <x> <y> [--label "Text"] [--library-path PATH]
   python scripts/add-arrow.py <diagram> <from-x> <from-y> <to-x> <to-y> [--label "Text"] [--style solid|dashed|dotted] [--color HEX]
   ```
   Both edit through a `.excalidraw.edit` copy by default (avoids editor overwrite); `--no-use-edit-suffix` disables that. `add-arrow.py` makes unbound arrows, so re-run the validator and bind them if the diagram will be edited.
3. Manual icon insertion (reading icon JSON) costs thousands of lines of context; use only if Python is unavailable.
4. No libraries: use shapes plus color and labels.

## Output

Deliver: the `.excalidraw` path, a one-sentence summary (type, element counts), assumptions or inferred items, validator result, and how to open it (excalidraw.com > Open or drag-drop; or VS Code extension).

## Validation checklist

- [ ] Valid JSON, `"type": "excalidraw"`, unique ids
- [ ] All text `fontFamily: 5`, size >= 16
- [ ] Arrows bound to shapes, directions match the intended flow
- [ ] No overlaps; consistent palette; <= ~20 elements
- [ ] `validate-excalidraw.py` passes

## References

`references/excalidraw-schema.md` (full JSON schema), `references/element-types.md` (element specs), `templates/` (8 starters), `scripts/` (validator, add-icon, add-arrow, library splitter, README).
