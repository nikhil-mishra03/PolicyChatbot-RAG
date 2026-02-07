from app.services import embeddings, vector_store
from app.core.logger_config import get_logger
from flashrank import Ranker, RerankRequest
from starlette.concurrency import run_in_threadpool
from app.core import globals

logger = get_logger(__name__)

# Cache the ranker to avoid reloading model on every request
_ranker_instance = None

def _get_ranker():
    global _ranker_instance
    if _ranker_instance is None:
        # distinct model for re-ranking. 'ms-marco-MiniLM-L-12-v2' is a good balance.
        # FlashRank defaults to a small quantization.
        _ranker_instance = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=".cache")
    return _ranker_instance

async def retrieve_relevant_chunks(*, tenant_id: str, question: str, settings) -> list[dict]:
    """
    Retrieves and re-ranks chunks.
    Returns a list of dicts: {'text': str, 'metadata': dict, 'score': float}
    """
    try:
        # Stage 1: Vector Retrieval (High Recall)
        # Fetch 25 candidates (to be re-ranked down to 'num_retrieved_chunks')
        INITIAL_TOP_K = 25
         
        question_embedding = await embeddings.embed_text(question)
        logger.info(f"Generated question embedding for tenant_id: {tenant_id}")
        
        client = globals.get_chroma_client()
        collection = vector_store._get_collection(client, collection_name=settings.chromadb_collection_name)
        
        logger.info(f"Querying vector store (Top-{INITIAL_TOP_K}) for tenant_id: {tenant_id}")
        
        def _query_chroma():
            return collection.query(
                query_embeddings=question_embedding,
                n_results=INITIAL_TOP_K,
                where={"tenant_id": tenant_id}
            )
        
        results = await run_in_threadpool(_query_chroma)
        
        # Parse Chroma results into flat list for Reranker
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        ids = results.get('ids', [[]])[0]
        
        if not docs:
            logger.info("No documents found in vector store.")
            return []

        passages = [
            {"id": id, "text": doc, "meta": meta} 
            for id, doc, meta in zip(ids, docs, metas)
        ]
        
        logger.info(f"Fetched {len(passages)} candidates. Starting Re-ranking.")

        # Stage 2: Re-ranking (High Precision)
        ranker = _get_ranker()
        rerank_request = RerankRequest(query=question, passages=passages)
        ranked_results = await run_in_threadpool(ranker.rerank, rerank_request)
        
        # Take Top N (e.g. 5)
        final_top_k = settings.num_retrieved_chunks
        top_results = ranked_results[:final_top_k]
        
        logger.info(f"Re-ranking complete. Returning top {len(top_results)} results.")
        
        # Standardize Output
        return [
            {
                "text": res["text"],
                "metadata": res["meta"],
                "score": res["score"],
                "id": res["id"]
            }
            for res in top_results
        ]

    except Exception as e:
        logger.error(f"Failed to retrieve/rerank answers. Error: {e}")
        raise RuntimeError(f"Failed to retrieve answers. Error: {e}")
