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


class CACreateRequest(BaseModel):
    title: str
    description: str
    action_plan: str
    assigned_to: str
    planned_start_date: date
    planned_completion_date: date
    nc_id: Optional[str] = None
    priority: str = "medium"


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


class AuditCreateRequest(BaseModel):
    title: str
    audit_type: AuditType
    scope_description: str
    planned_date: date
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
