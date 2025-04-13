## 🧹 Prompt: Markdown Cleanup with Marker Preservation + Content TOC + Optional Fix Logging + Embedded Heading Extraction

**(Note: Markers use [[ ... ]] syntax for visibility during copy/paste. Treat these exactly like standard comment markers.)**

### 🎯 Objective

Clean and fix the **structure** of the provided Markdown content **WITHOUT altering the original text content**. Generate a Table of Contents based on the final cleaned structure. Key goals:

- **Preserve Text Integrity (Highest Priority):** All structural fixes below **MUST** retain the exact original wording, phrasing, punctuation, and numbering (e.g., `1.2` in headings, specific item phrasing in lists) of the content. **Do not** perform text correction (spelling, grammar) or rephrasing. Focus *exclusively* on fixing the Markdown *syntax* and *layout* around the existing text.

- **Correct Heading Levels & Extract Embedded Headings:**
    - Adjust the Markdown heading markers (`#`, `##`, etc.) on *standard* headings to ensure logical hierarchy and consistency (e.g., no skipping levels like `#` directly to `###`).
    - **Crucially: Identify potential heading text *even if embedded within other elements* (like table cells or incorrectly indented lists). Prioritize recognition based on patterns indicating document structure, especially **sequential numerical prefixes** (e.g., `6.1`, `2.3.4`) and their logical place in the document's overall outline (e.g., text like `2.1 Section Title` appearing after a `2.0` heading). The specific number of `#` characters present *in the original embedded location* (e.g., the `###` in `### 2.1 Section Title`) is **irrelevant** for *identifying* it as a structural heading; the **numerical sequence (`2.1`) is the key indicator.**
    - **Move** this identified heading text *out* of the element it was embedded in (e.g., remove it from the table cell).
    - **Place** the extracted text as a proper, standard Markdown heading on its own line in the correct hierarchical position within the document flow. **Assign the correct heading level (`#`, `##`, etc.) based on its logical position in the hierarchy (e.g., a `6.1` section following a `# 2.0` section should be placed as `## 2.1 ...`), irrespective of the number of `#`s it might have had when embedded.**
    - **Always keep the exact original heading text intact** during extraction and placement, including the crucial **leading/trailing numbers** (`2.1`, etc.) and specific phrasing. Only its location and final `#` level should change.

- **Normalize List Formatting:** Ensure consistent use of list markers (`*`, `-`, `1.`, `a.`, etc.) and proper indentation for nested lists. **Do not change the text content** of the list items themselves.
- **Fix Paragraph Structure:** Correct broken line breaks *within* paragraphs to form proper paragraph blocks. Merge incorrectly split lines where appropriate. Preserve the original sentences and wording; avoid re-wrapping text in a way that alters phrasing or creates awkward breaks.
- **Reconstruct Tables:** Format data clearly intended as tables into valid Markdown table syntax (`| Header | ... | \n |---|---| \n | Cell | ... |`). Use the **original, unaltered text** for all cell content *except* for heading-like text that has been extracted as per the "Correct Heading Levels & Extract Embedded Headings" rule above. Rows that *only* contained an extracted heading should be removed from the final table structure. Use `<br>` within cells only if essential to retain required internal line breaks from the source text.
- **Remove Junk Characters:** Delete only obvious, non-content artifacts (e.g., isolated control characters, clearly unintended symbol repetitions like `^^^` if not part of the actual content) without removing *any* legitimate text, numbers, punctuation, or symbols that are part of the content. Be conservative; if unsure, leave the character/symbol in.
- **Ensure Consistent Formatting:** Apply proper Markdown spacing (e.g., around headings, lists, code blocks), nesting, and indentation throughout, based on standard practices, always respecting the priority of text integrity.
- **Generate TOC (from Content):** After applying all structure-only fixes (including heading extraction), create a Table of Contents reflecting the final cleaned structure, using the exact, preserved heading text as specified in the TOC generation section below.

---

### 🚫 Do Not Modify the Following Markers or Their Contents

Leave these segments **completely untouched**, including their content, formatting, spacing, and line breaks:

