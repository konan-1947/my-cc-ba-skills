# Skill coverage for producing the EDUA-style SRS (Report 3 v1.2)

Sample analysed: `Report3_Software_Requirement_Specification_v1.2.docx`, about 10,000 paragraphs, 177 tables, 79 images.

## Statistics of the sample

| Item | Count |
|---|---|
| UC specifications (2.x.y) | 109 in 17 feature groups |
| Screen specifications (3.x.y) | 56 (52 with Field Description) |
| Main workflows (1.2) | 5 |
| Business rules (BR-xx) | 18 |
| System messages (MSGnn) | about 218 |
| NFR requirements (4) | about 12 (INT-UI, INT-SW, USR, PRF, ROB, SEC, ITG) |
| Diagrams | context, use case diagrams per role, screen flows per role, ERD, workflows |

## Coverage by SRS part (current)

| SRS part | Skill | Validator | Status |
|---|---|---|---|
| Record of Changes | `srs-writer` | none | Covered (template + rules) |
| 1.1 Context narrative, 1.2 workflow tables, 1.3.1-1.3.2, 1.4.2-1.4.3, 1.5 entity table | `srs-overall` | `check-overall.py` | Covered |
| 1.3.3 Use case diagrams | `usecase-diagram` | `validate-drawio.py` | Covered |
| 1.2 workflow diagrams, 1.4.1 screen flows | `flowchart-bpmn` | `validate-drawio.py` | Covered |
| 1.1 context diagram, 1.5 ERD | `diagramming` | engine validators | Covered |
| 2 UC specifications | `uc-fpt` (company: `uc-company`) | `validate-uc-fpt.py` | Covered |
| 3 Screen specifications | `srs-screen-spec` | `validate-screen-spec.py` | Covered |
| 4 NFR | `srs-nfr` | `validate-nfr.py` | Covered |
| 5.1 / 5.2 BR and MSG + cross-references | `srs-br-msg` | `check-refs.py` | Covered |
| Orchestration, order, full check | `srs-writer` | all of the above | Covered |
| User stories and AC (upstream) | `user-story-ac-writer` | its checklist | Available |
| Requirement discovery | `ba` | none | Available |
| Import/audit/edit of an existing .docx | `srs-writer` (import_docx.py, audit_srs.py, docx_edit.py) | audit report | Covered (tested on EDUA v1.2) |
| Word assembly (cover, TOC, heading styles, 4-column UC tables, images, footer) | `srs-docx-builder` | Word finalize + PDF review | Covered (sample project of 8 pages verified) |

## Remaining gaps

1. **Single traceability table** (low): the audit reports UC <-> catalog, UC -> BR/MSG, screens -> UC and matrix -> screens as separate findings; one merged UC x screen x BR x MSG matrix export (xlsx/Markdown) is not built.
2. **Edit operations** (medium): `docx_edit.py` covers replace, delete empty headings and add a UC (cloning). Not yet: add a screen spec, add/renumber BR or MSG rows, add a catalog row, edit tables of the Record of Changes. Do these in Word, or extend the script the same way (clone an existing table, change cell text).
3. **Matching an official template exactly** (low): `srs-docx-builder` reproduces the EDUA look, not its internal styles; editing the user's own file in place (`docx_edit.py`) keeps their styles.
4. **Non-Windows finalization** (low): table-of-contents refresh and PDF export use Microsoft Word COM; no LibreOffice path is packaged.
5. **Author decisions the audit cannot make**: whether authorization-matrix screen names should equal section 3 headings, which unmapped UCs are Non-UI, whether `IT Supporter` or `IT Support Staff` is the official name.

## Notes

- The scripts are now tested on the real EDUA v1.2 file (audit of 110 UC tables, 177 tables, 75 images; in-place edits checked by re-auditing and opening in Word). `srs-docx-builder` was verified on an 8-page sample (cover, contents, tables, two diagrams, registers) by exporting the PDF from Word and reading the pages.
- `grill-with-docs` is superseded by `ba` for elicitation and can be removed once nothing else references it.
