from gradio import ChatMessage
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage


def langchain_messages_to_gradio(
    messages: list[BaseMessage],
) -> list[ChatMessage]:
    gradio_messages: list[ChatMessage] = []
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
        gradio_messages.append(ChatMessage(role=role, content=content))

    return gradio_messages


def gradio_messages_to_langchain(
    messages: list[ChatMessage],
) -> list[BaseMessage]:
    langchain_messages: list[BaseMessage] = []
    for message in messages:
        if message.role == "assistant":
            langchain_messages.append(AIMessage(content=str(message.content)))
        elif message.role == "user":
            langchain_messages.append(HumanMessage(content=str(message.content)))
        elif message.role == "system":
            langchain_messages.append(SystemMessage(content=str(message.content)))
    return langchain_messages
