from uuid import UUID
from app.schemas.common import BaseSchema

class UploadResponse(BaseSchema):
    tenant_id: str
    user_id: str
    doc_id: UUID
    task_id: UUID
    filename: str
    url: str
    bucket: str
    status: str
