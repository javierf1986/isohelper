"""
Artifact Management Service
Phase 4.3: Compliance Artifacts

Handles Non-Conformities, Corrective Actions, Audits, and compliance tracking.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import uuid

from backend.models.artifact_models import (
    NonConformity, CorrectiveAction, InternalAudit,
    ManagementReview, TrainingRecord, CustomerComplaint,
    NCStatus, NCSeverity, CAStatus, AuditStatus
)


class ArtifactService:
    """Service for managing compliance artifacts"""
    
    # ===== Non-Conformity Management =====
    
    @staticmethod
    def create_nc(
        db: Session,
        workspace_id: str,
        title: str,
        description: str,
        severity: NCSeverity,
        reported_by: str,
        detected_date: date,
        category: Optional[str] = None,
        detected_location: Optional[str] = None,
        iso_standard_id: Optional[str] = None,
        iso_clause_number: Optional[str] = None
    ) -> NonConformity:
        """Create a new Non-Conformity"""
        # Generate NC number
        year = datetime.now().year
        count = db.query(func.count(NonConformity.id)).filter(
            NonConformity.workspace_id == workspace_id
        ).scalar() or 0
        nc_number = f"NC-{year}-{count + 1:03d}"
        
        nc = NonConformity(
            id=str(uuid.uuid4()),
            nc_number=nc_number,
            workspace_id=workspace_id,
            title=title,
            description=description,
            severity=severity,
            reported_by=reported_by,
            detected_date=detected_date,
            category=category,
            detected_location=detected_location,
            iso_standard_id=iso_standard_id,
            iso_clause_number=iso_clause_number,
            status=NCStatus.OPEN
        )
        
        db.add(nc)
        db.commit()
        db.refresh(nc)
        
        return nc
    
    @staticmethod
    def update_nc_status(
        db: Session,
        nc_id: str,
        status: NCStatus,
        user_id: str
    ) -> NonConformity:
        """Update NC status"""
        nc = db.query(NonConformity).filter(NonConformity.id == nc_id).first()
        if not nc:
            raise ValueError(f"NC {nc_id} not found")
        
        nc.status = status
        
        if status == NCStatus.CLOSED:
            nc.actual_closure_date = date.today()
        
        if status == NCStatus.VERIFIED:
            nc.verified_by = user_id
            nc.verified_at = datetime.utcnow()
        
        db.commit()
        db.refresh(nc)
        
        return nc
    
    @staticmethod
    def add_root_cause(
        db: Session,
        nc_id: str,
        root_cause: str,
        contributing_factors: Optional[List[str]] = None
    ) -> NonConformity:
        """Add root cause analysis to NC"""
        nc = db.query(NonConformity).filter(NonConformity.id == nc_id).first()
        if not nc:
            raise ValueError(f"NC {nc_id} not found")
        
        nc.root_cause = root_cause
        if contributing_factors:
            import json
            nc.contributing_factors = json.dumps(contributing_factors)
        
        db.commit()
        db.refresh(nc)
        
        return nc
    
    @staticmethod
    def get_workspace_ncs(
        db: Session,
        workspace_id: str,
        status: Optional[NCStatus] = None,
        severity: Optional[NCSeverity] = None,
        limit: int = 100
    ) -> List[NonConformity]:
        """Get NCs for a workspace with filters"""
        query = db.query(NonConformity).filter(
            NonConformity.workspace_id == workspace_id
        )
        
        if status:
            query = query.filter(NonConformity.status == status)
        if severity:
            query = query.filter(NonConformity.severity == severity)
        
        return query.order_by(NonConformity.created_at.desc()).limit(limit).all()
    
    # ===== Corrective Action Management =====
    
    @staticmethod
    def create_ca(
        db: Session,
        workspace_id: str,
        title: str,
        description: str,
        action_plan: str,
        assigned_to: str,
        planned_start_date: date,
        planned_completion_date: date,
        nc_id: Optional[str] = None,
        priority: str = "medium"
    ) -> CorrectiveAction:
        """Create a new Corrective Action"""
        # Generate CA number
        year = datetime.now().year
        count = db.query(func.count(CorrectiveAction.id)).filter(
            CorrectiveAction.workspace_id == workspace_id
        ).scalar() or 0
        ca_number = f"CA-{year}-{count + 1:03d}"
        
        ca = CorrectiveAction(
            id=str(uuid.uuid4()),
            ca_number=ca_number,
            workspace_id=workspace_id,
            nc_id=nc_id,
            title=title,
            description=description,
            action_plan=action_plan,
            assigned_to=assigned_to,
            planned_start_date=planned_start_date,
            planned_completion_date=planned_completion_date,
            priority=priority,
            status=CAStatus.PLANNED
        )
        
        db.add(ca)
        db.commit()
        db.refresh(ca)
        
        return ca
    
    @staticmethod
    def update_ca_status(
        db: Session,
        ca_id: str,
        status: CAStatus,
        actual_date: Optional[date] = None
    ) -> CorrectiveAction:
        """Update CA status"""
        ca = db.query(CorrectiveAction).filter(CorrectiveAction.id == ca_id).first()
        if not ca:
            raise ValueError(f"CA {ca_id} not found")
        
        ca.status = status
        
        if status == CAStatus.IN_PROGRESS and not ca.actual_start_date:
            ca.actual_start_date = actual_date or date.today()
        
        if status == CAStatus.COMPLETED and not ca.actual_completion_date:
            ca.actual_completion_date = actual_date or date.today()
        
        db.commit()
        db.refresh(ca)
        
        return ca
    
    @staticmethod
    def verify_ca_effectiveness(
        db: Session,
        ca_id: str,
        is_effective: bool,
        effectiveness_results: str
    ) -> CorrectiveAction:
        """Verify CA effectiveness"""
        ca = db.query(CorrectiveAction).filter(CorrectiveAction.id == ca_id).first()
        if not ca:
            raise ValueError(f"CA {ca_id} not found")
        
        ca.is_effective = is_effective
        ca.effectiveness_results = effectiveness_results
        ca.effectiveness_check_date = date.today()
        ca.status = CAStatus.EFFECTIVE if is_effective else CAStatus.NOT_EFFECTIVE
        
        db.commit()
        db.refresh(ca)
        
        return ca
    
    # ===== Internal Audit Management =====
    
    @staticmethod
    def create_audit(
        db: Session,
        workspace_id: str,
        title: str,
        audit_type: str,
        scope_description: str,
        planned_date: date,
        lead_auditor: str,
        iso_standard_id: Optional[str] = None
    ) -> InternalAudit:
        """Create a new Internal Audit"""
        # Generate audit number
        year = datetime.now().year
        quarter = (datetime.now().month - 1) // 3 + 1
        count = db.query(func.count(InternalAudit.id)).filter(
            InternalAudit.workspace_id == workspace_id
        ).scalar() or 0
        audit_number = f"AUDIT-{year}-Q{quarter}-{count + 1:02d}"
        
        audit = InternalAudit(
            id=str(uuid.uuid4()),
            audit_number=audit_number,
            workspace_id=workspace_id,
            title=title,
            audit_type=audit_type,
            scope_description=scope_description,
            planned_date=planned_date,
            lead_auditor=lead_auditor,
            iso_standard_id=iso_standard_id,
            status=AuditStatus.PLANNED
        )
        
        db.add(audit)
        db.commit()
        db.refresh(audit)
        
        return audit
    
    @staticmethod
    def complete_audit(
        db: Session,
        audit_id: str,
        actual_date: date,
        major_findings: int,
        minor_findings: int,
        observations: int,
        findings_summary: str
    ) -> InternalAudit:
        """Complete an audit with findings"""
        audit = db.query(InternalAudit).filter(InternalAudit.id == audit_id).first()
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")
        
        audit.status = AuditStatus.COMPLETED
        audit.actual_date = actual_date
        audit.major_findings = major_findings
        audit.minor_findings = minor_findings
        audit.observations = observations
        audit.findings_summary = findings_summary
        
        db.commit()
        db.refresh(audit)
        
        return audit
    
    # ===== Analytics & Reporting =====
    
    @staticmethod
    def get_nc_statistics(
        db: Session,
        workspace_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get NC statistics for a workspace"""
        query = db.query(NonConformity).filter(
            NonConformity.workspace_id == workspace_id
        )
        
        if start_date:
            query = query.filter(NonConformity.detected_date >= start_date)
        if end_date:
            query = query.filter(NonConformity.detected_date <= end_date)
        
        ncs = query.all()
        
        total = len(ncs)
        by_status = {}
        by_severity = {}
        by_category = {}
        
        for nc in ncs:
            # Count by status
            status = nc.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by severity
            severity = nc.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by category
            if nc.category:
                by_category[nc.category] = by_category.get(nc.category, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "by_severity": by_severity,
            "by_category": by_category,
            "open_rate": by_status.get("open", 0) / total if total > 0 else 0,
            "closure_rate": by_status.get("closed", 0) / total if total > 0 else 0
        }
    
    @staticmethod
    def get_ca_effectiveness_rate(
        db: Session,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Calculate CA effectiveness rate"""
        cas = db.query(CorrectiveAction).filter(
            CorrectiveAction.workspace_id == workspace_id,
            CorrectiveAction.is_effective.isnot(None)
        ).all()
        
        total_verified = len(cas)
        effective = sum(1 for ca in cas if ca.is_effective)
        
        return {
            "total_verified": total_verified,
            "effective": effective,
            "not_effective": total_verified - effective,
            "effectiveness_rate": effective / total_verified if total_verified > 0 else 0
        }
    
    @staticmethod
    def get_audit_summary(
        db: Session,
        workspace_id: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get audit summary for a workspace"""
        query = db.query(InternalAudit).filter(
            InternalAudit.workspace_id == workspace_id
        )
        
        if year:
            from sqlalchemy import extract
            query = query.filter(extract('year', InternalAudit.planned_date) == year)
        
        audits = query.all()
        
        total = len(audits)
        completed = sum(1 for a in audits if a.status in [AuditStatus.COMPLETED, AuditStatus.REPORT_ISSUED])
        total_major = sum(a.major_findings for a in audits if a.major_findings)
        total_minor = sum(a.minor_findings for a in audits if a.minor_findings)
        
        return {
            "total_audits": total,
            "completed": completed,
            "in_progress": sum(1 for a in audits if a.status == AuditStatus.IN_PROGRESS),
            "planned": sum(1 for a in audits if a.status == AuditStatus.PLANNED),
            "total_major_findings": total_major,
            "total_minor_findings": total_minor,
            "completion_rate": completed / total if total > 0 else 0
        }
