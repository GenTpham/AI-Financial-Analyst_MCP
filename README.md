# AI Financial Analyst – MCP Demo

This repository demonstrates a **Multi‑Agent Control Plane (MCP)** pipeline that
turns raw market data into:

* Numeric indicators (CAGR, SMA‑20/50, Sharpe)
* Interactive charts (Plotly)
* Narrative insights via **DeepSeek‑LLM 7B** pulled from Hugging Face Hub
* Consolidated reports (Markdown + PDF)

## Quick Start
```bash
# clone & enter
$ git clone <repo‑url> ai_financial_analyst_mcp && cd $_

# create venv (optional)
$ python -m venv .venv && source .venv/bin/activate

# install deps
$ pip install -r requirements.txt

# supply your Hugging Face token (one‑time)
$ echo "HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXX" > .env

# launch API server
$ uvicorn server.main:app --reload

# query from CLI (another shell)
$ python client/finance_client.py --symbols AAPL,MSFT --start 2023-01-01 --end 2024-01-01
