from sentence_transformers import SentenceTransformer
from app.services.chunker import Chunk
from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def _get_model():
    model = SentenceTransformer(MODEL_NAME)
    return model

def embed_chunks(chunks: list[Chunk]) -> list[float]:
    model = _get_model()
    texts = [chunk.text for chunk in chunks]
    embedding = model.encode(texts)
    return embedding

def embed_text(texts: list[str]) -> list[float]:
    model = _get_model()
    embedding = model.encode(texts)
    return embedding