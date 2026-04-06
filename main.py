"""
Fernova Orchestrator Service - Entry Point
Single file application with FastAPI factory
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from api.routes import health, search_query


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware that validates X-User-ID header
    
    Args:
        request: The incoming request
        call_next: The next middleware/route handler
        
    Returns:
        Response from the next middleware/handler
    """
    # Allow health checks without authentication
    if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Validate X-User-ID header for all other endpoints
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing X-User-ID header"}
        )
    
    # Attach user_id to request state for downstream use
    request.state.user_id = user_id
    request.state.is_admin = request.headers.get("X-Is-Admin", "false").lower() == "true"
    
    return await call_next(request)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Add authentication middleware (before CORS to protect routes)
    app.middleware("http")(auth_middleware)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(search_query.router)
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }
    
    return app


# Create app instance for uvicorn
app = create_app()


def main():
    """Start the Fernova Orchestrator Service"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()