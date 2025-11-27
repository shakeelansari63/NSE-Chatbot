from typing import Any

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage

from agent.graph import GraphState
from server_config import get_server_config as sc

from .model import GradioMessage, GradioMessageContent


def langchain_messages_to_gradio(
    messages: list[BaseMessage],
) -> list[GradioMessage]:
    gradio_messages: list[GradioMessage] = []
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
        message_content = str(message.content)
        if isinstance(message.content, list):
            message_content = " ".join([str(item) for item in message.content])
        gradio_messages.append(
            GradioMessage(
                role=role,
                content=[GradioMessageContent(type="text", text=message_content)],
            )
        )

    return gradio_messages


def gradio_messages_to_langchain(
    messages: list[GradioMessage],
) -> list[BaseMessage]:
    langchain_messages: list[BaseMessage] = []
    for message in messages:
        if message["role"] == "assistant":
            langchain_messages.append(
                AIMessage(content=str(message["content"][0]["text"]))
            )
        elif message["role"] == "user":
            langchain_messages.append(
                HumanMessage(content=str(message["content"][0]["text"]))
            )
        elif message["role"] == "system":
            langchain_messages.append(
                SystemMessage(content=str(message["content"][0]["text"]))
            )
    return langchain_messages


def generate_agent_state_from_messages(
    messages: list[GradioMessage],
) -> GraphState | dict[str, Any]:
    # Convert messages to Langchain format
    lc_messages = gradio_messages_to_langchain(messages)

    # Use message in state
    if sc().select_agent_type == "flow":
        return GraphState(messages=lc_messages)
    else:
        return {"messages": lc_messages}
