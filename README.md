# Agentic RAG Assistant

A question-answering assistant over your own documents, built with fully free, local components.

> Retrieval, agent, API, chat UI, evaluation set and Docker setup are all done and tested.

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
- [x] FastAPI + Streamlit chat UI
- [x] Evaluation set (20 questions) with a generated report
- [x] Docker Compose setup (Ollama + API + UI), tested end to end

## Run
```bash
pip install -r requirements.txt
ollama pull llama3.2:3b
mkdir -p data/docs        # put your PDFs / .txt / .md files here
python -m app.ingest
python -m app.agent "How does a photovoltaic cell work?"   # CLI
uvicorn app.api:app --port 8000                             # API, docs at /docs
streamlit run ui/app.py                                     # chat UI at :8501
pytest                                                      # unit + API tests
python scripts/smoke_test.py                                # end-to-end check
```

## API
`POST /ask` with `{"question": "..."}` returns
```json
{"answer": "...", "route": "docs", "sources": ["notes.pdf p3"]}
```
`GET /health` returns `{"status": "ok"}`. Errors: `422` for an empty question, `503` if the model or index isn't available.

## Evaluation
`python -m scripts.evaluate` runs the 20 questions in `eval/questions.json` (12 answerable from the documents, 6 that aren't, 2 arithmetic) and writes `eval/results.md`.

Latest run on the sample notes:

| Metric | Result |
|---|---|
| Overall pass rate | 19/20 (95%) |
| Routing accuracy | 20/20 |
| Retrieval hit rate | 12/12 |
| Answer correctness | 11/12 |
| Correct refusals | 6/6 |
| Calculator | 2/2 |

The one failure, "What is a binary-cycle geothermal plant?", is a model failure rather than a retrieval one. The right passage was retrieved, but the 3B model still answered "I don't know". Possible fixes are a larger model, a reranker, or a prompt that asks the model to quote the passage before answering.

Answer correctness is a keyword check against the expected fact, so it's a lower bound: a correct answer phrased differently could be marked wrong.

## Docker
```bash
docker compose up --build            # API on :8000, chat UI on :8501
python -m scripts.docker_check       # waits for the stack, asks a test question
```
This starts four services: `ollama`, a one-off `ollama-pull` job that downloads Llama 3.2, `api` and `ui`. `./data/docs` is mounted into the API container, and the index is built on first start. Host ports can be changed with `API_PORT` and `UI_PORT`, for example if something else already uses 8000.

Tested with Docker Desktop 4.96 on Windows: all four containers started, `/health` and the UI responded, and `/ask` answered a question from the documents correctly.

## Relevance threshold
`MIN_SCORE` decides when the assistant says "I don't know". `scripts/score_check.py` prints the top retrieval score for on-topic and off-topic questions. On the sample notes, on-topic questions scored 0.24 or higher and off-topic ones 0.21 or lower, so the threshold is 0.22. Re-run it when you add your own documents.

## Example
```
Q: What limits the efficiency of a wind turbine?
A: The Betz limit: the maximum fraction of wind energy that can be captured is 16/27, about 59.3%.

Q: Who won the 2018 FIFA World Cup?
A: I don't know. That isn't covered in your documents.
```
