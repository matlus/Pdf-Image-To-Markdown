import asyncio
import os
import time
from pathlib import Path
from typing import Optional

from pdf_image_to_markdown.managers.models.azure_openai_config import AzureOpenAiConfig
from pdf_image_to_markdown.managers.models.storage_account_config import StorageAccountConfig
from pdf_image_to_markdown.managers.pdf_image_to_markdown_manager import PdfImageToMarkdownManager


def get_configuration_settings() -> tuple[StorageAccountConfig, AzureOpenAiConfig]:
    # Azure Storage Configuration
    blob_container_url = os.getenv("BLOB_CONTAINER_URL")
    assert blob_container_url is not None, "BLOB_CONTAINER_URL environment variable is not set"

    # Get Azure Open API related Configuration
    endpoint = os.getenv("endpoint")
    assert endpoint is not None, "endpoint environment variable is not set"
    api_version = os.getenv("apiVersion")
    assert api_version is not None, "apiVersion environment variable is not set"
    model_deployment_name = os.getenv("modelDeploymentName")
    assert model_deployment_name is not None, "modelDeploymentName environment variable is not set"

    # Optional Configuration
    # api_key or token_provider_url must be present
    api_key: Optional[str] = os.getenv("accessKey")
    token_provider_url: Optional[str] = os.getenv("tokenProviderUrl")

    azure_open_ai_config = AzureOpenAiConfig(endpoint, api_version, model_deployment_name, "", "", api_key, token_provider_url)
    storage_account_config = StorageAccountConfig(blob_container_url, token_provider_url)

    return storage_account_config, azure_open_ai_config


async def main() -> None:
    start_time = time.perf_counter()

    # Get configuration settings from environment variables
    storage_account_config, azure_open_ai_config = get_configuration_settings()

    pdf_image_to_markdown_manager = PdfImageToMarkdownManager(azure_open_ai_config)

    pdf_file_path_and_name: str = "Test Case RFx document.pdf"
    markdown: str = await pdf_image_to_markdown_manager.get_markdown_for_pdf_document_using_page_images(pdf_file_path_and_name)
    # markdown: str = await pdf_image_to_markdown_manager.get_markdown_for_pdf_document_using_plain_text(pdf_file_path_and_name)

    markdown_file_path = pdf_file_path_and_name.replace(".pdf", ".md")
    with Path(markdown_file_path).open("w", encoding="utf-8") as markdown_file:
        markdown_file.write(markdown)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = elapsed_time % 60

    # Format and print the time
    print(f"Execution time: {hours}:{minutes:02}:{seconds:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
    # Run the main function
