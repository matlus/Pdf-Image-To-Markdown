import tempfile
from pathlib import Path

import fitz

from pdf_image_to_markdown.managers.gateways.gpt_vision_gateway import GptVisionGateway
from pdf_image_to_markdown.managers.models.azure_openai_config import AzureOpenAiConfig
from pdf_image_to_markdown.managers.processors.markdown_custom_markers_cleaner import MarkdownCustomMarkesCleaner
from pdf_image_to_markdown.managers.processors.plaintext_to_markdown_prompt_result_processor import (
    PlaintextToMarkdownPromptResultProcessor,  # PyMuPDF
)


class PdfImageToMarkdownManager:
    def __init__(self, azure_openai_config: AzureOpenAiConfig) -> None:
        self.pdf_image_to_markdown_prompt: str = self._get_system_prompt("pdf_image_to_markdown_prompt_v3")
        self.pdf_text_to_markdown_prompt: str = self._get_system_prompt("simple_markdown_prompt")
        self.markdown_fixup_clean_prompt: str = self._get_system_prompt("markdown_fixup_clean_prompt_v2")
        self.azure_openai_config: AzureOpenAiConfig = azure_openai_config
        self.gpt_vision_gateway: GptVisionGateway = GptVisionGateway(azure_openai_config, self.pdf_image_to_markdown_prompt)

    def _get_system_prompt(self, prompt_file_name: str) -> str:
        current_file: Path = Path(__file__).resolve()
        prompts_dir: Path = current_file.parent / "prompts"
        full_path: Path = prompts_dir / prompt_file_name
        with open(f"{full_path}.md", encoding="utf-8") as f:
            return f.read()

    async def get_markdown_for_pdf_document_using_page_images(self, pdf_path: str, batch_size: int = 1) -> str:
        # Step 1: Convert PDF document pages to images
        print("Convert PDF document pages to images")
        image_paths: list[Path] = self.convert_pdf_document_pages_to_images(pdf_path)
        print(f"Converted: {len(image_paths)} PDF document pages to images")

        # Step 2: Generate markdown for image pages in batches
        markdown_pages: list[str] = []
        total_pages: int = len(image_paths)
        toc_from_content: dict[int, list[str]] = {}

        # Step 3: Process images in batches of the specified size
        for batch_start in range(0, total_pages, batch_size):
            # Get the current batch of images (handle the last batch which might be smaller)
            batch_end: int = min(batch_start + batch_size, total_pages)
            current_batch: list[Path] = image_paths[batch_start:batch_end]

            # Process the whole batch at once if multiple pages
            if len(current_batch) > 1:
                batch_markdown: str = await self.gpt_vision_gateway.get_markdown_for_pages(current_batch)
                with Path(f"batch-markdown{batch_start + 1}.md").open("w", encoding="utf-8") as batch_markdown_file:
                    batch_markdown_file.write(batch_markdown)

                fixedup_markdown: str = await self.gpt_vision_gateway.fixup_and_clean_markdown(batch_markdown, self.markdown_fixup_clean_prompt)
                with Path(f"batch-markdown-fixed{batch_start + 1}.md").open("w", encoding="utf-8") as batch_markdown_file:
                    batch_markdown_file.write(fixedup_markdown)

                markdown_pages.append(fixedup_markdown)
            # Process single page with the single-page method
            else:
                initial_markdown_string: str = await self.gpt_vision_gateway.get_markdown_for_page(current_batch[0])
                with Path(f"batch-markdown-initial{batch_start + 1}.md").open("w", encoding="utf-8") as batch_markdown_file:
                    batch_markdown_file.write(initial_markdown_string)

                markdown_string_without_markers = MarkdownCustomMarkesCleaner.clean_up_markers(initial_markdown_string)

                if not MarkdownCustomMarkesCleaner.has_maaningful_content(markdown_string_without_markers):
                    continue

                with Path(f"batch-markdown-without-markers{batch_start + 1}.md").open("w", encoding="utf-8") as batch_markdown_file:
                    batch_markdown_file.write(markdown_string_without_markers)

                initial_fixedup_and_clean_markdown: str = await self.gpt_vision_gateway.fixup_and_clean_markdown(
                    markdown_string_without_markers, self.markdown_fixup_clean_prompt
                )
                (fixedup_markdown, toc_from_page_content) = MarkdownCustomMarkesCleaner.clean_markers_and_extract_toc(
                    initial_fixedup_and_clean_markdown
                )
                if toc_from_page_content:
                    toc_from_content[batch_start + 1] = toc_from_page_content

                if not fixedup_markdown.endswith("\n-----\n"):
                    fixedup_markdown += "\n-----\n"

                with Path(f"batch-markdown-fixed{batch_start + 1}.md").open("w", encoding="utf-8") as batch_markdown_file:
                    batch_markdown_file.write(fixedup_markdown)

                markdown_pages.append(fixedup_markdown)

            print(f"Completed processing pages {batch_start + 1} to {batch_end} of {total_pages}")

        return "".join(markdown_pages)

    async def get_markdown_for_pdf_document_using_plain_text(self, pdf_path: str, batch_size: int = 1) -> str:
        # Step 1: Get pages from the PDF document
        pdf_document: fitz.Document = fitz.open(pdf_path)
        pages_text: list[str] = []

        try:
            # Using proper text extraction parameters
            for page_num in range(len(pdf_document)):
                page: fitz.Page = pdf_document.load_page(page_num)
                # Use "text" mode with flags for better extraction
                page_text: str = page.get_text("text")

                # Add page number for clarity
                pages_text.append(f"[Page {page_num + 1}]\n{page_text}")
        finally:
            pdf_document.close()

        # Step 2: Create batches of pages
        batches: list[list[str]] = []
        for i in range(0, len(pages_text), batch_size):
            batch: list[str] = pages_text[i : i + batch_size]
            batches.append(batch)

        # Steps 3-6: Process each batch
        markdown_pages: list[str] = []
        current_prompt: str = self.pdf_text_to_markdown_prompt

        prompt_processor: PlaintextToMarkdownPromptResultProcessor = PlaintextToMarkdownPromptResultProcessor()

        for batch_idx, batch in enumerate(batches):
            batch_text: str = "\n\n-----\n\n".join(batch)

            # Call LLM with the batch text and current prompt
            prompt_result: str = await self.gpt_vision_gateway.get_markdown_for_text(batch_text, current_prompt)
            with Path(f"prompt_result-{batch_idx + 1}.md").open("w", encoding="utf-8") as batch_file:
                batch_file.write(prompt_result)

            # Process the result to get markdown and updated state information
            markdown_content: str
            updated_prompt: str
            markdown_content, updated_prompt = prompt_processor.process_prompt_result(prompt_result, self.pdf_text_to_markdown_prompt)

            # Update the current prompt with state information for next batch
            current_prompt = updated_prompt

            with Path(f"batch-{batch_idx + 1}.md").open("w", encoding="utf-8") as batch_file:
                batch_file.write(markdown_content)

            markdown_pages.append(markdown_content)
            print(f"Completed processing batch {batch_idx + 1} of {len(batches)}")

        return "".join(markdown_pages)

    # Step 1: Convert PDF document Pages to Images
    def convert_pdf_document_pages_to_images(self, pdf_path: str) -> list[Path]:
        image_paths: list[Path] = []
        temp_dir: str = tempfile.mkdtemp()

        # Open the PDF file
        pdf_document: fitz.Document = fitz.open(pdf_path)
        try:
            # Use range-based iteration with explicit page loading to satisfy type checker
            for page_num in range(len(pdf_document)):
                page: fitz.Page = pdf_document.load_page(page_num)  # type: ignore
                # Convert page to image using fitz
                pixmap: fitz.Pixmap = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # type: ignore

                # Save image to temp folder
                image_path: Path = Path(temp_dir) / f"page_{page_num + 1}.png"
                pixmap.save(filename=str(image_path), output=None, jpg_quality=100)  # type: ignore

                # Add to list of image paths
                image_paths.append(image_path)

            return image_paths

        finally:
            pdf_document.close()
