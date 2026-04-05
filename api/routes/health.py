"""
Health and Diagnostics Routes
"""
import httpx
from typing import Dict, Any
from fastapi import APIRouter

from config import settings
from models.responses import HealthResponse, DiagnosticsResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    
    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        status="healthy",
        service="orchestrator"
    )


@router.get("/diagnostics", response_model=DiagnosticsResponse)
async def diagnostics() -> Dict[str, Any]:
    """
    Check if all backend services are reachable
    
    Returns:
        Diagnostics with status of each service
    """
    diagnostics_result = {
        "orchestrator": "ok",
        "services": {}
    }
    
    services = {
        "embeddings": settings.EMBEDDING_SERVICE_URL,
        "search": settings.SEARCH_SERVICE_URL,
        "llm": settings.LLM_SERVICE_URL,
    }
    
    for service_name, service_url in services.items():
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                health_resp = await client.get(f"{service_url}/health")
                diagnostics_result["services"][service_name] = {
                    "url": service_url,
                    "status": "ok" if health_resp.status_code == 200 else f"error_{health_resp.status_code}",
                    "response": health_resp.json() if health_resp.status_code == 200 else None
                }
        except Exception as e:
            diagnostics_result["services"][service_name] = {
                "url": service_url,
                "status": "unreachable",
                "error": str(e)
            }
    
    return diagnostics_result
