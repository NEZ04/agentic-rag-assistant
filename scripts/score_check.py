"""Print the top retrieval score for questions that should and shouldn't match,
to choose a sensible MIN_SCORE threshold."""
from app.retriever import Retriever

IN_DOCS = [
    "What is the Betz limit?",
    "Betz limit",
    "How does a solar cell work?",
    "What is biogas?",
    "How do geothermal plants work?",
    "efficiency of silicon cells",
]
OUT_OF_DOCS = [
    "Who won the 2018 FIFA World Cup?",
    "What is the capital of France?",
    "How do I bake bread?",
    "Explain quicksort",
    "What is nuclear fusion?",
]

r = Retriever()
for label, qs in (("IN", IN_DOCS), ("OUT", OUT_OF_DOCS)):
    for q in qs:
        print(f"{label:3} {r.search(q, k=1)[0]['score']:.3f}  {q}")
