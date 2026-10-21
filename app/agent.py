"""Step 2: a LangGraph agent that answers questions from your documents.

Flow:
    route ──math──▶ calculator ──▶ END
      │
      └──docs──▶ retrieve ──▶ generate ──▶ END

- route:      decides whether the question is arithmetic or needs the documents
- calculator: has the LLM pull out the expression, then evaluates it safely
- retrieve:   FAISS search over your indexed chunks
- generate:   answers ONLY from the retrieved chunks and cites them; if nothing
              relevant was found, says so instead of guessing

Run with:  python -m app.agent "how does a solar cell work?"
"""
import re
import sys
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from app import config
from app.calculator import safe_eval

_retriever = None
_llm = None


def get_retriever():
    # Loaded lazily so importing this module doesn't load the embedding model
    global _retriever
    if _retriever is None:
        from app.retriever import Retriever
        _retriever = Retriever()
    return _retriever


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOllama(model=config.LLM_MODEL, temperature=0, base_url=config.OLLAMA_URL)
    return _llm


class AgentState(TypedDict, total=False):
    question: str
    route: str
    hits: list
    answer: str
    sources: list


# ---------- nodes ----------

MATH_HINT = re.compile(r"^[\d\s\.\+\-\*/\^\(\)%x×÷=?]+$|\b(calculate|compute|what is \d|how much is \d)", re.I)


def route(state: AgentState) -> AgentState:
    """Cheap check first; only ask the LLM when the question is ambiguous."""
    q = state["question"]
    if not re.search(r"\d", q):
        return {"route": "docs"}  # no numbers at all -> can't be arithmetic
    if MATH_HINT.search(q):
        return {"route": "math"}
    reply = get_llm().invoke([
        ("system", "Classify the user's question. Reply with exactly one word: "
                   "MATH if it is a pure arithmetic calculation, DOCS otherwise."),
        ("human", q),
    ]).content.strip().upper()
    return {"route": "math" if reply.startswith("MATH") else "docs"}


def calculator(state: AgentState) -> AgentState:
    q = state["question"]
    expr = get_llm().invoke([
        ("system", "Rewrite the user's question as a single Python arithmetic expression "
                   "using only numbers and + - * / ** ( ). Reply with the expression only."),
        ("human", q),
    ]).content.strip().strip("`")
    try:
        value = safe_eval(expr)
    except (ValueError, ZeroDivisionError) as e:
        return {"answer": f"I couldn't calculate that ({e}).", "sources": []}
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return {"answer": f"{expr} = {value}", "sources": ["calculator"]}


def retrieve(state: AgentState) -> AgentState:
    return {"hits": get_retriever().search(state["question"], k=config.TOP_K)}


def generate(state: AgentState) -> AgentState:
    hits = [h for h in state["hits"] if h["score"] >= config.MIN_SCORE]
    if not hits:
        # Nothing relevant enough: refusing beats making something up
        return {"answer": "I don't know. That isn't covered in your documents.", "sources": []}

    context = "\n\n".join(
        f"[{i}] (from {h['source']}{'' if h['page'] is None else ', page ' + str(h['page'])})\n{h['text']}"
        for i, h in enumerate(hits, start=1)
    )
    reply = get_llm().invoke([
        ("system",
         "You answer questions using ONLY the numbered context below. "
         "Cite the passages you used like [1] or [2]. "
         "If the context does not contain the answer, say \"I don't know\". "
         "Keep the answer short and clear.\n\nContext:\n" + context),
        ("human", state["question"]),
    ]).content.strip()

    cited = {int(n) for n in re.findall(r"\[(\d+)\]", reply) if 0 < int(n) <= len(hits)}
    if not cited:
        cited = {1}  # small models sometimes skip citations; fall back to the best match
    sources = sorted({
        hits[n - 1]["source"] + ("" if hits[n - 1]["page"] is None else f" p{hits[n - 1]['page']}")
        for n in cited
    })
    return {"answer": reply, "sources": sources}


# ---------- graph ----------

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("route", route)
    g.add_node("calculator", calculator)
    g.add_node("retrieve", retrieve)
    g.add_node("generate", generate)

    g.set_entry_point("route")
    g.add_conditional_edges("route", lambda s: s["route"], {"math": "calculator", "docs": "retrieve"})
    g.add_edge("retrieve", "generate")
    g.add_edge("calculator", END)
    g.add_edge("generate", END)
    return g.compile()


def ask(question: str) -> AgentState:
    return build_graph().invoke({"question": question})


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How does a photovoltaic cell work?"
    result = ask(question)
    print(f"Q: {question}")
    print(f"Route: {result['route']}")
    print(f"A: {result['answer']}")
    if result.get("sources"):
        print("Sources: " + ", ".join(result["sources"]))
