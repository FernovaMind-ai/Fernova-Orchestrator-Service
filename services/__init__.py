"""Services package"""
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from services.llm_service import LLMService

# Global service instances
embedding_service = EmbeddingService()
search_service = SearchService()
llm_service = LLMService()

__all__ = [
    "EmbeddingService",
    "SearchService",
    "LLMService",
    "embedding_service",
    "search_service",
    "llm_service",
]
