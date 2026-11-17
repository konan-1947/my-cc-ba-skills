# Usage, limits and provenance (from the upstream README)

## Trigger phrases

English: "Write a use case for [feature]", "Draft a UC for [functionality]", "Split this feature into a UC list", "Review my UC", "Write the Normal Course for this UC".
Vietnamese (reply in Vietnamese, UC artifact in English): "Viết use case cho [tính năng]", "Viết UC cho chức năng này", "Tách feature này thành UC list", "Review UC này giúp tôi", "Đặc tả use case cho [tính năng]".

## Example interaction (sequential mode)

```
User: Viết UC cho tính năng đặt lịch mentor 1-on-1

Assistant:
[Step 1] Mode: A (write new from feature description).
[Step 2] Scope: Primary actor: Learner (Premium subscriber). Goal: Book a 1-on-1 mentor session.
         System boundary: BA Zone Platform. Confirm to proceed to Step 3?

User: yes

Assistant: [Group 1: Identification + Actor + Description]
| Use Case ID: | UC-MENTOR-01 |
| Use Case Name: | Book 1-on-1 mentor session |
| ...
Group 1 done. Confirm to proceed to preconditions, postconditions, priority, frequency?
[... continues group by group, then the 20-point validation ...]
```

## This skill does NOT do

- Agile user stories: use `ba-zone-user-story-ac-writer`.
- Full PRD / URD / SRS documents: a UC is one section. For FPT capstone SRS use cases use `uc-fpt`.
- UML use case diagrams (text specs only): use the `diagramming` skill.
- Wireframes or UI mockups: a UC describes interaction, not visual design.
- Business process models: a business process spans many actors and systems; a UC is one actor and one system.

## Provenance and attribution

- Upstream: https://github.com/phucnt-bazone-vietnam/use-case-writer (MIT; also https://github.com/ba-zone). Version 1.0.0, 2026-05-14 (see `../CHANGELOG.md`).
- Author: **Phúc NT** · BA Zone (https://bazone.vn) · Digital School. The licence requires that any redistribution, in whole or in part, keeps this attribution (see `../LICENSE`).
- This folder is a derived copy with these local additions: skill renamed `uc-company`, optional `Trigger` row in `assets/uc-template.md`, `references/uc-writing-guide.md`, `references/examples-generic.md`, this file. The upstream README (installation options, bilingual feature overview) was not copied; re-clone the upstream repo for it.
