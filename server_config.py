from functools import cache

from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class ServerConfig(BaseSettings):
    # Symbol for testing
    test_symbol: str = "TCS"
    # Server Config
    host: str = "0.0.0.0"
    port: int = 8000
    ui_path: str = "/ui"
    mcp_path: str = "/mcp"
    favicon_path: str = "assets/favicon.ico"

    # Postgres DB Config
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "postgres"
    pg_pass: str = ""
    pg_db: str = "postgres"

    # MCP Config
    llm_api_key: str = ""
    llm_api_url: str = ""
    llm_model: str = ""

    # Generate DB URL from Config
    @computed_field
    @property
    def pg_url(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    # Generate MCP URL
    @computed_field
    @property
    def nse_mcp_url(self) -> str:
        return f"http://localhost:{self.port}{self.mcp_path}/"


@cache
def get_server_config() -> ServerConfig:
    _conf = ServerConfig()
    return _conf
