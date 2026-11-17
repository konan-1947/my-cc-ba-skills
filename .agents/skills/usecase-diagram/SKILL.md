---
name: usecase-diagram
description: Draw UML use case diagrams (actors, system boundary, use case ellipses, associations, include/extend, actor generalization) as editable draw.io files plus an SVG preview, generated from a small JSON spec so the layout is clean and ids are consistent with the UC catalog. Use for SRS section 1.3.3 "Use Case Diagrams" (one diagram per role or feature group), "vẽ use case diagram", "sơ đồ use case cho Teacher/Moderator", "UC diagram từ danh sách UC". Not for flowcharts/BPMN (use flowchart-bpmn) or other diagram types (use diagramming).
---

# Use case diagram

Generates `.drawio` (editable in draw.io / VS Code) and optional `.svg` from a JSON spec. Aligned with the SRS: UC names and ids come from the UC catalog (section 1.3.2), one diagram per role or feature group (EDUA: User, IT Support Staff, Moderator, Teacher with Math/Physics/Chemistry specializations, Student, Principal).

## Workflow

1. **Collect** from the UC catalog: the actors of the target role, and the UCs they perform (ids and names exactly as in the catalog). Secondary actors (AI/LLM Service, Google OAuth) appear on the right side.
2. **Write the spec** (copy `templates/spec-example.json`). Fields: `title` (for example `1.3.3.4 UCs for Teacher`), `system`, `actors` (`id`, `name`, `side`, optional `parent` for generalization), `usecases` (`id`, `name`), `links` (actor-uc), `includes` (`from` base -> `to` included), `extends` (`from` extension -> `to` base).
3. **Build**: `python scripts/build_ucd.py spec.json out.drawio --svg out.svg`
4. **Validate**: `python scripts/validate-drawio.py out.drawio`. The builder itself fails on duplicate or unknown ids and warns on orphan use cases and on more than 20 use cases.
5. **Check** the SVG visually (open in a browser) and the rules below, then deliver both files and name the SRS section they belong to.

## Modeling rules

- **Actors** are roles or external systems with goals, never internal components. Use a specialization (`parent`) when a role inherits all capabilities of another (Math Teacher inherits Teacher): draw the generalization once instead of repeating every link.
- **Use case names**: Verb + Object, identical to the catalog (UC-nn).
- **Include** = mandatory sub-behavior reused by several UCs (`Create Lesson Plan` includes `Login` only if login is a step of it; shared authentication is usually a precondition, so do not draw it unless the SRS does). **Extend** = optional behavior added under a condition.
- Keep **one diagram per role or feature group**; above about 15-20 use cases, split.
- No UI detail, no process order; that is flowchart-bpmn.
- The diagram must cover exactly the UCs the SRS section 2 specifies for that role: no extra, none missing (cross-check with the catalog).

## Output

`.drawio` is the source (commit it). `.svg` is a preview for review and for pasting into Word. Name files `ucd-<role>.drawio`. State assumptions (for example roles drawn by inheritance).

## Limits

The layout is automatic: straight association lines, system box with 1-3 columns of use cases, actors left and right. Dense diagrams may need manual tidying in draw.io. The SVG preview and the draw.io rendering differ slightly in routing.
