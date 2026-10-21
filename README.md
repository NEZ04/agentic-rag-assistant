# Agentic RAG Assistant

A question-answering assistant over your own documents, built with **fully free, local** components.

> 🚧 Work in progress. See `STEP1.md` for the current milestone.

## Stack
| Part | Tool |
|---|---|
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector search | FAISS |
| LLM | Llama 3.2 via Ollama (local) |
| Agent | LangGraph |
| API / UI | FastAPI, Streamlit |

## Roadmap
- [ ] Ingestion, chunking, FAISS retrieval
- [ ] LangGraph agent with tool calling
- [ ] FastAPI + Streamlit chat UI
- [ ] Docker + evaluation

## Run
```bash
pip install -r requirements.txt
python -m app.ingest
python -m app.retriever "your question"
```
