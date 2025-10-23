"""
Artifact Management API Routes
Phase 4.3: REST endpoints for NC, CA, Audits
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import case
from pydantic import BaseModel

from backend.database.session import get_db
from backend.services.auth_service import get_current_user
from backend.models.user import User
from backend.models.artifact_models import (
    NCStatus, NCSeverity, CAStatus, AuditType, AuditStatus
)
from backend.services.artifact_service import ArtifactService


router = APIRouter(prefix="/artifacts", tags=["artifacts"])


# ===== Request/Response Models =====

class NCCreateRequest(BaseModel):
    title: str
    description: str
    severity: NCSeverity
    detected_date: date
    category: Optional[str] = None
    detected_location: Optional[str] = None
    iso_standard_id: Optional[str] = None
    iso_clause_number: Optional[str] = None


class NCUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[NCSeverity] = None
    detected_date: Optional[date] = None
    category: Optional[str] = None
    detected_location: Optional[str] = None
    iso_standard_id: Optional[str] = None
    iso_clause_number: Optional[str] = None
    immediate_actions: Optional[str] = None
    target_closure_date: Optional[date] = None


class NCResponse(BaseModel):
    id: str
    nc_number: str
    title: str
    description: str
    severity: str
    status: str
    detected_date: date
    category: Optional[str]
    reported_by: str
    created_at: str
    
    class Config:
        from_attributes = True


class NCDetailResponse(BaseModel):
    id: str
    nc_number: str
    title: str
    description: str
    severity: str
    status: str
    detected_date: date
    category: Optional[str]
    detected_location: Optional[str]
    reported_by: str
    iso_standard_id: Optional[str]
    iso_clause_number: Optional[str]
    root_cause: Optional[str]
    contributing_factors: Optional[str]
    immediate_actions: Optional[str]
    ai_analysis: Optional[str]
    target_closure_date: Optional[date]
    actual_closure_date: Optional[date]
    verified_by: Optional[str]
    verified_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class CACreateRequest(BaseModel):
    title: str
    description: str
    action_plan: str
    assigned_to: str
    planned_start_date: date
    planned_completion_date: date
    nc_id: Optional[str] = None
    priority: str = "medium"


class CAUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    action_plan: Optional[str] = None
    assigned_to: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_completion_date: Optional[date] = None
    nc_id: Optional[str] = None
    priority: Optional[str] = None


class CAResponse(BaseModel):
    id: str
    ca_number: str
    title: str
    description: str
    status: str
    priority: str
    assigned_to: str
    planned_completion_date: date
    nc_id: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class CADetailResponse(BaseModel):
    id: str
    ca_number: str
    title: str
    description: str
    action_plan: str
    status: str
    priority: str
    assigned_to: str
    nc_id: Optional[str]
    nc_number: Optional[str]
    planned_start_date: date
    planned_completion_date: date
    actual_start_date: Optional[date]
    actual_completion_date: Optional[date]
    progress_updates: Optional[str]
    resources_required: Optional[str]
    is_effective: Optional[bool]
    effectiveness_results: Optional[str]
    effectiveness_check_date: Optional[date]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AuditCreateRequest(BaseModel):
    title: str
    audit_type: AuditType
    scope_description: str
    planned_date: date
    iso_standard_id: Optional[str] = None


class AuditUpdateRequest(BaseModel):
    title: Optional[str] = None
    audit_type: Optional[AuditType] = None
    scope_description: Optional[str] = None
    planned_date: Optional[date] = None
    iso_standard_id: Optional[str] = None


class AuditResponse(BaseModel):
    id: str
    audit_number: str
    title: str
    audit_type: str
    status: str
    planned_date: date
    lead_auditor: str
    major_findings: int
    minor_findings: int
    created_at: str
    
    class Config:
        from_attributes = True


class AuditDetailResponse(BaseModel):
    id: str
    audit_number: str
    title: str
    audit_type: str
    status: str
    scope_description: str
    planned_date: date
    actual_date: Optional[date]
    lead_auditor: str
    team_members: Optional[str]
    major_findings: int
    minor_findings: int
    observations: int
    findings_summary: Optional[str]
    recommendations: Optional[str]
    follow_up_required: bool
    iso_standard_id: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ManagementReviewDetailResponse(BaseModel):
    id: str
    review_number: str
    review_date: date
    attendees: Optional[str]
    agenda: Optional[str]
    minutes: Optional[str]
    decisions: Optional[str]
    action_items: Optional[str]
    next_review_date: Optional[date]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class TrainingRecordDetailResponse(BaseModel):
    id: str
    record_number: str
    employee_id: str
    training_title: str
    training_date: date
    trainer_name: Optional[str]
    training_hours: Optional[float]
    training_type: Optional[str]
    competency_area: Optional[str]
    passed: bool
    score: Optional[int]
    certificate_number: Optional[str]
    expiry_date: Optional[date]
    notes: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class CustomerComplaintDetailResponse(BaseModel):
    id: str
    complaint_number: str
    complaint_title: str
    complaint_description: str
    customer_name: str
    received_date: date
    complaint_source: str
    product_service: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    root_cause: Optional[str]
    resolution: Optional[str]
    resolution_date: Optional[date]
    resolution_target_date: Optional[date]
    customer_feedback: Optional[str]
    preventive_measures: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# ===== Non-Conformity Endpoints =====

@router.post("/nc", response_model=NCResponse, status_code=status.HTTP_201_CREATED)
async def create_nc(
    request: NCCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Non-Conformity"""
    try:
        nc = ArtifactService.create_nc(
            db=db,
            workspace_id=current_user.workspace_id,
            title=request.title,
            description=request.description,
            severity=request.severity,
            reported_by=current_user.id,
            detected_date=request.detected_date,
            category=request.category,
            detected_location=request.detected_location,
            iso_standard_id=request.iso_standard_id,
            iso_clause_number=request.iso_clause_number
        )
        
        return NCResponse(
            id=nc.id,
            nc_number=nc.nc_number,
            title=nc.title,
            description=nc.description,
            severity=nc.severity.value,
            status=nc.status.value,
            detected_date=nc.detected_date,
            category=nc.category,
            reported_by=nc.reported_by,
            created_at=nc.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nc", response_model=List[NCResponse])
async def list_ncs(
    status: Optional[NCStatus] = None,
    severity: Optional[NCSeverity] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List Non-Conformities with filters"""
    ncs = ArtifactService.get_workspace_ncs(
        db=db,
        workspace_id=current_user.workspace_id,
        status=status,
        severity=severity,
        limit=limit
    )
    
    return [
        NCResponse(
            id=nc.id,
            nc_number=nc.nc_number,
            title=nc.title,
            description=nc.description,
            severity=nc.severity.value,
            status=nc.status.value,
            detected_date=nc.detected_date,
            category=nc.category,
            reported_by=nc.reported_by,
            created_at=nc.created_at.isoformat()
        )
        for nc in ncs
    ]


@router.get("/nc/{nc_id}", response_model=NCDetailResponse)
async def get_nc(
    nc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific Non-Conformity by ID"""
    nc = ArtifactService.get_nc_by_id(
        db=db,
        nc_id=nc_id,
        workspace_id=current_user.workspace_id
    )
    
    if not nc:
        raise HTTPException(status_code=404, detail="Non-Conformity not found")
    
    return NCDetailResponse(
        id=nc.id,
        nc_number=nc.nc_number,
        title=nc.title,
        description=nc.description,
        severity=nc.severity.value,
        status=nc.status.value,
        detected_date=nc.detected_date,
        category=nc.category,
        detected_location=nc.detected_location,
        reported_by=nc.reported_by,
        iso_standard_id=nc.iso_standard_id,
        iso_clause_number=nc.iso_clause_number,
        root_cause=nc.root_cause,
        contributing_factors=nc.contributing_factors,
        immediate_actions=nc.immediate_actions,
        ai_analysis=nc.ai_analysis,
        target_closure_date=nc.target_closure_date,
        actual_closure_date=nc.actual_closure_date,
        verified_by=nc.verified_by,
        verified_at=nc.verified_at.isoformat() if nc.verified_at else None,
        created_at=nc.created_at.isoformat(),
        updated_at=nc.updated_at.isoformat()
    )


@router.put("/nc/{nc_id}", response_model=NCDetailResponse)
async def update_nc(
    nc_id: str,
    request: NCUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a Non-Conformity"""
    try:
        # Build update dict from request
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        if request.severity is not None:
            update_data['severity'] = request.severity
        if request.detected_date is not None:
            update_data['detected_date'] = request.detected_date
        if request.category is not None:
            update_data['category'] = request.category
        if request.detected_location is not None:
            update_data['detected_location'] = request.detected_location
        if request.iso_standard_id is not None:
            update_data['iso_standard_id'] = request.iso_standard_id
        if request.iso_clause_number is not None:
            update_data['iso_clause_number'] = request.iso_clause_number
        if request.immediate_actions is not None:
            update_data['immediate_actions'] = request.immediate_actions
        if request.target_closure_date is not None:
            update_data['target_closure_date'] = request.target_closure_date
        
        nc = ArtifactService.update_nc(
            db=db,
            nc_id=nc_id,
            workspace_id=current_user.workspace_id,
            **update_data
        )
        
        return NCDetailResponse(
            id=nc.id,
            nc_number=nc.nc_number,
            title=nc.title,
            description=nc.description,
            severity=nc.severity.value,
            status=nc.status.value,
            detected_date=nc.detected_date,
            category=nc.category,
            detected_location=nc.detected_location,
            reported_by=nc.reported_by,
            iso_standard_id=nc.iso_standard_id,
            iso_clause_number=nc.iso_clause_number,
            root_cause=nc.root_cause,
            contributing_factors=nc.contributing_factors,
            immediate_actions=nc.immediate_actions,
            ai_analysis=nc.ai_analysis,
            target_closure_date=nc.target_closure_date,
            actual_closure_date=nc.actual_closure_date,
            verified_by=nc.verified_by,
            verified_at=nc.verified_at.isoformat() if nc.verified_at else None,
            created_at=nc.created_at.isoformat(),
            updated_at=nc.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/nc/{nc_id}/status")
async def update_nc_status(
    nc_id: str,
    new_status: NCStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update NC status"""
    try:
        nc = ArtifactService.update_nc_status(
            db=db,
            nc_id=nc_id,
            status=new_status,
            user_id=current_user.id
        )
        return {"message": "NC status updated", "nc_number": nc.nc_number, "status": nc.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/nc/{nc_id}/root-cause")
async def add_root_cause(
    nc_id: str,
    root_cause: str,
    contributing_factors: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add root cause analysis to NC"""
    try:
        nc = ArtifactService.add_root_cause(
            db=db,
            nc_id=nc_id,
            root_cause=root_cause,
            contributing_factors=contributing_factors
        )
        return {"message": "Root cause added", "nc_number": nc.nc_number}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/nc/{nc_id}")
async def delete_nc(
    nc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a Non-Conformity"""
    try:
        ArtifactService.delete_nc(
            db=db,
            nc_id=nc_id,
            workspace_id=current_user.workspace_id
        )
        return {"message": "Non-Conformity deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Corrective Action Endpoints =====

@router.post("/ca", response_model=CAResponse, status_code=status.HTTP_201_CREATED)
async def create_ca(
    request: CACreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Corrective Action"""
    try:
        ca = ArtifactService.create_ca(
            db=db,
            workspace_id=current_user.workspace_id,
            title=request.title,
            description=request.description,
            action_plan=request.action_plan,
            assigned_to=request.assigned_to,
            planned_start_date=request.planned_start_date,
            planned_completion_date=request.planned_completion_date,
            nc_id=request.nc_id,
            priority=request.priority
        )
        
        return CAResponse(
            id=ca.id,
            ca_number=ca.ca_number,
            title=ca.title,
            description=ca.description,
            status=ca.status.value,
            priority=ca.priority,
            assigned_to=ca.assigned_to,
            planned_completion_date=ca.planned_completion_date,
            nc_id=ca.nc_id,
            created_at=ca.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/ca/{ca_id}/status")
async def update_ca_status(
    ca_id: str,
    new_status: CAStatus,
    actual_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update CA status"""
    try:
        ca = ArtifactService.update_ca_status(
            db=db,
            ca_id=ca_id,
            status=new_status,
            actual_date=actual_date
        )
        return {"message": "CA status updated", "ca_number": ca.ca_number, "status": ca.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/ca/{ca_id}/verify")
async def verify_ca_effectiveness(
    ca_id: str,
    is_effective: bool,
    effectiveness_results: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify CA effectiveness"""
    try:
        ca = ArtifactService.verify_ca_effectiveness(
            db=db,
            ca_id=ca_id,
            is_effective=is_effective,
            effectiveness_results=effectiveness_results
        )
        return {
            "message": "CA effectiveness verified",
            "ca_number": ca.ca_number,
            "is_effective": ca.is_effective
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/ca/{ca_id}")
async def delete_ca(
    ca_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a Corrective Action"""
    try:
        ArtifactService.delete_ca(
            db=db,
            ca_id=ca_id,
            workspace_id=current_user.workspace_id
        )
        return {"message": "Corrective Action deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/ca", response_model=List[CAResponse])
async def list_cas(
    status: Optional[CAStatus] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List Corrective Actions with filters"""
    cas = ArtifactService.get_workspace_cas(
        db=db,
        workspace_id=current_user.workspace_id,
        status=status,
        priority=priority,
        limit=limit
    )
    
    return [
        CAResponse(
            id=ca.id,
            ca_number=ca.ca_number,
            title=ca.title,
            description=ca.description,
            status=ca.status.value,
            priority=ca.priority,
            assigned_to=ca.assigned_to,
            planned_completion_date=ca.planned_completion_date,
            nc_id=ca.nc_id,
            created_at=ca.created_at.isoformat()
        ) for ca in cas
    ]


@router.get("/ca/{ca_id}", response_model=CADetailResponse)
async def get_ca(
    ca_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific Corrective Action by ID"""
    ca = ArtifactService.get_ca_by_id(
        db=db,
        ca_id=ca_id,
        workspace_id=current_user.workspace_id
    )
    
    if not ca:
        raise HTTPException(status_code=404, detail="Corrective Action not found")
    
    # Get NC number if linked
    nc_number = None
    if ca.nc_id:
        from backend.models.artifact_models import NonConformity
        nc = db.query(NonConformity).filter(NonConformity.id == ca.nc_id).first()
        if nc:
            nc_number = nc.nc_number
    
    return CADetailResponse(
        id=ca.id,
        ca_number=ca.ca_number,
        title=ca.title,
        description=ca.description,
        action_plan=ca.action_plan,
        status=ca.status.value,
        priority=ca.priority,
        assigned_to=ca.assigned_to,
        nc_id=ca.nc_id,
        nc_number=nc_number,
        planned_start_date=ca.planned_start_date,
        planned_completion_date=ca.planned_completion_date,
        actual_start_date=ca.actual_start_date,
        actual_completion_date=ca.actual_completion_date,
        progress_updates=ca.progress_updates,
        resources_required=ca.resources_required,
        is_effective=ca.is_effective,
        effectiveness_results=ca.effectiveness_results,
        effectiveness_check_date=ca.effectiveness_check_date,
        created_at=ca.created_at.isoformat(),
        updated_at=ca.updated_at.isoformat()
    )


@router.put("/ca/{ca_id}", response_model=CADetailResponse)
async def update_ca(
    ca_id: str,
    request: CAUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a Corrective Action"""
    # Build update dict from request
    update_data = {}
    if request.title is not None:
        update_data['title'] = request.title
    if request.description is not None:
        update_data['description'] = request.description
    if request.action_plan is not None:
        update_data['action_plan'] = request.action_plan
    if request.assigned_to is not None:
        update_data['assigned_to'] = request.assigned_to
    if request.planned_start_date is not None:
        update_data['planned_start_date'] = request.planned_start_date
    if request.planned_completion_date is not None:
        update_data['planned_completion_date'] = request.planned_completion_date
    if request.nc_id is not None:
        update_data['nc_id'] = request.nc_id
    if request.priority is not None:
        update_data['priority'] = request.priority
    
    try:
        ca = ArtifactService.update_ca(
            db=db,
            ca_id=ca_id,
            workspace_id=current_user.workspace_id,
            **update_data
        )
        
        # Get NC number if linked
        nc_number = None
        if ca.nc_id:
            from backend.models.artifact_models import NonConformity
            nc = db.query(NonConformity).filter(NonConformity.id == ca.nc_id).first()
            if nc:
                nc_number = nc.nc_number
        
        return CADetailResponse(
            id=ca.id,
            ca_number=ca.ca_number,
            title=ca.title,
            description=ca.description,
            action_plan=ca.action_plan,
            status=ca.status.value,
            priority=ca.priority,
            assigned_to=ca.assigned_to,
            nc_id=ca.nc_id,
            nc_number=nc_number,
            planned_start_date=ca.planned_start_date,
            planned_completion_date=ca.planned_completion_date,
            actual_start_date=ca.actual_start_date,
            actual_completion_date=ca.actual_completion_date,
            progress_updates=ca.progress_updates,
            resources_required=ca.resources_required,
            is_effective=ca.is_effective,
            effectiveness_results=ca.effectiveness_results,
            effectiveness_check_date=ca.effectiveness_check_date,
            created_at=ca.created_at.isoformat(),
            updated_at=ca.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Internal Audit Endpoints =====

@router.post("/audit", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    request: AuditCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Internal Audit"""
    try:
        audit = ArtifactService.create_audit(
            db=db,
            workspace_id=current_user.workspace_id,
            title=request.title,
            audit_type=request.audit_type,
            scope_description=request.scope_description,
            planned_date=request.planned_date,
            lead_auditor=current_user.id,
            iso_standard_id=request.iso_standard_id
        )
        
        return AuditResponse(
            id=audit.id,
            audit_number=audit.audit_number,
            title=audit.title,
            audit_type=audit.audit_type.value,
            status=audit.status.value,
            planned_date=audit.planned_date,
            lead_auditor=audit.lead_auditor,
            major_findings=audit.major_findings,
            minor_findings=audit.minor_findings,
            created_at=audit.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/audit/{audit_id}/complete")
async def complete_audit(
    audit_id: str,
    actual_date: date,
    major_findings: int,
    minor_findings: int,
    observations: int,
    findings_summary: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an audit with findings"""
    try:
        audit = ArtifactService.complete_audit(
            db=db,
            audit_id=audit_id,
            actual_date=actual_date,
            major_findings=major_findings,
            minor_findings=minor_findings,
            observations=observations,
            findings_summary=findings_summary
        )
        return {
            "message": "Audit completed",
            "audit_number": audit.audit_number,
            "status": audit.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/audit/{audit_id}")
async def delete_audit(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an Internal Audit"""
    try:
        ArtifactService.delete_audit(
            db=db,
            audit_id=audit_id,
            workspace_id=current_user.workspace_id
        )
        return {"message": "Internal Audit deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/audit", response_model=List[AuditResponse])
async def list_audits(
    status: Optional[AuditStatus] = None,
    audit_type: Optional[AuditType] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List Internal Audits with filters"""
    audits = ArtifactService.get_workspace_audits(
        db=db,
        workspace_id=current_user.workspace_id,
        status=status,
        audit_type=audit_type,
        limit=limit
    )
    
    return [
        AuditResponse(
            id=audit.id,
            audit_number=audit.audit_number,
            title=audit.title,
            audit_type=audit.audit_type.value,
            status=audit.status.value,
            planned_date=audit.planned_date,
            lead_auditor=audit.lead_auditor,
            major_findings=audit.major_findings,
            minor_findings=audit.minor_findings,
            created_at=audit.created_at.isoformat()
        ) for audit in audits
    ]


@router.get("/audit/{audit_id}", response_model=AuditDetailResponse)
async def get_audit(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific Internal Audit by ID"""
    audit = ArtifactService.get_audit_by_id(
        db=db,
        audit_id=audit_id,
        workspace_id=current_user.workspace_id
    )
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return AuditDetailResponse(
        id=audit.id,
        audit_number=audit.audit_number,
        title=audit.title,
        audit_type=audit.audit_type.value,
        status=audit.status.value,
        scope_description=audit.scope_description,
        planned_date=audit.planned_date,
        actual_date=audit.actual_date,
        lead_auditor=audit.lead_auditor,
        team_members=audit.team_members,
        major_findings=audit.major_findings,
        minor_findings=audit.minor_findings,
        observations=audit.observations,
        findings_summary=audit.findings_summary,
        recommendations=audit.recommendations,
        follow_up_required=audit.follow_up_required,
        iso_standard_id=audit.iso_standard_id,
        created_at=audit.created_at.isoformat(),
        updated_at=audit.updated_at.isoformat()
    )


@router.put("/audit/{audit_id}", response_model=AuditDetailResponse)
async def update_audit(
    audit_id: str,
    request: AuditUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an Internal Audit"""
    # Build update dict from request
    update_data = {}
    if request.title is not None:
        update_data['title'] = request.title
    if request.audit_type is not None:
        update_data['audit_type'] = request.audit_type
    if request.scope_description is not None:
        update_data['scope_description'] = request.scope_description
    if request.planned_date is not None:
        update_data['planned_date'] = request.planned_date
    if request.iso_standard_id is not None:
        update_data['iso_standard_id'] = request.iso_standard_id
    
    try:
        audit = ArtifactService.update_audit(
            db=db,
            audit_id=audit_id,
            workspace_id=current_user.workspace_id,
            **update_data
        )
        
        return AuditDetailResponse(
            id=audit.id,
            audit_number=audit.audit_number,
            title=audit.title,
            audit_type=audit.audit_type.value,
            status=audit.status.value,
            scope_description=audit.scope_description,
            planned_date=audit.planned_date,
            actual_date=audit.actual_date,
            lead_auditor=audit.lead_auditor,
            team_members=audit.team_members,
            major_findings=audit.major_findings,
            minor_findings=audit.minor_findings,
            observations=audit.observations,
            findings_summary=audit.findings_summary,
            recommendations=audit.recommendations,
            follow_up_required=audit.follow_up_required,
            iso_standard_id=audit.iso_standard_id,
            created_at=audit.created_at.isoformat(),
            updated_at=audit.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Analytics Endpoints =====

@router.get("/analytics/nc-statistics")
async def get_nc_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get NC statistics"""
    stats = ArtifactService.get_nc_statistics(
        db=db,
        workspace_id=current_user.workspace_id,
        start_date=start_date,
        end_date=end_date
    )
    return stats


@router.get("/analytics/ca-effectiveness")
async def get_ca_effectiveness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CA effectiveness rate"""
    effectiveness = ArtifactService.get_ca_effectiveness_rate(
        db=db,
        workspace_id=current_user.workspace_id
    )
    return effectiveness


@router.get("/analytics/audit-summary")
async def get_audit_summary(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit summary"""
    summary = ArtifactService.get_audit_summary(
        db=db,
        workspace_id=current_user.workspace_id,
        year=year
    )
    return summary


# ===== Management Review Endpoints =====

class ManagementReviewCreateRequest(BaseModel):
    review_date: date
    attendees: Optional[str] = None
    agenda: Optional[str] = None
    minutes: Optional[str] = None
    decisions: Optional[str] = None
    action_items: Optional[str] = None
    next_review_date: Optional[date] = None


class ManagementReviewUpdateRequest(BaseModel):
    review_date: Optional[date] = None
    attendees: Optional[str] = None
    agenda: Optional[str] = None
    minutes: Optional[str] = None
    decisions: Optional[str] = None
    action_items: Optional[str] = None
    next_review_date: Optional[date] = None


class ManagementReviewResponse(BaseModel):
    id: str
    review_number: str
    review_date: date
    attendees: Optional[str]
    agenda: Optional[str]
    minutes: Optional[str]
    decisions: Optional[str]
    action_items: Optional[str]
    next_review_date: Optional[date]
    created_by: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/management-review", response_model=ManagementReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_management_review(
    request: ManagementReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new management review"""
    from datetime import datetime
    review = ArtifactService.create_management_review(
        db=db,
        workspace_id=current_user.workspace_id,
        review_date=datetime.combine(request.review_date, datetime.min.time()),
        attendees=request.attendees,
        agenda=request.agenda,
        minutes=request.minutes,
        decisions=request.decisions,
        action_items=request.action_items,
        next_review_date=datetime.combine(request.next_review_date, datetime.min.time()) if request.next_review_date else None,
        created_by=current_user.id
    )
    return review


@router.get("/management-review", response_model=List[ManagementReviewResponse])
async def list_management_reviews(
    year: Optional[int] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List management reviews for workspace"""
    reviews = ArtifactService.get_workspace_reviews(
        db=db,
        workspace_id=current_user.workspace_id,
        year=year,
        limit=limit
    )
    return reviews


@router.get("/management-review/{review_id}", response_model=ManagementReviewDetailResponse)
async def get_management_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific Management Review by ID"""
    review = ArtifactService.get_review_by_id(
        db=db,
        review_id=review_id,
        workspace_id=current_user.workspace_id
    )
    
    if not review:
        raise HTTPException(status_code=404, detail="Management Review not found")
    
    return ManagementReviewDetailResponse(
        id=review.id,
        review_number=review.review_number,
        review_date=review.review_date,
        attendees=review.attendees,
        agenda=review.agenda,
        minutes=review.minutes,
        decisions=review.decisions,
        action_items=review.action_items,
        next_review_date=review.next_review_date,
        created_at=review.created_at.isoformat(),
        updated_at=review.updated_at.isoformat()
    )


@router.put("/management-review/{review_id}", response_model=ManagementReviewDetailResponse)
async def update_management_review(
    review_id: str,
    request: ManagementReviewUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a Management Review"""
    # Build update dict from request
    update_data = {}
    if request.review_date is not None:
        update_data['review_date'] = request.review_date
    if request.attendees is not None:
        update_data['attendees'] = request.attendees
    if request.agenda is not None:
        update_data['agenda'] = request.agenda
    if request.minutes is not None:
        update_data['minutes'] = request.minutes
    if request.decisions is not None:
        update_data['decisions'] = request.decisions
    if request.action_items is not None:
        update_data['action_items'] = request.action_items
    if request.next_review_date is not None:
        update_data['next_review_date'] = request.next_review_date
    
    try:
        review = ArtifactService.update_management_review(
            db=db,
            review_id=review_id,
            workspace_id=current_user.workspace_id,
            **update_data
        )
        
        return ManagementReviewDetailResponse(
            id=review.id,
            review_number=review.review_number,
            review_date=review.review_date,
            attendees=review.attendees,
            agenda=review.agenda,
            minutes=review.minutes,
            decisions=review.decisions,
            action_items=review.action_items,
            next_review_date=review.next_review_date,
            created_at=review.created_at.isoformat(),
            updated_at=review.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/management-review/{review_id}")
async def delete_management_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a Management Review"""
    try:
        ArtifactService.delete_management_review(
            db=db,
            review_id=review_id,
            workspace_id=current_user.workspace_id
        )
        return {"message": "Management Review deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Training Record Endpoints =====

class TrainingRecordCreateRequest(BaseModel):
    employee_id: str
    training_title: str
    training_date: date
    trainer_name: Optional[str] = None
    training_hours: Optional[float] = None
    training_type: Optional[str] = None
    competency_area: Optional[str] = None
    passed: Optional[bool] = None
    score: Optional[float] = None
    certificate_number: Optional[str] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class TrainingRecordUpdateRequest(BaseModel):
    employee_id: Optional[str] = None
    training_title: Optional[str] = None
    training_date: Optional[date] = None
    trainer_name: Optional[str] = None
    training_hours: Optional[float] = None
    training_type: Optional[str] = None
    competency_area: Optional[str] = None
    passed: Optional[bool] = None
    score: Optional[float] = None
    certificate_number: Optional[str] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class TrainingRecordResponse(BaseModel):
    id: str
    employee_id: str
    training_title: str
    training_date: date
    trainer_name: Optional[str]
    training_hours: Optional[float]
    training_type: Optional[str]
    competency_area: Optional[str]
    passed: Optional[bool]
    score: Optional[float]
    certificate_number: Optional[str]
    expiry_date: Optional[date]
    notes: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/training", response_model=TrainingRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_training_record(
    request: TrainingRecordCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new training record"""
    from datetime import datetime
    record = ArtifactService.create_training_record(
        db=db,
        workspace_id=current_user.workspace_id,
        employee_id=request.employee_id,
        training_title=request.training_title,
        training_date=datetime.combine(request.training_date, datetime.min.time()),
        trainer_name=request.trainer_name,
        training_hours=request.training_hours,
        training_type=request.training_type,
        competency_area=request.competency_area,
        passed=request.passed,
        score=request.score,
        certificate_number=request.certificate_number,
        expiry_date=datetime.combine(request.expiry_date, datetime.min.time()) if request.expiry_date else None,
        notes=request.notes,
        created_by=current_user.id
    )
    return record


@router.get("/training", response_model=List[TrainingRecordResponse])
async def list_training_records(
    employee_id: Optional[str] = None,
    competency_area: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List training records for workspace"""
    records = ArtifactService.get_workspace_training(
        db=db,
        workspace_id=current_user.workspace_id,
        employee_id=employee_id,
        competency_area=competency_area,
        limit=limit
    )
    return records


@router.get("/training/{training_id}", response_model=TrainingRecordDetailResponse)
async def get_training_record(
    training_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific Training Record by ID"""
    training = ArtifactService.get_training_by_id(
        db=db,
        training_id=training_id,
        workspace_id=current_user.workspace_id
    )
    
    if not training:
        raise HTTPException(status_code=404, detail="Training Record not found")
    
    return TrainingRecordDetailResponse(
        id=training.id,
        record_number=training.record_number,
        employee_id=training.employee_id,
        training_title=training.training_title,
        training_date=training.training_date,
        trainer_name=training.trainer_name,
        training_hours=training.training_hours,
        training_type=training.training_type,
        competency_area=training.competency_area,
        passed=training.passed,
        score=training.score,
        certificate_number=training.certificate_number,
        expiry_date=training.expiry_date,
        notes=training.notes,
        created_at=training.created_at.isoformat(),
        updated_at=training.updated_at.isoformat()
    )


@router.put("/training/{training_id}", response_model=TrainingRecordDetailResponse)
async def update_training_record(
    training_id: str,
    request: TrainingRecordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a Training Record"""
    # Build update dict from request
    update_data = {}
    if request.employee_id is not None:
        update_data['employee_id'] = request.employee_id
    if request.training_title is not None:
        update_data['training_title'] = request.training_title
    if request.training_date is not None:
        update_data['training_date'] = request.training_date
    if request.trainer_name is not None:
        update_data['trainer_name'] = request.trainer_name
    if request.training_hours is not None:
        update_data['training_hours'] = request.training_hours
    if request.training_type is not None:
        update_data['training_type'] = request.training_type
    if request.competency_area is not None:
        update_data['competency_area'] = request.competency_area
    if request.passed is not None:
        update_data['passed'] = request.passed
    if request.score is not None:
        update_data['score'] = request.score
    if request.certificate_number is not None:
        update_data['certificate_number'] = request.certificate_number
    if request.expiry_date is not None:
        update_data['expiry_date'] = request.expiry_date
    if request.notes is not None:
        update_data['notes'] = request.notes
    
    try:
        training = ArtifactService.update_training_record(
            db=db,
            training_id=training_id,
            workspace_id=current_user.workspace_id,
            **update_data
        )
        
        return TrainingRecordDetailResponse(
            id=training.id,
            record_number=training.record_number,
            employee_id=training.employee_id,
            training_title=training.training_title,
            training_date=training.training_date,
            trainer_name=training.trainer_name,
            training_hours=training.training_hours,
            training_type=training.training_type,
            competency_area=training.competency_area,
            passed=training.passed,
            score=training.score,
            certificate_number=training.certificate_number,
            expiry_date=training.expiry_date,
            notes=training.notes,
            created_at=training.created_at.isoformat(),
            updated_at=training.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/training/{training_id}")
async def delete_training_record(
    training_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a Training Record"""
    try:
        ArtifactService.delete_training_record(
            db=db,
            training_id=training_id,
            workspace_id=current_user.workspace_id
        )
        return {"message": "Training Record deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Customer Complaint Endpoints =====

class CustomerComplaintCreateRequest(BaseModel):
    complaint_title: str
    complaint_description: str
    customer_name: str
    received_date: date
    complaint_source: Optional[str] = None
    product_service: Optional[str] = None
    priority: Optional[str] = "medium"
    assigned_to: Optional[str] = None
    resolution_target_date: Optional[date] = None


class CustomerComplaintUpdateRequest(BaseModel):
    complaint_title: Optional[str] = None
    complaint_description: Optional[str] = None
    customer_name: Optional[str] = None
    received_date: Optional[date] = None
    complaint_source: Optional[str] = None
    product_service: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_target_date: Optional[date] = None


class CustomerComplaintResponse(BaseModel):
    id: str
    complaint_number: str
    complaint_title: str
    complaint_description: str
    customer_name: str
    received_date: date
    complaint_source: Optional[str]
    product_service: Optional[str]
    priority: Optional[str]
    status: str
    assigned_to: Optional[str]
    resolution_target_date: Optional[date]
    resolution_date: Optional[date]
    customer_satisfaction: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/complaint", response_model=CustomerComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_complaint(
    request: CustomerComplaintCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new customer complaint"""
    from datetime import datetime
    complaint = ArtifactService.create_customer_complaint(
        db=db,
        workspace_id=current_user.workspace_id,
        complaint_title=request.complaint_title,
        complaint_description=request.complaint_description,
        customer_name=request.customer_name,
        received_date=datetime.combine(request.received_date, datetime.min.time()),
        complaint_source=request.complaint_source,
        product_service=request.product_service,
        priority=request.priority,
        assigned_to=request.assigned_to,
        resolution_target_date=datetime.combine(request.resolution_target_date, datetime.min.time()) if request.resolution_target_date else None,
        created_by=current_user.id
    )
    return complaint


@router.get("/complaint", response_model=List[CustomerComplaintResponse])
async def list_customer_complaints(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List customer complaints for workspace"""
    complaints = ArtifactService.get_workspace_complaints(
        db=db,
        workspace_id=current_user.workspace_id,
        status=status,
        priority=priority,
        limit=limit
    )
    return complaints


@router.get("/complaint/{complaint_id}", response_model=CustomerComplaintDetailResponse)
async def get_customer_complaint(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific Customer Complaint by ID"""
    complaint = ArtifactService.get_complaint_by_id(
        db=db,
        complaint_id=complaint_id,
        workspace_id=current_user.workspace_id
    )
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Customer Complaint not found")
    
    return CustomerComplaintDetailResponse(
        id=complaint.id,
        complaint_number=complaint.complaint_number,
        complaint_title=complaint.complaint_title,
        complaint_description=complaint.complaint_description,
        customer_name=complaint.customer_name,
        received_date=complaint.received_date,
        complaint_source=complaint.complaint_source,
        product_service=complaint.product_service,
        status=complaint.status,
        priority=complaint.priority,
        assigned_to=complaint.assigned_to,
        root_cause=complaint.root_cause,
        resolution=complaint.resolution,
        resolution_date=complaint.resolution_date,
        resolution_target_date=complaint.resolution_target_date,
        customer_feedback=complaint.customer_feedback,
        preventive_measures=complaint.preventive_measures,
        created_at=complaint.created_at.isoformat(),
        updated_at=complaint.updated_at.isoformat()
    )


@router.put("/complaint/{complaint_id}", response_model=CustomerComplaintDetailResponse)
async def update_customer_complaint(
    complaint_id: str,
    request: CustomerComplaintUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a Customer Complaint"""
    # Build update dict from request
    update_data = {}
    if request.complaint_title is not None:
        update_data['complaint_title'] = request.complaint_title
    if request.complaint_description is not None:
        update_data['complaint_description'] = request.complaint_description
    if request.customer_name is not None:
        update_data['customer_name'] = request.customer_name
    if request.received_date is not None:
        update_data['received_date'] = request.received_date
    if request.complaint_source is not None:
        update_data['complaint_source'] = request.complaint_source
    if request.product_service is not None:
        update_data['product_service'] = request.product_service
    if request.priority is not None:
        update_data['priority'] = request.priority
    if request.assigned_to is not None:
        update_data['assigned_to'] = request.assigned_to
    if request.resolution_target_date is not None:
        update_data['resolution_target_date'] = request.resolution_target_date
    
    try:
        complaint = ArtifactService.update_customer_complaint(
            db=db,
            complaint_id=complaint_id,
            workspace_id=current_user.workspace_id,
            **update_data
        )
        
        return CustomerComplaintDetailResponse(
            id=complaint.id,
            complaint_number=complaint.complaint_number,
            complaint_title=complaint.complaint_title,
            complaint_description=complaint.complaint_description,
            customer_name=complaint.customer_name,
            received_date=complaint.received_date,
            complaint_source=complaint.complaint_source,
            product_service=complaint.product_service,
            status=complaint.status,
            priority=complaint.priority,
            assigned_to=complaint.assigned_to,
            root_cause=complaint.root_cause,
            resolution=complaint.resolution,
            resolution_date=complaint.resolution_date,
            resolution_target_date=complaint.resolution_target_date,
            customer_feedback=complaint.customer_feedback,
            preventive_measures=complaint.preventive_measures,
            created_at=complaint.created_at.isoformat(),
            updated_at=complaint.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/complaint/{complaint_id}")
async def delete_customer_complaint(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a Customer Complaint"""
    try:
        ArtifactService.delete_customer_complaint(
            db=db,
            complaint_id=complaint_id,
            workspace_id=current_user.workspace_id
        )
        return {"message": "Customer Complaint deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Enhanced Analytics Endpoints =====

@router.get("/analytics/trends/nc-by-month")
async def get_nc_trends_by_month(
    months: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get NC trends by month for the last N months"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract
    
    workspace_id = current_user.workspace_id
    start_date = datetime.now() - timedelta(days=months * 30)
    
    # Query NC grouped by month
    results = db.query(
        extract('year', NonConformity.identified_date).label('year'),
        extract('month', NonConformity.identified_date).label('month'),
        func.count(NonConformity.id).label('count'),
        func.sum(case((NonConformity.status == 'Open', 1), else_=0)).label('open'),
        func.sum(case((NonConformity.status == 'Closed', 1), else_=0)).label('closed')
    ).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.identified_date >= start_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    trends = []
    for r in results:
        trends.append({
            'month': f"{int(r.year)}-{int(r.month):02d}",
            'count': r.count,
            'open': r.open or 0,
            'closed': r.closed or 0
        })
    
    return {"trends": trends}


@router.get("/analytics/trends/ca-by-month")
async def get_ca_trends_by_month(
    months: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CA trends by month for the last N months"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract
    
    workspace_id = current_user.workspace_id
    start_date = datetime.now() - timedelta(days=months * 30)
    
    # Query CA grouped by month
    results = db.query(
        extract('year', CorrectiveAction.action_date).label('year'),
        extract('month', CorrectiveAction.action_date).label('month'),
        func.count(CorrectiveAction.id).label('count'),
        func.sum(case((CorrectiveAction.status == 'Completed', 1), else_=0)).label('completed'),
        func.sum(case((CorrectiveAction.effectiveness == 'Effective', 1), else_=0)).label('effective')
    ).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.action_date >= start_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    trends = []
    for r in results:
        trends.append({
            'month': f"{int(r.year)}-{int(r.month):02d}",
            'count': r.count,
            'completed': r.completed or 0,
            'effective': r.effective or 0
        })
    
    return {"trends": trends}


@router.get("/analytics/trends/audits-by-quarter")
async def get_audit_trends_by_quarter(
    years: int = 2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit trends by quarter"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract
    
    workspace_id = current_user.workspace_id
    start_date = datetime.now() - timedelta(days=years * 365)
    
    # Query audits grouped by quarter
    results = db.query(
        extract('year', InternalAudit.audit_date).label('year'),
        extract('quarter', InternalAudit.audit_date).label('quarter'),
        func.count(InternalAudit.id).label('count'),
        func.sum(InternalAudit.major_findings).label('major_findings'),
        func.sum(InternalAudit.minor_findings).label('minor_findings')
    ).filter(
        InternalAudit.workspace_id == workspace_id,
        InternalAudit.audit_date >= start_date
    ).group_by('year', 'quarter').order_by('year', 'quarter').all()
    
    trends = []
    for r in results:
        trends.append({
            'quarter': f"{int(r.year)}-Q{int(r.quarter)}",
            'count': r.count,
            'major_findings': r.major_findings or 0,
            'minor_findings': r.minor_findings or 0
        })
    
    return {"trends": trends}


@router.get("/analytics/severity-distribution")
async def get_severity_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get severity distribution across all artifacts"""
    from sqlalchemy import func
    
    workspace_id = current_user.workspace_id
    
    # NC by severity
    nc_severity = db.query(
        NonConformity.severity,
        func.count(NonConformity.id).label('count')
    ).filter(
        NonConformity.workspace_id == workspace_id
    ).group_by(NonConformity.severity).all()
    
    # Customer complaints by priority
    complaint_priority = db.query(
        CustomerComplaint.priority,
        func.count(CustomerComplaint.id).label('count')
    ).filter(
        CustomerComplaint.workspace_id == workspace_id
    ).group_by(CustomerComplaint.priority).all()
    
    return {
        'nc_by_severity': [{'severity': r.severity, 'count': r.count} for r in nc_severity],
        'complaints_by_priority': [{'priority': r.priority, 'count': r.count} for r in complaint_priority]
    }


@router.get("/analytics/category-breakdown")
async def get_category_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get category breakdown for NCs and CAs"""
    from sqlalchemy import func
    
    workspace_id = current_user.workspace_id
    
    # NC by category
    nc_categories = db.query(
        NonConformity.category,
        func.count(NonConformity.id).label('count')
    ).filter(
        NonConformity.workspace_id == workspace_id
    ).group_by(NonConformity.category).order_by(func.count(NonConformity.id).desc()).limit(10).all()
    
    # CA by action type
    ca_types = db.query(
        CorrectiveAction.action_type,
        func.count(CorrectiveAction.id).label('count')
    ).filter(
        CorrectiveAction.workspace_id == workspace_id
    ).group_by(CorrectiveAction.action_type).order_by(func.count(CorrectiveAction.id).desc()).limit(10).all()
    
    return {
        'nc_by_category': [{'category': r.category, 'count': r.count} for r in nc_categories],
        'ca_by_type': [{'type': r.action_type, 'count': r.count} for r in ca_types]
    }


@router.get("/analytics/performance-metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get key performance metrics"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    workspace_id = current_user.workspace_id
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # NC metrics
    total_nc = db.query(func.count(NonConformity.id)).filter(
        NonConformity.workspace_id == workspace_id
    ).scalar() or 0
    
    open_nc = db.query(func.count(NonConformity.id)).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.status == 'Open'
    ).scalar() or 0
    
    recent_nc = db.query(func.count(NonConformity.id)).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.identified_date >= thirty_days_ago
    ).scalar() or 0
    
    # CA metrics
    total_ca = db.query(func.count(CorrectiveAction.id)).filter(
        CorrectiveAction.workspace_id == workspace_id
    ).scalar() or 0
    
    completed_ca = db.query(func.count(CorrectiveAction.id)).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.status == 'Completed'
    ).scalar() or 0
    
    effective_ca = db.query(func.count(CorrectiveAction.id)).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.effectiveness == 'Effective'
    ).scalar() or 0
    
    # Audit metrics
    total_audits = db.query(func.count(InternalAudit.id)).filter(
        InternalAudit.workspace_id == workspace_id
    ).scalar() or 0
    
    completed_audits = db.query(func.count(InternalAudit.id)).filter(
        InternalAudit.workspace_id == workspace_id,
        InternalAudit.status == 'Completed'
    ).scalar() or 0
    
    # Training metrics
    total_training = db.query(func.count(TrainingRecord.id)).filter(
        TrainingRecord.workspace_id == workspace_id
    ).scalar() or 0
    
    completed_training = db.query(func.count(TrainingRecord.id)).filter(
        TrainingRecord.workspace_id == workspace_id,
        TrainingRecord.status == 'Completed'
    ).scalar() or 0
    
    return {
        'nc': {
            'total': total_nc,
            'open': open_nc,
            'recent_30_days': recent_nc,
            'closure_rate': round((total_nc - open_nc) / total_nc * 100, 1) if total_nc > 0 else 0
        },
        'ca': {
            'total': total_ca,
            'completed': completed_ca,
            'effective': effective_ca,
            'completion_rate': round(completed_ca / total_ca * 100, 1) if total_ca > 0 else 0,
            'effectiveness_rate': round(effective_ca / completed_ca * 100, 1) if completed_ca > 0 else 0
        },
        'audits': {
            'total': total_audits,
            'completed': completed_audits,
            'completion_rate': round(completed_audits / total_audits * 100, 1) if total_audits > 0 else 0
        },
        'training': {
            'total': total_training,
            'completed': completed_training,
            'completion_rate': round(completed_training / total_training * 100, 1) if total_training > 0 else 0
        }
    }


@router.get("/analytics/cost-summary")
def get_cost_summary(
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cost summary by artifact type"""
    
    # NC costs
    nc_cost = db.query(
        func.count(NonConformity.id).label('count'),
        func.coalesce(func.sum(NonConformity.potential_cost), 0).label('total')
    ).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.potential_cost.isnot(None)
    ).first()
    
    # CA costs
    ca_costs = db.query(
        func.count(CorrectiveAction.id).label('count'),
        func.coalesce(func.sum(CorrectiveAction.estimated_cost), 0).label('estimated'),
        func.coalesce(func.sum(CorrectiveAction.actual_cost), 0).label('actual'),
        func.coalesce(func.sum(CorrectiveAction.estimated_hours), 0).label('est_hours'),
        func.coalesce(func.sum(CorrectiveAction.actual_hours), 0).label('act_hours')
    ).filter(
        CorrectiveAction.workspace_id == workspace_id
    ).first()
    
    # Audit costs
    audit_costs = db.query(
        func.count(InternalAudit.id).label('count'),
        func.coalesce(func.sum(InternalAudit.estimated_cost), 0).label('estimated'),
        func.coalesce(func.sum(InternalAudit.actual_cost), 0).label('actual'),
        func.coalesce(func.sum(InternalAudit.auditor_hours), 0).label('hours')
    ).filter(
        InternalAudit.workspace_id == workspace_id
    ).first()
    
    # Management Review costs
    mr_costs = db.query(
        func.count(ManagementReview.id).label('count'),
        func.coalesce(func.sum(ManagementReview.meeting_cost), 0).label('cost'),
        func.coalesce(func.sum(ManagementReview.preparation_hours), 0).label('hours')
    ).filter(
        ManagementReview.workspace_id == workspace_id
    ).first()
    
    # Training costs
    training_costs = db.query(
        func.count(TrainingRecord.id).label('count'),
        func.coalesce(func.sum(TrainingRecord.training_cost), 0).label('total'),
        func.coalesce(func.sum(TrainingRecord.instructor_fee), 0).label('instructor'),
        func.coalesce(func.sum(TrainingRecord.material_cost), 0).label('materials'),
        func.coalesce(func.sum(TrainingRecord.venue_cost), 0).label('venue')
    ).filter(
        TrainingRecord.workspace_id == workspace_id
    ).first()
    
    # Complaint costs
    complaint_costs = db.query(
        func.count(CustomerComplaint.id).label('count'),
        func.coalesce(func.sum(CustomerComplaint.resolution_cost), 0).label('resolution'),
        func.coalesce(func.sum(CustomerComplaint.compensation_amount), 0).label('compensation'),
        func.coalesce(func.sum(CustomerComplaint.investigation_hours), 0).label('hours')
    ).filter(
        CustomerComplaint.workspace_id == workspace_id
    ).first()
    
    return {
        'non_conformities': {
            'count': nc_cost.count,
            'potential_cost': float(nc_cost.total),
            'avg_cost': float(nc_cost.total / nc_cost.count) if nc_cost.count > 0 else 0
        },
        'corrective_actions': {
            'count': ca_costs.count,
            'estimated_cost': float(ca_costs.estimated),
            'actual_cost': float(ca_costs.actual),
            'variance': float(ca_costs.actual - ca_costs.estimated),
            'estimated_hours': float(ca_costs.est_hours),
            'actual_hours': float(ca_costs.act_hours)
        },
        'audits': {
            'count': audit_costs.count,
            'estimated_cost': float(audit_costs.estimated),
            'actual_cost': float(audit_costs.actual),
            'variance': float(audit_costs.actual - audit_costs.estimated),
            'auditor_hours': float(audit_costs.hours)
        },
        'management_reviews': {
            'count': mr_costs.count,
            'meeting_cost': float(mr_costs.cost),
            'preparation_hours': float(mr_costs.hours)
        },
        'training': {
            'count': training_costs.count,
            'total_cost': float(training_costs.total),
            'instructor_fees': float(training_costs.instructor),
            'material_costs': float(training_costs.materials),
            'venue_costs': float(training_costs.venue)
        },
        'complaints': {
            'count': complaint_costs.count,
            'resolution_cost': float(complaint_costs.resolution),
            'compensation_amount': float(complaint_costs.compensation),
            'investigation_hours': float(complaint_costs.hours)
        },
        'totals': {
            'estimated': float(ca_costs.estimated + audit_costs.estimated),
            'actual': float(ca_costs.actual + audit_costs.actual + mr_costs.cost + training_costs.total + complaint_costs.resolution + complaint_costs.compensation),
            'potential_nc': float(nc_cost.total)
        }
    }


@router.get("/analytics/cost-trends")
def get_cost_trends(
    workspace_id: str = Query(...),
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get monthly cost trends"""
    from datetime import datetime, timedelta
    from sqlalchemy import extract
    
    cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
    
    # CA cost trends
    ca_trends = db.query(
        extract('year', CorrectiveAction.created_at).label('year'),
        extract('month', CorrectiveAction.created_at).label('month'),
        func.coalesce(func.sum(CorrectiveAction.estimated_cost), 0).label('estimated'),
        func.coalesce(func.sum(CorrectiveAction.actual_cost), 0).label('actual')
    ).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.created_at >= cutoff_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Training cost trends
    training_trends = db.query(
        extract('year', TrainingRecord.training_date).label('year'),
        extract('month', TrainingRecord.training_date).label('month'),
        func.coalesce(func.sum(TrainingRecord.training_cost), 0).label('cost')
    ).filter(
        TrainingRecord.workspace_id == workspace_id,
        TrainingRecord.training_date >= cutoff_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Complaint cost trends
    complaint_trends = db.query(
        extract('year', CustomerComplaint.complaint_date).label('year'),
        extract('month', CustomerComplaint.complaint_date).label('month'),
        func.coalesce(func.sum(CustomerComplaint.resolution_cost), 0).label('resolution'),
        func.coalesce(func.sum(CustomerComplaint.compensation_amount), 0).label('compensation')
    ).filter(
        CustomerComplaint.workspace_id == workspace_id,
        CustomerComplaint.complaint_date >= cutoff_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return {
        'ca_costs': [
            {
                'month': f"{int(row.year)}-{int(row.month):02d}",
                'estimated': float(row.estimated),
                'actual': float(row.actual)
            }
            for row in ca_trends
        ],
        'training_costs': [
            {
                'month': f"{int(row.year)}-{int(row.month):02d}",
                'cost': float(row.cost)
            }
            for row in training_trends
        ],
        'complaint_costs': [
            {
                'month': f"{int(row.year)}-{int(row.month):02d}",
                'resolution': float(row.resolution),
                'compensation': float(row.compensation),
                'total': float(row.resolution + row.compensation)
            }
            for row in complaint_trends
        ]
    }


@router.get("/analytics/budget-tracking")
def get_budget_tracking(
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Compare estimated vs actual costs for budget tracking"""
    
    # CA budget tracking
    ca_budget = db.query(
        func.coalesce(func.sum(CorrectiveAction.estimated_cost), 0).label('estimated'),
        func.coalesce(func.sum(CorrectiveAction.actual_cost), 0).label('actual'),
        func.count(case((CorrectiveAction.actual_cost > CorrectiveAction.estimated_cost, 1))).label('over_budget'),
        func.count(case((CorrectiveAction.actual_cost <= CorrectiveAction.estimated_cost, 1))).label('on_budget')
    ).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.estimated_cost.isnot(None),
        CorrectiveAction.actual_cost.isnot(None)
    ).first()
    
    # Audit budget tracking
    audit_budget = db.query(
        func.coalesce(func.sum(InternalAudit.estimated_cost), 0).label('estimated'),
        func.coalesce(func.sum(InternalAudit.actual_cost), 0).label('actual'),
        func.count(case((InternalAudit.actual_cost > InternalAudit.estimated_cost, 1))).label('over_budget'),
        func.count(case((InternalAudit.actual_cost <= InternalAudit.estimated_cost, 1))).label('on_budget')
    ).filter(
        InternalAudit.workspace_id == workspace_id,
        InternalAudit.estimated_cost.isnot(None),
        InternalAudit.actual_cost.isnot(None)
    ).first()
    
    return {
        'corrective_actions': {
            'estimated': float(ca_budget.estimated),
            'actual': float(ca_budget.actual),
            'variance': float(ca_budget.actual - ca_budget.estimated),
            'variance_percent': round((ca_budget.actual - ca_budget.estimated) / ca_budget.estimated * 100, 1) if ca_budget.estimated > 0 else 0,
            'over_budget_count': ca_budget.over_budget,
            'on_budget_count': ca_budget.on_budget
        },
        'audits': {
            'estimated': float(audit_budget.estimated),
            'actual': float(audit_budget.actual),
            'variance': float(audit_budget.actual - audit_budget.estimated),
            'variance_percent': round((audit_budget.actual - audit_budget.estimated) / audit_budget.estimated * 100, 1) if audit_budget.estimated > 0 else 0,
            'over_budget_count': audit_budget.over_budget,
            'on_budget_count': audit_budget.on_budget
        },
        'overall': {
            'total_estimated': float(ca_budget.estimated + audit_budget.estimated),
            'total_actual': float(ca_budget.actual + audit_budget.actual),
            'total_variance': float((ca_budget.actual + audit_budget.actual) - (ca_budget.estimated + audit_budget.estimated))
        }
    }


@router.get("/analytics/cost-by-category")
def get_cost_by_category(
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cost breakdown by categories"""
    
    # NC costs by category
    nc_by_category = db.query(
        NonConformity.category,
        func.count(NonConformity.id).label('count'),
        func.coalesce(func.sum(NonConformity.potential_cost), 0).label('cost')
    ).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.potential_cost.isnot(None)
    ).group_by(NonConformity.category).order_by(func.sum(NonConformity.potential_cost).desc()).limit(10).all()
    
    # CA costs by type
    ca_by_type = db.query(
        CorrectiveAction.action_type,
        func.count(CorrectiveAction.id).label('count'),
        func.coalesce(func.sum(CorrectiveAction.actual_cost), 0).label('cost')
    ).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.actual_cost.isnot(None)
    ).group_by(CorrectiveAction.action_type).order_by(func.sum(CorrectiveAction.actual_cost).desc()).limit(10).all()
    
    # Training costs by type
    training_by_type = db.query(
        TrainingRecord.training_type,
        func.count(TrainingRecord.id).label('count'),
        func.coalesce(func.sum(TrainingRecord.training_cost), 0).label('cost')
    ).filter(
        TrainingRecord.workspace_id == workspace_id,
        TrainingRecord.training_cost.isnot(None)
    ).group_by(TrainingRecord.training_type).order_by(func.sum(TrainingRecord.training_cost).desc()).all()
    
    return {
        'nc_by_category': [
            {
                'category': row.category or 'Uncategorized',
                'count': row.count,
                'cost': float(row.cost)
            }
            for row in nc_by_category
        ],
        'ca_by_type': [
            {
                'type': row.action_type or 'Unspecified',
                'count': row.count,
                'cost': float(row.cost)
            }
            for row in ca_by_type
        ],
        'training_by_type': [
            {
                'type': row.training_type or 'Unspecified',
                'count': row.count,
                'cost': float(row.cost)
            }
            for row in training_by_type
        ]
    }


@router.get("/analytics/predictions")
def get_predictions(
    workspace_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get predictive analytics for NC trends, CA completion, and risk scoring"""
    from datetime import datetime, timedelta
    from sqlalchemy import extract
    
    # NC Trend Forecasting (last 6 months + predict next 3)
    cutoff_date = datetime.utcnow() - timedelta(days=180)
    
    nc_monthly = db.query(
        extract('year', NonConformity.created_at).label('year'),
        extract('month', NonConformity.created_at).label('month'),
        func.count(NonConformity.id).label('count')
    ).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.created_at >= cutoff_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Simple moving average for prediction
    nc_counts = [row.count for row in nc_monthly]
    if len(nc_counts) >= 3:
        avg_trend = sum(nc_counts[-3:]) / 3
        # Linear trend
        if len(nc_counts) >= 6:
            early_avg = sum(nc_counts[:3]) / 3
            late_avg = sum(nc_counts[-3:]) / 3
            trend_slope = (late_avg - early_avg) / 3
        else:
            trend_slope = 0
        
        predictions = []
        last_month = nc_monthly[-1] if nc_monthly else None
        if last_month:
            current_year = int(last_month.year)
            current_month = int(last_month.month)
            
            for i in range(1, 4):
                next_month = current_month + i
                next_year = current_year
                if next_month > 12:
                    next_month -= 12
                    next_year += 1
                
                predicted_count = max(0, int(avg_trend + (trend_slope * i)))
                predictions.append({
                    'month': f"{next_year}-{next_month:02d}",
                    'predicted_count': predicted_count,
                    'confidence': 'medium' if len(nc_counts) >= 6 else 'low'
                })
    else:
        predictions = []
    
    # CA Completion Predictions
    pending_ca = db.query(CorrectiveAction).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.status.in_(['Open', 'In Progress']),
        CorrectiveAction.target_completion_date.isnot(None)
    ).all()
    
    completed_ca = db.query(
        func.avg(
            func.julianday(CorrectiveAction.actual_completion_date) - 
            func.julianday(CorrectiveAction.created_at)
        )
    ).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.status == 'Completed',
        CorrectiveAction.actual_completion_date.isnot(None)
    ).scalar()
    
    avg_completion_days = completed_ca if completed_ca else 30  # Default 30 days
    
    ca_predictions = []
    for ca in pending_ca[:10]:  # Top 10
        days_since_creation = (datetime.utcnow() - ca.created_at).days
        progress_ratio = days_since_creation / avg_completion_days if avg_completion_days > 0 else 0
        
        if ca.target_completion_date:
            days_until_target = (ca.target_completion_date - datetime.utcnow().date()).days
            predicted_completion = datetime.utcnow() + timedelta(days=max(1, avg_completion_days - days_since_creation))
            
            ca_predictions.append({
                'ca_id': ca.id,
                'ca_number': ca.action_number,
                'title': ca.action_description[:100] if ca.action_description else 'N/A',
                'predicted_completion_date': predicted_completion.strftime('%Y-%m-%d'),
                'target_date': ca.target_completion_date.strftime('%Y-%m-%d'),
                'on_track': days_until_target > (avg_completion_days - days_since_creation),
                'progress_percent': min(100, int(progress_ratio * 100))
            })
    
    # Risk Scoring (0-100)
    open_nc_count = db.query(func.count(NonConformity.id)).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.status == 'Open'
    ).scalar() or 0
    
    critical_nc = db.query(func.count(NonConformity.id)).filter(
        NonConformity.workspace_id == workspace_id,
        NonConformity.status == 'Open',
        NonConformity.severity == 'Critical'
    ).scalar() or 0
    
    overdue_ca = db.query(func.count(CorrectiveAction.id)).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.status.in_(['Open', 'In Progress']),
        CorrectiveAction.target_completion_date < datetime.utcnow().date()
    ).scalar() or 0
    
    ineffective_ca = db.query(func.count(CorrectiveAction.id)).filter(
        CorrectiveAction.workspace_id == workspace_id,
        CorrectiveAction.effectiveness == 'Not Effective'
    ).scalar() or 0
    
    major_findings = db.query(func.sum(InternalAudit.major_findings)).filter(
        InternalAudit.workspace_id == workspace_id,
        InternalAudit.audit_date >= datetime.utcnow() - timedelta(days=365)
    ).scalar() or 0
    
    # Risk calculation (weighted)
    risk_score = min(100, int(
        (open_nc_count * 2) +
        (critical_nc * 10) +
        (overdue_ca * 5) +
        (ineffective_ca * 8) +
        (major_findings * 3)
    ))
    
    risk_level = 'low' if risk_score < 30 else 'medium' if risk_score < 70 else 'high'
    
    risk_factors = []
    if open_nc_count > 5:
        risk_factors.append(f"{open_nc_count} open non-conformities")
    if critical_nc > 0:
        risk_factors.append(f"{critical_nc} critical NC(s)")
    if overdue_ca > 0:
        risk_factors.append(f"{overdue_ca} overdue corrective action(s)")
    if ineffective_ca > 0:
        risk_factors.append(f"{ineffective_ca} ineffective CA(s)")
    if major_findings > 3:
        risk_factors.append(f"{int(major_findings)} major audit findings in last year")
    
    return {
        'nc_forecast': {
            'historical': [
                {
                    'month': f"{int(row.year)}-{int(row.month):02d}",
                    'count': row.count
                }
                for row in nc_monthly
            ],
            'predictions': predictions
        },
        'ca_predictions': ca_predictions,
        'risk_assessment': {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'recommendation': (
                'Continue current practices' if risk_score < 30 else
                'Monitor key indicators closely' if risk_score < 70 else
                'Immediate action required'
            )
        }
    }
