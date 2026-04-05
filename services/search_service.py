"""
Search Service - Handles communication with Fernova AI Search Service
"""
import httpx
from typing import Dict, Any, List

from config import settings
from utils.exceptions import SearchServiceError, ServiceUnavailableError
from utils.logging import log_search_step


class SearchService:
    """Service for semantic search operations"""
    
    def __init__(self):
        self.base_url = settings.SEARCH_SERVICE_URL
        self.timeout = settings.TIMEOUT_SECONDS
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        method: str = "ensemble"
    ) -> Dict[str, Any]:
        """
        Perform semantic search on indexed documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
            method: Embedding method (ensemble, base, etc.)
        
        Returns:
            Dictionary with search results
        
        Raises:
            SearchServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/integrate/search",
                    json={
                        "query": query,
                        "search_type": "semantic",
                        "top": top_k,
                        "method": method,
                    },
                )
            
            if response.status_code >= 400:
                raise SearchServiceError(
                    response.status_code,
                    response.text
                )
            
            data = response.json()
            search_results = data.get("results", [])
            
            # Log search results
            top_score = search_results[0].get("score") if search_results else None
            log_search_step(len(search_results), top_score)
            
            return data
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Search", str(exc))
    
    async def store_document(
        self,
        doc_id: str,
        text: str,
        title: str,
        description: str,
        category: str = "general",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Store a single document
        
        Args:
            doc_id: Document ID
            text: Document content text
            title: Document title
            description: Document description
            category: Document category
            metadata: Optional metadata
        
        Returns:
            Response from search service
        
        Raises:
            SearchServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        try:
            payload = {
                "doc_id": doc_id,
                "text": text,
                "title": title,
                "description": description,
                "category": category,
            }
            if metadata:
                payload["metadata"] = metadata
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/integrate/store",
                    json=payload,
                )
            
            if response.status_code >= 400:
                raise SearchServiceError(
                    response.status_code,
                    response.text
                )
            
            return response.json()
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Search", str(exc))
    
    async def batch_store_documents(
        self,
        documents: List[Dict[str, Any]],
        method: str = "ensemble"
    ) -> Dict[str, Any]:
        """
        Store multiple documents
        
        Args:
            documents: List of document dictionaries
            method: Embedding method
        
        Returns:
            Response from search service
        
        Raises:
            SearchServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/integrate/batch-store",
                    json={
                        "documents": documents,
                        "method": method,
                    },
                )
            
            if response.status_code >= 400:
                raise SearchServiceError(
                    response.status_code,
                    response.text
                )
            
            return response.json()
            
        except httpx.RequestError as exc:
            raise ServiceUnavailableError("Search", str(exc))
