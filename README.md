# Agentic RAG Assistant

A question-answering assistant over your own documents, built with fully free, local components.

> Work in progress. Retrieval and the agent are done; the API and UI are next.

## How it works
```
question ──▶ route ──math──▶ safe calculator ──▶ answer
               │
               └──docs──▶ FAISS retrieval ──▶ Llama 3.2 (grounded, cited) ──▶ answer + sources
```
- Answers come only from your documents, with citations like `[1]`.
- If nothing relevant is found, it says "I don't know" instead of guessing.
- Arithmetic is evaluated with an AST-based calculator (no `eval`).

## Stack
| Part | Tool |
|---|---|
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector search | FAISS |
| LLM | Llama 3.2 3B via Ollama (local) |
| Agent | LangGraph |
| API / UI | FastAPI, Streamlit |

## Roadmap
- [x] Ingestion, chunking, FAISS retrieval
- [x] LangGraph agent with routing, calculator and grounded answers
- [ ] FastAPI + Streamlit chat UI
- [ ] Docker + evaluation

## Run
```bash
pip install -r requirements.txt
ollama pull llama3.2:3b
mkdir -p data/docs        # put your PDFs / .txt / .md files here
python -m app.ingest
python -m app.agent "How does a photovoltaic cell work?"
pytest
```

## Example
```
Q: What limits the efficiency of a wind turbine?
A: The Betz limit: the maximum fraction of wind energy that can be captured is 16/27, about 59.3%.

Q: Who won the 2018 FIFA World Cup?
A: I don't know. That isn't covered in your documents.
```
