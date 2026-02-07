import chromadb
from openai import AsyncOpenAI
from typing import Optional

# Global variables to hold client instances
_openai_client: Optional[AsyncOpenAI] = None
_chroma_client: Optional[chromadb.Client] = None

# OpenAI Client Management
def set_openai_client(client: AsyncOpenAI):
    global _openai_client
    _openai_client = client

def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        raise RuntimeError("Global OpenAI Client not initialized. Ensure app startup or worker init has run.")
    return _openai_client

# ChromaDB Client Management
def set_chroma_client(client: chromadb.Client):
    global _chroma_client
    _chroma_client = client

def get_chroma_client() -> chromadb.Client:
    global _chroma_client
    if _chroma_client is None:
        raise RuntimeError("Global ChromaDB Client not initialized. Ensure app startup or worker init has run.")
    return _chroma_client
