## 🧹 Prompt: Markdown Cleanup and Structuring with Derived Content Generation

**(Note: Markers use [[ ... ]] syntax for visibility during copy/paste. Treat these exactly like standard comment markers.)**

### 🎯 Objective

Analyze, clean, and restructure the provided Markdown content according to the rules below. The primary goal is to improve Markdown formatting and logical structure based *solely on the patterns and text present in the input*. Key tasks include preserving text integrity, correcting structural elements like headings and lists, reconstructing tables from input data, and generating analytical summaries (TOC, Fix Log) where applicable.

### ✨ Core Principles & Constraints

1. **Input Grounding:** ALL analysis, restructuring, and generation MUST be based *strictly* on the text and patterns found within the 'ORIGINAL MARKDOWN CONTENT' provided below.
2. **Text Content Preservation:** The exact wording, phrasing, punctuation, and specific numbering (e.g., `1.2` in headings, specific item phrasing in lists) of the *original input text content* MUST be preserved unless explicitly stated otherwise (e.g., removing text when extracting an embedded heading). Do not perform spelling/grammar correction or rephrase sentences.
3. **Prohibition on Content Invention:** **CRITICAL:** You MUST NOT invent, add, or hallucinate *substantive text content*. This includes creating new paragraphs, list items, descriptive sentences, or table cell contents that are not directly present in, or derived from, the input text. Do not add information based solely on the document's apparent topic or title if it's not in the input text itself.
4. **Permitted Structural Modification & Generation:** While inventing substantive text is forbidden, **modifying structure** around *existing input text* (e.g., adding heading markers `#`, table syntax `|`, list markers `*`) IS permitted and necessary when required by the rules below to correctly format the input content. Furthermore, **generating requested analytical blocks** (TOC, Fix Log) based *entirely* on the analysis of the cleaned input structure and the actions taken IS permitted and required when their conditions are met. This includes adding the specified `[[ MARKER START ]]` and `[[ MARKER END ]]` tags for those blocks.
5. **Handling Simple Input:** If the input text is minimal or lacks the specific patterns required for complex actions (like table reconstruction or embedded heading extraction), apply only basic applicable syntax corrections and omit optional generated blocks (TOC, Fix Log) as per their specific rules. The output complexity should reflect the input complexity.

### 🛠️ Specific Restructuring and Generation Rules

- **Correct Heading Levels & Promote Embedded Headings:**
    - Adjust Markdown heading markers (`#`, `##`, etc.) on standard headings *found in the input* to ensure logical hierarchy and consistency based on the input's structure.
    - Identify text within the input (even if embedded in other elements like tables or lists) that functions as a structural heading, primarily indicated by patterns *in the input* like sequential numerical prefixes (e.g., `6.1`, `2.3.4`).
    - **If such heading text is identified based on input patterns,** you MUST extract it and restructure it as a standard Markdown heading. This involves placing the *exact original text* (including numbers) on its own line and **adding the appropriate number of `#` markers** based on its logical position in the input-derived hierarchy. The original text is removed from its embedded location.

- **Normalize List Formatting:** For list-like structures *identified in the input*, ensure consistent use of standard Markdown list markers (`*`, `-`, `1.`, `a.`, etc.) and proper indentation for nesting. This may involve **adding** appropriate markers to lines of text clearly intended as list items based on input patterns. Preserve the original text of items.

- **Fix Paragraph Structure:** Correct broken line breaks within paragraphs *found in the input* to form proper paragraph blocks, preserving the original sentences and wording.

- **Reconstruct Tables:** If text *in the input* clearly represents tabular data but uses incorrect/broken formatting, restructure it into valid Markdown table syntax (`| Header | ... |`). This involves **adding** the necessary `|` and `---` syntax around the *existing input text*. Use the original input text for cell content (unless heading text was extracted as per that rule). Remove rows *from the input* that only contained extracted heading text.

- **Remove Junk Characters:** Delete only obvious, non-content artifacts *found in the input*. Be conservative.

- **Ensure Consistent Formatting:** Apply standard Markdown spacing, nesting, and indentation based on the restructured content derived from the input.

- **Generate Table of Contents (Conditional):** See Section `📝` below.

- **Generate Fix Log (Conditional):** See Section `🪵` below.

---

### 🚫 Do Not Modify Protected Markers

If the following markers are present *in the input*, leave them and their enclosed content **completely untouched**:

- `[[ HEADER START ]]` to `[[ HEADER END ]]`
- `[[ FOOTER START ]]` to `[[ FOOTER END ]]`
- `[[ TOC START ]]` to `[[ TOC END ]]` (Note: This refers to a TOC potentially present *in the input*, distinct from the TOC you might generate at the end).
- Page break markers: `-----` (five dashes)
Apply corrections only *outside* these blocks, based on the input content found there.

---

### 📝 Generated Table of Contents (Conditional)

- **Requirement:** After applying all structural corrections *based strictly on the input*, determine if the resulting cleaned output contains 2 or more standard Markdown headings (lines starting with `#` followed by a space).
- **Action:** **IF AND ONLY IF** the cleaned output meets this condition (>= 2 headings), you **must generate** a Table of Contents (TOC) block reflecting the final heading structure derived from the input.
- **Generated Block Structure:** This generated block MUST be enclosed precisely within `[[ TOC FROM CONTENT START ]]` and `[[ TOC FROM CONTENT END ]]` markers. The content between these markers must be *only* the derived TOC headings, formatted using standard Markdown heading syntax (`#`, `##`, etc., reflecting the hierarchy) and using the exact, preserved text (including numbering) of the headings from the cleaned output. Do not use list items for the TOC.
- **Placement:** This entire generated block (markers + content) must be placed at the **very end** of the final output.
- **Omission:** If the condition (>= 2 headings) is not met, this entire block (markers and content) MUST be omitted.

---

### 🪵 Optional Fix Logging (Conditional)

- **Requirement:** Track any structural modifications made *based on analyzing the input* (e.g., correcting heading levels, reformatting a list found in input, promoting an embedded heading identified in input, reconstructing a table found in input).
- **Action:** **IF AND ONLY IF** one or more such modifications were made based on the input, you **must generate** a Fix Log summarizing these actions.
- **Generated Block Structure:** This generated block MUST be enclosed precisely within `[[ FIXES START ]]` and `[[ FIXES END ]]` markers. The content between these markers must be a simple bulleted list describing *only the actual changes made* based on the input.
- **Placement:** This entire generated block (markers + content) must be placed at the **very top** of the final output.
- **Omission:** If no structural modifications based on the input were performed, this entire block (markers and content) MUST be omitted.

---

### ✅ Output Requirements

- Structure: [Optional Fix Log Block] -> [Cleaned/Restructured Main Content including preserved protected blocks from input] -> [Optional Generated TOC Block].
- Return **only** this complete raw Markdown output.
- **No extra text:** Do not add explanations, apologies, or other text not part of the specified output structure.
- **No code blocks:** Do not enclose the final result in Markdown code blocks (` ``` `).
- **Preserve Line Breaks:** Maintain original line breaks within text content unless merging lines was part of paragraph fixing based on input analysis.

---

**FINAL REMINDER:** Base all actions strictly on the provided 'ORIGINAL MARKDOWN CONTENT'. Do not invent substantive text. Structural modifications (adding `#`, `|`, `*`) and generating the conditional TOC/Fix Log blocks (including their `[[...]]` markers) *are permitted and required* when justified by the input and the rules above.

### 📄 ORIGINAL MARKDOWN CONTENT FOLLOWS
