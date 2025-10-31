from model import OpenAIMessage
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from pprint import pprint


def langchain_messages_to_openai(
    messages: list[AIMessage | HumanMessage | ToolMessage | SystemMessage],
):
    openai_messages: list[OpenAIMessage] = []
    for message in messages:
        # Role
        role = "system"
        if isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, ToolMessage):
            role = "function"

        # Content
        content: str = str(message.content)
        if isinstance(message.content, list):
            content = " ".join([str(item) for item in message.content])
        openai_messages.append({"role": role, "content": content})

    return openai_messages


def openai_messages_to_langchain(
    messages: list[OpenAIMessage],
):
    langchain_messages: list[
        AIMessage | HumanMessage | ToolMessage | SystemMessage
    ] = []
    for message in messages:
        if message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=message["content"]))
        elif message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "function":
            langchain_messages.append(ToolMessage(content=message["content"]))
        elif message["role"] == "system":
            langchain_messages.append(SystemMessage(content=message["content"]))
    return langchain_messages
