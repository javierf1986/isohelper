"""
ISO 9001 AI Documentation Generator - Main API Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from api.routes import documents, templates, compliance
from config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    print("🚀 Starting ISO 9001 AI Documentation Generator")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    yield
    # Shutdown
    print("🛑 Shutting down application")

app = FastAPI(
    title="ISO 9001 AI Documentation Generator",
    description="Autonomous generation and management of ISO 9001 certification documentation",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Templates"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance"])

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "ISO 9001 AI Documentation Generator API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
