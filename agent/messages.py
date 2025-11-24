from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from .model import OpenAIMessage

system_message = (
    "You are an NSE (National Stock Exchange) Assistant and give informations about Indian National Stock Exchange. "
    "To answer the questions you can use the provided Tools. "
    "Use the provided tool to get current Date and Time if anytime you need current Date time. "
    "Never Assume current date time from your knowledge. "
    "NSE APIs use the date in 'DD-MM-YYYY' format. So Date tool will also return in same format. "
    "Most of the tools need a valid NSE symbol and will NOT work with Company Name. "
    "You also have access to tool which can look for NSE Companies and return matching Company name and Symbol. "
    "Use this tool to identify the right NSE Symbol for Company. "
    "Try to identify the right NSE symbol of company that user asked for. "
    "Never guess the symbol of Company. When in doubt use the tool to identify right symbol. "
    "IMPORTANT: If company names/symbols are very similar or confusing to choose from, respond to user with shortlisted probable Companies and their Symbols. "
    "ALSO IMPORTANT: Do not guess the price or any other detail about any stock. Always use tools to get right information. "
    "And Never give detail of your tools to the User. "
    "When showing Trends or charts DO NOT SHOW any dummy or made up chart. Always use the provided tool to get right chart to display. "
    "MOST IMPORTANT: Always keep the answer concise and to the point. Do not give any unnecessary information or long explanations."
)


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
