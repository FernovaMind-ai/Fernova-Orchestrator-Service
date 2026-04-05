"""
Response models for Fernova Orchestrator Service
"""
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class SearchLLMResult(BaseModel):
    """Response model for search-and-query endpoint"""
    
    status: str = Field(..., description="Operation status (success, error, etc.)")
    query: str = Field(..., description="Original search query")
    search_results: List[Dict[str, Any]] = Field(..., description="List of search results")
    llm_response: Dict[str, Any] = Field(..., description="LLM response with answer")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")


class OrchestratorResult(BaseModel):
    """Response model for extract-embed-store endpoint"""
    
    status: str = Field(..., description="Operation status")
    doc_id: str = Field(..., description="Document ID")
    source_pages: int = Field(..., description="Number of pages in source document")
    documents_indexed: int = Field(..., description="Number of documents indexed")
    embedding_method: str = Field(..., description="Embedding method used")
    ocr_response: Dict[str, Any] = Field(..., description="OCR service response")
    embedding_response: Dict[str, Any] = Field(..., description="Embedding service response")
    search_response: Dict[str, Any] = Field(..., description="Search service response")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")


class DiagnosticsResponse(BaseModel):
    """Response model for diagnostics endpoint"""
    
    orchestrator: str = Field(..., description="Orchestrator status")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Status of each backend service")


class ErrorResponse(BaseModel):
    """Response model for error responses"""
    
    status: str = Field(default="error", description="Error status")
    detail: str = Field(..., description="Error detail message")
    error_code: int = Field(..., description="HTTP error code")
