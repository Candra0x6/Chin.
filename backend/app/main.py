"""
Main FastAPI application entry point for Chin .
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import upload, analysis, chat, results, test


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize directories
    settings.get_upload_path()
    settings.get_results_path()
    settings.get_model_path()
    
    print("🚀 Chin  Backend Started")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📁 Results directory: {settings.results_dir}")
    print(f"📁 Models directory: {settings.model_path}")
    
    yield
    
    # Shutdown: Cleanup if needed
    print("👋 Chin  Backend Shutting Down")


# Initialize FastAPI application
app = FastAPI(
    title="Chin  API",
    description="Video-based Emergency Room Flow Analyzer with AI insights",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(results.router)
app.include_router(test.router)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Chin  API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "directories": {
            "uploads": str(settings.get_upload_path()),
            "results": str(settings.get_results_path()),
            "models": str(settings.get_model_path())
        }
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "detail": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
