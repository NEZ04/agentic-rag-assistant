"""Step 1b: load the saved index and return the most relevant chunks for a question.

Try it with:  python -m app.retriever "what is a photovoltaic cell?"
"""
import json
import sys

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app import config


class Retriever:
    def __init__(self):
        index_path = config.INDEX_DIR / "faiss.index"
        if not index_path.exists():
            raise SystemExit("No index found. Run `python -m app.ingest` first.")
        self.index = faiss.read_index(str(index_path))
        with open(config.INDEX_DIR / "chunks.json", encoding="utf-8") as f:
            self.chunks = json.load(f)
        # Must be the SAME model used at indexing time: different models produce
        # vectors in different spaces, so similarity scores would be meaningless.
        self.model = SentenceTransformer(config.EMBED_MODEL)

    def search(self, query: str, k: int = config.TOP_K) -> list[dict]:
        """Return the top-k chunks as [{"text", "source", "page", "score"}, ...]."""
        q = self.model.encode([query], normalize_embeddings=True)
        q = np.asarray(q, dtype="float32")
        k = min(k, self.index.ntotal)
        scores, ids = self.index.search(q, k)  # both shaped (1, k)

        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:  # FAISS pads with -1 when there are fewer than k results
                continue
            hit = dict(self.chunks[idx])
            hit["score"] = float(score)  # cosine similarity, higher = more relevant
            results.append(hit)
        return results


if __name__ == "__main__":
    r = Retriever()
    for hit in r.search(" ".join(sys.argv[1:]) or "test"):
        print(f"[{hit['score']:.3f}] {hit['source']} p{hit['page']}: {hit['text'][:150]}...")
