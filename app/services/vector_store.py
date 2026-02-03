import chromadb
from app.core.config import Settings
from app.core.logger_config import get_logger
from app.services.chunker import Chunk

logger = get_logger(__name__)

_chroma_client_instance = None
_chroma_collection_cache = {}

def _get_chroma_client(settings: Settings) -> chromadb.Client:
    global _chroma_client_instance
    if _chroma_client_instance is not None:
        return _chroma_client_instance
    try:
        client = chromadb.CloudClient(
            api_key=settings.chroma_api_key,
            tenant=settings.chroma_tenant,
            database=settings.chroma_database
        )
        logger.info("ChromaDB client created successfully")
        _chroma_client_instance = client
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to create ChromaDB client: {e}")
    
def _get_collection(client: chromadb.Client, collection_name: str) -> chromadb.api.models.Collection.Collection:

    global _chroma_collection_cache
    if collection_name in _chroma_collection_cache:
        return _chroma_collection_cache[collection_name]
    try:
        collection = client.get_collection(name=collection_name)
        logger.info(f"Retrieved existing collection: {collection_name}")
        _chroma_collection_cache[collection_name] = collection
        return collection
    except Exception:
        logger.info("Collection not found, creating a new one")
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"})
        logger.info(f"Created new collection: {collection_name}")
        _chroma_collection_cache[collection_name] = collection
        return collection

def store_vectors(*, vectors: list[float], tenant_id: str, user_id: str, doc_id: str, s3_url: str, chunks: list[Chunk], s3_key: str, settings: Settings):
    client = _get_chroma_client(settings)
    collection = _get_collection(client, collection_name=settings.chromadb_collection_name)
    ids = []
    metadatas = []
    documents = []
    try:
        for chunk in chunks:
            id = f"{tenant_id}_{doc_id}_{chunk.id}"
            ids.append(id)
            metadatas.append({
                "tenant_id": tenant_id,
                "user_id": user_id,
                "doc_id": doc_id,
                "s3_url": s3_url,
                "chunk_index": chunk.index,
                "s3_key": s3_key
            })
            documents.append(chunk.text)
    except Exception as e:
        raise RuntimeError(f"Failed to prepare vectors for ChromaDB: {e}")
    try:
        collection.add(
            ids = ids,
            embeddings = vectors,
            metadatas = metadatas,
            documents = documents
        )
    except Exception as e:
        logger.info(f"Error details: {e}")
        raise RuntimeError(f"Failed to store vectors in ChromaDB: {e}")
    logger.info(f"Stored {len(vectors)} vectors in ChromaDB")
    




  

    