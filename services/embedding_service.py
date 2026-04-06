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
    
    async def embed_text(self, text: str, method: str = "ensemble", headers: dict = None) -> Dict[str, Any]:
        """
        Convert text to embeddings
        
        Args:
            text: Text to convert
            method: Embedding method (ensemble, base, etc.)
            headers: Optional headers to propagate (e.g., X-User-ID)
        
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
                    headers=headers or {}
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
    
    async def embed_batch(self, texts: List[str], method: str = "ensemble", headers: dict = None) -> Dict[str, Any]:
        """
        Convert multiple texts to embeddings
        
        Args:
            texts: List of texts to convert
            method: Embedding method
            headers: Optional headers to propagate (e.g., X-User-ID)
        
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
                    headers=headers or {}
                )
            
            if response.status_code >= 400:
                raise EmbeddingServiceError(
                    response.status_code,
                    response.text
                )
            
            return response.json()
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Embedding", str(exc))
    
    async def split_text(
        self,
        text: str,
        target_tokens: int = 400,
        overlap_tokens: int = 50,
        method: str = "similarity",
        headers: dict = None
    ) -> Dict[str, Any]:
        """
        Split text into token-optimized chunks using BAAI/bge tokenizer
        
        This calls Vector Service for RAG-optimized chunking:
        - Target: 400 tokens per chunk
        - Overlap: 50 tokens for semantic stitching
        - Boundary: Sentence-aware breaking
        
        Args:
            text: Text to split
            target_tokens: Target tokens per chunk (default 400)
            overlap_tokens: Token overlap between chunks (default 50)
            method: Chunking method (default "similarity")
            headers: Optional headers to propagate (e.g., X-User-ID)
        
        Returns:
            Dictionary with chunks and token statistics
        
        Raises:
            EmbeddingServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/split-text",
                    json={
                        "text": text,
                        "target_tokens": target_tokens,
                        "overlap_tokens": overlap_tokens,
                        "method": method,
                    },
                    headers=headers or {}
                )
            
            if response.status_code >= 400:
                raise EmbeddingServiceError(
                    response.status_code,
                    response.text
                )
            
            return response.json()
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Embedding/Chunking", str(exc))
