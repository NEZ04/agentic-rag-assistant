FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# CPU-only PyTorch keeps the image ~2 GB smaller than the default CUDA build
COPY requirements.txt .
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install -r requirements.txt

# Bake the embedding model into the image so containers start offline
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY app ./app
COPY ui ./ui
COPY scripts ./scripts

EXPOSE 8000 8501
# Build the index on first start if it isn't there yet, then serve the API
CMD ["sh", "-c", "[ -f index/faiss.index ] || python -m app.ingest; uvicorn app.api:app --host 0.0.0.0 --port 8000"]
