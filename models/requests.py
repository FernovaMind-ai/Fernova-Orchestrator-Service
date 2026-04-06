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


class EmbedTextRequest(BaseModel):
    """Request model for embedding a single text"""
    
    text: str = Field(..., description="Text to embed")
    method: str = Field(default="ensemble", description="Embedding method (ensemble, bge, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog",
                "method": "ensemble"
            }
        }


class EmbedBatchRequest(BaseModel):
    """Request model for embedding multiple texts"""
    
    texts: list[str] = Field(..., description="List of texts to embed")
    method: str = Field(default="ensemble", description="Embedding method (ensemble, bge, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": ["Text 1", "Text 2", "Text 3"],
                "method": "ensemble"
            }
        }


class TokenCountRequest(BaseModel):
    """Request model for getting token count"""
    
    text: str = Field(..., description="Text to count tokens for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog"
            }
        }


class ChunkTextRequest(BaseModel):
    """Request model for chunking text for RAG"""
    
    text: str = Field(..., description="Text to chunk")
    target_tokens: int = Field(default=400, ge=100, le=2000, description="Target tokens per chunk")
    overlap_tokens: int = Field(default=50, ge=0, le=500, description="Overlap tokens between chunks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Long document text...",
                "target_tokens": 400,
                "overlap_tokens": 50
            }
        }

