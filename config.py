from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class AppConfig(BaseSettings):
    groq_api_key: str
    groq_api_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-20b"
    nse_mcp_url: str = 'https://nse-mcp-tools.azurewebsites.net/mcp'

config = AppConfig()