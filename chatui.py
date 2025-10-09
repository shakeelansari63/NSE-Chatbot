from dotenv import load_dotenv
import gradio as gr
from graph import get_agent

load_dotenv(override=True)

async def chat_app(message: str, history: list[str] = []):
    agent = await get_agent()
    resp = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]}
    )

    return resp["messages"][-1].content

ui = gr.ChatInterface(chat_app, type="messages")