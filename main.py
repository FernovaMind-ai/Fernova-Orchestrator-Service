"""
Fernova Orchestrator Service - Entry Point
Single file application with FastAPI factory
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.routes import health, search_query


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