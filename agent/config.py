from dataclasses import dataclass
from typing import TypedDict

from server_config import get_server_config


@dataclass
class LLMConfig:
    llm_api_url: str = get_server_config().llm_api_url
    llm_api_key: str = get_server_config().llm_api_key
    llm_model: str = get_server_config().llm_model
    nse_mcp_url: str = get_server_config().nse_mcp_url


class ProviderConfig(TypedDict):
    url: str
    models: list[str]


_config = LLMConfig()


# Get Config Object
def get_config() -> LLMConfig:
    return _config


# Set LLM Config
def set_llm_config(url: str, api_key: str, model: str):
    global _config

    # Set URL by provider
    _config.llm_api_url = url
    _config.llm_api_key = api_key
    _config.llm_model = model


def get_provider_url(provider: str) -> str:
    provider_info = provider_llm_map.get(provider.lower(), None)
    if provider_info:
        return provider_info["url"]
    else:
        return ""


def get_provider_models(provider: str) -> list[str]:
    provider_info = provider_llm_map.get(provider.lower(), None)
    if provider_info:
        return provider_info["models"]
    else:
        return []


provider_llm_map: dict[str, ProviderConfig] = {
    "openai": {
        "url": "https://api.openai.com/v1",
        "models": [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
        ],
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1",
        "models": [],
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1",
        "models": [],
    },
    "claude": {
        "url": "https://api.anthropic.com/v1",
        "models": [
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-opus-4-1",
            "claude-sonnet-4-0",
            "claude-3-7-sonnet-latest",
            "claude-opus-4-0",
            "claude-3-5-haiku-latest",
        ],
    },
}
