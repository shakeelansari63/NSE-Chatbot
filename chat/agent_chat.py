from typing import Any

from agent.graph import get_agent

from .model import GradioMessage, GradioMessageContent
from .utils import (
    generate_agent_state_from_messages,
    langchain_messages_to_gradio,
)


async def agent_chat_fn(
    message: str,
    history: list[GradioMessage],
) -> list[GradioMessage]:
    agent = await get_agent()

    # Add User question to history
    history.append(
        GradioMessage(
            role="user",
            content=[GradioMessageContent(type="message", text=message)],
        )
    )

    # Generate State Object
    state = generate_agent_state_from_messages(history)

    resp = await agent.ainvoke(state)
    return langchain_messages_to_gradio(resp["messages"])


def send_message_to_ui(
    message: str, history: list[GradioMessage]
) -> tuple[list[GradioMessage], str]:
    return history + [
        GradioMessage(
            role="user",
            content=[GradioMessageContent(type="text", text=message)],
        )
    ], ""
