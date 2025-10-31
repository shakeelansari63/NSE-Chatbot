from pydantic_settings import BaseSettings
import os


class AppConfig(BaseSettings):
    llm_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    llm_api_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "openai/gpt-oss-20b:free"
    nse_mcp_url: str = "https://nse-mcp-tools.azurewebsites.net/mcp"


_config = AppConfig()


# Get Config Object
def get_config():
    return _config


# Set LLM Config
def set_llm_config(provider: str | None, url: str, api_key: str, model: str):
    global _config

    # Set URL by provider
    if provider and provider.lower() == "openai":
        _config.llm_api_url = "https://api.openai.com/v1"
    elif provider and provider.lower() == "openrouter":
        _config.llm_api_url = "https://openrouter.ai/api/v1"
    else:
        _config.llm_api_url = url

    _config.llm_api_key = api_key
    _config.llm_model = model

    # Debug
    print(_config)
