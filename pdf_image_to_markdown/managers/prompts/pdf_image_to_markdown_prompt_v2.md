# PDF-to-Markdown Conversion Prompt

When provided with an image of a PDF document page, please convert all visible text to clean markdown format with the following specifications:

## Structure Preservation

- Maintain the document's hierarchical structure and indentation
- Preserve proper heading levels (# for main headings, ## for subheadings, etc.)
- Retain all paragraph relationships and logical flow
- Format lists correctly (numbered and bulleted)

## Special Section Identification

Mark these sections with markdown comments:

- Table of contents: <!-- TOC START --> content <!-- TOC END -->
- Headers: <!-- HEADER START --> content <!-- HEADER END -->
- Footers: <!-- FOOTER START --> content <!-- FOOTER END -->

## Text Organization

- Process multi-column layouts from left to right, top to bottom
- Intelligently incorporate floating or boxed text into its related paragraph
- Place floating text directly **after** the paragraph it visually relates to
- Format floating/callout/boxed text as blockquotes using ">" syntax
- If placement is ambiguous, attach the floating text after the preceding full paragraph

## Tables (Critical)

- If the content is visually structured as a table, it **must** be rendered using Markdown table syntax:
    - Use a single line for each row, with `|` to separate columns
    - First row should be treated as the header row
    - Second row should use `|---|---|` to define the table columns
    - Avoid line breaks inside rows
    - Use `<br>` within a cell if necessary to preserve key line breaks or phrasing
- If the page contains multiple repeated sections (e.g., headings or labels followed by bullet-style groupings), and those sections follow a consistent structure, interpret the entire page as a **table** even if no visible borders are present.

## Post-OCR Structural Inference

- After extracting the visible text from the image, apply **language-based reasoning** to determine the appropriate structure (e.g., table, list, section).
- Do not rely solely on visual layout or line breaks when determining formatting.
- Use semantic patterns such as repeated headings, field groupings, or label/bullet combinations to detect tabular or list structures.
- When the text suggests a repeated, structured pattern (such as "Label + Field + Bullets"), assume a **tabular format** is intended.
- Prefer **semantic structure** over visual spacing or indentation — if the text "reads like" a table, render it as a table.

## Critical Requirements

- NEVER omit any visible text
- Include ALL text from the page — including floating, disconnected, or sidebar content
- When in doubt about placement, **include the text and place it where it most logically fits**
- Preserve semantic structure and intent of the original content

## Output Format

- Return clean markdown only — no backticks, code blocks, or extra explanation
- Do not explain your output
- Only return markdown representing the entire page content
