from typing import Any

from gradio import ChatMessage

from agent.graph import get_agent

from .utils import (
    generate_agent_state_from_messages,
    langchain_messages_to_gradio,
)


async def agent_chat_fn(
    message: str,
    history: list[ChatMessage | dict[str, Any]],
) -> list[ChatMessage]:
    agent = await get_agent()

    # Refine History
    refined_history: list[ChatMessage] = []

    for history_msg in history:
        if isinstance(history_msg, ChatMessage):
            refined_history.append(history_msg)
        else:
            refined_history.append(
                ChatMessage(role=history_msg["role"], content=history_msg["content"])
            )

    # Add User question to history
    refined_history.append(ChatMessage(role="user", content=message))

    # Generate State Object
    state = generate_agent_state_from_messages(refined_history)

    resp = await agent.ainvoke(state)
    return langchain_messages_to_gradio(resp["messages"])


def send_message_to_ui(message: str, history: list[ChatMessage]):
    return [*history, ChatMessage(role="user", content=message)], ""
