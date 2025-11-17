from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from .config import get_config
from .messages import system_message

config = get_config()


async def get_agent():
    mcp_client = MultiServerMCPClient(
        {
            "nse-mcp": {
                "url": config.nse_mcp_url,
                "transport": "streamable_http",
            }
        }
    )

    tools = await mcp_client.get_tools()

    agent = create_agent(
        model=ChatOpenAI(
            base_url=config.llm_api_url,
            api_key=SecretStr(config.llm_api_key),
            model=config.llm_model,
        ),
        tools=tools,
        system_prompt=system_message,
    )

    return agent
