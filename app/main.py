from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.routes import health_router
from app.api.routes import uploads_router
from app.api.routes import chat_router
from app.core import globals
from app.core.config import get_settings
from app.services import vector_store
from openai import AsyncOpenAI

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    # Initialize OpenAI
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    globals.set_openai_client(openai_client)
    
    # Initialize ChromaDB (Sync)
    chroma_client = vector_store._create_chroma_client(settings)
    globals.set_chroma_client(chroma_client)
    
    yield
    
    # Cleanup
    await openai_client.close()

app = FastAPI(title="Policy RAG Chatbot", lifespan=lifespan)
app.include_router(health_router)
app.include_router(uploads_router)
app.include_router(chat_router)
settings = get_settings()

@app.get('/')
async def root():
    return JSONResponse({
        "message": "PolicyChatbot Q&A"
    })



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=settings.port_no,
        reload=True
    )

