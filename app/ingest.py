"""Step 1a: load documents, split them into chunks, embed them, and save a FAISS index.

Run with:  python -m app.ingest
"""
import json

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from app import config

SUPPORTED_TEXT = {".txt", ".md"}


def load_documents() -> list[dict]:
    """Read every .pdf / .txt / .md in DOCS_DIR.

    Returns one dict per PDF page (or per text file):
        {"text": "...", "source": "notes.pdf", "page": 3}
    We keep source + page so answers can cite where they came from.
    """
    docs = []
    for path in sorted(config.DOCS_DIR.iterdir()):
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            reader = PdfReader(path)
            for page_num, page in enumerate(reader.pages, start=1):
                # extract_text() returns None for scanned/image-only pages
                text = (page.extract_text() or "").strip()
                if text:
                    docs.append({"text": text, "source": path.name, "page": page_num})
        elif suffix in SUPPORTED_TEXT:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            if text:
                docs.append({"text": text, "source": path.name, "page": None})
    return docs


def chunk_text(text: str, size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping windows of at most `size` characters.

    Why overlap? If a key sentence is cut at a chunk boundary, the overlap means
    it still appears whole in the neighbouring chunk.

    We try to end each chunk at a natural break (paragraph, newline, sentence)
    so chunks read cleanly, falling back to a hard cut.
    """
    if overlap >= size:
        raise ValueError("overlap must be smaller than size, otherwise the window never moves forward")

    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))

        # Look for a nice break point in the last ~30% of the window
        if end < len(text):
            window = text[start:end]
            min_cut = int(size * 0.7)
            for sep in ("\n\n", "\n", ". "):
                cut = window.rfind(sep)
                if cut >= min_cut:
                    end = start + cut + len(sep)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        # Step back by `overlap` so neighbours share context, then move forward
        # to the next space so the new chunk doesn't start mid-word.
        next_start = end - overlap
        space = text.find(" ", next_start, end)
        if space != -1:
            next_start = space + 1
        start = max(next_start, start + 1)  # always move forward, never loop forever
    return chunks


def build_index() -> None:
    """Load -> chunk -> embed -> save index/faiss.index and index/chunks.json."""
    docs = load_documents()
    if not docs:
        raise SystemExit(f"No documents found in {config.DOCS_DIR}. Add some PDFs or .txt files first.")

    # Flatten pages into chunks, carrying the metadata along
    chunks = []
    for doc in docs:
        for piece in chunk_text(doc["text"]):
            chunks.append({"text": piece, "source": doc["source"], "page": doc["page"]})
    print(f"Loaded {len(docs)} pages -> {len(chunks)} chunks")

    # Turn each chunk into a 384-dim vector. normalize_embeddings=True makes every
    # vector length 1, so inner product == cosine similarity.
    model = SentenceTransformer(config.EMBED_MODEL)
    vectors = model.encode(
        [c["text"] for c in chunks],
        batch_size=64,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    vectors = np.asarray(vectors, dtype="float32")  # FAISS requires float32

    # IndexFlatIP = exact search by inner product. Fine for thousands of chunks;
    # for millions you'd switch to an approximate index like IVF or HNSW.
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    # FAISS only stores vectors and returns row numbers, so we save the chunk
    # texts in the SAME order to map row number -> text later.
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(config.INDEX_DIR / "faiss.index"))
    with open(config.INDEX_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    print(f"Saved index with {index.ntotal} vectors to {config.INDEX_DIR}")


if __name__ == "__main__":
    build_index()
