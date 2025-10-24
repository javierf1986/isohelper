"""
Gap Analysis API Routes
Endpoints for AI-powered compliance gap analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import shutil

from backend.database.database import get_db
from backend.api.dependencies import get_current_user
from backend.models.gap_models import (
    GapAnalysis, Gap, RoadmapItem, AnalysisStatus, GapSeverity, RoadmapItemStatus
)
from backend.services.gap_analysis_service import GapAnalysisService
from backend.services.roadmap_generator import RoadmapGeneratorService
from backend.services.document_parser import DocumentParser


router = APIRouter(prefix="/api/v1/gap-analysis")


# Pydantic Models
class AnalysisCreateRequest(BaseModel):
    document_name: str
    iso_standard_id: str
    workspace_id: str


class AnalysisResponse(BaseModel):
    id: str
    analysis_number: str
    workspace_id: str
    document_name: str
    document_type: Optional[str]
    iso_standard_id: str
    status: str
    progress_percent: int
    total_requirements: int
    total_gaps: int
    critical_gaps: int
    major_gaps: int
    minor_gaps: int
    observations: int
    compliance_score: Optional[float]
    coverage_percent: Optional[float]
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class GapResponse(BaseModel):
    id: str
    analysis_id: str
    iso_clause: str
    iso_clause_title: Optional[str]
    severity: str
    gap_description: str
    current_state: Optional[str]
    required_state: Optional[str]
    impact_description: Optional[str]
    risk_level: Optional[str]
    evidence_score: Optional[float]
    ai_confidence: Optional[float]
    recommended_action: Optional[str]
    implementation_effort: Optional[str]
    priority_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapItemResponse(BaseModel):
    id: str
    item_number: Optional[str]
    title: str
    description: Optional[str]
    priority: Optional[int]
    impact: Optional[str]
    effort: Optional[str]
    estimated_cost: Optional[float]
    estimated_hours: Optional[float]
    estimated_duration_days: Optional[int]
    status: str
    progress_percent: int
    milestone: Optional[str]
    planned_start_date: Optional[datetime]
    planned_completion_date: Optional[datetime]
    gap_count: int
    deliverables: Optional[List[str]]

    class Config:
        from_attributes = True


class RoadmapUpdateRequest(BaseModel):
    status: str
    progress_percent: int
    notes: Optional[str] = None


# Endpoints

@router.post("/upload", response_model=AnalysisResponse, status_code=201)
async def upload_document_for_analysis(
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    iso_standard_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a document for gap analysis
    
    Supports PDF, DOCX, and TXT files up to 50MB
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.pdf', '.docx', '.txt', '.doc']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension}. Supported: PDF, DOCX, TXT"
        )
    
    # Create upload directory
    upload_dir = os.path.join("uploads", "gap_analysis", workspace_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
    
    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create analysis record
    try:
        analysis = GapAnalysisService.create_analysis(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user['user_id'],
            document_name=file.filename,
            document_path=file_path,
            iso_standard_id=iso_standard_id
        )
        
        return AnalysisResponse.model_validate(analysis)
        
    except Exception as e:
        # Clean up file if analysis creation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to create analysis: {str(e)}")


@router.post("/{analysis_id}/analyze", response_model=AnalysisResponse)
async def start_gap_analysis(
    analysis_id: str,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Start AI-powered gap analysis
    
    This is a long-running operation that:
    1. Parses the uploaded document
    2. Analyzes each ISO clause for compliance gaps
    3. Generates gap records with severity and recommendations
    """
    # Get analysis
    analysis = GapAnalysisService.get_analysis(db, analysis_id, workspace_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != AnalysisStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis already {analysis.status.value}. Cannot restart."
        )
    
    try:
        # Parse document
        parse_result = GapAnalysisService.parse_document(
            db=db,
            analysis_id=analysis_id,
            document_path=analysis.document_path
        )
        
        # Validate content
        DocumentParser.validate_content(parse_result['text'], min_words=100)
        
        # Perform AI analysis
        gaps = GapAnalysisService.analyze_gaps_with_ai(
            db=db,
            analysis_id=analysis_id,
            openai_api_key=None  # Uses env variable
        )
        
        # Generate roadmap
        RoadmapGeneratorService.generate_roadmap(
            db=db,
            analysis_id=analysis_id,
            workspace_id=workspace_id
        )
        
        # Refresh analysis
        db.refresh(analysis)
        return AnalysisResponse.model_validate(analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/", response_model=List[AnalysisResponse])
def list_gap_analyses(
    workspace_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all gap analyses for a workspace"""
    analyses = GapAnalysisService.get_workspace_analyses(
        db=db,
        workspace_id=workspace_id,
        limit=limit
    )
    
    return [AnalysisResponse.model_validate(a) for a in analyses]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_gap_analysis(
    analysis_id: str,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get gap analysis details"""
    analysis = GapAnalysisService.get_analysis(db, analysis_id, workspace_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisResponse.model_validate(analysis)


@router.get("/{analysis_id}/gaps", response_model=List[GapResponse])
def get_analysis_gaps(
    analysis_id: str,
    workspace_id: str = Query(...),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all gaps for an analysis
    
    Optional filter by severity: critical, major, minor, observation
    """
    gaps = GapAnalysisService.get_gaps(db, analysis_id, workspace_id)
    
    # Filter by severity if provided
    if severity:
        try:
            severity_enum = GapSeverity[severity.upper()]
            gaps = [g for g in gaps if g.severity == severity_enum]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    
    return [GapResponse.model_validate(g) for g in gaps]


@router.get("/{analysis_id}/roadmap", response_model=List[RoadmapItemResponse])
def get_analysis_roadmap(
    analysis_id: str,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get implementation roadmap for an analysis"""
    roadmap_items = RoadmapGeneratorService.get_roadmap(
        db=db,
        analysis_id=analysis_id,
        workspace_id=workspace_id
    )
    
    return [RoadmapItemResponse.model_validate(item) for item in roadmap_items]


@router.get("/{analysis_id}/roadmap/statistics")
def get_roadmap_statistics(
    analysis_id: str,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get summary statistics for roadmap"""
    stats = RoadmapGeneratorService.get_roadmap_statistics(
        db=db,
        analysis_id=analysis_id,
        workspace_id=workspace_id
    )
    
    return stats


@router.put("/roadmap/{item_id}", response_model=RoadmapItemResponse)
def update_roadmap_item(
    item_id: str,
    update: RoadmapUpdateRequest,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update progress on a roadmap item"""
    
    # Validate status
    try:
        status_enum = RoadmapItemStatus[update.status.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {update.status}")
    
    try:
        item = RoadmapGeneratorService.update_roadmap_progress(
            db=db,
            roadmap_item_id=item_id,
            workspace_id=workspace_id,
            status=status_enum,
            progress_percent=update.progress_percent,
            notes=update.notes
        )
        
        return RoadmapItemResponse.model_validate(item)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.delete("/{analysis_id}")
def delete_gap_analysis(
    analysis_id: str,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a gap analysis and all related data"""
    analysis = GapAnalysisService.get_analysis(db, analysis_id, workspace_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Delete uploaded file
    if analysis.document_path and os.path.exists(analysis.document_path):
        try:
            os.remove(analysis.document_path)
        except Exception as e:
            print(f"Warning: Could not delete file: {str(e)}")
    
    # Delete from database (cascades to gaps and roadmap)
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}


@router.get("/{analysis_id}/export/report")
def export_gap_report(
    analysis_id: str,
    workspace_id: str = Query(...),
    format: str = Query("json", regex="^(json|pdf|excel)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export gap analysis report
    
    Formats: json, pdf (future), excel (future)
    """
    analysis = GapAnalysisService.get_analysis(db, analysis_id, workspace_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    gaps = GapAnalysisService.get_gaps(db, analysis_id, workspace_id)
    roadmap = RoadmapGeneratorService.get_roadmap(db, analysis_id, workspace_id)
    
    # For now, return JSON (PDF/Excel export can be added later)
    if format == "json":
        return {
            "analysis": AnalysisResponse.model_validate(analysis).model_dump(),
            "gaps": [GapResponse.model_validate(g).model_dump() for g in gaps],
            "roadmap": [RoadmapItemResponse.model_validate(r).model_dump() for r in roadmap]
        }
    else:
        raise HTTPException(status_code=501, detail=f"Format '{format}' not yet implemented")
