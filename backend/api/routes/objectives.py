"""
Quality Objectives API Routes
ISO 6.2 - Quality objectives and planning
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import uuid

from backend.database.database import get_db
from backend.models.artifact_models import QualityObjective, ObjectiveStatus
from backend.models.user_models import User
from backend.api.dependencies import get_current_user

router = APIRouter()


# ===== Pydantic Schemas =====

class ObjectiveCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_value: str
    current_value: Optional[str] = None
    unit_of_measure: Optional[str] = None
    measurement_method: Optional[str] = None
    measurement_frequency: Optional[str] = None
    department: Optional[str] = None
    target_date: date
    start_date: Optional[date] = None
    iso_standard_id: Optional[str] = None
    related_clause: Optional[str] = None
    linked_processes: Optional[str] = None
    linked_risks: Optional[str] = None


class ObjectiveUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[str] = None
    current_value: Optional[str] = None
    unit_of_measure: Optional[str] = None
    measurement_method: Optional[str] = None
    measurement_frequency: Optional[str] = None
    status: Optional[ObjectiveStatus] = None
    progress_percentage: Optional[float] = None
    department: Optional[str] = None
    target_date: Optional[date] = None
    achieved_date: Optional[date] = None
    review_comments: Optional[str] = None
    evidence: Optional[str] = None
    progress_notes: Optional[str] = None


class ObjectiveResponse(BaseModel):
    id: str
    objective_number: str
    title: str
    description: Optional[str]
    target_value: str
    current_value: Optional[str]
    status: str
    progress_percentage: float
    responsible_person: str
    department: Optional[str]
    target_date: date
    achieved_date: Optional[date]
    related_clause: Optional[str]
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


# ===== API Endpoints =====

@router.get("/", response_model=List[ObjectiveResponse])
async def list_objectives(
    status: Optional[ObjectiveStatus] = None,
    department: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all quality objectives with optional filtering
    """
    query = db.query(QualityObjective).filter(
        QualityObjective.workspace_id == current_user.workspace_id
    )
    
    if status:
        query = query.filter(QualityObjective.status == status)
    
    if department:
        query = query.filter(QualityObjective.department == department)
    
    if is_active is not None:
        query = query.filter(QualityObjective.is_active == is_active)
    
    objectives = query.order_by(QualityObjective.target_date.desc()).offset(skip).limit(limit).all()
    
    return objectives


