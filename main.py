import gradio as gr
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import server_config as sc
from mcp_tools.main import mcp as mcp_app

load_dotenv(override=True)

from ui.chatui import ui as gradio_ui  # noqa

# Create MCP HTTP App
mcp_http_app = mcp_app.http_app(path="/")

# Create Fastapi app with MCP's Lifespan
app = FastAPI(title="NSE App", lifespan=mcp_http_app.lifespan)


# Add route for redirecting root to UI
@app.get("/")
def redirect_to_ui():
    return RedirectResponse(sc.ui_path)


# Mount Gradio UI on App
app = gr.mount_gradio_app(app, gradio_ui, path=sc.ui_path)

# Mount MCP ON app
app.mount(sc.mcp_path, mcp_http_app)

if __name__ == "__main__":
    uvicorn.run(app, host=sc.host, port=sc.port)
