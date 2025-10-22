"""
Document Generation API Routes
Epic 1, Feature 1.1: Document Generator
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.document_generator import DocumentGenerator

router = APIRouter()
generator = DocumentGenerator()

class DocumentGenerationRequest(BaseModel):
    """Request model for document generation"""
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    company_size: str = Field(description="Company size: small, medium, large")
    clauses: List[str] = Field(description="ISO 9001 clauses to include")
    language: str = Field(default="en", description="Document language")
    format: str = Field(default="markdown", description="Output format: markdown, pdf, docx")
    generate_full_manual: bool = Field(default=True, description="Generate combined manual vs individual files")
    custom_context: Optional[str] = Field(default=None, description="Additional company context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Manufacturing Inc",
                "industry": "manufacturing",
                "company_size": "medium",
                "clauses": ["4.1", "4.2", "5.1"],
                "format": "markdown",
                "generate_full_manual": True
            }
        }

class DocumentResponse(BaseModel):
    """Response model for generated documents"""
    document_id: str = Field(description="Unique document identifier")
    status: str = Field(description="Generation status: completed, failed")
    created_at: datetime = Field(description="Document generation timestamp")
    file_path: Optional[str] = Field(default=None, description="Path to generated file")
    file_name: Optional[str] = Field(default=None, description="Generated file name")
    file_size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    clauses_included: Optional[List[str]] = Field(default=None, description="ISO clauses included")
    generation_time_ms: Optional[float] = Field(default=None, description="Generation time")
    download_url: Optional[str] = Field(default=None, description="Download URL")
    message: Optional[str] = Field(default=None, description="Additional information or error message")

@router.post("/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a new ISO 9001 document based on company profile
    
    User Story: As a Quality Manager, I want to generate a complete ISO 9001 manual 
    automatically, so that I can have a baseline for certification.
    """
    import time
    import uuid
    
    start_time = time.time()
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    
    try:
        # Build company data dict
        company_data = {
            "company_name": request.company_name,
            "industry": request.industry,
            "company_size": request.company_size,
        }
        
        if request.custom_context:
            company_data["custom_context"] = request.custom_context
        
        # Generate document (returns file path)
        if request.generate_full_manual:
            file_path = generator.generate_full_manual(request.clauses, company_data)
        else:
            # Generate individual clause
            if len(request.clauses) != 1:
                raise HTTPException(
                    status_code=400,
                    detail="When generate_full_manual=False, provide exactly one clause"
                )
            file_path = generator.generate_document(request.clauses[0], company_data)
        
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Document generation failed - check template availability"
            )
        
        # Get file info
        file_path_obj = Path(file_path)
        file_size = file_path_obj.stat().st_size
        file_name = file_path_obj.name
        generation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return DocumentResponse(
            document_id=doc_id,
            status="completed",
            created_at=datetime.now(),
            file_path=str(file_path_obj),
            file_name=file_name,
            file_size_bytes=file_size,
            clauses_included=request.clauses,
            generation_time_ms=round(generation_time, 2),
            download_url=f"/api/documents/{doc_id}/download",
            message=f"Successfully generated {len(request.clauses)} clause(s)"
        )
        
    except Exception as e:
        return DocumentResponse(
            document_id=doc_id,
            status="failed",
            created_at=datetime.now(),
            message=f"Generation failed: {str(e)}"
        )

@router.get("/{document_id}/download")
async def download_document(document_id: str):
    """Download a generated document"""
    from fastapi.responses import FileResponse
    
    output_dir = Path("output")
    
    # Find file matching document_id
    matching_files = list(output_dir.glob(f"{document_id}_*"))
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = matching_files[0]
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="text/markdown"
    )

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Retrieve document metadata by ID"""
    output_dir = Path("output")
    matching_files = list(output_dir.glob(f"{document_id}_*"))
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = matching_files[0]
    file_stat = file_path.stat()
    
    return DocumentResponse(
        document_id=document_id,
        status="completed",
        created_at=datetime.fromtimestamp(file_stat.st_ctime),
        file_path=str(file_path),
        file_name=file_path.name,
        file_size_bytes=file_stat.st_size,
        download_url=f"/api/documents/{document_id}/download"
    )

@router.get("/")
async def list_documents(skip: int = 0, limit: int = 10):
    """List all generated documents with pagination"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    all_files = sorted(
        output_dir.glob("doc_*"),
        key=lambda p: p.stat().st_ctime,
        reverse=True
    )
    
    paginated = all_files[skip:skip+limit]
    
    documents = []
    for file_path in paginated:
        # Extract doc_id from filename (doc_abc123_...)
        doc_id = file_path.name.split('_')[0] + '_' + file_path.name.split('_')[1]
        file_stat = file_path.stat()
        
        documents.append({
            "document_id": doc_id,
            "file_name": file_path.name,
            "file_size_bytes": file_stat.st_size,
            "created_at": datetime.fromtimestamp(file_stat.st_ctime),
            "download_url": f"/api/documents/{doc_id}/download"
        })
    
    return {
        "documents": documents,
        "total": len(all_files),
        "skip": skip,
        "limit": limit
    }
