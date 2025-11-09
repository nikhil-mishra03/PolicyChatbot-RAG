from fastapi import APIRouter, status, HTTPException, Query, UploadFile,File, Depends, status
from fastapi.responses import JSONResponse
from app.core.config import Settings, get_settings
from app.services.s3_upload import S3UploadService, UploadObject
from app.services.ingest import process_document_from_s3

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/files")
async def upload_policy_document(
    tenant_id: str,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
) -> dict[str, str]:
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id is required"
        )

    # ToDo : Add S3 upload logic in storage file 
    s3_upload_service = S3UploadService(settings)
    try:
        upload_object: UploadObject = s3_upload_service.upload_file(tenant_id, file)
        url = upload_object.url

        s3_key = upload_object.key
        process_document_from_s3(
            tenant_id=tenant_id,
            s3_key=s3_key,
            settings=settings
        )
        

        return JSONResponse({
            "tenant_id": tenant_id,
            "filename" : file.filename,
            "url": upload_object.url,
            "bucket": upload_object.bucket,
            "status": "uploaded"
        })
    except RuntimeError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )



