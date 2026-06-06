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
            "gpt-5.5",
            "gpt-5.5-pro",
            "gpt-5.5-instant",
            "gpt-5.4-mini",
            "gpt-5.4-nano",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
        ],
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1",
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-4-scout-17b-16e-instruct",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen3-32b",
            "deepseek-r1-distill-llama-70b",
            "moonshotai/kimi-k2-instruct",
        ],
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1",
        "models": [],
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "models": [
            "gemini-3.5-flash",
            "gemini-3.5-pro",
            "gemini-3.1-flash-lite",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
        ],
    },
    "claude": {
        "url": "https://api.anthropic.com/v1",
        "models": [
            "claude-opus-4-8",
            "claude-opus-4-7",
            "claude-sonnet-4-6",
            "claude-sonnet-5-fennec",
            "claude-haiku-4-5",
        ],
    },
}
