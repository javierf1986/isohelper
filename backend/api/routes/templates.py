"""
Template Management API Routes
Provides ISO standards, clauses, and template information
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.iso_models import ISOStandard, ISOClause

router = APIRouter()

# Response Models
class ISOStandardResponse(BaseModel):
    """ISO Standard response model for frontend"""
    id: str
    name: str
    version: str
    description: str | None
    
    class Config:
        from_attributes = True

class ClauseResponse(BaseModel):
    """Clause response model for frontend"""
    id: str
    number: str
    title: str
    description: str
    required: bool
    
    class Config:
        from_attributes = True

@router.get("/standards", response_model=List[ISOStandardResponse])
async def get_iso_standards(db: Session = Depends(get_db)):
    """
    Get all available ISO standards
    Returns list of standards with basic info for the wizard
    """
    standards = db.query(ISOStandard).filter(ISOStandard.is_active == True).all()
    
    # Transform to match frontend interface
    return [
        {
            "id": std.id,
            "name": std.name,
            "version": std.version,
            "description": std.description or std.full_title
        }
        for std in standards
    ]

@router.get("/{standard_id}/clauses", response_model=List[ClauseResponse])
async def get_clauses_by_standard(
    standard_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all clauses for a specific ISO standard
    Returns simplified clause list for the wizard checkbox selection
    """
    # Verify standard exists
    standard = db.query(ISOStandard).filter(ISOStandard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="ISO standard not found")
    
    # Get all clauses for this standard, ordered by clause_number
    clauses = db.query(ISOClause).filter(
        ISOClause.standard_id == standard_id
    ).order_by(ISOClause.clause_number).all()
    
    # Transform to match frontend interface
    result = []
    for clause in clauses:
        # Get content safely
        content = str(clause.content) if clause.content is not None else ""
        description = content[:200] + "..." if len(content) > 200 else content
        result.append({
            "id": str(clause.id),
            "number": str(clause.clause_number),
            "title": str(clause.title),
            "description": description,
            "required": bool(clause.is_mandatory)
        })
    
    return result

# Legacy endpoints for backward compatibility
class TemplateMetadata(BaseModel):
    """Template metadata model"""
    template_id: str
    name: str
    iso_clause: str
    description: str
    version: str
    language: str

@router.get("/", response_model=List[TemplateMetadata])
async def list_templates(clause: Optional[str] = None, language: str = "en"):
    """
    List available ISO 9001 templates (legacy endpoint)
    """
    return []

@router.get("/template/{template_id}")
async def get_template(template_id: str):
    """Retrieve a specific template by ID (legacy endpoint)"""
    raise HTTPException(status_code=404, detail="Template not found")

@router.post("/template")
async def create_template(template: dict):
    """Create a new custom template (legacy endpoint)"""
    return {"message": "Template creation not yet implemented"}
