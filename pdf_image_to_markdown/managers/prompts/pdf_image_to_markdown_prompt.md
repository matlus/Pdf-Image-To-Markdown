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
- Intelligently handle floating text by incorporating it into its appropriate parent paragraph
- Maintain the semantic structure of the document

## Critical Requirements

- NEVER omit any text visible in the image, even if it appears to be floating or disconnected
- Format ALL tables using proper markdown table syntax:

  | Column 1 | Column 2 | Column 3 |
  |----------|----------|----------|
  | Data 1   | Data 2   | Data 3   |

- When in doubt about text placement, include it rather than omit it
- For callout boxes or sidebar text, preserve them as blockquotes using ">" syntax

## Output Format

- Return clean markdown only - no backticks, code block indicators, or extraneous text
- No explanatory comments or extra content beyond the markdown conversion of the PDF
- Include all visible text from the image in properly structured markdown
- Include ALL visible text from the image - nothing should be omitted
- Tables MUST be properly formatted using standard markdown table syntax with pipes (|)
