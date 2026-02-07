# CLAUDE.md

## Project Overview
PolicyChatbot is a RAG (Retrieval-Augmented Generation) application designed to answer questions based on uploaded policy documents. It uses FastAPI for the backend, ChromaDB for vector storage, and OpenAI for generation.

## Architecture
- **Backend Framework**: FastAPI (`app/main.py`)
- **Storage**:
  - **S3**: Stores raw uploaded documents (`app/services/s3_upload.py`).
  - **ChromaDB**: Stores vector embeddings of document chunks (`app/services/vector_store.py`).
- **RAG Pipeline**:
  - **Ingestion**: `app/services/ingest.py` orchestrates fetching from S3, parsing, chunking, embedding, and storing.
  - **Parsing**: Supports PDF, RTF, and Text (`app/services/parser.py`).
  - **Embedding**: Uses `sentence-transformers/all-MiniLM-L6-v2` (`app/services/embeddings.py`).
  - **Generation**: Uses OpenAI Chat Completion (`app/services/generator.py`).

## File Structure
- `app/api/routes`: API endpoints (chat, uploads, health).
- `app/services`: Core logic (AWS S3, ChromaDB, OpenAI, Parsing, Chunking).
- `app/core`: Configuration and logging.

## Commands
- **Run Server**: `uvicorn app.main:app --reload --port 8000`
- **Install Dependencies**: `uv sync` (assuming `uv` based on `uv.lock`) or `pip install -r requirements.txt` (if generated).

## Configuration
- Environment variables managed via `pydantic-settings`.
- Key variables: `OPENAI_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CHROMA_API_KEY` (if cloud), `CHROMA_TENANT`, `CHROMA_DATABASE`.