- [[ HEADER START ]] to [[ HEADER END ]]
- [[ FOOTER START ]] to [[ FOOTER END ]]
- [[ TOC START ]] to [[ TOC END ]]
- Page break markers: `-----` (five dashes)

Do **not** rewrap or restructure anything between these `[[ ... ]]` markers. Apply all corrections **only outside** of these protected blocks.

---

### 📝 Generated Table of Contents (from Content)

- After cleaning and structuring the main Markdown content (outside the protected blocks, **without altering text content**, and **including any extracted embedded headings**), generate a new Table of Contents (TOC).
- Base this TOC on the main sections identified within the **final, cleaned** document content, using the **preserved heading text**. Use structural analysis of the cleaned content for hierarchy. This **must include** headings that were extracted from elements like tables.
- **Crucially:** Do *not* include any headings or content found within the original [[ TOC START ]] and [[ TOC END ]] block when generating this new TOC.
- Format this generated TOC using standard Markdown **heading syntax** (`#`, `##`, `###`, etc.). For each entry in the TOC:
    - Use the **exact text** of the corresponding heading from the **cleaned content**, **including any original numbering** (e.g., `## 6.1 Cloud Infrastructure` should appear exactly like that in the TOC, adjusted only by the number of `#` needed for hierarchy relative to its parent, like `# 6.0 TECHNICAL REQUIREMENTS`).
    - Apply the appropriate Markdown heading level (`#` for the highest level identified, `##` for the next, etc.) based on its structural hierarchy within the cleaned content.
    - **Do not use list items.**
- Place this *entire* generated TOC section at the **very end** of the cleaned Markdown output, *after* all other content.
- Enclose the generated TOC **directly** within the following specific comment tags. Ensure that **only** the markdown headings representing the TOC appear between the start and end tags:
    [[ TOC FROM CONTENT START ]]
[Generated TOC using #, ## headings with original text/numbering here]
    [[ TOC FROM CONTENT END ]]
    *(Note: The line above `[Generated TOC using...]` is for explanation only and should NOT appear in the output; only the headings themselves go between the tags).*

---

### 🪵 Optional Fix Logging

If you made any **structural corrections** (affecting Markdown syntax/layout only, not text, *including extracting embedded headings*) to the Markdown *outside* the protected blocks, include a summary of those changes at the **very top of the final Markdown output**, wrapped inside the following tags:

[[ FIXES START ]]

- Brief list of structural changes made (1 bullet per fix, e.g., "- Extracted embedded heading '### 6.1 Cloud Infrastructure' from table and placed as standard H2 heading.")
[[ FIXES END ]]

This fix log should be concise, plain text, and placed **before** the main cleaned Markdown content. If no structural fixes were required, **omit the log entirely**.

---

### ✅ Output Requirements

- The final output structure must be:
    1. Optional [[ FIXES START ]]...[[ FIXES END ]] block (only if structural fixes were made).
    2. The main Markdown content with corrected **structure** (including extracted headings placed correctly) but **unaltered text** (respecting the `🚫 Do Not Modify` rules). Tables should be reformed *without* the extracted heading rows.
    3. The mandatory [[ TOC FROM CONTENT START ]]...[[ TOC FROM CONTENT END ]] block containing *only* the generated TOC (formatted as markdown headings with preserved text, including extracted headings) between the tags.
- Return **only** the complete, structured Markdown output as described above.
- **Do not enclose the result in code blocks** (in the AI's *final* response to this prompt).
- **Do not add any explanations, apologies, or introductory/concluding text**.
- Preserve original line breaks within the main content unless paragraph formatting required merging lines during cleanup (without changing words).
- Do not introduce extra headings, page labels, or additional metadata beyond the specified Fix Log and Generated TOC blocks.

---

**CRITICAL REMINDER:** Output *only* the raw Markdown following the structure: [Optional Fix Log] -> [Cleaned **Structure** / Preserved **Text** Content including extracted headings] -> [Generated TOC Block (`[[ TOC FROM CONTENT START ]]` followed immediately by TOC headings with preserved text, then `[[ TOC FROM CONTENT END ]]`)]. Do not include *any* other text or formatting.

### 📄 ORIGINAL MARKDOWN CONTENT FOLLOWS
