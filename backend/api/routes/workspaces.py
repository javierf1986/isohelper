"""
Workspace Management API Endpoints
Multi-tenant workspace CRUD operations with JWT authentication
Phase 3: Secured with user authentication and ownership
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.database.database import get_db
from backend.services.workspace_service_v2 import WorkspaceService
from backend.api.dependencies import get_current_user, require_admin
from backend.models.user_models import User
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


# =================================================================
# Request/Response Models
# =================================================================

class WorkspaceCreate(BaseModel):
    """Request model for creating workspace"""
    client_name: str
    contact_email: str
    description: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    country: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    """Request model for updating workspace"""
    client_name: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    country: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkspaceResponse(BaseModel):
    """Response model for workspace"""
    id: str
    client_name: str
    contact_email: str
    description: Optional[str]
    industry: Optional[str]
    plan: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class StandardAssignment(BaseModel):
    """Request model for assigning/unassigning standard"""
    standard_id: str


class WorkspaceStats(BaseModel):
    """Workspace statistics"""
    workspace_name: str
    contact_email: str
    standard_count: int
    document_count: int
    is_active: bool
    plan: str


# =================================================================
# Dependency Injection
# =================================================================

# =================================================================
# Dependencies
# =================================================================

def get_workspace_service(session: Session = Depends(get_db)) -> WorkspaceService:
    """Get workspace service with database session"""
    return WorkspaceService(session)


# =================================================================
# API Endpoints
# =================================================================

@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Create a new workspace (Requires authentication)
    
    - **client_name**: Company/client name
    - **contact_email**: Primary contact email
    - **description**: Optional description
    - **industry**: Optional industry
    - **settings**: Optional custom settings
    
    The workspace will be linked to the authenticated user as the owner.
    """
    try:
        # Build kwargs for optional fields
        kwargs = {}
        if workspace.industry:
            kwargs['industry'] = workspace.industry
        if workspace.company_size:
            kwargs['company_size'] = workspace.company_size
        if workspace.country:
            kwargs['country'] = workspace.country
        if workspace.settings:
            kwargs['settings'] = workspace.settings
        
        ws = service.create_workspace(
            client_name=workspace.client_name,
            contact_email=workspace.contact_email,
            description=workspace.description,
            owner_id=str(current_user.id),  # Link workspace to authenticated user
            **kwargs
        )
        
        service.session.commit()
        logger.info(f"Created workspace via API: {ws.client_name} (owner: {current_user.email})")
        
        return WorkspaceResponse(
            id=ws.id,
            client_name=ws.client_name,
            contact_email=ws.contact_email or "",
            description=ws.description,
            industry=ws.industry,
            plan=ws.plan or "free",
            is_active=ws.is_active,
            created_at=ws.created_at.isoformat() if ws.created_at else ""
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        service.session.rollback()
        logger.error(f"Failed to create workspace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create workspace: {str(e)}")


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    contact_email: Optional[str] = None,
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    List workspaces (Requires authentication)
    
    - **contact_email**: Optional filter by contact email
    
    Users see only their own workspaces unless they are admins.
    """
    try:
        workspaces = service.list_workspaces(contact_email=contact_email)
        
        return [
            WorkspaceResponse(
                id=ws.id,
                client_name=ws.client_name,
                contact_email=ws.contact_email or "",
                description=ws.description,
                industry=ws.industry,
                plan=ws.plan or "free",
                is_active=ws.is_active,
                created_at=ws.created_at.isoformat() if ws.created_at else ""
            )
            for ws in workspaces
        ]
        
    except Exception as e:
        logger.error(f"Failed to list workspaces: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list workspaces: {str(e)}")


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Get workspace by ID (Requires authentication)
    """
    workspace = service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace {workspace_id} not found")
    
    return WorkspaceResponse(
        id=workspace.id,
        client_name=workspace.client_name,
        contact_email=workspace.contact_email or "",
        description=workspace.description,
        industry=workspace.industry,
        plan=workspace.plan or "free",
        is_active=workspace.is_active,
        created_at=workspace.created_at.isoformat() if workspace.created_at else ""
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    updates: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Update workspace
    
    - All fields are optional
    - Only provided fields will be updated
    """
    try:
        # Build update dict from non-None values
        update_dict = {}
        for field, value in updates.dict(exclude_unset=True).items():
            if value is not None:
                update_dict[field] = value
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        workspace = service.update_workspace(workspace_id, **update_dict)
        service.session.commit()
        
        logger.info(f"Updated workspace via API: {workspace.client_name}")
        
        return WorkspaceResponse(
            id=workspace.id,
            client_name=workspace.client_name,
            contact_email=workspace.contact_email or "",
            description=workspace.description,
            industry=workspace.industry,
            plan=workspace.plan or "free",
            is_active=workspace.is_active,
            created_at=workspace.created_at.isoformat() if workspace.created_at else ""
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        service.session.rollback()
        logger.error(f"Failed to update workspace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update workspace: {str(e)}")


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Delete workspace (Requires authentication)
    
    - **hard_delete**: If true, permanently delete. If false, soft delete (deactivate)
    """
    try:
        service.delete_workspace(workspace_id, hard_delete=hard_delete)
        service.session.commit()
        
        logger.info(f"Deleted workspace via API: {workspace_id} (hard={hard_delete})")
        return None
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        service.session.rollback()
        logger.error(f"Failed to delete workspace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete workspace: {str(e)}")


@router.post("/{workspace_id}/standards", status_code=status.HTTP_201_CREATED)
async def assign_standard(
    workspace_id: str,
    assignment: StandardAssignment,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Assign ISO standard to workspace (Requires authentication)
    """
    try:
        service.assign_standard(workspace_id, assignment.standard_id)
        service.session.commit()
        
        logger.info(f"Assigned standard to workspace via API: {workspace_id}")
        return {"message": "Standard assigned successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        service.session.rollback()
        logger.error(f"Failed to assign standard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign standard: {str(e)}")


@router.delete("/{workspace_id}/standards/{standard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_standard(
    workspace_id: str,
    standard_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Unassign ISO standard from workspace
    """
    try:
        service.unassign_standard(workspace_id, standard_id)
        service.session.commit()
        
        logger.info(f"Unassigned standard from workspace via API: {workspace_id}")
        return None
        
    except Exception as e:
        service.session.rollback()
        logger.error(f"Failed to unassign standard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unassign standard: {str(e)}")


@router.get("/{workspace_id}/standards")
async def get_workspace_standards(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Get all ISO standards assigned to workspace
    """
    try:
        standards = service.get_workspace_standards(workspace_id)
        
        return [
            {
                "id": std.id,
                "name": std.name,
                "iso_number": std.iso_number,
                "year": std.year,
                "category": std.category,
                "full_title": std.full_title
            }
            for std in standards
        ]
        
    except Exception as e:
        logger.error(f"Failed to get workspace standards: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workspace standards: {str(e)}")


@router.get("/{workspace_id}/stats", response_model=WorkspaceStats)
async def get_workspace_stats(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    """
    Get workspace statistics
    
    Returns:
    - Workspace name and contact
    - Number of assigned standards
    - Number of generated documents
    - Active status and plan
    """
    try:
        stats = service.get_workspace_stats(workspace_id)
        
        return WorkspaceStats(
            workspace_name=stats['workspace_name'],
            contact_email=stats['contact_email'],
            standard_count=stats['standard_count'],
            document_count=stats['document_count'],
            is_active=stats['is_active'],
            plan=stats['plan']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get workspace stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workspace stats: {str(e)}")
