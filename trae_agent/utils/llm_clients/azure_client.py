# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Azure client wrapper with tool integrations"""

import openai

from trae_agent.utils.config import ModelConfig
from trae_agent.utils.llm_clients.openai_compatible_base import (
    OpenAICompatibleClient,
    ProviderConfig,
)

from azure.identity import DefaultAzureCredential, AzureCliCredential, get_bearer_token_provider


class AzureProvider(ProviderConfig):
    """Azure OpenAI provider configuration."""

    def create_client(
        self, api_key: str, base_url: str | None, api_version: str | None
    ) -> openai.OpenAI:
        """Create Azure OpenAI client."""
        if not base_url:
            raise ValueError("base_url is required for AzureClient")

        if "aoai" in base_url:
            identity_id = api_key
            gpt_endpoint = base_url
            token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
            api_version = "2024-12-01-preview"
            client = openai.AzureOpenAI(azure_endpoint=gpt_endpoint, azure_ad_token_provider=token_provider, api_version=api_version)        
        elif "cloudgpt" in base_url:
            api_scope_base = "api://feb7b661-cac7-44a8-8dc1-163b63c23df2"
            scope = api_scope_base + "/.default"
            tenant_id = api_key
            token_provider = get_bearer_token_provider(AzureCliCredential(tenant_id=tenant_id), scope)
            client = openai.AzureOpenAI(api_version=api_version, base_url=gpt_endpoint, azure_ad_token_provider=token_provider)
        else:
            client = openai.OpenAI(
                api_key="mock_api_key_for_azure_client",
                base_url=base_url
            )

        return client

    def get_service_name(self) -> str:
        """Get the service name for retry logging."""
        return "Azure OpenAI"

    def get_provider_name(self) -> str:
        """Get the provider name for trajectory recording."""
        return "azure"

    def get_extra_headers(self) -> dict[str, str]:
        """Get Azure-specific headers (none needed)."""
        return {}

    def supports_tool_calling(self, model_name: str) -> bool:
        """Check if the model supports tool calling."""
        # Azure OpenAI models generally support tool calling
        return True


class AzureClient(OpenAICompatibleClient):
    """Azure client wrapper that maintains compatibility while using the new architecture."""

    def __init__(self, model_config: ModelConfig):
        super().__init__(model_config, AzureProvider())
