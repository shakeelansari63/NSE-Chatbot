from functools import cache
from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, SecretStr

from server_config import get_server_config as sc

from .config import get_config
from .local_tools import get_line_chart_for_data
from .messages import (
    get_execution_system_message,
    get_shortlist_message,
)

config = get_config()


# Define State Schema for Graph
class GraphState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    tools: list[BaseTool] = Field(default_factory=list)
    evaluator_feedback: str | None = None


# Structured Output for Tool Shortlisting Agent
class ShortlistOutput(TypedDict):
    tools: list[str]


async def _get_all_tools():
    mcp_client = MultiServerMCPClient(
        {
            "nse-mcp": {
                "url": config.nse_mcp_url,
                "transport": "streamable_http",
            }
        }
    )

    all_tools = await mcp_client.get_tools()

    #  Add Local Tools
    all_tools.append(get_line_chart_for_data)

    # Return Tools
    return all_tools


def _get_llm_model() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=config.llm_api_url,
        api_key=SecretStr(config.llm_api_key),
        model=config.llm_model,
    )


# Generate First Node to Shortlist tools for the task
async def tools_shortlist_node(state: GraphState) -> GraphState:
    # Generate List of Tool Names
    all_tools = await _get_all_tools()
    all_tool_names = [tool.name for tool in all_tools]

    # Instruction for Model
    user_message = [
        HumanMessage(content=get_shortlist_message(all_tool_names, state.messages))
    ]

    llm = _get_llm_model().with_structured_output(ShortlistOutput, strict=True)
    output: ShortlistOutput = llm.invoke(user_message)

    # Extract the shortlisted tools from the output
    shortlisted_tools = [tool for tool in all_tools if tool.name in output["tools"]]

    # Update and return State
    state.tools = shortlisted_tools

    return state


# Node to execute User command with available Tools
async def user_command_execution_node(state: GraphState) -> GraphState:
    # Generate Tool calling Agent
    execution_agent = create_agent(
        model=_get_llm_model(),
        tools=state.tools,
        system_prompt=get_execution_system_message(),
    )

    # Execute With Tool Calling Agent
    output = await execution_agent.ainvoke({"messages": state.messages})

    # Update and return State
    state.messages = output["messages"]
    return state


async def get_agent_react():
    # Get All Tools
    all_tools = await _get_all_tools()

    # Return ReAct agent with all tools
    return create_agent(
        model=_get_llm_model(),
        tools=all_tools,
        system_prompt=get_execution_system_message(),
    )


# Memoize Agent Flow Graph
@cache
def get_agent_flow():
    # Define new State Graph
    graph = StateGraph(GraphState)

    # Add Nodes
    graph.add_node("tool_shortlist", tools_shortlist_node)
    graph.add_node("user_command_execution", user_command_execution_node)

    # Edges for Graph Execution
    graph.add_edge(START, "tool_shortlist")
    graph.add_edge("tool_shortlist", "user_command_execution")
    graph.add_edge("user_command_execution", END)

    # Compile Graph
    agent_flow = graph.compile()

    # Return Agent Flow
    return agent_flow


async def get_agent():
    # Get agent based on config
    if sc().select_agent_type == "flow":
        return get_agent_flow()
    else:
        return await get_agent_react()
