from .health import router as health_router
from .uploads import router as uploads_router
from .chat import router as chat_router

__all__ = ["health_router", "uploads_router"]
