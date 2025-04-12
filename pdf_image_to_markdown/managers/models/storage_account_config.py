from dataclasses import dataclass
from typing import Optional
from urllib.parse import ParseResult, urlparse


@dataclass
class StorageAccountConfig:
    def __init__(self, blob_container_url: str, token_provider_url: Optional[str]):
        [blob_storage_endpoint, container_name, table_storage_endpoint] = self.get_storage_account_info(blob_container_url)
        self.blob_storage_endpoint: str = blob_storage_endpoint
        self.container_name: str = container_name
        self.table_storage_endpoint: str = table_storage_endpoint
        self.token_provider_url: Optional[str] = token_provider_url

    def get_storage_account_info(self, blob_container_url: str) -> tuple[str, str, str]:
        parse_result: ParseResult = urlparse(blob_container_url)
        blob_storage_endpoint: str = f"{parse_result.scheme}://{parse_result.netloc}/"
        container_name: str = parse_result.path.split("/")[-1]
        hostname: str = parse_result.netloc
        account_name: str = hostname.split(".")[0]
        table_storage_endpoint: str = f"{parse_result.scheme}://{account_name}.table.core.windows.net"
        return blob_storage_endpoint, container_name, table_storage_endpoint
