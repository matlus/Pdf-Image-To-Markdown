import base64
from pathlib import Path
from typing import Callable

from azure.identity import DefaultAzureCredential
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam, ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_content_part_image_param import ChatCompletionContentPartImageParam
from openai.types.chat.chat_completion_content_part_param import ChatCompletionContentPartParam
from openai.types.chat.chat_completion_content_part_text_param import ChatCompletionContentPartTextParam

from pdf_image_to_markdown.managers.models.azure_openai_config import AzureOpenAiConfig


class GptVisionGateway:
    def __init__(self, azure_openai_config: AzureOpenAiConfig, image_to_markdown_prompt: str) -> None:
        self.config: AzureOpenAiConfig = azure_openai_config
        self.image_to_markdown_prompt: str = image_to_markdown_prompt
        self.max_tokens: int = azure_openai_config.max_tokens
        self.model_deployment_name: str = azure_openai_config.model_deployment_name
        self.client: AsyncAzureOpenAI = self.__create_client(azure_openai_config)

    def __create_client(self, config: AzureOpenAiConfig) -> AsyncAzureOpenAI:
        if config.token_provider_url:
            credential: DefaultAzureCredential = DefaultAzureCredential()
            token_provider: Callable[[], str] = self.__get_bearer_token_provider(credential, config.token_provider_url)
            return AsyncAzureOpenAI(
                api_version=config.api_version,
                azure_endpoint=config.endpoint,
                azure_ad_token_provider=token_provider,
            )
        return AsyncAzureOpenAI(
            api_version=config.api_version,
            azure_endpoint=config.endpoint,
            api_key=config.api_key,
        )

    def __get_bearer_token_provider(self, credential: DefaultAzureCredential, token_provider_url: str) -> Callable[[], str]:
        def token_provider() -> str:
            return credential.get_token(token_provider_url).token

        return token_provider

    def __encode_image_to_base64_uri(self, image_path: Path) -> str:
        suffix: str = image_path.suffix.lower()
        mime_type: str = "image/png" if suffix == ".png" else "image/jpeg"
        with image_path.open("rb") as file:
            encoded: bytes = base64.b64encode(file.read())
        return f"data:{mime_type};base64,{encoded.decode('utf-8')}"

    async def get_markdown_for_text(self, document_text: str, pdf_text_to_markdown_prompt_with_state: str) -> str:
        response: ChatCompletion = await self.client.chat.completions.create(
            model=self.model_deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": f"{pdf_text_to_markdown_prompt_with_state}\n\n{document_text}",
                }
            ],
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content or ""

    async def fixup_and_clean_markdown(self, markdown_of_pages: str, markdown_fixup_clean_prompt: str) -> str:
        response: ChatCompletion = await self.client.chat.completions.create(
            model=self.model_deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": f"{markdown_fixup_clean_prompt}\n\n{markdown_of_pages}",
                }
            ],
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content or ""

    async def get_markdown_for_pages(self, image_paths: list[Path]) -> str:
        text_part: ChatCompletionContentPartTextParam = {"type": "text", "text": self.image_to_markdown_prompt}

        content_parts: list[ChatCompletionContentPartParam] = []
        content_parts.append(text_part)

        for image_path in image_paths:
            image_part: ChatCompletionContentPartImageParam = {
                "type": "image_url",
                "image_url": {"url": self.__encode_image_to_base64_uri(image_path)},
            }
            content_parts.append(image_part)

        user_message: ChatCompletionUserMessageParam = {"role": "user", "content": content_parts}

        messages: list[ChatCompletionMessageParam] = [user_message]

        response: ChatCompletion = await self.client.chat.completions.create(
            model=self.model_deployment_name,
            messages=messages,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content or ""

    async def get_markdown_for_page(self, image_path_and_name: Path) -> str:
        image_uri: str = self.__encode_image_to_base64_uri(image_path_and_name)

        text_part: ChatCompletionContentPartTextParam = {"type": "text", "text": self.image_to_markdown_prompt}
        image_part: ChatCompletionContentPartImageParam = {"type": "image_url", "image_url": {"url": image_uri}}

        content_parts: list[ChatCompletionContentPartParam] = []
        content_parts.append(text_part)
        content_parts.append(image_part)

        user_message: ChatCompletionUserMessageParam = {"role": "user", "content": content_parts}

        messages: list[ChatCompletionMessageParam] = [user_message]

        response: ChatCompletion = await self.client.chat.completions.create(
            model=self.model_deployment_name,
            messages=messages,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content or ""
