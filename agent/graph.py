import json
import re
from functools import cache
from typing import Annotated, Any, TypedDict

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, SecretStr

from .config import get_config
from .local_tools import get_line_chart_for_data
from .messages import (
    get_execution_system_message,
    get_out_of_scope_system_message,
    get_shortlist_message,
)

config = get_config()


# Define State Schema for Graph
class GraphState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    tools: list[BaseTool] = Field(default_factory=list)
    evaluator_feedback: str | None = None
    llm_api_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    scope_valid: bool = True


# Structured Output for Out-of-Scope Detector
class ScopeOutput(TypedDict):
    is_in_scope: bool
    response: str


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


def _get_llm_model(
    api_url: str = "",
    api_key: str = "",
    model: str = "",
) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=api_url or config.llm_api_url,
        api_key=SecretStr(api_key or config.llm_api_key),
        model=model or config.llm_model,
    )


_JSON_RE = re.compile(r"\{[^}]+\}")


def _parse_scope_output(text: str) -> dict:
    """Parse JSON from LLM text response, with fallback to regex defaults."""
    try:
        match = _JSON_RE.search(text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    # Fallback: treat any free-form text as in-scope to avoid false rejections
    return {"is_in_scope": True, "response": ""}


# First Node: Detect if the query is NSE-stock related
async def out_of_scope_detector_node(state: GraphState) -> GraphState:
    user_message = [
        HumanMessage(content=get_out_of_scope_system_message(state.messages))
    ]

    llm = _get_llm_model(state.llm_api_url, state.llm_api_key, state.llm_model)

    # Primary path: structured output (OpenAI, etc.)
    result: dict[str, Any] = {"is_in_scope": True, "response": ""}
    try:
        structured = llm.with_structured_output(ScopeOutput, strict=True)
        result = structured.invoke(user_message)  # type: ignore[assignment]
    except Exception:
        # Fallback: parse JSON from plain-text response (Gemma, etc.)
        output = llm.invoke(user_message)
        result = _parse_scope_output(output.content)

    if not result.get("is_in_scope", True):
        state.scope_valid = False
        state.messages.append(AIMessage(content=result.get("response", "")))

    return state


def route_after_scope(state: GraphState) -> str:
    return "tool_shortlist" if state.scope_valid else END


# Generate Second Node to Shortlist tools for the task
async def tools_shortlist_node(state: GraphState) -> GraphState:
    # Generate List of Tool Names
    all_tools = await _get_all_tools()
    all_tool_names = [tool.name for tool in all_tools]

    # Instruction for Model
    user_message = [
        HumanMessage(content=get_shortlist_message(all_tool_names, state.messages))
    ]

    llm = _get_llm_model(
        state.llm_api_url, state.llm_api_key, state.llm_model
    ).with_structured_output(ShortlistOutput, strict=True)
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
        model=_get_llm_model(state.llm_api_url, state.llm_api_key, state.llm_model),
        tools=state.tools,
        system_prompt=get_execution_system_message(),
    )

    # Execute With Tool Calling Agent
    output = await execution_agent.ainvoke({"messages": state.messages})

    # Update and return State
    state.messages = output["messages"]
    return state


# Memoize Agent Flow Graph — the graph structure is fixed; LLM config
# flows through the state, so it's safe to cache across sessions.
@cache
def get_agent():
    graph = StateGraph(GraphState)

    # Add Nodes
    graph.add_node("out_of_scope_detector", out_of_scope_detector_node)
    graph.add_node("tool_shortlist", tools_shortlist_node)
    graph.add_node("user_command_execution", user_command_execution_node)

    # Edges for Graph Execution
    graph.add_edge(START, "out_of_scope_detector")
    graph.add_conditional_edges(
        "out_of_scope_detector",
        route_after_scope,
    )
    graph.add_edge("tool_shortlist", "user_command_execution")
    graph.add_edge("user_command_execution", END)

    # Compile Graph
    agent_flow = graph.compile()

    return agent_flow
