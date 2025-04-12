## 📄 PDF Image(s) to Markdown Conversion Prompt (Batch-Aware)

# PDF Image(s) to Markdown Conversion Prompt

When provided with one or more images of PDF document pages, convert all visible text to clean Markdown format with the following specifications:

## Structure Preservation

- Maintain each page’s hierarchical structure and indentation
- Preserve proper heading levels (`#` for main headings, `##` for subheadings, etc.)
- Retain paragraph relationships and logical flow
- Format lists correctly (numbered and bulleted)

## Special Section Identification

Mark these sections with Markdown comments if detected:

- Table of contents: `<!-- TOC START -->` content `<!-- TOC END -->`
- Headers: `<!-- HEADER START -->` content `<!-- HEADER END -->`
- Footers: `<!-- FOOTER START -->` content `<!-- FOOTER END -->`

## Text Organization

- Process multi-column layouts from left to right, top to bottom
- Intelligently incorporate floating or boxed text into its related paragraph
- Place floating/boxed text directly **after** the paragraph it visually relates to
- Format floating/callout/boxed text as blockquotes using `>` syntax
- If placement is ambiguous, attach floating text after the preceding full paragraph

## Tables (Critical)

- If the content is visually structured as a table, render it using Markdown table syntax:
    - One line per row using `|` to separate columns
    - First row as the header, second row as `|---|---|`
    - Avoid line breaks inside rows
    - Use `<br>` within cells only if necessary
- If multiple repeated structures exist (e.g., label + bullet groupings), interpret as a table even if no borders are visible

## Post-OCR Structural Inference

- After extracting visible text, use **language-based reasoning** to infer structure (e.g., table, list, or section)
- Use semantic patterns like repeated headings, label/field/bullet combinations to detect structured intent
- Favor **semantic structure** over pure visual layout

## Embedded Image Handling

- Do **not extract or interpret** any text inside embedded images, diagrams, or figures
- When such an embedded image is detected, insert a placeholder comment like:
  
  `<!-- IMAGE DETECTED -->`

## Multi-Page Output Formatting

- Return a single Markdown output representing **all images**, in order
- Insert the following page break delimiter **between each page**: `-----`

- Do **not** add page numbers, extra headings, or labels like “Page 1”, “Page 2”

## Critical Requirements

- NEVER omit any visible text (unless it's embedded inside a graphic or figure)
- Include ALL text from every page, including disconnected or sidebar content
- When unsure about placement, include the text and insert it where it most logically fits
- Always preserve the original semantic intent

## Output Format

- Return clean Markdown only — no backticks, code blocks, or commentary
- The final Markdown should reflect the **combined, cleaned content of all submitted images**
