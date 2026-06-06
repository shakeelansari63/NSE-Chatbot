import gradio as gr

from agent.config import get_provider_models, get_provider_url
from chat.agent_chat import agent_chat_fn, send_message_to_ui
from server_config import get_server_config as sc

from .components.docs import docs_page
from .components.navbar import navbar
from .config import socials

from .examples import get_examples, strip_example


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


def _update_llm_state(
    api_url: str, api_key: str, model: str, _current: dict
) -> dict:
    """Store per-session LLM config in Gradio state instead of global variables."""
    return {"url": api_url, "key": api_key, "model": model}


# Per-session LLM config — initialised from env defaults
# so each browser tab starts with a fresh, isolated copy.
_DEFAULT_LLM_CONFIG = {"url": sc().llm_api_url, "key": sc().llm_api_key, "model": sc().llm_model}

with gr.Blocks(
    title="NSE Chatbot",
) as ui:
    # Per-session state for LLM config
    llm_state = gr.State(_DEFAULT_LLM_CONFIG)

    # Navbar
    navbar()

    # Header
    with gr.Row():
        gr.HTML(
            f"""
            <span style="display: flex; justify-content: space-between; align-items: center;">
            <h1>🚀 NSE Chatbot 🚀</h1>
            <a href="{socials["github"]}" target="_blank" title="Star us on GitHub"><i class="fa-brands fa-github fa-2xl"></i></a>
            </span>
            """
        )

    # Select LLM Provider
    with gr.Sidebar(
        position="right",
        open=False,
    ):
        with gr.Row():
            with gr.Row():
                gr.Markdown("### Select your own LLM Provider")
                llm_provider = gr.Dropdown(
                    choices=["OpenAI", "Groq", "OpenRouter", "Gemini", "Claude", "Other"],
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

            save_llm_detail = gr.Button("Save", variant="primary")

            # Based on Provider, show API url field
            llm_provider.change(
                llm_form_by_provider,
                inputs=llm_provider,
                outputs=[llm_api_url, llm_model],
            )

            # Save LLM details to per-session state (not global variables)
            save_llm_detail.click(
                _update_llm_state,
                inputs=[llm_api_url, llm_api_key, llm_model, llm_state],
                outputs=[llm_state],
            )

    # Chat Bot
    with gr.Row():
        with gr.Group():
            chatbot = gr.Chatbot(
                show_label=False,
                max_height=400,
                container=False,
                elem_id="nse-chatbot",
            )

            with gr.Group():
                text_input = gr.Textbox(
                    show_label=False,
                    placeholder="Ask your question...",
                    autofocus=True,
                    interactive=True,
                )
                send_button = gr.Button(
                    "Ask",
                    variant="primary",
                )

    with gr.Row():
        gr.HTML(
            """
            <center><h2>💡 Try some examples</h2></center>
            """
        )
    # Examples
    with gr.Row():
        ex1 = gr.Button("", variant="huggingface")
        ex2 = gr.Button("", variant="huggingface")
        ex3 = gr.Button("", variant="huggingface")
        ex4 = gr.Button("", variant="huggingface")

        # Get New Examples on Every Load
        ui.load(get_examples, inputs=None, outputs=[ex1, ex2, ex3, ex4])

        # Set Text on Example Click
        ex1.click(lambda x: strip_example(x), inputs=ex1, outputs=text_input)
        ex2.click(lambda x: strip_example(x), inputs=ex2, outputs=text_input)
        ex3.click(lambda x: strip_example(x), inputs=ex3, outputs=text_input)
        ex4.click(lambda x: strip_example(x), inputs=ex4, outputs=text_input)

    # Bottom Disclaimer
    with gr.Row():
        gr.HTML(
            """
            <center><h3 style="color: #858585;">Disclaimer</h3></center>
            <center style="color: #858585;">This Chatbot uses Free tier LLM model from Gemini which would be rate limited. If you have personal key for OpenAI/OpenRouter/Groq/Claude, please choose at the top.</center>
            <center style="color: #858585;">This Chatbot is neither affiliated with nor endorsed by NSE (National Stock Exchange). This is standalone project built for educational purpose.</center>
            """
        )

    # Event Handlers — per-session llm_state is passed to the chat function
    send_button.click(
        send_message_to_ui, inputs=[text_input, chatbot], outputs=[chatbot, text_input]
    )
    send_button.click(
        agent_chat_fn, inputs=[text_input, chatbot, llm_state], outputs=chatbot
    )

    text_input.submit(
        send_message_to_ui, inputs=[text_input, chatbot], outputs=[chatbot, text_input]
    )
    text_input.submit(
        agent_chat_fn, inputs=[text_input, chatbot, llm_state], outputs=chatbot
    )

# Add more pages In app
with ui.route("Docs", "/docs"):
    docs_page()
