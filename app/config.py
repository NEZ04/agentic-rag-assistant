"""Central settings. Change models/paths here, not scattered through the code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "data" / "docs"
INDEX_DIR = ROOT / "index"

# Free local embedding model (~90 MB, runs on CPU)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Free local LLM served by Ollama
LLM_MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434"

CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 150   # characters shared between neighbouring chunks
TOP_K = 4             # chunks returned per query
MIN_SCORE = 0.35      # below this cosine similarity a chunk counts as "not relevant"
