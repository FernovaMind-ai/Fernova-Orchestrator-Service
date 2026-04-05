"""
Request models for Fernova Orchestrator Service
"""
from typing import Optional
from pydantic import BaseModel, Field


class SearchQueryRequest(BaseModel):
    """Request model for search-and-query endpoint"""
    
    query: str = Field(..., description="Search query string")
    llm_provider: str = Field(default="openai", description="LLM provider (openai, gemini, etc.)")
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM model name")
    api_key: str = Field(default="", description="API key for LLM provider")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens in response")
    search_type: str = Field(default="semantic", description="Type of search (semantic, full_text, hybrid)")
    top: int = Field(default=10, ge=1, le=100, description="Number of top results")
    embedding_method: str = Field(default="ensemble", description="Embedding method to use")
    response_type: str = Field(default="summary", description="Response type: general, analysis, summary, qna, next_query, creative")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "explain what is fingerprint reconstruction",
                "llm_provider": "gemini",
                "llm_model": "gemini-2.5-flash",
                "api_key": "your-api-key",
                "temperature": 0.7,
                "max_tokens": None,
                "search_type": "semantic",
                "top": 10,
                "embedding_method": "ensemble",
                "response_type": "analysis"
            }
        }


class ExtractEmbedStoreRequest(BaseModel):
    """Request model for extract-embed-store endpoint (file upload handled separately)"""
    
    doc_id_prefix: Optional[str] = Field(default="doc", description="Prefix for document ID")
    method: Optional[str] = Field(default="ensemble", description="Embedding method")
    category: Optional[str] = Field(default="general", description="Document category")
    split_by_page: Optional[bool] = Field(default=True, description="Split content by page")
