---
name: srs-br-msg
description: Write and maintain the SRS appendix (section 5) - Business Rules register (BR-xx) and System Messages register (MSGnn with type, context, UI text) - allocate next ids without collisions, and cross-check that every BR/MSG cited in use cases, screen specs and NFRs is registered and every registered one is used. Use for "viết Business Rules", "viết System Messages", "đăng ký MSG mới", "kiểm tra BR/MSG có trong UC không", "sổ BR/MSG", SRS section 5.1 / 5.2. Companion of uc-fpt and srs-screen-spec.
---

# SRS section 5: Business Rules and System Messages

The registers are the single source of truth for ids. UC specs, screen specs and NFRs only cite ids (`BR-10`, `MSG164`); wording lives here.

## Files

- [templates/registry-templates.md](templates/registry-templates.md): table formats for 5.1 and 5.2 with examples from the EDUA SRS.
- `scripts/check-refs.py`: cross-reference checker.

## Workflow

1. **Collect rules and messages** while writing UCs and screens. A *business rule* is a constraint or policy independent of the screen (who may do what, limits, lifecycle). A *system message* is every user-facing feedback: validation, confirmation, error, empty state, button state.
2. **Register**
   - Next id = highest existing + 1 (never reuse or renumber published ids; the sample SRS has about 18 BR and 220 MSG).
   - BR: one rule per row, one sentence, testable ("may / must / may not ... when ...").
   - MSG: `# | Message code | Message Type | Context | Content`. Type: Inline (with placement), Toast, Toast (error), Popup, Confirmation popup, Dialog, Banner, Button state, Status label, Email, Notification. Context names the trigger so it matches the citing UC step. Content is the exact UI text in the product language, with placeholders in brackets.
   - Reuse an existing message when the context and wording are the same (for example the shared "required field is empty" inline message) instead of creating near-duplicates.
3. **Resolve placeholders**: `uc-fpt` writes `MSG??` / `BR-??` for anything not yet registered. Register them, then replace the placeholders in the documents with the new ids.
4. **Check**: `python scripts/check-refs.py --registry br-registry.md msg-registry.md --scan uc/ screens/ nfr.md`
   - ERROR: cited but not registered; duplicate id; invalid message type.
   - WARN: registered but never cited; numbering gaps.
   - TODO: placeholders still to register.
   Run before every delivery and after any renumbering (renumbering needs a search-and-replace over all documents).

## Basis of these rules

Register formats and the message-type vocabulary come from the EDUA SRS and are conventions. What is universal: every cited id is registered, ids are unique and never reused, a rule states one testable constraint.

## Rules

- Never invent an id inside a UC or screen document; register first.
- One message per situation: Inline for field validation, Toast for operation result, Popup/Dialog when the user must decide, Button state for in-progress labels.
- A rule that only restates a screen detail (field order, color) is not a business rule.
- Rules referenced by role names must match the actor names of SRS section 1.3.1.
