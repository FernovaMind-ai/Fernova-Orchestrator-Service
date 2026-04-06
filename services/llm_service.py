"""
LLM Service - Handles communication with Fernova LLM API Service
"""
import httpx
from typing import Dict, Any, Optional

from config import settings
from utils.exceptions import LLMServiceError, ServiceUnavailableError
from utils.logging import log_llm_step, log_llm_response, log_error


class LLMService:
    """Service for LLM query operations"""
    
    def __init__(self):
        self.base_url = settings.LLM_SERVICE_URL
        self.timeout = settings.TIMEOUT_SECONDS
    
    async def query(
        self,
        query: str,
        context: str,
        provider: str,
        model: str,
        api_key: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_type: str = "summary",
        headers: dict = None,
    ) -> Dict[str, Any]:
        """
        Query LLM with context
        
        Args:
            query: User query
            context: Context for the LLM
            provider: LLM provider (openai, gemini, etc.)
            model: Model name
            api_key: API key for the provider
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            response_type: Type of response (general, analysis, summary, qna, next_query, creative)
            headers: Optional headers to propagate (e.g., X-User-ID)
        
        Returns:
            Dictionary with LLM response
        
        Raises:
            LLMServiceError: If service returns error
            ServiceUnavailableError: If service is unreachable
        """
        # Log the step
        log_llm_step(provider, model, len(context), bool(api_key))
        
        payload = {
            "query": query,
            "llm_config": {
                "provider": provider,
                "model": model,
                "api_key": api_key,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            "response_type": response_type,
            "context": context,
        }
        
        try:
            # Prepare headers with auth and content-type
            request_headers = headers or {}
            request_headers["Content-Type"] = "application/json"
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/query",
                    json=payload,
                    headers=request_headers
                )
            
            # Log response status
            log_llm_response(response.status_code)
            
            if response.status_code >= 400:
                error_msg = f"LLM service error: {response.status_code} - {response.text}"
                log_error("LLMServiceError", error_msg)
                raise LLMServiceError(response.status_code, response.text)
            
            # Parse response
            data = response.json()
            return data
            
        except httpx.RequestError as exc:
            error_msg = f"LLM Service Connection Error: {str(exc)}"
            log_error("ServiceUnavailableError", error_msg)
            raise ServiceUnavailableError("LLM", str(exc))
