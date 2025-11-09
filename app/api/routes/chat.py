from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import Settings, get_settings
from app.core.logger_config import get_logger
from app.services.retriever import retrieve_relevant_chunks
from app.services.generator import GeneratorService

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask")
async def ask_question(
        user_id: str,
        tenant_id: str,
        question: str
):
    if not tenant_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id and user_id are required"
        )
    logger.info(f"Received question from user_id: {user_id} for tenant_id: {tenant_id} with question: {question}")
    retrieved_chunks = retrieve_relevant_chunks(
        tenant_id = tenant_id,
        question = question,
        settings = get_settings()
    )
    generator_service = GeneratorService(settings = get_settings())
    try:
        answer = generator_service.generate_answer(
            question = question,
            retrieval_results = retrieved_chunks,
        )
        return answer
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"An error occurred while processing your request. Detail: {e}"}
        )

    
