"""
Document Generation API Routes
Epic 1, Feature 1.1: Document Generator
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import sys
from sqlalchemy.orm import Session

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.document_generator import DocumentGenerator
from backend.database.database import get_db
from backend.models.iso_models import ISOStandard, ISOClause

router = APIRouter()
generator = DocumentGenerator()

class DocumentGenerationRequest(BaseModel):
    """Request model for document generation"""
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    company_size: str = Field(description="Company size: small, medium, large")
    clauses: List[str] = Field(description="ISO clauses to include")
    language: str = Field(default="en", description="Document language")
    format: str = Field(default="markdown", description="Output format: markdown, pdf, docx")
    generate_full_manual: bool = Field(default=True, description="Generate combined manual vs individual files")
    custom_context: Optional[str] = Field(default=None, description="Additional company context")
    enable_ai_enhancement: bool = Field(default=False, description="Enable AI-powered content enhancement")
    ai_enhancement_level: str = Field(default="moderate", description="AI enhancement level: light, moderate, comprehensive")
    
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

class WizardGenerationRequest(BaseModel):
    """Request model from document generation wizard"""
    iso_standard: str = Field(description="ISO standard ID (e.g., ISO-9001-2015)")
    selected_clauses: List[str] = Field(description="List of clause numbers to include")
    company_name: str = Field(description="Company name")
    company_description: Optional[str] = Field(default=None, description="Company description")
    scope: Optional[str] = Field(default=None, description="QMS scope")
    use_ai_enhancement: bool = Field(default=True, description="Enable AI enhancement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "iso_standard": "ISO-9001-2015",
                "selected_clauses": ["4.1", "4.2", "5.1"],
                "company_name": "Acme Corp",
                "company_description": "Manufacturing company",
                "scope": "Design and production of widgets",
                "use_ai_enhancement": True
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
async def generate_document_wizard(
    request: WizardGenerationRequest, 
    db: Session = Depends(get_db)
):
    """
    Generate document from wizard (new format)
    Accepts ISO standard ID and clause numbers from the frontend wizard
    """
    import time
    import uuid
    
    start_time = time.time()
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    
    try:
        # Verify ISO standard exists
        standard = db.query(ISOStandard).filter(ISOStandard.id == request.iso_standard).first()
        if not standard:
            raise HTTPException(status_code=404, detail=f"ISO standard {request.iso_standard} not found")
        
        # Verify clauses exist
        clauses = db.query(ISOClause).filter(
            ISOClause.standard_id == request.iso_standard,
            ISOClause.clause_number.in_(request.selected_clauses)
        ).all()
        
        if len(clauses) != len(request.selected_clauses):
            found_numbers = {str(c.clause_number) for c in clauses}
            missing = set(request.selected_clauses) - found_numbers
            raise HTTPException(
                status_code=400, 
                detail=f"Clauses not found: {', '.join(missing)}"
            )
        
        # Build company data
        company_data = {
            "company_name": request.company_name,
            "industry": "general",  # Default
            "company_size": "medium",  # Default
        }
        
        if request.company_description:
            company_data["custom_context"] = request.company_description
        
        if request.scope:
            company_data["scope"] = request.scope
        
        # Generate document
        file_path = generator.generate_full_manual(request.selected_clauses, company_data)
        
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Document generation failed"
            )
        
        # Get file info
        file_path_obj = Path(file_path)
        file_size = file_path_obj.stat().st_size
        file_name = file_path_obj.name
        generation_time = (time.time() - start_time) * 1000
        
        return DocumentResponse(
            document_id=doc_id,
            status="completed",
            created_at=datetime.now(),
            file_path=str(file_path_obj),
            file_name=file_name,
            file_size_bytes=file_size,
            clauses_included=request.selected_clauses,
            generation_time_ms=round(generation_time, 2),
            download_url=f"/api/v1/documents/{doc_id}/download",
            message=f"Successfully generated document with {len(request.selected_clauses)} clause(s)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return DocumentResponse(
            document_id=doc_id,
            status="failed",
            created_at=datetime.now(),
            message=f"Generation failed: {str(e)}"
        )

@router.post("/generate/legacy", response_model=DocumentResponse)
async def generate_document(request: DocumentGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a new ISO document based on company profile
    
    User Story: As a Quality Manager, I want to generate a complete ISO manual 
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


# ============================================================================
# AI Enhancement Endpoints
# ============================================================================

class AIEnhancementRequest(BaseModel):
    """Request model for AI content enhancement"""
    clause: str = Field(description="ISO clause number")
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    company_size: str = Field(description="Company size")
    custom_context: Optional[str] = Field(default=None, description="Additional context")
    enhancement_level: str = Field(default="moderate", description="Enhancement level: light, moderate, comprehensive")
    ai_provider: Optional[str] = Field(default=None, description="AI provider: mistral, openai, local")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clause": "4.1",
                "company_name": "TechCorp Industries",
                "industry": "software development",
                "company_size": "medium",
                "enhancement_level": "moderate",
                "ai_provider": "mistral"
            }
        }


class AIEnhancementResponse(BaseModel):
    """Response model for AI enhancement"""
    clause: str
    enhanced_content: str
    provider_used: str
    enhancement_level: str
    generation_time_ms: float
    status: str
    message: Optional[str] = None


@router.post("/enhance", response_model=AIEnhancementResponse)
async def enhance_content(request: AIEnhancementRequest):
    """
    Enhance ISO clause content using AI
    
    User Story: As a Quality Manager, I want AI-generated industry-specific 
    examples and context, so that my documentation is more relevant and comprehensive.
    """
    import time
    from backend.services.ai_enhancer import AIEnhancer
    from config.settings import settings
    
    # Check if AI enhancement is enabled
    if not settings.ENABLE_AI_ENHANCEMENT:
        raise HTTPException(
            status_code=503,
            detail="AI enhancement is currently disabled. Enable it in settings."
        )
    
    start_time = time.time()
    provider_str = "mistral"  # Default
    
    try:
        # Determine AI provider
        provider_str = request.ai_provider or settings.AI_PROVIDER
        if provider_str not in ["mistral", "openai", "local"]:
            provider_str = "mistral"
        
        # Initialize AI enhancer
        ai_enhancer = AIEnhancer(provider=provider_str)  # type: ignore
        
        # First generate base content
        company_data = {
            "company_name": request.company_name,
            "industry": request.industry,
            "company_size": request.company_size,
        }
        
        if request.custom_context:
            company_data["custom_context"] = request.custom_context
        
        # Generate base content
        base_content = generator.generate_document(request.clause, company_data)
        
        if not base_content:
            raise HTTPException(
                status_code=404,
                detail=f"Template not found for clause {request.clause}"
            )
        
        # Read the generated base content
        base_file = Path(base_content)
        base_text = base_file.read_text(encoding="utf-8")
        
        # Validate enhancement level
        level = request.enhancement_level
        if level not in ["light", "moderate", "comprehensive"]:
            level = "moderate"
        
        # Enhance with AI
        enhanced_content = await ai_enhancer.enhance_clause_content(
            clause=request.clause,
            base_content=base_text,
            company_data=company_data,
            enhancement_level=level  # type: ignore
        )
        
        generation_time = (time.time() - start_time) * 1000
        
        return AIEnhancementResponse(
            clause=request.clause,
            enhanced_content=enhanced_content,
            provider_used=ai_enhancer.provider.get_provider_name(),
            enhancement_level=request.enhancement_level,
            generation_time_ms=round(generation_time, 2),
            status="completed",
            message=f"Successfully enhanced clause {request.clause} content"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AIEnhancementResponse(
            clause=request.clause,
            enhanced_content="",
            provider_used=provider_str,
            enhancement_level=request.enhancement_level,
            generation_time_ms=0,
            status="failed",
            message=f"Enhancement failed: {str(e)}"
        )


@router.post("/examples", response_model=dict)
async def generate_industry_examples(
    clause: str,
    industry: str,
    company_size: str,
    ai_provider: Optional[str] = None
):
    """
    Generate industry-specific examples for an ISO clause
    
    User Story: As a Quality Manager, I want to see real-world examples 
    from my industry, so that I can better understand how to implement the requirements.
    """
    from backend.services.ai_enhancer import AIEnhancer
    from config.settings import settings
    import time
    
    if not settings.ENABLE_AI_ENHANCEMENT:
        raise HTTPException(
            status_code=503,
            detail="AI enhancement is currently disabled"
        )
    
    start_time = time.time()
    
    try:
        provider_str = ai_provider or settings.AI_PROVIDER
        if provider_str not in ["mistral", "openai", "local"]:
            provider_str = "mistral"
        ai_enhancer = AIEnhancer(provider=provider_str)  # type: ignore
        
        examples = await ai_enhancer.generate_industry_specific_examples(
            clause=clause,
            industry=industry,
            company_size=company_size
        )
        
        generation_time = (time.time() - start_time) * 1000
        
        return {
            "clause": clause,
            "industry": industry,
            "company_size": company_size,
            "examples": examples,
            "provider": ai_enhancer.provider.get_provider_name(),
            "generation_time_ms": round(generation_time, 2),
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Example generation failed: {str(e)}"
        )


@router.get("/ai/status")
async def ai_status():
    """Get current AI provider status and configuration"""
    from config.settings import settings
    
    return {
        "ai_enabled": settings.ENABLE_AI_ENHANCEMENT,
        "default_provider": settings.AI_PROVIDER,
        "available_providers": ["mistral", "openai", "local"],
        "model": settings.AI_MODEL,
        "temperature": settings.AI_TEMPERATURE,
        "max_tokens": settings.MAX_TOKENS
    }
