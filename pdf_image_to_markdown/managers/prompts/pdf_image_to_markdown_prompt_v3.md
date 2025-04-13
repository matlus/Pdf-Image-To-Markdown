# PDF IMAGE-to-Markdown Conversion Prompt

When provided with an image of a PDF document page, please convert all visible text to clean markdown format with the following specifications:

## Structure Preservation

- Maintain the document's hierarchical structure and indentation.
- Preserve proper heading levels (# for main headings, ## for subheadings, etc.).
- Retain all paragraph relationships and logical flow.
- Format lists correctly (numbered and bulleted).

## Special Section Identification & Marking

Accurately identify and mark the following standard document sections using markdown comments. Apply these markers *around* the relevant content **found on the current page image**:

- **Table of Contents:** Identify content belonging to a Table of Contents based on the following:
    - **Full TOC Start:** Look for a prominent title (e.g., "Contents", "Table of Contents", "Index") combined with a structured list mapping section titles/headings (often with numbering like `1.2`, `III-A`) to page numbers. These lists often feature distinct formatting, indentation, and right-aligned page numbers (sometimes with leader dots/spaces).
    - **TOC Continuation:** **Crucially, even if a prominent TOC title is *absent* on the current page image,** identify content as part of a TOC if it consists *predominantly* of lines matching the characteristic structure of a TOC list (i.e., `Section Title/Number ......... Page Number`). This indicates a continuation from a previous page.
    - **Marking:** If *any* content on the page is identified as belonging to a Table of Contents (either a start or a continuation), enclose **all of that specific TOC content visible on the current page** within `[[ TOC START ]]` and `[[ TOC END ]]`. Format the content *inside* these markers according to the general structure preservation rules (lists, indentation, etc.) as accurately as possible based on the OCR text. *Note: These markers define the TOC content *on this page*, even if the logical TOC continues across pages.*

- **Page Headers:** Identify recurring text typically found at the very top margin of the page (e.g., document title, chapter title, section name, page number). Enclose *only* this distinct header text within `[[ HEADER START ]]` and `[[ HEADER END ]]`. Include all parts if multi-line.

- **Page Footers:** Identify recurring text typically found at the very bottom margin of the page (e.g., page number, confidentiality notices, version numbers). Enclose *only* this distinct footer text within `[[ FOOTER START ]]` and `[[ FOOTER END ]]`. Include all parts if multi-line.

- **Strikethrough Text:** Identify text that visually appears with a line through it (struck-through or crossed-out). Enclose **only the specific struck-through text itself** within `[[ STRIKETHROUGH START ]]` and `[[ STRIKETHROUGH END ]]`, leaving it in its original position relative to the surrounding text.
    - *Example:* `The quick brown fox [[ STRIKETHROUGH START ]]jumped over[[ STRIKETHROUGH END ]] leaps over the lazy dog.`

## Text Organization

- Process multi-column layouts reading order (typically left-to-right, then top-to-bottom within columns).
- Intelligently incorporate floating text elements (like callout boxes or side notes) into the main flow.
- **Identify Floating Text Title:** Determine if the floating text block itself begins with a short, distinct phrase that acts as a title (e.g., "Note:", "Important:", "Warning:", often visually separated or styled differently like bold).
- **Placement:** Place the entire floating text block immediately **after** the paragraph or element it visually relates to most closely. If placement is ambiguous, attach it after the immediately preceding full paragraph or structural element.
- **Formatting Floating Text:**
    - Use Markdown blockquotes (`>`) to enclose the *entire* floating text element (body and title, if present).
    - Apply the blockquote marker (`>`) to the beginning of each line of the floating text content.
    - **Preserve Internal Structure:** The formatting *inside* the blockquote MUST accurately reflect the original structure of the floating text, including paragraphs, line breaks, and especially **numbered or bulleted lists**. Standard Markdown list formatting should be used within the blockquote context.
    - **If a title was identified:**
        - Place the title on the first line inside the blockquote.
        - Format the title using **bold** markdown (`**Title Text:**`).
        - Place the rest of the floating text body (preserving its internal structure like lists) on the subsequent lines within the blockquote.
       *Example (Titled with List):*

       ```markdown
       > **Key Points:**
       > * This is the first point inside the callout.
       > * This is the second point.
       >   1. This is a nested numbered item.
       >   2. Another nested item.
       > * Back to the main bullet level.
       ```

    - **If no title was identified:**
        - Place all lines of the floating text inside the blockquote, preserving its internal structure (paragraphs, lists, etc.) without special formatting on the first line.
       *Example (Untitled with List):*

       ```markdown
       > * An item in an untitled callout list.
       > * Another item.
       > * A third item perhaps with
       >   a line break correctly preserved.
       ```

## Tables (Critical)

- If the content is visually structured as a clear grid or table, it **must** be rendered using Markdown table syntax:
    - Use a single line for each row, with `|` to separate cell content. Pad cells with spaces for clarity (`| Cell Content |`).
    - The first row should generally be treated as the header row.
    - The second row must be a separator line defining columns: `|---|---|---|` (adjust dashes and pipes for the number of columns).
    - Avoid unnecessary line breaks *within* table rows.
    - Use `<br>` *within a cell* only if essential to preserve necessary line breaks or multi-line phrasing from the source.
- **Inferred Tables:** If the page contains multiple repeated sections or groups of information (e.g., label-value pairs, headings followed by consistent bullet/item groups) that follow a *consistent structure*, interpret and render this entire section as a **Markdown table**, even if no visible grid lines are present. Use the repeating elements to define the columns.

## Post-OCR Structural Inference

- After extracting the visible text, apply **semantic understanding and language-based reasoning** to determine the most appropriate Markdown structure (e.g., table, list, nested lists, headings, paragraphs).
- Do not rely solely on visual spacing, alignment, or raw line breaks when determining formatting. Use these as clues, but prioritize the logical structure.
- Use semantic patterns like repeated headings, field groupings, label/value pairs, or consistent item/description combinations to detect implicit tabular or list structures.
- When text suggests a repeated, structured pattern (like "Label: Value \n Description...") across multiple entries, strongly consider a **tabular format** for clarity and structure.
- Prefer **semantic meaning and logical structure** over literal visual layout – if the content *functions* like a table or a structured list, render it that way.

## Critical Requirements

- NEVER omit any visible text from the image.
- Include ALL text content — including headers, footers, marginalia, text in images (if OCR-able), captions, floating boxes, etc.
- When in doubt about the exact placement or structure of ambiguous text, **include the text** and place it where it seems most logically connected to the surrounding content, potentially using blockquotes if it seems like a distinct note.
- Preserve the semantic structure and intent of the original content as accurately as possible in Markdown.

## Output Format

- Return clean markdown only.
- Do not wrap the final output in triple backticks (` ``` `) or any other code block formatting.
- Do not add any introductory text, explanations, apologies, or concluding remarks.
- Return *only* the Markdown representing the entire processed page content according to the rules above.
