# 🚀 NSE Chatbot

AI-powered conversational agent for the National Stock Exchange of India (NSE). Built with FastAPI, LangGraph, Gradio, and the Model Context Protocol (MCP).

## Features

- **Real-time stock prices** — current price, previous close, market status
- **Historical trends** — price history with auto-generated charts
- **52-week high/low scanners** — stocks at their yearly extremes
- **Volume gainers** — weekly volume breakout detection
- **Sector/industry search** — list top stocks by market cap in any industry
- **Corporate filings** — board meetings, financial results, dividends, shareholding patterns
- **Multi-LLM support** — bring your own key for OpenAI, Groq, OpenRouter, Google Gemini, Claude, or any OpenAI-compatible endpoint

## Project Structure

```
├── agent/                  # LangGraph agent logic
│   ├── config.py           # LLM provider map + config
│   ├── graph.py            # Agent state graph (tool shortlisting + execution)
│   ├── local_tools.py      # Local tools (chart generation)
│   └── messages.py         # System prompts + input sanitisation
├── assets/                 # Static assets (favicon)
├── chat/                   # Chat interface adapters
│   ├── agent_chat.py       # Agent chat handler
│   ├── model.py            # Gradio message types
│   └── utils.py            # Message format converters
├── dbman/                  # Database layer
│   ├── actions.py          # Metadata refresh logic
│   ├── helper.py           # CRUD + fuzzy search (trigram, Levenshtein)
│   └── nse_metadata.py     # SQLModel schema
├── migrations/             # Alembic DB migrations
│   └── versions/           # Migration scripts
├── nse/                    # NSE API client
│   ├── config.py           # API endpoints + headers
│   ├── helper.py           # Business logic layer
│   ├── models.py           # Pydantic response models
│   └── nse_http.py         # HTTP client (rate-limited, retry, thread-safe)
├── ui/                     # Gradio frontend
│   ├── chatui.py           # Main chat UI
│   ├── components/         # Reusable UI components
│   ├── config.py           # Social links
│   ├── examples.py         # Example prompts
│   └── theme.py            # Ocean theme + custom CSS
├── .env.template           # Environment variable template (see template for Supabase setup)
├── main.py                 # FastAPI app entry point
├── Taskfile.yaml           # Convenience tasks (task run, task setup)
├── mcp_tools.py            # MCP tool definitions
├── pyproject.toml          # Project metadata + dependencies
└── server_config.py        # Pydantic settings (env-based config)
```

## How to Run Locally

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- PostgreSQL database (or [Supabase](https://supabase.com) free tier)
- LLM API key (OpenAI / Groq / OpenRouter / Claude / local Ollama)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/shakeelansari63/NSE-Chatbot.git
cd NSE-Chatbot

# 2. Copy environment template and fill in your values
cp .env.template .env

# 3. Configure .env with your credentials:
#    - LLM_API_KEY, LLM_API_URL, LLM_MODEL
#    - PG_HOST, PG_PORT, PG_USER, PG_PASS, PG_DB

# 4. Install dependencies
uv sync
# or: pip install -r requirements.txt  (generate with: uv pip compile pyproject.toml -o requirements.txt)

# 5. Run database migrations
alembic upgrade head

# 6. Pre-load NSE stock metadata (optional but recommended)
#    Start the server, then visit http://localhost:8000/refresh

# 7. Start the server
task run
# or: uv run main.py
# or: python main.py
```

The app will be available at **http://localhost:8000** — the chat UI is at `/ui` and the MCP endpoint at `/mcp`.

### Using Docker

```bash
docker build -t nse-chatbot .
docker run -p 8000:8000 --env-file .env nse-chatbot
```

## Deploy on Azure Web App

The repository includes a pre-configured GitHub Actions workflow (`.github/workflows/azure-webapp-python-deploy.yml`) that deploys automatically on pushes to `main`.

### One-time Azure Setup

1. **Create an Azure Web App**
   ```bash
   az webapp create \
     --resource-group <group> \
     --plan <plan> \
     --name nse-chatbot \
     --runtime "PYTHON:3.12" \
     --startup-file "python main.py"
   ```

2. **Configure App Settings** in Azure Portal or via CLI:
   ```
   LLM_API_KEY, LLM_API_URL, LLM_MODEL
   PG_HOST, PG_PORT, PG_USER, PG_PASS, PG_DB
   ```

3. **Configure GitHub Secrets** (`Settings → Secrets and variables → Actions`):
   | Secret | Value |
   |--------|-------|
   | `AZUREAPPSERVICE_CLIENTID_*` | Azure AD client ID |
   | `AZUREAPPSERVICE_TENANTID_*` | Azure AD tenant ID |
   | `AZUREAPPSERVICE_SUBSCRIPTIONID_*` | Azure subscription ID |

   These are generated when you run:
   ```bash
   az ad sp create-for-rbac \
     --name "nse-chatbot-sp" \
     --role contributor \
     --scopes /subscriptions/<id>/resourceGroups/<group> \
     --sdk-auth
   ```

4. **Push to `main`** — the workflow builds and deploys automatically.

### Deploy Manually (without CI/CD)

```bash
az webapp up \
  --resource-group <group> \
  --name nse-chatbot \
  --runtime "PYTHON:3.12" \
  --startup-file "python main.py"
```

## Deploy on Other Platforms

### Render / Railway / Fly.io

Create a `start.sh`:
```bash
#!/bin/bash
alembic upgrade head
python main.py
```

Set the build command to `pip install -r requirements.txt` (or `uv sync`) and the start command to `bash start.sh`. Configure environment variables via the platform dashboard.

---

## ⚖️ License

This project is licensed under the Apache 2.0 License — see the [LICENSE](LICENSE) file for details.

## 🤝 Contributors

<a href="https://github.com/shakeelansari63/NSE-Chatbot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=shakeelansari63/NSE-Chatbot" alt="Contributors" />
</a>

## 📌 Disclaimer

This Chatbot is neither affiliated with nor endorsed by NSE (National Stock Exchange). This is a standalone project built for educational purposes only.

## ⭐ Credits

Thanks to owners of following repos who did hard work with NSE APIs:
- [stock-nse-india](https://github.com/hi-imcodeman/stock-nse-india)
- [nse-bse-api](https://github.com/bshada/nse-bse-api)
