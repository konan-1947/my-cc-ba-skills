---
name: srs-nfr
description: Write the Non-Functional Requirements section of an SRS (quality attributes, no external-interfaces subsection) as measurable, uniquely identified "shall" statements using a catalog of 16 quality attributes (availability, installability, integrity, interoperability, performance, reliability, robustness, safety, security, usability, efficiency, modifiability, portability, reusability, scalability, verifiability) with elicitation questions and requirement patterns, and validate ids, wording, measurability and attribute coverage with a script. Use for "viết non-functional requirements", "NFR cho SRS", "yêu cầu phi chức năng", "quality attributes", "thuộc tính chất lượng", "kiểm tra NFR có đo được không".
---

# SRS: non-functional requirements (quality attributes)

This section covers **quality attributes** only. External interfaces are not written here: describe screens in the functional requirements, and express data exchange with other systems as Interoperability (IOP).

## Files

- [references/quality-attributes.md](references/quality-attributes.md): the catalog of 16 attributes (from the user's `Quality Attributes.xlsx`): meaning, questions to ask, requirement pattern, whether a threshold is needed, when it applies, plus the source's example requirements (illustrations of the form, not templates).
- [templates/nfr-template.md](templates/nfr-template.md): section skeleton with placeholders to fill by analysis.
- `scripts/validate-nfr.py`: validator.

## Workflow

1. **Gather inputs**: functional scope (SRS sections 1-3), users and roles, data held, integrations, expected load and growth, constraints from the client or the course. Ask for numbers you lack; never invent thresholds.
2. **Screen the 16 attributes**: for each one decide *relevant* or *not relevant, and why* (the catalog's "Applies when" column helps). Not every product needs all of them; write an explicit `CODE: Not applicable - <reason>` line for those you drop, so a reader can tell "forgotten" from "decided".
3. **Elicit per relevant attribute** with the catalog's questions: what matters for **this** product, which functions, which data, which users, which numbers. Record the answers as notes first.
4. **Write each requirement** with the attribute's pattern: `CODE-NN: The system shall ...` (codes AVL INS INT IOP PER REL ROB SAF SEC USE EFF MOD POR REU SCA VER; two digits; per-attribute numbering from 01; never reuse an id).
   - One verifiable obligation per id; one `shall`.
   - A number with a unit (a percentage, a time, a count, a period) wherever the attribute needs one: AVL, PER, REL, ROB, SCA, SAF (error if missing); INS, EFF, USE normally too (warning if missing). Security, integrity, interoperability, portability and modifiability are often measured by named controls, formats, versions or times.
   - Put the assumptions in the requirement: the load, the environment, the provider conditions.
5. **Trade-offs**: where attributes pull against each other (performance vs security, portability vs efficiency), note the decision next to the requirements.
6. **Trace**: link each requirement to the UC or screen it constrains where relevant (by id); move a limit that is really a business rule into the business-rules register (`srs-br-msg`).
7. **Validate**: `python scripts/validate-nfr.py nfr.md [--strict]`
   - ERROR: unknown code, duplicate id, missing `shall`, missing threshold for AVL PER REL ROB SCA SAF.
   - WARN: vague words (fast, user-friendly, robust, appropriate, seamless...), several `shall` in one id, numbering gaps, an N/A declaration without a reason, an external-interface requirement (`INT-UI`, `INT-SW`...).
   - NOTE: attributes with neither a requirement nor an N/A declaration (check they were decided, not forgotten); alias codes (`PRF`, `USR`, `ITG`, `SCL`) accepted but the catalog code is preferred.

## Basis of these rules

The 16 attributes, their descriptions, questions and the example requirements come from the user's `Quality Attributes.xlsx`; the three-letter codes follow that file (note `INT` = Integrity). Patterns and the "applies when" hints are analysis added on top and marked as such in the catalog. Universal practice (ISO/IEC/IEEE 29148, ISO 25010): one verifiable requirement per id, unique stable ids, a measurable threshold for quality attributes. A project template that uses other codes (PRF, USR, ITG...) is a convention; the validator accepts the aliases with a note.

## Rules

- Measurable or deleted: "The system shall be fast" is not a requirement.
- Do not duplicate functional behavior (that belongs to UCs); an NFR constrains how well, not what.
- State the load, environment and provider assumptions inside the requirement.
- Keep the intro sentence of the section: which attributes are covered, and that the rest are declared not applicable.
- Examples in the catalog belong to other products (chemical tracking, ATM, text editor): learn the form, derive your own content.
