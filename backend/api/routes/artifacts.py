"""
Artifact Management API Routes
Phase 4.3: REST endpoints for NC, CA, Audits
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
