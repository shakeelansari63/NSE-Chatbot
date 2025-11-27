from typing import Any

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage

from agent.graph import GraphState
from server_config import get_server_config as sc

from .model import GradioChatMessage


def langchain_messages_to_gradio(
    messages: list[BaseMessage],
) -> list[GradioChatMessage]:
    gradio_messages: list[GradioChatMessage] = []
    for message in messages:
        # Role
        role = "system"
        if isinstance(message, AIMessage):
            # Skip Tool Call where Content was empty
            if not message.content:
                continue

            # Otherwise register as Assistant message
            role = "assistant"
        elif isinstance(message, HumanMessage):
            role = "user"

        # Stop processing any other message type
        else:
            continue

        # Content
        content: str = str(message.content)
        if isinstance(message.content, list):
            content = " ".join([str(item) for item in message.content])
        gradio_messages.append(GradioChatMessage(role=role, content=content))

    return gradio_messages


def gradio_messages_to_langchain(
    messages: list[GradioChatMessage],
) -> list[BaseMessage]:
    langchain_messages: list[BaseMessage] = []
    for message in messages:
        if message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=str(message["content"])))
        elif message["role"] == "user":
            langchain_messages.append(HumanMessage(content=str(message["content"])))
        elif message["role"] == "system":
            langchain_messages.append(SystemMessage(content=str(message["content"])))
    return langchain_messages


def generate_agent_state_from_messages(
    messages: list[GradioChatMessage],
) -> GraphState | dict[str, Any]:
    # Convert messages to Langchain format
    lc_messages = gradio_messages_to_langchain(messages)

    # Use message in state
    if sc().select_agent_type == "flow":
        return GraphState(messages=lc_messages)
    else:
        return {"messages": lc_messages}
