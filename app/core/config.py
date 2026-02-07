from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow',
    )

    port_no: int
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    policy_bucket_name: str
    chroma_api_key: str
    chroma_tenant: str
    chroma_database: str
    chromadb_collection_name: str = "policy_rag_openai_v1"
    num_retrieved_chunks: int = 9
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str
    openai_model_name: str
    openai_embedding_model: str = "text-embedding-3-small"


def get_settings() -> Settings:
    return Settings()
    