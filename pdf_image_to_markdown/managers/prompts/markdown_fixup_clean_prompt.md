## 🧹 Prompt: Markdown Cleanup with Marker Preservation + Optional Fix Logging

### 🎯 Objective  

Clean and fix the structure of the provided Markdown content with the following goals:

- Correct broken or inconsistent heading levels  
- Normalize list formatting (bulleted and numbered)  
- Fix broken line breaks within paragraphs  
- Reconstruct malformed tables  
- Remove duplicated or junk characters  
- Ensure proper nesting, spacing, and consistent indentation

---

### 🚫 Do Not Modify the Following Markers or Their Contents

Leave these segments **completely untouched**, including their content, formatting, spacing, and line breaks:

- `<!-- HEADER START -->` to `<!-- HEADER END -->`  
- `<!-- FOOTER START -->` to `<!-- FOOTER END -->`  
- `<!-- TOC START -->` to `<!-- TOC END -->`  
- Page break markers: `-----` (five dashes)

Do **not** rewrap or restructure anything between these markers.

---

### ✅ Output Requirements

- Return only the cleaned Markdown (**no code blocks, no explanations, no extra wrapping**)
- Resulting Markdown **MUST NOT be enclosed in code block**
- Preserve the original line breaks unless paragraph formatting or readability requires changes
- Do not introduce extra headings, page labels, or additional metadata
- Apply all corrections **only outside** of the protected marker blocks

---

### 🪵 Optional Fix Logging

If you made any structural corrections, include a summary of those changes at the **top of the Markdown output**, wrapped inside the following tags:

```
<! FIXES START >
- Brief list of changes made (1 bullet per fix)
<! FIXES END >
```

This fix log should be concise, plain text, and placed before the main Markdown content.  
If no fixes were required, **omit the log entirely**.

---

**CRITICAL REMINDER:** Output *only* the raw, cleaned Markdown content. Do not include *any* explanations, introductory text, apologies, or code block fences

### 📄 ORIGINAL MARKDOWN CONTENT FOLLOWS
