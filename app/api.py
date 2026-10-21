"""Step 3a: HTTP API around the agent.

Run with:  uvicorn app.api:app --port 8000
Docs at:   http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent import ask

app = FastAPI(
    title="Agentic RAG Assistant",
    description="Ask questions about your own documents. Runs fully locally.",
    version="0.3.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, examples=["How does a solar cell work?"])


class AskResponse(BaseModel):
    answer: str
    route: str
    sources: list[str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# A plain `def` (not async) so FastAPI runs it in a worker thread: the LLM call
# blocks for a few seconds and must not freeze the server for other requests.
@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest) -> AskResponse:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question is empty")
    try:
        result = ask(question)
    except SystemExit as e:  # e.g. the index hasn't been built yet
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # e.g. Ollama isn't running
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {e}")
    return AskResponse(
        answer=result.get("answer", ""),
        route=result.get("route", "docs"),
        sources=result.get("sources", []),
    )
