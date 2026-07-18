# AI Sports Quiz Agent 🏟️

A LangGraph workflow leveraging Retrieval-Augmented Generation (RAG) to generate factual sports trivia. Powered by Google Gemini, ChromaDB, and DuckDuckGo web search.

## Prerequisites
* Python 3.10+
* [uv](https://docs.astral.sh/uv/) installed on your system.

## 1. Installation

This project is managed via `pyproject.toml` and `uv.lock`. To create the virtual environment and install all dependencies strictly according to the lockfile, run:

```bash
uv sync

```

## 2. Configuration

Create a `.env` file in the root directory and add your API keys:

```env
OPENAI_API_KEY="your-openai-api-key-here"
GOOGLE_API_KEY="your-google-api-key-here"

# Optional: Set to "huggingface" to use local mxbai embeddings instead of OpenAI
EMBEDDING_PROVIDER="openai" 

```

## 3. Hydrate the Database

Before running the app, you must process your local `data/sports_facts.json` file into the ChromaDB vector store.

Run the following command from the project root:

```bash
uv run python -c "from src.database import db_manager; db_manager.ingest_raw_json('data/sports_facts.json')"

```

*(Note: If you change the `EMBEDDING_PROVIDER` in your `.env`, you must delete the `chroma_db/` folder and re-run this command).*

## 4. Run the Application

Launch the Streamlit user interface natively through `uv`:

```bash
uv run streamlit run app.py
```
