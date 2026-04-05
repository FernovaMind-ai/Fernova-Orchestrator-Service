"""
Configuration management for Fernova Orchestrator Service
"""
import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables"""
    
    # Service URLs
    OCR_SERVICE_URL: str = os.getenv("OCR_SERVICE_URL", "http://127.0.0.1:8000")
    EMBEDDING_SERVICE_URL: str = os.getenv("EMBEDDINGS_SERVICE_URL", "http://127.0.0.1:8001")
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://127.0.0.1:8002")
    LLM_SERVICE_URL: str = os.getenv("LLM_SERVICE_URL", "http://127.0.0.1:8003")
    
    # Timeout configuration
    TIMEOUT_SECONDS: int = int(os.getenv("ORCHESTRATOR_TIMEOUT", "1000"))
    
    # Application metadata
    APP_NAME: str = "Fernova Orchestrator Service"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Pipeline orchestration across OCR, embeddings, and search services"
    
    # API configuration
    API_V1_PREFIX: str = "/api/v1"
    ORCHESTRATOR_PREFIX: str = "/api/v1/orchestrator"
    
    # Default values for requests
    DEFAULT_EMBEDDING_METHOD: str = "ensemble"
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_K: int = 10
    
    # Search configuration
    DEFAULT_SEARCH_TYPE: str = "semantic"
    SNIPPET_MAX_LENGTH: int = 400
    
    @classmethod
    def get_services(cls) -> dict:
        """Get all service URLs as a dictionary"""
        return {
            "ocr": cls.OCR_SERVICE_URL,
            "embeddings": cls.EMBEDDING_SERVICE_URL,
            "search": cls.SEARCH_SERVICE_URL,
            "llm": cls.LLM_SERVICE_URL,
        }


# Global settings instance
settings = Settings()
