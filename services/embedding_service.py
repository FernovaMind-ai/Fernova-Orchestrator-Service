"""
Embedding Service - Handles communication with Fernova Vector Embeddings Service
"""
import httpx
from typing import List, Dict, Any

from config import settings
from utils.exceptions import EmbeddingServiceError, ServiceUnavailableError
from utils.logging import log_embedding_step, log_error


class EmbeddingService:
    """Service for converting text to embeddings"""
    
    def __init__(self):
        self.base_url = settings.EMBEDDING_SERVICE_URL
        self.timeout = settings.TIMEOUT_SECONDS
    
    async def embed_text(self, text: str, method: str = "ensemble") -> Dict[str, Any]:
        """
        Convert text to embeddings
        
        Args:
            text: Text to convert
            method: Embedding method (ensemble, base, etc.)
        
        Returns:
            Dictionary with embedding vector and metadata
        
        Raises:
            EmbeddingServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/embed",
                    json={
                        "text": text,
                        "method": method,
                    },
                )
            
            if response.status_code >= 400:
                raise EmbeddingServiceError(
                    response.status_code,
                    response.text
                )
            
            data = response.json()
            
            # Log success
            query_embedding = data.get("embedding", [])
            embedding_dimensions = data.get("dimensions", 0)
            log_embedding_step(embedding_dimensions, method, query_embedding[:5])
            
            return data
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Embedding", str(exc))
    
    async def embed_batch(self, texts: List[str], method: str = "ensemble") -> Dict[str, Any]:
        """
        Convert multiple texts to embeddings
        
        Args:
            texts: List of texts to convert
            method: Embedding method
        
        Returns:
            Dictionary with embeddings and metadata
        
        Raises:
            EmbeddingServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/embed/batch",
                    json={
                        "texts": texts,
                        "method": method,
                    },
                )
            
            if response.status_code >= 400:
                raise EmbeddingServiceError(
                    response.status_code,
                    response.text
                )
            
            return response.json()
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Embedding", str(exc))
