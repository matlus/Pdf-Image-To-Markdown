from typing import Optional


class MarkdownCustomMarkesCleaner:
    # The specific marker prefix to *always* ignore during the first pass cleanup
    # and target during the second pass extraction.
    EXTRACTION_MARKER_PREFIX: str = "TOC FROM CONTENT"

    @staticmethod
    def _parse_tag(stripped_line: str) -> Optional[tuple[str, str]]:
        if stripped_line.startswith("[[") and stripped_line.endswith("]]"):
            content = stripped_line[2:-2].strip()
            if content.endswith(" START"):
                marker_prefix = content[: -len(" START")].strip()
                return marker_prefix, "START"
            if content.endswith(" END"):
                marker_prefix = content[: -len(" END")].strip()
                return marker_prefix, "END"
        return None

    @staticmethod
    def has_maaningful_content(markdown_string: str) -> bool:
        return any(char != "-" and not char.isspace() for char in markdown_string)

    @staticmethod
    def clean_up_markers(markdown_string: str) -> str:
        input_lines: list[str] = markdown_string.splitlines()
        output_lines: list[str] = []
        is_inside_removal_block: bool = False

        for current_line in input_lines:
            stripped_line: str = current_line.strip()
            tag_info = MarkdownCustomMarkesCleaner._parse_tag(stripped_line)

            # --- Block Removal Logic (Ignoring Extraction Marker) ---
            if tag_info:
                marker_prefix, tag_type = tag_info

                # Check if it's the special marker *before* general removal logic
                if marker_prefix == MarkdownCustomMarkesCleaner.EXTRACTION_MARKER_PREFIX:
                    # Always keep the extraction marker tags and content during this phase,
                    # unless we are already inside a *different* removal block.
                    pass  # Let it fall through to the "Keep Line" logic below
                # It's a standard marker, apply removal logic
                elif tag_type == "START":
                    is_inside_removal_block = True
                    continue  # Skip the start tag line
                elif tag_type == "END":  # Assumes it matches the block we are in
                    is_inside_removal_block = False
                    continue  # Skip the end tag line

            # If currently inside a standard removal block, skip the line
            if is_inside_removal_block:
                continue

            # --- Line-Specific Removal Logic ---
            # Simple check for "TABLE OF CONTENTS" line (case-insensitive)
            # Ensure this check doesn't remove lines inside the extraction block
            # (which it won't because we only reach here if not inside a removal block)
            if "table of contents" in current_line.lower():
                continue  # Skip this line

            # --- Keep Line ---
            # Keep lines that are not inside a removal block (or are part of the extraction block)
            output_lines.append(current_line)

        cleaned_markdown_string: str = "\n".join(output_lines)
        return cleaned_markdown_string

    @staticmethod
    def clean_markers_and_extract_toc(markdown_string: str) -> tuple[str, Optional[list[str]]]:  # <-- Updated Return Type Hint
        """
        Performs a full cleanup and extracts content from the special block.

        First calls `clean_up` to remove standard blocks, then processes
        that result to find, extract, and remove the special extraction block.

        Args:
            markdown_string: The original input markdown string.

        Returns:
            A tuple containing:
            - The fully cleaned markdown string (str).
            - A list of strings representing the lines within the extraction
              block if it was found and contained content, otherwise None
              (Optional[List[str]]).
        """
        intermediate_cleaned_string = MarkdownCustomMarkesCleaner.clean_up_markers(markdown_string)

        input_lines: list[str] = intermediate_cleaned_string.splitlines()
        output_lines_final: list[str] = []
        extracted_lines: list[str] = []  # This will be returned if not empty
        is_inside_extraction_block: bool = False
        extraction_block_found: bool = False

        for current_line in input_lines:
            stripped_line: str = current_line.strip()
            tag_info = MarkdownCustomMarkesCleaner._parse_tag(stripped_line)

            # --- Extraction Block Handling ---
            if tag_info:
                marker_prefix, tag_type = tag_info
                if marker_prefix == MarkdownCustomMarkesCleaner.EXTRACTION_MARKER_PREFIX:
                    if tag_type == "START":
                        is_inside_extraction_block = True
                        extraction_block_found = True
                        continue
                    if tag_type == "END":
                        is_inside_extraction_block = False
                        continue

            # Collect content if inside the extraction block
            if is_inside_extraction_block:
                extracted_lines.append(current_line)
                continue

            # --- Keep Line ---
            output_lines_final.append(current_line)

        final_cleaned_string: str = "\n".join(output_lines_final)
        extracted_content_list: Optional[list[str]] = extracted_lines if extraction_block_found and extracted_lines else None

        return final_cleaned_string, extracted_content_list
