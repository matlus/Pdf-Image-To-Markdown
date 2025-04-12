class PlaintextToMarkdownPromptResultProcessor:
    _VALIDATION_REPORT_MARKER: str = "## Transformation Validation Report"
    _STATE_INFO_MARKER: str = "## State Information for Next Batch"
    _CODE_FENCE_START: str = "```markdown"
    _CODE_FENCE_END: str = "```"

    def _remove_code_fences(self, text_content: str) -> str:
        lines: list[str] = text_content.splitlines()

        first_non_empty_idx: int = -1
        last_non_empty_idx: int = -1

        # Find the index of the first non-empty line
        for i, line in enumerate(lines):
            if line.strip():
                first_non_empty_idx = i
                break

        # Find the index of the last non-empty line (iterate backwards)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():
                last_non_empty_idx = i
                break

        # Proceed only if we found both a start and an end non-empty line,
        # and the start comes before the end (handles single non-empty line case).
        if (
            first_non_empty_idx != -1
            and last_non_empty_idx != -1
            and first_non_empty_idx < last_non_empty_idx  # Crucial check
            and lines[first_non_empty_idx].strip() == self._CODE_FENCE_START
            and lines[last_non_empty_idx].strip() == self._CODE_FENCE_END
        ):
            # Return the content *between* the fence lines.
            # Slicing handles empty content between fences correctly.
            return "\n".join(lines[first_non_empty_idx + 1 : last_non_empty_idx])
        # If fences aren't the first/last non-empty lines, or < 2 lines, return original.
        return text_content

    def process_prompt_result(self, prompt_result: str, fresh_prompt: str) -> tuple[str, str]:
        # Step 1: Remove surrounding ```markdown ... ``` fences if they are the first/last non-empty lines.
        content_no_fences: str = self._remove_code_fences(prompt_result)

        # Step 2: Remove the validation report section (searching bottom-up) from the potentially modified content.
        content_before_report: str = self._remove_validation_report(content_no_fences)

        # Step 3: Split the cleaned content into Markdown and State info (searching bottom-up).
        markdown_content: str
        state_info: str
        markdown_content, state_info = self._split_content_and_state(content_before_report)

        # Step 4: Extract state key-value pairs (line-by-line scanning).
        state: dict[str, str] = self._extract_state_line_by_line(state_info)

        # Step 5: Insert state into the fresh prompt.
        updated_prompt: str = self._insert_state(fresh_prompt, state)

        return markdown_content, updated_prompt

    def _remove_validation_report(self, text_content: str) -> str:
        lines: list[str] = text_content.splitlines()
        report_start_index: int = -1

        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == self._VALIDATION_REPORT_MARKER:
                report_start_index = i
                break

        if report_start_index == -1:
            return text_content

        content_lines: list[str] = lines[:report_start_index]
        return "\n".join(content_lines)

    def _split_content_and_state(self, processed_content: str) -> tuple[str, str]:
        lines: list[str] = processed_content.splitlines()
        state_marker_index: int = -1

        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == self._STATE_INFO_MARKER:
                state_marker_index = i
                break

        if state_marker_index == -1:
            return processed_content, ""

        markdown_content: str = "\n".join(lines[:state_marker_index])
        state_info: str = "\n".join(lines[state_marker_index:])

        return markdown_content, state_info

    def _extract_state_line_by_line(self, state_section: str) -> dict[str, str]:
        state: dict[str, str] = {
            "previous_heading": "",
            "previous_content": "",
            "continuing_table": "NO",
            "table_headers": "",
            "column_count": "0",
            "column_alignment": "",
            "continuing_list": "NO",
            "list_type": "",
            "list_level": "0",
            "current_number": "1",
        }

        if not state_section:
            return state

        lines: list[str] = state_section.splitlines()
        if not lines:
            return state

        current_section: str = ""
        content_buffer: list[str] = []
        start_line_index: int = 0

        if lines[0].strip() == self._STATE_INFO_MARKER:
            start_line_index = 1

        for line in lines[start_line_index:]:
            line_stripped: str = line.strip()
            is_new_section_header = False
            new_section_type = ""

            if line_stripped.startswith("### Last Heading"):
                is_new_section_header = True
                new_section_type = "last_heading"
            elif line_stripped.startswith("### Last Content"):
                is_new_section_header = True
                new_section_type = "last_content"
            elif line_stripped.startswith("### Continuing Structures"):
                is_new_section_header = True
                new_section_type = "structures"
            elif line_stripped.startswith("###"):
                is_new_section_header = True
                new_section_type = ""

            if is_new_section_header:
                if current_section == "last_heading" and content_buffer:
                    state["previous_heading"] = "\n".join(content_buffer).strip()
                elif current_section == "last_content" and content_buffer:
                    state["previous_content"] = "\n".join(content_buffer).strip()

                current_section = new_section_type
                content_buffer = []
                continue  # Don't process header line as content

            if current_section in ["last_heading", "last_content"]:
                content_buffer.append(line)  # Keep original line for formatting
            elif current_section == "structures":
                if line_stripped.startswith("- Table:"):
                    value: str = self._extract_bracket_content(line_stripped)
                    state["continuing_table"] = value.upper() if value else "NO"
                elif line_stripped.startswith("- Headers:"):
                    state["table_headers"] = self._extract_bracket_content(line_stripped)
                elif line_stripped.startswith("- Column Count:"):
                    value: str = self._extract_bracket_content(line_stripped)
                    state["column_count"] = value if value else "0"
                elif line_stripped.startswith("- Alignment:"):
                    state["column_alignment"] = self._extract_bracket_content(line_stripped)
                elif line_stripped.startswith("- List:"):
                    value: str = self._extract_bracket_content(line_stripped)
                    state["continuing_list"] = value.upper() if value else "NO"
                elif line_stripped.startswith("- Type:"):
                    state["list_type"] = self._extract_bracket_content(line_stripped)
                elif line_stripped.startswith("- Current Level:"):
                    value: str = self._extract_bracket_content(line_stripped)
                    state["list_level"] = value if value else "0"
                elif line_stripped.startswith("- Current Number:"):
                    value: str = self._extract_bracket_content(line_stripped)
                    state["current_number"] = value if value else "1"

        # Save final buffer content after loop finishes
        if current_section == "last_heading" and content_buffer:
            state["previous_heading"] = "\n".join(content_buffer).strip()
        elif current_section == "last_content" and content_buffer:
            state["previous_content"] = "\n".join(content_buffer).strip()

        return state

    def _extract_bracket_content(self, line: str) -> str:
        start_idx: int = line.find("[")
        end_idx: int = line.find("]", start_idx + 1 if start_idx != -1 else -1)

        if start_idx != -1 and end_idx != -1:
            # Extract and strip content within brackets
            return line[start_idx + 1 : end_idx].strip()
        return ""

    def _insert_state(self, prompt_template: str, state: dict[str, str]) -> str:
        lines: list[str] = prompt_template.splitlines()
        modified_lines: list[str] = []

        # Map placeholders to state keys, using .get for safety
        placeholders: dict[str, str] = {
            "[PREVIOUS_HEADING]": state.get("previous_heading", ""),
            "[PREVIOUS_CONTENT]": state.get("previous_content", ""),
            # YES/NO handled specially below
            "[TABLE_HEADERS]": state.get("table_headers", ""),
            "[COLUMN_COUNT]": state.get("column_count", "0"),
            "[COLUMN_ALIGNMENT]": state.get("column_alignment", ""),
            "[LIST_TYPE]": state.get("list_type", ""),
            "[LIST_LEVEL]": state.get("list_level", "0"),
            "[CURRENT_NUMBER]": state.get("current_number", "1"),
        }

        for line in lines:
            modified_line: str = line

            # Special handling for specific YES/NO lines
            if "- Continuing Table: [" in modified_line and "[YES/NO]" in modified_line:
                modified_line = modified_line.replace("[YES/NO]", f"[{state.get('continuing_table', 'NO')}]")
            elif "- Continuing List: [" in modified_line and "[YES/NO]" in modified_line:
                modified_line = modified_line.replace("[YES/NO]", f"[{state.get('continuing_list', 'NO')}]")
            else:
                # General replacement for other placeholders
                for placeholder, value in placeholders.items():
                    if placeholder in modified_line:
                        modified_line = modified_line.replace(placeholder, value)

            modified_lines.append(modified_line)

        return "\n".join(modified_lines)


