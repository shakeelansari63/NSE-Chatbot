import logging
import warnings
from datetime import datetime

import gradio as gr
from anyio import ClosedResourceError

# gradio still uses deprecated HTTP_422_UNPROCESSABLE_ENTITY (starlette)
warnings.filterwarnings("ignore", message=".*HTTP_422_UNPROCESSABLE_ENTITY.*")
# uvicorn still uses deprecated websockets.legacy module
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
# gradio's queue uses pandas APIs deprecated in pandas 3 (harmless)
warnings.filterwarnings("ignore", message=".*no_silent_downcasting.*")
warnings.filterwarnings("ignore", message=".*The copy keyword is deprecated.*")
import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from dbman.actions import refresh_market_metadata
from mcp_tools import mcp as mcp_app
from server_config import get_server_config as sc
from ui.chatui import ui as gradio_ui
from ui.theme import app_css, app_theme


class _MCPDisconnectFilter(logging.Filter):
    """Drop the harmless SSE-writer error MCP logs when a client disconnects.

    On session termination the MCP SDK closes the standalone SSE stream while
    its writer is still awaiting the stream, which raises ClosedResourceError.
    The SDK logs that at ERROR level even though it is expected teardown.
    """

    _MESSAGES = {
        "Error in standalone SSE writer",
        "Error in standalone SSE response",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        if record.getMessage() not in self._MESSAGES:
            return True
        exc = record.exc_info[1] if record.exc_info else None
        return not isinstance(exc, ClosedResourceError)


logging.getLogger("mcp.server.streamable_http").addFilter(_MCPDisconnectFilter())

# Create MCP HTTP App (stateless: no session or standalone SSE stream to maintain)
mcp_http_app = mcp_app.http_app(path="/", stateless_http=True)

# Create Fastapi app with MCP's Lifespan
app = FastAPI(title="NSE Chatbot App", lifespan=mcp_http_app.lifespan)

# CORS: Allow requests from any origin for the public-facing API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    head="<style>#nse-chatbot{border:0 none!important;border-width:0!important;border-style:none!important}</style>",
)

# Mount MCP ON app
app.mount(sc().mcp_path, mcp_http_app)

if __name__ == "__main__":
    uvicorn.run(app, host=sc().host, port=sc().port)
