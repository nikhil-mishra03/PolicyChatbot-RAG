from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import Settings, get_settings

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def upload_policy_document(
) -> dict[str, str]:
    
    settings = get_settings()
    
    return JSONResponse({
        "tenant_id": None,
        "filename" : None,
        "bucket": settings.policy_bucket_name,
        "status": "pending"
    })



