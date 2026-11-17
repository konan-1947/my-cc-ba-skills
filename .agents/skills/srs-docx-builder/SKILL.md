---
name: srs-docx-builder
description: Assemble the SRS Word file (.docx) from the Markdown parts written by the other SRS skills - cover page, auto table of contents, Heading 1-6 styles in the EDUA look, Record of Changes and Field Description tables, the 4-column Use Case table, BR/MSG registers, diagram images (SVG converted to PNG), footer "Page X / Y" - with pure Python (no pip or npm installs), then optionally refresh fields and export a PDF through Microsoft Word. Use for "xuất SRS ra Word", "ghép các phần thành file docx", "build file Word cho báo cáo Report 3", "cập nhật mục lục", "xuất PDF", "chèn sơ đồ vào Word". Part of the srs-writer workflow.
---

# SRS Word builder

Turns the Markdown outputs of `srs-overall`, `uc-fpt`, `srs-screen-spec`, `srs-nfr`, `srs-br-msg` and the diagram skills into one `.docx` that opens cleanly in Word.

## Files

- `scripts/build_srs_docx.py`: builder (standard library only; Python 3).
- `scripts/finalize-docx.ps1`: opens the file in Microsoft Word (COM), updates the table of contents and all fields, saves, exports PDF.
- `templates/sample-srs/`: a complete example project (manifest, six parts, two diagrams) that builds an 8-page document.

## Workflow

1. **Organize the parts** in folders, one Markdown file per SRS part, in reading order, for example `00-record.md`, `01-overall.md`, `02-usecases/*.md`, `03-screens.md`, `04-nfr.md`, `05-appendix.md`. Keep the heading numbers typed in the text (`## 1. Overall Requirements`, `#### 2.2.1 Create Lesson Plan`), exactly as the other skills produce them.
2. **Write `manifest.json`** (copy `templates/sample-srs/manifest.json`): `title`, `subtitle`, `date_line`, `footer`, optional `logo`, `page` (`A4`, `A3`, `Letter`), `font`, `font_size`, `toc_levels`, `parts` (file names or globs, in order).
3. **Check the parts first**: run the validators listed in `srs-writer` (UC, screens, NFR, overall, refs). Build only from checked content.
4. **Build**: `python scripts/build_srs_docx.py manifest.json out.docx`
5. **Finalize** (Windows with Word): `powershell -File scripts/finalize-docx.ps1 -Docx out.docx -Pdf out.pdf`. This fills the table of contents with page numbers and exports the PDF. Without Word, open the file and choose Update Field on the table of contents (Word may also offer to update fields when the file opens).
6. **Review the PDF** page by page (`pdftoppm -png -r 70 out.pdf pg`), at least: cover, contents, one UC table, one screen table, each diagram, the registers.

## Markdown rules the builder understands

| Markdown | Word result |
|---|---|
| `# ` ... `###### ` | Heading 1 to 6 (red H1, bold H2, blue H3, italic H4...), included in the contents |
| plain line | paragraph (one source line = one paragraph) |
| `**bold**`, `*italic*`, `` `code` `` | character formatting |
| `- item`, `  - sub`, `1. item` | bullet and numbered lists (3 levels; each numbered list restarts at 1) |
| pipe table | table, shaded bold header row, column widths from content (no word breaks) |
| table whose first cell is `**Primary Actors**` | UC table: 4-column first row, label column shaded, other rows spanning the content area; `<br>` splits paragraphs inside a cell |
| `![Figure 1.2.1 - caption](diagrams/x.svg)` | centered picture scaled to the text width, caption below; `.png`/`.jpg` as is, `.svg` converted to PNG with headless Edge/Chrome |
| `<!-- pagebreak -->` | page break |

Not supported: nested tables, merged cells other than the UC table, footnotes, tracked changes (use the `docx` skill to edit afterwards), SVG without Edge/Chrome installed.

## Rules and limits

- Source of truth stays in the Markdown parts and the diagram sources (`.drawio` / JSON specs); regenerate the Word file instead of editing it by hand, otherwise the next build overwrites the edits.
- Wide diagrams (BPMN with many ranks) become small on portrait A4. Use `"page": "A3"` (the EDUA sample is A3), shorten the diagram, or split it into sub-processes.
- The SVG previews from `usecase-diagram` and `flowchart-bpmn` include their own title line; keep the figure caption in Markdown and accept the duplication, or remove the `title` before building.
- Fonts: Calibri by default; Vietnamese text renders correctly. Change `font` in the manifest to match the school template.
- The builder reproduces the structure and look of the EDUA sample (colors, header shading, UC table layout, footer), not its exact internal styles; to match an official template pixel for pixel, apply the template in Word afterwards (or use the `docx` skill's template workflow).
- Keep all citations by id (BR/MSG/UC) intact: the builder does not check them; `srs-br-msg` does.
- `finalize-docx.ps1` needs Microsoft Word installed (Windows). On other systems export the PDF with LibreOffice (`soffice --headless --convert-to pdf`).
