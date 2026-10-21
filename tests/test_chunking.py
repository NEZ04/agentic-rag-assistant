"""Run with: pytest"""
from app.ingest import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("hello world", size=100, overlap=10) == ["hello world"]


def test_chunks_respect_size():
    chunks = chunk_text("a" * 1000, size=200, overlap=50)
    assert all(len(c) <= 200 for c in chunks)


def test_overlap_covers_whole_text():
    text = "".join(str(i % 10) for i in range(1000))
    chunks = chunk_text(text, size=200, overlap=50)
    assert chunks[0].startswith(text[:10])
    assert chunks[-1].endswith(text[-10:])


def test_empty_text():
    assert chunk_text("", size=100, overlap=10) == []
