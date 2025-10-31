import gradio as gr
from graph import get_agent
from config import set_llm_config
from messages import langchain_messages_to_openai
from model import OpenAIMessage


async def chat_app(message: str, history: list[OpenAIMessage]):
    agent = await get_agent()

    # Add User question to history
    history.append(OpenAIMessage(role="user", content=message))
    resp = await agent.ainvoke({"messages": history})
    return langchain_messages_to_openai(resp["messages"])


def send_message_to_ui(message: str, history: list[OpenAIMessage]):
    return [*history, OpenAIMessage(role="user", content=message)], ""


# ui = gr.ChatInterface(chat_app, type="messages")
with gr.Blocks() as ui:
    # Select LLM Provider
    with gr.Accordion(
        "The default LLM uses free tier OpenRouter and will be rate limited. If you have a paid account to frontier model, please select it accordingly",
        open=False,
    ):
        with gr.Row():
            with gr.Group():
                with gr.Row():
                    llm_provider = gr.Dropdown(
                        choices=["OpenAI", "OpenRouter", "Other"], label="LLM Provider"
                    )
                    llm_api_url = gr.Textbox(label="API URL", visible=False)
                    llm_api_key = gr.Textbox(
                        label="API Key", type="password", visible=True
                    )
                    llm_model = gr.Textbox(label="Model", visible=True)
                save_llm_detail = gr.Button("Save")

            # Based on Provider, show API url field
            llm_provider.change(
                lambda x: gr.Textbox(label="API URL", visible=(x == "Other")),
                inputs=llm_provider,
                outputs=llm_api_url,
            )

            # Save LLM details
            save_llm_detail.click(
                lambda provider, url, key, model: set_llm_config(
                    provider, url, key, model
                ),
                inputs=[llm_provider, llm_api_url, llm_api_key, llm_model],
                outputs=[],
            )

    # Chat Bot
    with gr.Row():
        chatbot = gr.Chatbot(type="messages", label="NSE Chatbot")

    with gr.Row():
        with gr.Group():
            text_input = gr.Textbox(label="", placeholder="Ask your question...")
            send_button = gr.Button("Ask")

    # Event Handlers
    send_button.click(chat_app, inputs=[text_input, chatbot], outputs=chatbot)
    send_button.click(
        send_message_to_ui, inputs=[text_input, chatbot], outputs=[chatbot, text_input]
    )
    text_input.submit(chat_app, inputs=[text_input, chatbot], outputs=chatbot)
    text_input.submit(
        send_message_to_ui, inputs=[text_input, chatbot], outputs=[chatbot, text_input]
    )
