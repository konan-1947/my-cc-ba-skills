---
name: srs-screen-spec
description: Write screen specifications for SRS section 3 "Functional Requirements" - per screen a purpose paragraph, Mapped Use Case(s), the "screen allows the role to:" capability list and a Field Description table - and validate them against the UC catalog. Use for "viết đặc tả màn hình", "Field Description", "Functional Requirements theo màn hình", "mapped use case", "screen spec cho SRS", section 3.x. Companion of uc-fpt (behavior) and srs-br-msg (ids). Not for UI mockups (use prototype / frontend-design).
---

# SRS section 3: screen specifications

The sample SRS has 56 screens (3.1 Lesson ... 3.10 User), 52 with a Field Description table. A screen spec is the bridge between UC behavior (section 2) and the UI: it says what each screen offers and what every field/control means, without styling.

## Files

- [templates/screen-spec-template.md](templates/screen-spec-template.md): blank template with rules.
- [templates/screen-spec-example.md](templates/screen-spec-example.md): filled example (3.1.1 Create lesson).
- `scripts/validate-screen-spec.py`: validator.

## Workflow

1. **Inputs**: the UC catalog (ids), the UC specs of the feature group, and the screen list (from screen flows, SRS 1.4.1, and the authorization matrix, 1.4.2). Ask for missing inputs; do not invent screens.
2. **One screen at a time**, section numbering `3.<group>.<n>[.<m>]` where the group matches the section 2 feature group (Lesson, Slide, Homework, Landing Page, Authorization, Blog, Class, Simulation Hub, Community Hub, User).
3. **Fill the template**:
   - Purpose: context the screen sets up, the user's decision, what the system does next.
   - **Mapped Use Case(s)**: every UC whose steps happen on this screen (a screen may map several; a UC may span several screens). Use `Non-UI` only for functions without a screen.
   - "The <screen> screen allows the <Role> to:" 3-8 capability bullets, in the order a user does them.
   - **Field Description**: every visible field, control, display element and button, in screen order. Description starts with a verb. Cite constraints and messages by id (`MSG220`, `BR-10`), never by text.
4. **Validate**: `python scripts/validate-screen-spec.py screens/ --catalog uc-catalog.md`
   - ERROR: missing purpose / Mapped Use Case(s) / capability list / Field Description, empty descriptions, unknown UC id.
   - WARN: description without a verb, styling detail, catalog UC mapped by no screen.
5. **Cross-check ids** with `srs-br-msg` (`check-refs.py --scan screens/`).

## Basis of these rules

The four-part screen layout (purpose, Mapped Use Case(s), capability list, Field Description) is inferred from the EDUA SRS; it is a convention, adjust it to the project's template. What is universal: every UC is traced to a screen or marked Non-UI, descriptions state behavior not styling, names match the UC steps.

## Rules

- Behavior only: no colors, pixel sizes, positions, fonts. Layout belongs to the prototype.
- Names are the labels the user sees; keep them identical across screen spec, UC steps and screen flow.
- Each role-specific capability names the role (Teacher / Moderator / Student); roles come from SRS 1.3.1.
- Every UC-nn is mapped to at least one screen, or is explicitly Non-UI (and listed in 1.4.3 Non-UI Functions).
- Editors and nested screens (outline preview, deck editor) get their own sub-heading.
- Keep the UC step text out of the screen spec; link by id.
