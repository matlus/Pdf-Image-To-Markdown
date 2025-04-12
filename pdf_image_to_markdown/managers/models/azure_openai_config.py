from dataclasses import dataclass
from typing import Optional


@dataclass
class AzureOpenAiConfig:
    def __init__(  # noqa: PLR0913
        self,
        endpoint: str,
        api_version: str,
        model_deployment_name: str,
        embedding_model_deployment_name: str,
        embedding_model_api_version: str,
        api_key: Optional[str],
        token_provider_url: Optional[str] = None,
        max_tokens: int = 16384,
    ):
        self.endpoint: str = endpoint
        self.api_version: str = api_version
        self.model_deployment_name: str = model_deployment_name
        self.embedding_model_deployment_name: str = embedding_model_deployment_name
        self.embedding_model_api_version = embedding_model_api_version
        self.api_key: Optional[str] = api_key
        self.token_provider_url: Optional[str] = token_provider_url
        self.max_tokens: int = max_tokens
