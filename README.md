# NSE-Chatbot
Chatbot for NSE related info

## Requirement
Need OPENROUTER API key for using LLM Models from OpenRouter.
Add `OPENROUTER_API_KEY=gsk_********` in `.env`

## Deployment
Add `HF_TOKEN=hf_*****` in `.env` and run `uv run dotenv -f .env run -- uv run gradio deploy` for deploying app to HF Spaces.
