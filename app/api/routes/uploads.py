from fastapi import APIRouter, status, HTTPException, Query, UploadFile,File, Depends, status
from fastapi.responses import JSONResponse
from app.core.config import Settings, get_settings
from app.services.s3_upload import S3UploadService, UploadObject
from app.services.s3_upload import S3UploadService, UploadObject

router = APIRouter(prefix="/uploads", tags=["uploads"])

from uuid import uuid4

from app.schemas.uploads import UploadResponse

@router.post("/files", response_model=UploadResponse)
async def upload_policy_document(
    tenant_id: str,
    user_id: str,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
) -> UploadResponse:
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id is required"
        )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required"
        )

    s3_upload_service = S3UploadService(settings)
    try:
        upload_object: UploadObject = s3_upload_service.upload_file(tenant_id, file)
        url = upload_object.url

        s3_key = upload_object.key
        doc_id = str(uuid4()) # Generate a unique document ID

        # Offload to Celery
        from app.tasks.ingestion_tasks import process_document_task
        task = process_document_task.delay(
            tenant_id=tenant_id,
            user_id=user_id,
            doc_id=doc_id,
            s3_url=url,
            s3_key=s3_key
        )

        return UploadResponse(
            tenant_id=tenant_id,
            user_id=user_id,
            doc_id=doc_id, # Casting UUID to string handled by Pydantic if needed, or vice versa
            task_id=task.id,
            filename=file.filename,
            url=upload_object.url,
            bucket=upload_object.bucket,
            status="processing_started"
        )
    except RuntimeError as e:
        # Pydantic/FastAPI handles exceptions, but if we catch generic ones:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



