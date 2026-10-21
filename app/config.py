"""Central settings. Change models/paths here, not scattered through the code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "data" / "docs"
INDEX_DIR = ROOT / "index"

# Free local embedding model (~90 MB, runs on CPU)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Free local LLM served by Ollama (used from Step 2)
LLM_MODEL = "llama3.2:3b"

CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 150   # characters shared between neighbouring chunks
TOP_K = 4             # chunks returned per query
