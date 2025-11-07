from fastapi import FastAPI
from fastapi.responses import JSONResponse
from uvicorn import run
from app.api.routes import health_router
from app.api.routes import uploads_router
from app.core.config import get_settings

app = FastAPI()
app.include_router(health_router)
app.include_router(uploads_router)
settings = get_settings()

@app.get('/')
async def root():
    return JSONResponse({
        "message": "PolicyChatbot Q&A"
    })



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.port_no,
        reload=True
    )