# class PlaintextToMarkdownPromptResultProcessor:
#     def process_prompt_result(self, prompt_result: str, fresh_prompt: str) -> tuple[str, str]:
#         markdown_content: str
#         state_info: str
#         markdown_content, state_info = self._split_content_and_state(prompt_result)

#         state: dict[str, str] = self._extract_state_line_by_line(state_info)
#         updated_prompt: str = self._insert_state(fresh_prompt, state)

#         return markdown_content, updated_prompt

#     def _split_content_and_state(self, prompt_result: str) -> tuple[str, str]:
#         lines: list[str] = prompt_result.splitlines()

#         # Start from the bottom and work upward for efficiency
#         state_marker_index: int = -1
#         for i in range(len(lines) - 1, -1, -1):
#             if lines[i].strip() == "## State Information for Next Batch":
#                 state_marker_index = i
#                 break

#         # If no state marker found, assume all content is markdown
#         if state_marker_index == -1:
#             return prompt_result, ""

#         # Split the content
#         markdown_content: str = "\n".join(lines[:state_marker_index])
#         state_info: str = "\n".join(lines[state_marker_index:])

#         return markdown_content, state_info

#     def _extract_state_line_by_line(self, state_section: str) -> dict[str, str]:
#         # Initialize state with default values
#         state: dict[str, str] = {
#             "previous_heading": "",
#             "previous_content": "",
#             "continuing_table": "NO",
#             "table_headers": "",
#             "column_count": "0",
#             "column_alignment": "",
#             "continuing_list": "NO",
#             "list_type": "",
#             "list_level": "0",
#             "current_number": "1",
#         }

