from app.services.chunker import Chunk
from app.core.config import get_settings
from app.core import globals

async def embed_chunks(chunks: list[Chunk]) -> list[float]:
    client = globals.get_openai_client()
    settings = get_settings()
    texts = [chunk.text for chunk in chunks]
    if not texts:
        return []

    # OpenAI handles batching, but for huge lists we might want to chunk requests.
    # For now, assuming reasonable document sizes.
    response = await client.embeddings.create(
        input=texts,
        model=settings.openai_embedding_model
    )
    # Extract embeddings in order
    return [data.embedding for data in response.data]

async def embed_text(texts: list[str]) -> list[float]:
    client = globals.get_openai_client()
    settings = get_settings()
    
    if isinstance(texts, str):
        texts = [texts]
        
    response = await client.embeddings.create(
        input=texts,
        model=settings.openai_embedding_model
    )
    return [data.embedding for data in response.data]