@router.post("/", response_model=ObjectiveResponse)
async def create_objective(
    objective: ObjectiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new quality objective
    """
    # Generate objective number
    year = datetime.now().year
    count = db.query(QualityObjective).filter(
        QualityObjective.workspace_id == current_user.workspace_id,
        func.extract('year', QualityObjective.created_at) == year
    ).count()
    
    objective_number = f"OBJ-{year}-{count + 1:03d}"
    
    new_objective = QualityObjective(
        id=str(uuid.uuid4()),
        workspace_id=current_user.workspace_id,
        objective_number=objective_number,
        title=objective.title,
        description=objective.description,
        target_value=objective.target_value,
        current_value=objective.current_value,
        unit_of_measure=objective.unit_of_measure,
        measurement_method=objective.measurement_method,
        measurement_frequency=objective.measurement_frequency,
        department=objective.department,
        responsible_person=current_user.id,
        target_date=objective.target_date,
        start_date=objective.start_date or date.today(),
        iso_standard_id=objective.iso_standard_id,
        related_clause=objective.related_clause,
        linked_processes=objective.linked_processes,
        linked_risks=objective.linked_risks,
        created_by=current_user.id,
        status=ObjectiveStatus.PLANNED
    )
    
    db.add(new_objective)
    db.commit()
    db.refresh(new_objective)
    
    return new_objective


@router.get("/{objective_id}", response_model=ObjectiveResponse)
async def get_objective(
    objective_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific quality objective by ID
    """
    objective = db.query(QualityObjective).filter(
        QualityObjective.id == objective_id,
        QualityObjective.workspace_id == current_user.workspace_id
    ).first()
    
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    return objective


@router.patch("/{objective_id}", response_model=ObjectiveResponse)
async def update_objective(
    objective_id: str,
    updates: ObjectiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a quality objective
    """
    objective = db.query(QualityObjective).filter(
        QualityObjective.id == objective_id,
        QualityObjective.workspace_id == current_user.workspace_id
    ).first()
    
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    # Update fields
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(objective, field, value)
    
    # Auto-set achieved_date if status changed to ACHIEVED
    if updates.status == ObjectiveStatus.ACHIEVED and not objective.achieved_date:
        objective.achieved_date = date.today()
        objective.progress_percentage = 100.0
    
    db.commit()
    db.refresh(objective)
    
    return objective


@router.patch("/{objective_id}/progress")
async def update_progress(
    objective_id: str,
    current_value: str,
    progress_percentage: float,
    note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update objective progress
    """
    objective = db.query(QualityObjective).filter(
        QualityObjective.id == objective_id,
        QualityObjective.workspace_id == current_user.workspace_id
    ).first()
    
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    objective.current_value = current_value
    objective.progress_percentage = min(100.0, max(0.0, progress_percentage))
    
    # Add progress note
    if note:
        import json
        notes = json.loads(objective.progress_notes) if objective.progress_notes else []
        notes.append({
            "date": date.today().isoformat(),
            "progress": progress_percentage,
            "note": note,
            "updated_by": current_user.id
        })
        objective.progress_notes = json.dumps(notes)
    
    # Auto-update status based on progress
    if progress_percentage >= 100.0:
        objective.status = ObjectiveStatus.ACHIEVED
        objective.achieved_date = date.today()
    elif progress_percentage > 0:
        objective.status = ObjectiveStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(objective)
    
    return {
        "success": True,
        "objective_id": objective_id,
        "current_value": current_value,
        "progress_percentage": progress_percentage
    }


@router.delete("/{objective_id}")
async def delete_objective(
    objective_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete (soft delete) a quality objective
    """
    objective = db.query(QualityObjective).filter(
        QualityObjective.id == objective_id,
        QualityObjective.workspace_id == current_user.workspace_id
    ).first()
    
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    objective.is_active = False
    db.commit()
    
    return {"success": True, "message": f"Objective {objective.objective_number} deleted"}


@router.get("/analytics/summary")
async def get_objectives_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics summary for quality objectives
    """
    workspace_id = current_user.workspace_id
    
    # Total objectives
    total = db.query(QualityObjective).filter(
        QualityObjective.workspace_id == workspace_id,
        QualityObjective.is_active == True
    ).count()
    
    # By status
    by_status = {}
    for status in ObjectiveStatus:
        count = db.query(QualityObjective).filter(
            QualityObjective.workspace_id == workspace_id,
            QualityObjective.status == status,
            QualityObjective.is_active == True
        ).count()
        by_status[status.value] = count
    
    # Achievement rate
    achieved = by_status.get(ObjectiveStatus.ACHIEVED.value, 0)
    achievement_rate = (achieved / total * 100) if total > 0 else 0
    
    # Average progress
    avg_progress = db.query(func.avg(QualityObjective.progress_percentage)).filter(
        QualityObjective.workspace_id == workspace_id,
        QualityObjective.is_active == True
    ).scalar() or 0.0
    
    # Overdue objectives
    today = date.today()
    overdue = db.query(QualityObjective).filter(
        QualityObjective.workspace_id == workspace_id,
        QualityObjective.target_date < today,
        QualityObjective.status != ObjectiveStatus.ACHIEVED,
        QualityObjective.status != ObjectiveStatus.CANCELLED,
        QualityObjective.is_active == True
    ).count()
    
    # By department
    by_department = {}
    departments = db.query(
        QualityObjective.department,
        func.count(QualityObjective.id)
    ).filter(
        QualityObjective.workspace_id == workspace_id,
        QualityObjective.is_active == True,
        QualityObjective.department.isnot(None)
    ).group_by(QualityObjective.department).all()
    
    for dept, count in departments:
        by_department[dept] = count
    
    return {
        "total_objectives": total,
        "by_status": by_status,
        "achievement_rate": round(achievement_rate, 1),
        "average_progress": round(avg_progress, 1),
        "overdue_count": overdue,
        "by_department": by_department
    }
