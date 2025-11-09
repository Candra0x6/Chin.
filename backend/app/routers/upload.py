"""
Video upload API router.
Handles video file uploads and stores metadata in Supabase.
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import VideoUploadResponse, ErrorResponse
from app.database import get_supabase, Tables
from app.utils.validators import VideoValidator, format_file_size
from app.utils.file_handler import FileHandler


# Initialize router
router = APIRouter(
    prefix="/api/upload",
    tags=["upload"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)

# Initialize validator and file handler
video_validator = VideoValidator(
    allowed_formats=settings.allowed_formats_list,
    max_size=settings.max_upload_size
)

file_handler = FileHandler(
    upload_dir=str(settings.get_upload_path())
)


async def store_video_metadata(
    video_id: str,
    filename: str,
    file_path: str,
    file_size: int,
    mime_type: str
) -> None:
    """
    Store video upload metadata in Supabase.
    
    Args:
        video_id: Unique video identifier
        filename: Original filename
        file_path: Path where file is stored
        file_size: Size of file in bytes
        mime_type: MIME type of file
    """
    try:
        supabase = get_supabase()
        
        video_data = {
            "id": video_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": mime_type,
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table(Tables.VIDEO_UPLOADS).insert(video_data).execute()
        
        if not response.data:
            raise Exception("Failed to store video metadata")
            
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Warning: Failed to store metadata in Supabase: {e}")


async def cleanup_failed_upload(file_path: str) -> None:
    """
    Clean up file if upload fails.
    
    Args:
        file_path: Path to file to delete
    """
    try:
        file_handler.delete_file(file_path)
    except Exception as e:
        print(f"Warning: Failed to cleanup file {file_path}: {e}")


@router.post(
    "",
    response_model=VideoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload video for analysis",
    description="Upload a video file of ER queue for crowd analysis. "
                "Supported formats: MP4, AVI, MOV, MKV. Max size: 100MB."
)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(
        ...,
        description="Video file to analyze",
        media_type="video/*"
    )
) -> VideoUploadResponse:
    """
    Upload video file endpoint.
    
    Process:
    1. Validate file (format, size, type)
    2. Generate unique ID
    3. Save file to disk
    4. Store metadata in Supabase
    5. Return upload confirmation
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded video file
        
    Returns:
        VideoUploadResponse with upload details and job ID
        
    Raises:
        HTTPException: If validation fails or upload error occurs
    """
    
    # Validate upload
    try:
        await video_validator.validate_upload(file)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    
    # Save file
    try:
        saved_filename, file_path = await file_handler.save_upload_file(file)
        file_size = file_handler.get_file_size(file_path)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Store metadata in Supabase (synchronously to ensure it's available for analysis)
    try:
        await store_video_metadata(
            video_id=video_id,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=file.content_type or "video/mp4"
        )
    except Exception as e:
        # Clean up file if metadata storage fails
        background_tasks.add_task(cleanup_failed_upload, str(file_path))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store upload metadata: {str(e)}"
        )
    
    # Return response
    return VideoUploadResponse(
        id=video_id,
        filename=file.filename,
        path=str(file_path),
        status="uploaded",
        message=(
            f"Video '{file.filename}' uploaded successfully. "
            f"Size: {format_file_size(file_size)}. "
            f"Video ID: {video_id}. "
            f"Processing will begin shortly."
        ),
        created_at=datetime.utcnow()
    )


@router.get(
    "/status/{video_id}",
    summary="Get upload status",
    description="Check the status of a video upload by ID"
)
async def get_upload_status(video_id: str) -> dict:
    """
    Get status of video upload.
    
    Args:
        video_id: UUID of uploaded video
        
    Returns:
        Upload status information
        
    Raises:
        HTTPException: If video not found
    """
    try:
        supabase = get_supabase()
        
        response = supabase.table(Tables.VIDEO_UPLOADS)\
            .select('*')\
            .eq('id', video_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video with ID {video_id} not found"
            )
        
        video_data = response.data[0]
        
        return {
            "id": video_data['id'],
            "filename": video_data['filename'],
            "status": video_data['status'],
            "file_size": video_data['file_size'],
            "uploaded_at": video_data['created_at'],
            "message": f"Video status: {video_data['status']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving upload status: {str(e)}"
        )


@router.delete(
    "/{video_id}",
    summary="Delete uploaded video",
    description="Delete an uploaded video file and its metadata"
)
async def delete_video(video_id: str) -> dict:
    """
    Delete uploaded video.
    
    Args:
        video_id: UUID of video to delete
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If video not found or deletion fails
    """
    try:
        supabase = get_supabase()
        
        # Get video metadata
        response = supabase.table(Tables.VIDEO_UPLOADS)\
            .select('*')\
            .eq('id', video_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video with ID {video_id} not found"
            )
        
        video_data = response.data[0]
        
        # Delete file from disk
        file_path = video_data['file_path']
        filename = file_path.split('/')[-1]  # Extract filename from path
        file_handler.delete_file(filename)
        
        # Delete metadata from database
        supabase.table(Tables.VIDEO_UPLOADS)\
            .delete()\
            .eq('id', video_id)\
            .execute()
        
        return {
            "message": f"Video {video_data['filename']} deleted successfully",
            "video_id": video_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting video: {str(e)}"
        )


@router.get(
    "/list",
    summary="List all uploads",
    description="Get list of all uploaded videos"
)
async def list_uploads(
    limit: int = 10,
    offset: int = 0,
    status_filter: Optional[str] = None
) -> dict:
    """
    List uploaded videos with pagination.
    
    Args:
        limit: Number of results to return (max 100)
        offset: Number of results to skip
        status_filter: Optional filter by status
        
    Returns:
        List of uploaded videos
    """
    try:
        supabase = get_supabase()
        
        # Build query
        query = supabase.table(Tables.VIDEO_UPLOADS).select('*')
        
        if status_filter:
            query = query.eq('status', status_filter)
        
        # Apply pagination and sorting
        query = query.order('created_at', desc=True)\
            .range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "videos": response.data,
            "count": len(response.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing uploads: {str(e)}"
        )
