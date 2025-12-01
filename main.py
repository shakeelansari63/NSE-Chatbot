from datetime import datetime

import gradio as gr
import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from dbman.actions import refresh_market_metadata
from mcp_tools import mcp as mcp_app
from server_config import get_server_config as sc
from ui.chatui import ui as gradio_ui
from ui.theme import app_css, app_theme

# Create MCP HTTP App
mcp_http_app = mcp_app.http_app(path="/")

# Create Fastapi app with MCP's Lifespan
app = FastAPI(title="NSE Chatbot App", lifespan=mcp_http_app.lifespan)


# Return Favicon
@app.get("/favicon.ico")
async def favicon():
    return FileResponse(sc().favicon_path)


# Server Files Generated in Temp Assets Directory
app.mount(
    f"/{sc().temp_assets_dir}",
    StaticFiles(directory=sc().temp_assets_url),
    name=sc().temp_assets_dir,
)


# Add route for redirecting root to UI
@app.get("/")
async def redirect_to_ui():
    return RedirectResponse(sc().ui_path)


# Add Route to Refresh Equity Metadata
@app.get("/refresh")
async def refresh_metadata(background_tasks: BackgroundTasks):
    # Add Background Task
    background_tasks.add_task(refresh_market_metadata)

    # Return Response
    return f"Refreshed triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# Mount Gradio UI on App
app = gr.mount_gradio_app(
    app,
    gradio_ui,
    path=sc().ui_path,
    theme=app_theme,
    css=app_css,
)

# Mount MCP ON app
app.mount(sc().mcp_path, mcp_http_app)

if __name__ == "__main__":
    uvicorn.run(app, host=sc().host, port=sc().port)