#         if not state_section:
#             return state

#         lines: list[str] = state_section.splitlines()

#         current_section: str = ""
#         content_buffer: list[str] = []

#         for line in lines:
#             line_stripped: str = line.strip()

#             # Check for section headers
#             if line_stripped.startswith("### Last Heading"):
#                 current_section = "last_heading"
#                 content_buffer = []
#             elif line_stripped.startswith("### Last Content"):
#                 # Save previous section if needed
#                 if current_section == "last_heading" and content_buffer:
#                     state["previous_heading"] = "\n".join(content_buffer).strip()
#                 current_section = "last_content"
#                 content_buffer = []
#             elif line_stripped.startswith("### Continuing Structures"):
#                 # Save previous section if needed
#                 if current_section == "last_content" and content_buffer:
#                     state["previous_content"] = "\n".join(content_buffer).strip()
#                 current_section = "structures"
#                 # No need to collect the content as we'll parse individual lines
#             elif line_stripped.startswith("###"):
#                 # Unknown section, reset
#                 current_section = ""
#                 content_buffer = []
#             elif current_section in ["last_heading", "last_content"]:
#                 # Collect content for these sections
#                 content_buffer.append(line)
#             elif current_section == "structures":
#                 # Parse structure information
#                 if line_stripped.startswith("- Table:"):
#                     table_status: str = self._extract_bracket_content(line_stripped)
#                     state["continuing_table"] = table_status.upper()
#                 elif line_stripped.startswith("- Headers:"):
#                     state["table_headers"] = self._extract_bracket_content(line_stripped)
#                 elif line_stripped.startswith("- Column Count:"):
#                     state["column_count"] = self._extract_bracket_content(line_stripped)
#                 elif line_stripped.startswith("- Alignment:"):
#                     state["column_alignment"] = self._extract_bracket_content(line_stripped)
#                 elif line_stripped.startswith("- List:"):
#                     list_status: str = self._extract_bracket_content(line_stripped)
#                     state["continuing_list"] = list_status.upper()
#                 elif line_stripped.startswith("- Type:"):
#                     state["list_type"] = self._extract_bracket_content(line_stripped)
#                 elif line_stripped.startswith("- Current Level:"):
#                     state["list_level"] = self._extract_bracket_content(line_stripped)
#                 elif line_stripped.startswith("- Current Number:"):
#                     state["current_number"] = self._extract_bracket_content(line_stripped)

#         # Save last section if needed
#         if current_section == "last_heading" and content_buffer:
#             state["previous_heading"] = "\n".join(content_buffer).strip()
#         elif current_section == "last_content" and content_buffer:
#             state["previous_content"] = "\n".join(content_buffer).strip()

#         return state

#     def _extract_bracket_content(self, line: str) -> str:
#         """Extract content from within square brackets in a line"""
#         start_idx: int = line.find("[")
#         end_idx: int = line.find("]", start_idx)

#         if start_idx != -1 and end_idx != -1:
#             return line[start_idx + 1 : end_idx]
#         return ""

#     def _insert_state(self, prompt: str, state: dict[str, str]) -> str:
#         lines: list[str] = prompt.splitlines()
#         modified_lines: list[str] = []

#         placeholders: dict[str, str] = {
#             "[PREVIOUS_HEADING]": state["previous_heading"],
#             "[PREVIOUS_CONTENT]": state["previous_content"],
#             "[YES/NO]": state["continuing_table"],  # This will be handled specially
#             "[TABLE_HEADERS]": state["table_headers"],
#             "[COLUMN_COUNT]": state["column_count"],
#             "[COLUMN_ALIGNMENT]": state["column_alignment"],
#             "[LIST_TYPE]": state["list_type"],
#             "[LIST_LEVEL]": state["list_level"],
#             "[CURRENT_NUMBER]": state["current_number"],
#         }

#         for line in lines:
#             modified_line: str = line

#             # Special handling for Table and List YES/NO placeholders
#             if "- Continuing Table: [YES/NO]" in modified_line:
#                 modified_line = modified_line.replace("[YES/NO]", f"[{state['continuing_table']}]")
#             elif "- Continuing List: [YES/NO]" in modified_line:
#                 modified_line = modified_line.replace("[YES/NO]", f"[{state['continuing_list']}]")
#             else:
#                 for placeholder, value in placeholders.items():
#                     if placeholder in modified_line:
#                         modified_line = modified_line.replace(placeholder, value)

#             modified_lines.append(modified_line)

#         return "\n".join(modified_lines)
