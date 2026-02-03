# Takes in the question from the user
# retrieves relevant chunks from vector storage based on the tenant id

from app.services import embeddings, vector_store
from app.core.logger_config import get_logger

logger = get_logger(__name__)

def retrieve_relevant_chunks(*, tenant_id: str, question: str, settings):
    # Embed the question
    try:
        question_embedding = embeddings.embed_text(question)
        logger.info(f"Generated embedding for question for tenant_id: {tenant_id}")
        # Query the vector store
        client = vector_store._get_chroma_client(settings)
        collection = vector_store._get_collection(client, collection_name=settings.chromadb_collection_name)
        logger.info(f"Querying vector store for tenant_id: {tenant_id} with question: {question}")
        results = collection.query(
            query_embeddings=question_embedding,
            n_results = settings.num_retrieved_chunks,
            where = {"tenant_id": tenant_id}
        )
        logger.info(f"Retrieved {len(results.get('documents', [[]])[0])} chunks from vector store for tenant_id: {tenant_id}")
        return results

    except Exception as e:
        logger.info(f"Failed to retrieve answers. Error: {e}")
        raise RuntimeError(f"Failed to retrieve answers. Error: {e}")
