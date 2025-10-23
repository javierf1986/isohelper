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
    AuditType, AuditStatus,
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
    def update_nc(
        db: Session,
        nc_id: str,
        workspace_id: str,
        **kwargs
    ) -> NonConformity:
        """Update NC with provided fields"""
        nc = db.query(NonConformity).filter(
            and_(
                NonConformity.id == nc_id,
                NonConformity.workspace_id == workspace_id
            )
        ).first()
        
        if not nc:
            raise ValueError(f"NC {nc_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(nc, key):
                setattr(nc, key, value)
        
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
    
    @staticmethod
    def get_nc_by_id(db: Session, nc_id: str, workspace_id: str) -> Optional[NonConformity]:
        """Get a single NC by ID"""
        return db.query(NonConformity).filter(
            and_(
                NonConformity.id == nc_id,
                NonConformity.workspace_id == workspace_id
            )
        ).first()
    
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
    def update_ca(
        db: Session,
        ca_id: str,
        workspace_id: str,
        **kwargs
    ) -> CorrectiveAction:
        """Update CA with provided fields"""
        ca = db.query(CorrectiveAction).filter(
            and_(
                CorrectiveAction.id == ca_id,
                CorrectiveAction.workspace_id == workspace_id
            )
        ).first()
        
        if not ca:
            raise ValueError(f"CA {ca_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(ca, key):
                setattr(ca, key, value)
        
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
    
    @staticmethod
    def get_workspace_cas(
        db: Session,
        workspace_id: str,
        status: Optional[CAStatus] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[CorrectiveAction]:
        """Get CAs for a workspace with optional filters"""
        query = db.query(CorrectiveAction).filter(
            CorrectiveAction.workspace_id == workspace_id
        )
        
        if status:
            query = query.filter(CorrectiveAction.status == status)
        
        if priority:
            query = query.filter(CorrectiveAction.priority == priority)
        
        return query.order_by(CorrectiveAction.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_ca_by_id(db: Session, ca_id: str, workspace_id: str) -> Optional[CorrectiveAction]:
        """Get a single CA by ID"""
        return db.query(CorrectiveAction).filter(
            and_(
                CorrectiveAction.id == ca_id,
                CorrectiveAction.workspace_id == workspace_id
            )
        ).first()
    
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
    def update_audit(
        db: Session,
        audit_id: str,
        workspace_id: str,
        **kwargs
    ) -> InternalAudit:
        """Update audit with provided fields"""
        audit = db.query(InternalAudit).filter(
            and_(
                InternalAudit.id == audit_id,
                InternalAudit.workspace_id == workspace_id
            )
        ).first()
        
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(audit, key):
                setattr(audit, key, value)
        
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
    
    @staticmethod
    def get_workspace_audits(
        db: Session,
        workspace_id: str,
        status: Optional[AuditStatus] = None,
        audit_type: Optional[AuditType] = None,
        limit: int = 100
    ) -> List[InternalAudit]:
        """Get audits for a workspace with optional filters"""
        query = db.query(InternalAudit).filter(
            InternalAudit.workspace_id == workspace_id
        )
        
        if status:
            query = query.filter(InternalAudit.status == status)
        
        if audit_type:
            query = query.filter(InternalAudit.audit_type == audit_type)
        
        return query.order_by(InternalAudit.planned_date.desc()).limit(limit).all()
    
    @staticmethod
    def get_audit_by_id(db: Session, audit_id: str, workspace_id: str) -> Optional[InternalAudit]:
        """Get a single audit by ID"""
        return db.query(InternalAudit).filter(
            and_(
                InternalAudit.id == audit_id,
                InternalAudit.workspace_id == workspace_id
            )
        ).first()
    
    # ===== Management Review Methods =====
    
    @staticmethod
    def get_review_by_id(db: Session, review_id: str, workspace_id: str) -> Optional[ManagementReview]:
        """Get a single management review by ID"""
        return db.query(ManagementReview).filter(
            and_(
                ManagementReview.id == review_id,
                ManagementReview.workspace_id == workspace_id
            )
        ).first()
    
    @staticmethod
    def get_training_by_id(db: Session, training_id: str, workspace_id: str) -> Optional[TrainingRecord]:
        """Get a single training record by ID"""
        return db.query(TrainingRecord).filter(
            and_(
                TrainingRecord.id == training_id,
                TrainingRecord.workspace_id == workspace_id
            )
        ).first()
    
    @staticmethod
    def get_complaint_by_id(db: Session, complaint_id: str, workspace_id: str) -> Optional[CustomerComplaint]:
        """Get a single customer complaint by ID"""
        return db.query(CustomerComplaint).filter(
            and_(
                CustomerComplaint.id == complaint_id,
                CustomerComplaint.workspace_id == workspace_id
            )
        ).first()
    
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
    
    # Management Review methods
    @staticmethod
    def create_management_review(
        db: Session,
        workspace_id: str,
        review_date: datetime,
        attendees: Optional[str] = None,
        agenda: Optional[str] = None,
        minutes: Optional[str] = None,
        decisions: Optional[str] = None,
        action_items: Optional[str] = None,
        next_review_date: Optional[datetime] = None,
        created_by: Optional[str] = None
    ) -> ManagementReview:
        """Create a new management review"""
        # Generate review number (MR-YYYY-QN format)
        year = review_date.year
        quarter = (review_date.month - 1) // 3 + 1
        
        # Find next number for this year and quarter
        existing = db.query(ManagementReview).filter(
            ManagementReview.workspace_id == workspace_id,
            ManagementReview.review_number.like(f"MR-{year}-Q{quarter}%")
        ).count()
        
        review_number = f"MR-{year}-Q{quarter}"
        if existing > 0:
            review_number = f"MR-{year}-Q{quarter}-{existing + 1}"
        
        review = ManagementReview(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            review_number=review_number,
            review_date=review_date,
            attendees=attendees,
            agenda=agenda,
            minutes=minutes,
            decisions=decisions,
            action_items=action_items,
            next_review_date=next_review_date,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    
    @staticmethod
    def update_management_review(
        db: Session,
        review_id: str,
        workspace_id: str,
        **kwargs
    ) -> ManagementReview:
        """Update management review with provided fields"""
        review = db.query(ManagementReview).filter(
            and_(
                ManagementReview.id == review_id,
                ManagementReview.workspace_id == workspace_id
            )
        ).first()
        
        if not review:
            raise ValueError(f"Management Review {review_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(review, key):
                setattr(review, key, value)
        
        db.commit()
        db.refresh(review)
        
        return review
    
    @staticmethod
    def get_workspace_reviews(
        db: Session,
        workspace_id: str,
        year: Optional[int] = None,
        limit: int = 100
    ) -> List[ManagementReview]:
        """Get management reviews for a workspace"""
        query = db.query(ManagementReview).filter(
            ManagementReview.workspace_id == workspace_id
        )
        
        if year:
            from sqlalchemy import extract
            query = query.filter(extract('year', ManagementReview.review_date) == year)
        
        return query.order_by(ManagementReview.review_date.desc()).limit(limit).all()
    
    # Training Record methods
    @staticmethod
    def create_training_record(
        db: Session,
        workspace_id: str,
        employee_id: str,
        training_title: str,
        training_date: datetime,
        trainer_name: Optional[str] = None,
        training_hours: Optional[float] = None,
        training_type: Optional[str] = None,
        competency_area: Optional[str] = None,
        passed: Optional[bool] = None,
        score: Optional[float] = None,
        certificate_number: Optional[str] = None,
        expiry_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> TrainingRecord:
        """Create a new training record"""
        record = TrainingRecord(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            employee_id=employee_id,
            training_title=training_title,
            training_date=training_date,
            trainer_name=trainer_name,
            training_hours=training_hours,
            training_type=training_type,
            competency_area=competency_area,
            passed=passed,
            score=score,
            certificate_number=certificate_number,
            expiry_date=expiry_date,
            notes=notes,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def update_training_record(
        db: Session,
        training_id: str,
        workspace_id: str,
        **kwargs
    ) -> TrainingRecord:
        """Update training record with provided fields"""
        training = db.query(TrainingRecord).filter(
            and_(
                TrainingRecord.id == training_id,
                TrainingRecord.workspace_id == workspace_id
            )
        ).first()
        
        if not training:
            raise ValueError(f"Training Record {training_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(training, key):
                setattr(training, key, value)
        
        db.commit()
        db.refresh(training)
        
        return training
    
    @staticmethod
    def get_workspace_training(
        db: Session,
        workspace_id: str,
        employee_id: Optional[str] = None,
        competency_area: Optional[str] = None,
        limit: int = 100
    ) -> List[TrainingRecord]:
        """Get training records for a workspace"""
        query = db.query(TrainingRecord).filter(
            TrainingRecord.workspace_id == workspace_id
        )
        
        if employee_id:
            query = query.filter(TrainingRecord.employee_id == employee_id)
        
        if competency_area:
            query = query.filter(TrainingRecord.competency_area == competency_area)
        
        return query.order_by(TrainingRecord.training_date.desc()).limit(limit).all()
    
    # Customer Complaint methods
    @staticmethod
    def create_customer_complaint(
        db: Session,
        workspace_id: str,
        complaint_title: str,
        complaint_description: str,
        customer_name: str,
        received_date: datetime,
        complaint_source: Optional[str] = None,
        product_service: Optional[str] = None,
        priority: Optional[str] = None,
        status: str = "OPEN",
        assigned_to: Optional[str] = None,
        resolution_target_date: Optional[datetime] = None,
        resolution_description: Optional[str] = None,
        resolution_date: Optional[datetime] = None,
        customer_satisfaction: Optional[str] = None,
        related_nc_id: Optional[str] = None,
        root_cause: Optional[str] = None,
        preventive_actions: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> CustomerComplaint:
        """Create a new customer complaint"""
        # Generate complaint number (CC-YYYY-NNN format)
        year = received_date.year
        
        # Find next number for this year
        existing = db.query(CustomerComplaint).filter(
            CustomerComplaint.workspace_id == workspace_id,
            CustomerComplaint.complaint_number.like(f"CC-{year}-%")
        ).count()
        
        complaint_number = f"CC-{year}-{existing + 1:03d}"
        
        complaint = CustomerComplaint(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            complaint_number=complaint_number,
            complaint_title=complaint_title,
            complaint_description=complaint_description,
            customer_name=customer_name,
            received_date=received_date,
            complaint_source=complaint_source,
            product_service=product_service,
            priority=priority,
            status=status,
            assigned_to=assigned_to,
            resolution_target_date=resolution_target_date,
            resolution_description=resolution_description,
            resolution_date=resolution_date,
            customer_satisfaction=customer_satisfaction,
            related_nc_id=related_nc_id,
            root_cause=root_cause,
            preventive_actions=preventive_actions,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint
    
    @staticmethod
    def update_customer_complaint(
        db: Session,
        complaint_id: str,
        workspace_id: str,
        **kwargs
    ) -> CustomerComplaint:
        """Update customer complaint with provided fields"""
        complaint = db.query(CustomerComplaint).filter(
            and_(
                CustomerComplaint.id == complaint_id,
                CustomerComplaint.workspace_id == workspace_id
            )
        ).first()
        
        if not complaint:
            raise ValueError(f"Customer Complaint {complaint_id} not found")
        
        # Update only provided fields
        for key, value in kwargs.items():
            if value is not None and hasattr(complaint, key):
                setattr(complaint, key, value)
        
        db.commit()
        db.refresh(complaint)
        
        return complaint
    
    @staticmethod
    def get_workspace_complaints(
        db: Session,
        workspace_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[CustomerComplaint]:
        """Get customer complaints for a workspace"""
        query = db.query(CustomerComplaint).filter(
            CustomerComplaint.workspace_id == workspace_id
        )
        
        if status:
            query = query.filter(CustomerComplaint.status == status)
        
        if priority:
            query = query.filter(CustomerComplaint.priority == priority)
        
        return query.order_by(CustomerComplaint.received_date.desc()).limit(limit).all()
