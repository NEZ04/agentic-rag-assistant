"""Evaluate the assistant on a fixed question set and write eval/results.md.

Each question in eval/questions.json has a type:
  docs   - answerable from the documents; checks routing, retrieval and answer
  refuse - not in the documents; the assistant should say "I don't know"
  math   - arithmetic; should go to the calculator

Run with:  python -m scripts.evaluate   (needs Ollama running and the index built)
"""
import json
import time
from pathlib import Path

from app import config
from app.agent import ask, get_retriever

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "eval" / "questions.json"
REPORT = ROOT / "eval" / "results.md"


def has_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(k.lower() in text for k in keywords)


def refused(answer: str) -> bool:
    a = answer.lower().replace("’", "'")
    return "don't know" in a or "do not know" in a or "not covered" in a


def main() -> None:
    items = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    retriever = get_retriever()
    rows, latencies = [], []
    score = {"route": [0, 0], "retrieval": [0, 0], "answer": [0, 0], "refusal": [0, 0], "math": [0, 0]}

    for item in items:
        q, kind = item["q"], item["type"]
        start = time.perf_counter()
        result = ask(q)
        secs = time.perf_counter() - start
        latencies.append(secs)
        answer = result.get("answer", "")
        expected_route = "math" if kind == "math" else "docs"
        route_ok = result.get("route") == expected_route
        score["route"][0] += route_ok
        score["route"][1] += 1

        checks = []
        if kind == "docs":
            hits = retriever.search(q, k=config.TOP_K)
            retrieved = any(has_any(h["text"], item["keywords"]) for h in hits if h["score"] >= config.MIN_SCORE)
            correct = has_any(answer, item["keywords"]) and not refused(answer)
            score["retrieval"][0] += retrieved
            score["retrieval"][1] += 1
            score["answer"][0] += correct
            score["answer"][1] += 1
            checks = [("retrieval", retrieved), ("answer", correct)]
        elif kind == "refuse":
            ok = refused(answer)
            score["refusal"][0] += ok
            score["refusal"][1] += 1
            checks = [("refused", ok)]
        else:
            ok = has_any(answer, item["keywords"])
            score["math"][0] += ok
            score["math"][1] += 1
            checks = [("correct", ok)]

        passed = route_ok and all(ok for _, ok in checks)
        rows.append((q, kind, passed, answer.replace("\n", " ").replace("|", "/")[:120], secs))
        print(f"{'PASS' if passed else 'FAIL'}  {secs:5.1f}s  [{kind}] {q}")

    def pct(name):
        good, total = score[name]
        return f"{good}/{total} ({100 * good / total:.0f}%)" if total else "n/a"

    passed_all = sum(r[2] for r in rows)
    lines = [
        "# Evaluation results",
        "",
        f"Model: `{config.LLM_MODEL}` · Embeddings: `{config.EMBED_MODEL}` · "
        f"MIN_SCORE: {config.MIN_SCORE} · TOP_K: {config.TOP_K}",
        "",
        "Documents: `data/docs/sample_energy_notes.md` (short renewable-energy notes).",
        "",
        "| Metric | Result |",
        "|---|---|",
        f"| Overall pass rate | {passed_all}/{len(rows)} ({100 * passed_all / len(rows):.0f}%) |",
        f"| Routing accuracy | {pct('route')} |",
        f"| Retrieval hit rate (answerable questions) | {pct('retrieval')} |",
        f"| Answer correctness (answerable questions) | {pct('answer')} |",
        f"| Correct refusals (questions not in the documents) | {pct('refusal')} |",
        f"| Calculator correctness | {pct('math')} |",
        f"| Average latency (on a local laptop) | {sum(latencies) / len(latencies):.1f}s |",
        "",
        "Answer correctness is a keyword check against the expected fact, so it is a",
        "lower bound: a correct answer phrased differently could be marked wrong.",
        "",
        "## Per-question results",
        "",
        "| | Type | Question | Answer (truncated) | Time |",
        "|---|---|---|---|---|",
    ]
    for q, kind, ok, ans, secs in rows:
        lines.append(f"| {'✅' if ok else '❌'} | {kind} | {q} | {ans} | {secs:.1f}s |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nOverall: {passed_all}/{len(rows)} passed. Report written to {REPORT}")


if __name__ == "__main__":
    main()
