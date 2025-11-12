from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from model import OpenAIMessage

_system_message = (
    "You are National Stock Exchange Assistant and give informations about Indian National Stock Exchange (NSE). "
    "To answer the questions you can use the provided Tools. "
    "Most of the tools need a valid NSE symbol and will NOT work with just Company Name. "
    "You also have access to tool which can look for NSE Companies and return matching Company name and Symbol. "
    "Use this tool to identify the right NSE Symbol for Company. "
    "Never guess the symbol of Company. When in doubt use the tool to find the right symbol. "
)

system_prompt = OpenAIMessage(role="system", content=_system_message)


def langchain_messages_to_openai(
    messages: list[AIMessage | HumanMessage | ToolMessage | SystemMessage],
):
    openai_messages: list[OpenAIMessage] = []
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
        elif isinstance(message, ToolMessage):
            continue

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
