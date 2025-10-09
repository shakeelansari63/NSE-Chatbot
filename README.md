---
title: NSE-Chatbot
app_file: main.py
sdk: gradio
sdk_version: 5.49.1
---
# NSE-Chatbot
Chatbot for NSE related info

## Requirement
Need GROQ API key for using LLM Models fro Groq.   
Add `GROQ_API_KEY=gsk_********` in `.env` 

## Deployment
Add `HF_TOKEN=hf_*****` in `.env` and run `uv run dotenv -f .env run -- uv run gradio deploy` for deploying app to HF Spaces. 