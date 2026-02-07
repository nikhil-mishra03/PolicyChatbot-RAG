from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.ingestion_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

from celery.signals import worker_process_init
from app.core import globals
from app.services import vector_store
from openai import AsyncOpenAI
import asyncio

@worker_process_init.connect
def init_worker(**kwargs):
    settings = get_settings()
    
    # Initialize OpenAI (Global)
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    globals.set_openai_client(openai_client)
    
    # Initialize ChromaDB (Sync)
    chroma_client = vector_store._create_chroma_client(settings)
    globals.set_chroma_client(chroma_client)
    
    print("Worker initialized global clients.")
