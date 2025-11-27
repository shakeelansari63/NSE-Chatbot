from agent.graph import get_agent

from .model import GradioChatMessage
from .utils import (
    generate_agent_state_from_messages,
    langchain_messages_to_gradio,
)


async def agent_chat_fn(
    message: str,
    history: list[GradioChatMessage],
) -> list[GradioChatMessage]:
    agent = await get_agent()

    # Add User question to history
    history.append(GradioChatMessage(role="user", content=message))

    # Generate State Object
    state = generate_agent_state_from_messages(history)

    resp = await agent.ainvoke(state)
    return langchain_messages_to_gradio(resp["messages"])


def send_message_to_ui(message: str, history: list[GradioChatMessage]):
    return [*history, GradioChatMessage(role="user", content=message)], ""
