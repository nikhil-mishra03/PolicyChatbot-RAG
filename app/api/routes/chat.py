from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import Settings, get_settings
from app.core.logger_config import get_logger
from app.services.retriever import retrieve_relevant_chunks
from app.services.generator import GeneratorService

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

from app.schemas.chat import ChatRequest, ChatResponse

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
        request: ChatRequest
):
    user_id = request.user_id
    tenant_id = request.tenant_id
    question = request.question

    logger.info(f"Received question from user_id: {user_id} for tenant_id: {tenant_id} with question: {question}")
    retrieved_chunks = await retrieve_relevant_chunks(
        tenant_id = tenant_id,
        question = question,
        settings = get_settings()
    )
    generator_service = GeneratorService(settings = get_settings())
    try:
        answer_dict = await generator_service.generate_answer(
            question = question,
            retrieval_results = retrieved_chunks,
        )
        return ChatResponse(
            answer=answer_dict["answer"],
            sources=answer_dict["sources"]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request. Detail: {e}"
        )

    
