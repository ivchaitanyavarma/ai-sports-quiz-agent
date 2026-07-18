import os
import logging
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Strongly typed system configuration management."""
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # --- New Embedding Configuration ---
    # Set to either "openai" or "huggingface" in your .env file
    EMBEDDING_PROVIDER: Literal["openai", "huggingface"] = "openai"
    
    # OpenAI model (Used if provider is 'openai')
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Hugging Face model (Used if provider is 'huggingface')
    HF_EMBEDDING_MODEL: str = "mixedbread-ai/mxbai-embed-large-v1"
    
    LLM_MODEL: str = "gemini-3.5-flash"
    LLM_TEMPERATURE: float = 0.7
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        extra="ignore"
    )

settings = Settings()

def get_logger(name: str) -> logging.Logger:
    """Standardized production logging across application boundaries."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger