from dotenv import load_dotenv
import gradio as gr
from graph import get_agent

load_dotenv(override=True)


async def chat_app(message: str, history: list[str]):
    agent = await get_agent()
    resp = await agent.ainvoke({"messages": [{"role": "user", "content": message}]})

    return resp["messages"]


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
                save_llm_detail = gr.Button("Save")

            # Based on Provider, show API url field
            llm_provider.change(
                lambda x: gr.Textbox(label="API URL", visible=(x == "Other")),
                inputs=llm_provider,
                outputs=llm_api_url,
            )

            # Save LLM details
            save_llm_detail.click(
                lambda provider, url, key: save_llm(provider, url, key),
                inputs=[llm_provider, llm_api_url, llm_api_key],
                outputs=[],
            )

    # Chat Bot
    with gr.Row():
        chatbot = gr.Chatbot(type="messages")

    with gr.Row():
        with gr.Group():
            text_input = gr.Textbox(label="Message", placeholder="Ask your question...")
            send_button = gr.Button("Ask")

    # Event Handlers
    send_button.click(chat_app, inputs=[text_input, chatbot], outputs=chatbot)
