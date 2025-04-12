from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, cast

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobClient, BlobServiceClient, StorageStreamDownloader

from pdf_image_to_markdown.managers.exceptions.application_base_exception import LogEvent
from pdf_image_to_markdown.managers.exceptions.blob_move_file_exception import BlobMoveFileException
from pdf_image_to_markdown.managers.models.storage_account_config import StorageAccountConfig


class BlobMoveFileEvent(LogEvent):
    BlobMoveFileFailed = "BlobMoveFileFailed"


@dataclass
class FileInfo:
    def __init__(self, path: str, path_and_name: str, file_name: str, file_type: str):
        self.path: str = path
        self.path_and_name: str = path_and_name
        self.file_name: str = file_name
        self.file_type: str = file_type

    def __str__(self):
        return f"Path: {self.path}, Full Name: {self.path_and_name}, File Name: {self.file_name}, File Type: {self.file_type}"


class BlobStorageGateway:
    def __init__(self, storage_account_config: StorageAccountConfig):
        self.container_name: str = storage_account_config.container_name
        self.blob_service_client = self.__internal_create_blob_service_client(storage_account_config)
        self.blob_container_client = self.blob_service_client.get_container_client(storage_account_config.container_name)

    def __internal_create_blob_service_client(self, storage_account_config: StorageAccountConfig) -> BlobServiceClient:
        default_azure_credential = DefaultAzureCredential()
        if storage_account_config.token_provider_url:
            token_provider: Callable[[], str] = get_bearer_token_provider(default_azure_credential, storage_account_config.token_provider_url)
            return BlobServiceClient(account_url=storage_account_config.blob_storage_endpoint, token_provider=token_provider)
        return BlobServiceClient(account_url=storage_account_config.blob_storage_endpoint, credential=default_azure_credential)

    def get_all_files_from_container(self, sub_container_path: str | None = None) -> list[FileInfo]:
        blob_list = self.blob_container_client.list_blobs(name_starts_with=sub_container_path)

        files: list[FileInfo] = []
        for blob in blob_list:
            file_info: FileInfo = FileInfo(
                path=f"{Path(blob.name).parent}/",
                path_and_name=blob.name,
                file_name=Path(blob.name).name,
                file_type=Path(blob.name).suffix[1:].upper(),
            )

            files.append(file_info)
        return files

    def download_file_from_container(self, blob_name: str) -> bytes:
        blob_client: BlobClient = self.blob_container_client.get_blob_client(blob_name)
        storage_stream_downloader: StorageStreamDownloader[bytes] = blob_client.download_blob()
        file_content: bytes = storage_stream_downloader.readall()
        return file_content

    def upload_file_to_container(self, file_path_and_name: str, file_bytes: bytes, content_type: str) -> None:
        blob_client: BlobClient = self.blob_container_client.get_blob_client(file_path_and_name)

        options = {}
        if content_type:
            options["content_type"] = content_type

        blob_client.upload_blob(file_bytes, blob_type="BlockBlob", length=len(file_bytes), metadata=None, overwrite=True, **options)

    def blob_exists(self, blob_name: str):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
        return blob_client.exists()

    def move_file(self, source_blob_name: str, destination_blob_name: str) -> None:
        source_blob_client: BlobClient = self.blob_container_client.get_blob_client(source_blob_name)
        destination_blob_client: BlobClient = self.blob_container_client.get_blob_client(destination_blob_name)

        source_url: str = cast(str, source_blob_client.url)  # type: ignore
        copy_props: dict[str, Any] = destination_blob_client.start_copy_from_url(source_url)

        if copy_props["copy_status"] == "success":
            source_blob_client.delete_blob()
            return
        contextual_data: dict[str, Any] = {
            "source_blob_name": source_blob_name,
            "destination_blob_name": destination_blob_name,
            "source_url": source_url,
            "copy_status": copy_props["copy_status"],
        }
        message: str = f"Blob Copy operation failed with status: {copy_props['copy_status']}"
        raise BlobMoveFileException(message, log_event=BlobMoveFileEvent.BlobMoveFileFailed, context_data=contextual_data)
