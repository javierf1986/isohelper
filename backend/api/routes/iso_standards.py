"""
ISO Standards Management API Routes
Handles uploading, parsing, and managing ISO standard documents
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
from datetime import datetime
import logging

from backend.database.database import get_db
from backend.models.iso_models import ISOStandard, ISOClause, StandardCategory
from backend.api.dependencies import get_current_user
from backend.models.user_models import User
from backend.services.iso_importer import UniversalISOImporter

logger = logging.getLogger(__name__)
router = APIRouter()

class ISOStandardResponse(BaseModel):
    """ISO Standard response model"""
    id: str
    name: str
    iso_number: str
    year: int
    description: Optional[str]
    category: str
    clause_count: int
    is_active: bool
    imported_at: str
    
    class Config:
        from_attributes = True

class ISOStandardDetail(BaseModel):
    """Detailed ISO Standard response with clauses"""
    id: str
    name: str
    iso_number: str
    year: int
    description: Optional[str]
    category: str
    is_active: bool
    imported_at: str
    clauses: List[dict]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ISOStandardResponse])
async def list_iso_standards(
    db: Session = Depends(get_db),
    workspace_id: Optional[str] = Query(None)
):
    """
    List all available ISO standards in the workspace
    (Public endpoint for testing - authentication disabled)
    """
    query = db.query(ISOStandard).filter(ISOStandard.is_active.is_(True))
    
    if workspace_id:
        query = query.filter(ISOStandard.workspace_id == workspace_id)
    
    standards = query.order_by(ISOStandard.imported_at.desc()).all()
    
    # Add clause count to each standard
    result = []
    for std in standards:
        clause_count = db.query(ISOClause).filter(
            ISOClause.standard_id == std.id
        ).count()
        
        # Get imported_at timestamp
        imported_timestamp = datetime.now().isoformat()
        if hasattr(std, 'imported_at') and std.imported_at is not None:
            imported_timestamp = std.imported_at.isoformat()
        
        result.append({
            "id": std.id,
            "name": std.name,
            "iso_number": std.iso_number,
            "year": std.year,
            "description": std.description or std.full_title,
            "category": std.category if isinstance(std.category, str) else std.category.value,
            "clause_count": clause_count,
            "is_active": std.is_active,
            "imported_at": imported_timestamp
        })
    
    return result

@router.get("/{standard_id}", response_model=ISOStandardDetail)
async def get_iso_standard(
    standard_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific ISO standard including all clauses
    (Public endpoint for testing - authentication disabled)
    """
    standard = db.query(ISOStandard).filter(ISOStandard.id == standard_id).first()
    
    if not standard:
        raise HTTPException(status_code=404, detail="ISO standard not found")
    
    # Get all clauses for this standard
    clauses = db.query(ISOClause).filter(
        ISOClause.standard_id == standard_id
    ).order_by(ISOClause.clause_number).all()
    
    clause_list = [
        {
            "id": clause.id,
            "clause_number": clause.clause_number,
            "title": clause.title,
            "content": (clause.content[:200] if clause.content is not None else ""),  # Truncate for list view
            "is_mandatory": clause.is_mandatory
        }
        for clause in clauses
    ]
    
    # Get imported_at timestamp
    imported_timestamp = datetime.now().isoformat()
    if hasattr(standard, 'imported_at') and standard.imported_at is not None:
        imported_timestamp = standard.imported_at.isoformat()
    
    return {
        "id": standard.id,
        "name": standard.name,
        "iso_number": standard.iso_number,
        "year": standard.year,
        "description": standard.description or standard.full_title,
        "category": standard.category if isinstance(standard.category, str) else standard.category.value,
        "is_active": standard.is_active,
        "imported_at": imported_timestamp,
        "clauses": clause_list
    }

