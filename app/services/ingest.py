from app.core.config import Settings
from app.services import s3_upload, parser, chunker, embeddings, vector_store
from app.core.logger_config import get_logger

logger = get_logger(__name__)

def process_document_from_s3(*, tenant_id: str, s3_key: str, settings: Settings):
    # Run fetch, parse, chunk , embed, store pipeline for a single document
    # raise NotImplementedError("Ingest pipeline is not yet implemented.")
    s3_upload_service = s3_upload.S3UploadService(settings)
    logger.info(f"Start processing document for tenant_id: {tenant_id}, s3_key: {s3_key}")
    s3_file_info = s3_upload_service.stream_file(s3_key=s3_key)
    document_stream = s3_file_info['body']
    # logger.info(f"Download document from S3 {document_stream}")
    content_type = s3_file_info['content_type']
    raw_text = parser.extract_text(file_stream=document_stream, content_type=content_type, filename=s3_key)
    logger.info(f"Extracted raw text of length {len(raw_text)}")
    logger.info(f"Extracted text: {raw_text[:500]}...")  # Log first 500 characters
    logger.info(f"Starting text chunking")
    chunks = chunker.split_text(raw_text)
    logger.info(f"Created {len(chunks)} text chunks")
    logger.info(chunks[0:2])  # Log first 2 chunks
    vector = embeddings.embed_chunks(chunks=chunks)
    logger.info(f"Generated {len(vector)} embeddings")
    # chroma_client = vector_store.get_chroma_client(settings=settings)
    # logger.info(f"Storing vectors in vector store")
    vector_store.store_vectors(vectors =vector, tenant_id=tenant_id, chunks=chunks, s3_key=s3_key, settings=settings)
    logger.info(f"Completed processing document for tenant_id: {tenant_id}, s3_key: {s3_key}")

    # document_stream - returns document or file stream from S3
    # raw_text - returns extracted text from the document stream
    # chunks - returns list of text chunks from the raw text
    # vectors - returns list of embeddings from the chunks
    # store_vectors - stores the vectors in the vector DB or vector store