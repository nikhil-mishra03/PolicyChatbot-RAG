from app.worker import celery_app
from app.services import ingest
from app.core.config import get_settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, tenant_id: str, user_id: str, doc_id: str, s3_url: str, s3_key: str):
    logger.info(f"Processing document {doc_id} for tenant {tenant_id}")
    try:
        settings = get_settings()
        ingest.process_document_from_s3(
            tenant_id=tenant_id,
            user_id=user_id,
            doc_id=doc_id,
            s3_url=s3_url,
            s3_key=s3_key,
            settings=settings
        )
        logger.info(f"Successfully processed document {doc_id}")
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")
        # Retry in 5s, 10s, 20s...
        raise self.retry(exc=e, countdown=5 * (2 ** self.request.retries))
