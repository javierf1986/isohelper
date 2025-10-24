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

from backend.api.routes import documents, templates, compliance, workspaces, auth, export, artifacts, versions, gap_analysis
from backend.database.database import init_db
from config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    print("🚀 Starting ISO 9001 AI Documentation Generator")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print("🗄️  Initializing database...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down application")

app = FastAPI(
    title="ISO Helper - Universal Multi-ISO Platform",
    description="Enterprise platform for multi-ISO standard management with AI-powered document generation and workspace collaboration",
    version="3.0.0",
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
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Templates"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance"])
app.include_router(workspaces.router, tags=["Workspaces"])
app.include_router(export.router, tags=["Export"])
app.include_router(artifacts.router, prefix="/api/v1", tags=["Artifacts"])
app.include_router(versions.router, tags=["Versions"])
app.include_router(gap_analysis.router, tags=["Gap Analysis"])

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "ISO Helper - Universal Multi-ISO Platform",
        "version": "3.0.0",
        "phase": "Phase 3: Enterprise & Security",
        "features": [
            "Multi-ISO standard support (9001, 14001, 27001, 45001, etc.)",
            "JWT authentication and RBAC",
            "Multi-tenant workspaces",
            "AI-powered document generation",
            "78 clauses across 2 ISO standards"
        ],
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
