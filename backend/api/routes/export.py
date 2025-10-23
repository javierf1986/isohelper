"""
Document Export API Routes
Phase 3: PDF/DOCX/HTML Export Endpoints

Provides REST API endpoints for exporting documents to various formats.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Literal
from pathlib import Path
import os

from backend.services.export_service import export_service, ExportFormat
from backend.api.dependencies import get_current_user
from backend.models.user_models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/export", tags=["Export"])


# ===== Request/Response Models =====

class ExportRequest(BaseModel):
    """Export document request"""
    document_path: str
    format: ExportFormat
    company_name: Optional[str] = None
    include_branding: bool = True
    output_filename: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_path": "generated_documents/iso9001_manual.md",
                "format": "pdf",
                "company_name": "Acme Corporation",
                "include_branding": True,
                "output_filename": "QMS_Manual_v1.0"
            }
        }


class ExportResponse(BaseModel):
    """Export result response"""
    success: bool
    format: str
    file_path: str
    file_size_bytes: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "format": "pdf",
                "file_path": "generated_documents/exports/QMS_Manual_v1.0.pdf",
                "file_size_bytes": 245678,
                "message": "Document exported successfully to PDF"
            }
        }


# ===== Export Endpoints =====

@router.post("/", response_model=ExportResponse)
async def export_document(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Export a document to PDF, DOCX, or HTML format.
    
    Requires authentication. Exports markdown documents to professional
    formats with optional company branding.
    
    - **document_path**: Path to source markdown document
    - **format**: Output format (pdf, docx, html)
    - **company_name**: Optional company name for headers/footers
    - **include_branding**: Include headers/footers (default: true)
    - **output_filename**: Custom filename without extension
    
    Returns file path and metadata of exported document.
    """
    try:
        logger.info(f"User {current_user.email} requesting export: {request.document_path} to {request.format}")
        
        # Validate source file exists
        source_path = Path(request.document_path)
        if not source_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Source document not found: {request.document_path}"
            )
        
        # Validate format
        if request.format not in ["pdf", "docx", "html"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {request.format}. Must be pdf, docx, or html"
            )
        
        # Export document
        output_path = export_service.export_document(
            document_path=request.document_path,
            format=request.format,
            company_name=request.company_name,
            include_branding=request.include_branding,
            output_filename=request.output_filename
        )
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        return ExportResponse(
            success=True,
            format=request.format,
            file_path=output_path,
            file_size_bytes=file_size,
            message=f"Document exported successfully to {request.format.upper()}"
        )
    
    except FileNotFoundError as e:
        logger.error(f"Export failed - file not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValueError as e:
        logger.error(f"Export failed - invalid value: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Export failed with error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/download/{file_name}")
async def download_exported_file(
    file_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download an exported file.
    
    Requires authentication. Returns the exported file for download.
    
    - **file_name**: Name of the exported file (with extension)
    
    Returns the file as a downloadable attachment.
    """
    try:
        logger.info(f"User {current_user.email} downloading: {file_name}")
        
        # Construct file path
        file_path = export_service.exports_path / file_name
        
        # Validate file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_name}"
            )
        
        # Validate file is in exports directory (security check)
        if not str(file_path.resolve()).startswith(str(export_service.exports_path.resolve())):
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        # Determine media type based on extension
        extension = file_path.suffix.lower()
        media_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.html': 'text/html'
        }
        
        media_type = media_types.get(extension, 'application/octet-stream')
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=file_name,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


@router.get("/list")
async def list_exported_files(
    current_user: User = Depends(get_current_user),
    format: Optional[str] = Query(None, description="Filter by format (pdf, docx, html)")
):
    """
    List all exported files.
    
    Requires authentication. Returns a list of available exported documents.
    
    - **format**: Optional filter by file format
    
    Returns list of exported files with metadata.
    """
    try:
        logger.info(f"User {current_user.email} listing exported files")
        
        # Get all files in exports directory
        files = []
        
        for file_path in export_service.exports_path.iterdir():
            if file_path.is_file():
                # Filter by format if specified
                if format and not file_path.suffix.lower() == f".{format}":
                    continue
                
                files.append({
                    "filename": file_path.name,
                    "format": file_path.suffix[1:],  # Remove the dot
                    "size_bytes": file_path.stat().st_size,
                    "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    "download_url": f"/api/v1/export/download/{file_path.name}"
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "total": len(files),
            "files": files
        }
    
    except Exception as e:
        logger.error(f"List files failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )


@router.delete("/{file_name}")
async def delete_exported_file(
    file_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an exported file.
    
    Requires authentication. Removes the specified exported file.
    
    - **file_name**: Name of the file to delete
    
    Returns success message.
    """
    try:
        logger.info(f"User {current_user.email} deleting: {file_name}")
        
        # Construct file path
        file_path = export_service.exports_path / file_name
        
        # Validate file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_name}"
            )
        
        # Validate file is in exports directory (security check)
        if not str(file_path.resolve()).startswith(str(export_service.exports_path.resolve())):
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        # Delete file
        file_path.unlink()
        
        logger.info(f"File deleted successfully: {file_name}")
        
        return {
            "success": True,
            "message": f"File {file_name} deleted successfully"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )


# Import datetime for file listing
from datetime import datetime