@router.post("/upload")
async def upload_iso_standard(
    file: UploadFile = File(...),
    workspace_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Upload and parse an ISO standard document (PDF or DOCX)
    (Public endpoint for testing - authentication disabled)
    
    This endpoint:
    1. Saves the uploaded file
    2. Parses it using UniversalISOImporter to extract structure
    3. Creates ISOStandard and ISOClause records
    4. Returns the parsed standard information
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are supported"
        )
    
    file_path = None
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/iso_standards")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename or "document").suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Processing ISO standard: {file.filename}")
        
        # Parse the ISO standard using UniversalISOImporter
        importer = UniversalISOImporter()
        parsed_result = importer.import_from_file(file_path)
        
        if not parsed_result or 'metadata' not in parsed_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse ISO standard document. Please ensure it's a valid ISO standard format."
            )
        
        metadata = parsed_result['metadata']
        clauses = parsed_result['clauses']
        
        # Map category string to StandardCategory enum
        category_mapping = {
            'QMS': StandardCategory.QUALITY,
            'EMS': StandardCategory.ENVIRONMENTAL,
            'ISMS': StandardCategory.SECURITY,
            'OHSMS': StandardCategory.SAFETY,
            'FSMS': StandardCategory.FOOD_SAFETY,
            'EnMS': StandardCategory.ENERGY,
        }
        category = category_mapping.get(metadata.category, StandardCategory.OTHER)
        
        # Extract ISO number from standard_number (e.g., "ISO 9001" -> "9001")
        iso_number = metadata.standard_number.replace('ISO', '').replace(' ', '').replace('-', '')
        if not iso_number.isdigit():
            # Try to extract just the numeric part
            import re
            match = re.search(r'(\d+)', metadata.standard_number)
            iso_number = match.group(1) if match else "0000"
        
        # Generate standard ID (e.g., "ISO-9001-2015")
        standard_id = f"ISO-{iso_number}-{metadata.year}"
        
        # Check if standard already exists
        existing = db.query(ISOStandard).filter(
            ISOStandard.id == standard_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"ISO standard {metadata.standard_number} version {metadata.year} already exists in the database"
            )
        
        # Create ISOStandard record
        new_standard = ISOStandard(
            id=standard_id,
            name=metadata.standard_number,
            iso_number=iso_number,
            year=int(metadata.year),
            full_title=metadata.title,
            description=metadata.title,
            category=category.value,
            is_active=True,
            imported_at=datetime.now()
        )
        
        db.add(new_standard)
        db.flush()  # Get the ID before committing
        
        logger.info(f"Created ISO standard: {new_standard.name} v{new_standard.version}")
        
        # Create ISOClause records
        clause_count = 0
        for clause_data in clauses:
            new_clause = ISOClause(
                id=str(uuid.uuid4()),
                standard_id=new_standard.id,
                clause_number=clause_data.clause_number,
                title=clause_data.title,
                content=clause_data.content,
                parent_clause_id=None,  # Will be linked in post-processing if needed
                level=clause_data.level,
                is_mandatory=clause_data.is_requirement,
                created_at=datetime.now()
            )
            db.add(new_clause)
            clause_count += 1
        
        db.commit()
        
        logger.info(f"Successfully imported {clause_count} clauses")
        
        # Clean up uploaded file
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Could not delete temporary file: {e}")
        
        return {
            "success": True,
            "message": f"Successfully uploaded and parsed {metadata.standard_number}",
            "standard": {
                "id": new_standard.id,
                "name": new_standard.name,
                "iso_number": new_standard.iso_number,
                "year": new_standard.year,
                "category": category.value,
                "clause_count": clause_count
            },
            "statistics": parsed_result.get('statistics', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing ISO standard: {str(e)}", exc_info=True)
        
        # Clean up uploaded file on error
        try:
            if file_path is not None and file_path.exists():
                file_path.unlink()
        except:
            pass
            
        raise HTTPException(
            status_code=500,
            detail=f"Error processing ISO standard: {str(e)}"
        )

@router.delete("/{standard_id}")
async def delete_iso_standard(
    standard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an ISO standard and all its clauses
    """
    standard = db.query(ISOStandard).filter(ISOStandard.id == standard_id).first()
    
    if not standard:
        raise HTTPException(status_code=404, detail="ISO standard not found")
    
    # Delete all clauses first
    db.query(ISOClause).filter(ISOClause.standard_id == standard_id).delete()
    
    # Delete the standard
    db.delete(standard)
    db.commit()
    
    return {"success": True, "message": f"Deleted ISO standard {standard.name}"}

@router.patch("/{standard_id}/toggle-active")
async def toggle_iso_standard_active(
    standard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle the active status of an ISO standard
    """
    standard = db.query(ISOStandard).filter(ISOStandard.id == standard_id).first()
    
    if not standard:
        raise HTTPException(status_code=404, detail="ISO standard not found")
    
    # Get current status and toggle it
    current_status = bool(standard.is_active)
    new_status = not current_status
    
    # Update the active status
    db.query(ISOStandard).filter(ISOStandard.id == standard_id).update(
        {"is_active": new_status}
    )
    db.commit()
    db.refresh(standard)
    
    return {
        "success": True,
        "message": f"ISO standard {standard.name} is now {'active' if new_status else 'inactive'}",
        "is_active": new_status
    }
