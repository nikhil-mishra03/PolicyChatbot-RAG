from uuid import UUID
from typing import List, Optional
from app.schemas.common import BaseSchema

class ChatRequest(BaseSchema):
    user_id: str
    tenant_id: str
    question: str

class Source(BaseSchema):
    chunk_id: str
    tenant_id: str
    s3_key: str
    distance: float

class ChatResponse(BaseSchema):
    answer: str
    sources: List[Source]
