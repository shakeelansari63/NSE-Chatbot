from typing import Any

import gradio as gr

from .config import get_provider_models, get_provider_url, set_llm_config
from .graph import get_agent
from .messages import langchain_messages_to_openai
from .model import OpenAIMessage

# Force Dark Theme on Gradio
js_func = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""


async def chat_app(message: str, history: list[OpenAIMessage]):
    agent = await get_agent()

    # Add User question to history
    history.append(OpenAIMessage(role="user", content=message))
    resp = await agent.ainvoke({"messages": history})
    return langchain_messages_to_openai(resp["messages"])


def send_message_to_ui(message: str, history: list[OpenAIMessage]):
    return [*history, OpenAIMessage(role="user", content=message)], ""


def llm_form_by_provider(provider: str) -> tuple[gr.Textbox, gr.Dropdown]:
    url = get_provider_url(provider)
    model = get_provider_models(provider)

    # URL Component
    url_component = gr.Textbox(label="API URL", visible=False, value=url)
    # Check for Valid URl
    if not url:
        url_component = gr.Textbox(label="API URL", visible=True)

    # Model Component
    model_component = gr.Dropdown(
        choices=model,
        label="Model",
        visible=True,
        allow_custom_value=False,
    )

    # Check for Valid Model
    if len(model) == 0:
        model_component = gr.Dropdown(
            choices=model,
            label="Model",
            visible=True,
            allow_custom_value=True,
        )

    return url_component, model_component


# ui = gr.ChatInterface(chat_app, type="messages")
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="teal", neutral_hue="zinc"),
    js=js_func,
    css="footer {display:none !important}",
) as ui:
    # Header
    with gr.Row():
        gr.HTML(
            """
            <center><h1>🚀 NSE Chatbot 🚀</h1></center>
            """
        )
    # Select LLM Provider
    with gr.Accordion(
        "(Optional) Choose your own LLM Provider",
        open=False,
    ):
        with gr.Row():
            with gr.Group():
                with gr.Row():
                    llm_provider = gr.Dropdown(
                        choices=["OpenAI", "Groq", "OpenRouter", "Claude", "Other"],
                        label="LLM Provider",
                    )
                    llm_api_url = gr.Textbox(label="API URL", visible=False)
                    llm_model = gr.Dropdown(
                        choices=get_provider_models("OpenAI"),
                        label="Model",
                        visible=True,
                        allow_custom_value=False,
                    )
                    llm_api_key = gr.Textbox(
                        label="API Key",
                        type="password",
                        visible=True,
                    )

                save_llm_detail = gr.Button("Save")

            # Based on Provider, show API url field
            llm_provider.change(
                llm_form_by_provider,
                inputs=llm_provider,
                outputs=[llm_api_url, llm_model],
            )

            # Save LLM details
            save_llm_detail.click(
                set_llm_config,
                inputs=[llm_api_url, llm_api_key, llm_model],
                outputs=[],
            )

    # Chat Bot
    with gr.Row():
        chatbot = gr.Chatbot(
            type="messages",
            label="NSE Chatbot",
            resizable=True,
            height=500,
        )

    with gr.Row():
        with gr.Group():
            text_input = gr.Textbox(
                show_label=False, placeholder="Ask your question..."
            )
            send_button = gr.Button("Ask")

    # Bottom Disclaimer
    with gr.Row():
        disclaimer = gr.Markdown(
            "**Disclaimer:** This Chatbot uses Free tier LLM model from GROQ which would be rate limited. If you have personal key for OpenAI/OpenRouter/Groq/Claude, please choose at the top."
        )

    # Event Handlers
    send_button.click(chat_app, inputs=[text_input, chatbot], outputs=chatbot)
    send_button.click(
        send_message_to_ui, inputs=[text_input, chatbot], outputs=[chatbot, text_input]
    )
    text_input.submit(chat_app, inputs=[text_input, chatbot], outputs=chatbot)
    text_input.submit(
        send_message_to_ui, inputs=[text_input, chatbot], outputs=[chatbot, text_input]
    )
