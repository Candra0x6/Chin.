"""
Analysis API Router
Endpoints for video analysis and result retrieval.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Path as PathParam
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime
import uuid
import json

from app.database import get_supabase, Tables
from app.models import AnalysisResponse, AnalysisStatusResponse, AnalysisListResponse, AnalysisRequest
from app.services.video_analysis import VideoAnalysisService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

# Global analysis service instance
analysis_service: Optional[VideoAnalysisService] = None

# In-memory storage for analysis progress (in production, use Redis or database)
analysis_progress: Dict[str, Dict] = {}


def get_analysis_service(
    show_visual: bool = False,
    save_annotated_video: bool = False,
    output_video_path: Optional[Path] = None,
    frame_sample_rate: int = 30,
    confidence_threshold: float = 0.5,
    enable_ai_insights: bool = True,
    gemini_api_key: Optional[str] = None
) -> VideoAnalysisService:
    """
    Get or create the video analysis service instance with specified configuration.
    
    Args:
        show_visual: Show real-time visual display
        save_annotated_video: Save annotated video to file
        output_video_path: Path to save annotated video
        frame_sample_rate: Process every Nth frame
        confidence_threshold: Detection confidence threshold
        enable_ai_insights: Enable AI-powered insights generation
        gemini_api_key: Google Gemini API key (optional, can use env var)
    """
    # Create new service with specified configuration
    service = VideoAnalysisService(
        frame_sample_rate=frame_sample_rate,
        confidence_threshold=confidence_threshold,
        max_frames=None,  # Process all frames
        show_visual=show_visual,
        save_annotated_video=save_annotated_video,
        output_video_path=output_video_path,
        enable_ai_insights=enable_ai_insights,
        gemini_api_key=gemini_api_key
    )
    
    logger.info(f"Video analysis service created (visual={show_visual}, save={save_annotated_video}, ai={enable_ai_insights})")
    return service


async def run_video_analysis(
    video_id: str,
    analysis_id: str,
    video_path: Path,
    show_visual: bool = False,
    save_annotated_video: bool = False,
    frame_sample_rate: int = 30,
    confidence_threshold: float = 0.5,
    enable_ai_insights: bool = True,
    gemini_api_key: Optional[str] = None
):
    """
    Background task to run video analysis.
    
    Args:
        video_id: ID of the uploaded video
        analysis_id: ID for this analysis
        video_path: Path to video file
        show_visual: Show real-time visual display
        save_annotated_video: Save annotated video to file
        frame_sample_rate: Process every Nth frame
        confidence_threshold: Detection confidence threshold
        enable_ai_insights: Enable AI-powered insights
        gemini_api_key: Gemini API key (optional)
    """
    try:
        logger.info(f"Starting background analysis for video {video_id}")
        
        # Update progress
        analysis_progress[analysis_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Initializing..."
        }
        
        # Progress callback
        def progress_callback(current: int, total: int, message: str):
            analysis_progress[analysis_id] = {
                "status": "processing",
                "progress": current,
                "message": message
            }
        
        # Prepare output path for annotated video if requested
        output_video_path = None
        if save_annotated_video:
            results_dir = settings.RESULTS_DIR
            results_dir.mkdir(parents=True, exist_ok=True)
            output_video_path = results_dir / f"annotated_{video_id}.mp4"
        
        # Run analysis
        service = get_analysis_service(
            show_visual=show_visual,
            save_annotated_video=save_annotated_video,
            output_video_path=output_video_path,
            frame_sample_rate=frame_sample_rate,
            confidence_threshold=confidence_threshold,
            enable_ai_insights=enable_ai_insights,
            gemini_api_key=gemini_api_key
        )
        results = service.analyze_video(
            video_path=video_path,
            progress_callback=progress_callback,
            save_detections=True
        )
        
        if results.get("status") == "completed":
            # Save results to database
            supabase = get_supabase()
            
            # Get video info for video_name
            video_info = supabase.table(Tables.VIDEO_UPLOADS).select("filename").eq("id", video_id).execute()
            video_name = video_info.data[0]["filename"] if video_info.data else "Unknown"
            
            analysis_data = {
                "id": analysis_id,
                "video_id": video_id,
                "video_name": video_name,
                "status": "completed",
                "duration_seconds": float(results["video_metadata"]["duration_seconds"]),
                "frames_processed": int(results["processing_info"]["frames_processed"]),
                "results": results,  # Full results as JSONB
                "crowd_level": results["insights"]["crowd_level"],
                "peak_count": int(results["statistics"]["max_person_count"]),
                "avg_count": float(results["statistics"]["average_person_count"]),
                "suggested_nurses": int(results["insights"]["suggested_nurses"]),
                "processing_time_seconds": float(results["processing_info"]["processing_time_seconds"]),
                "ai_summary": results["insights"]["summary"],
                "created_at": datetime.now().isoformat()
            }
            
            response = supabase.table(Tables.ANALYSIS_RESULTS).insert(analysis_data).execute()
            
            # Update progress
            analysis_progress[analysis_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Analysis complete!",
                "analysis_id": analysis_id
            }
            
            logger.info(f"Analysis completed for video {video_id}: {analysis_id}")
            
        else:
            # Analysis failed
            error_message = results.get("error", "Unknown error")
            
            # Save error to database with required fields
            supabase = get_supabase()
            
            # Get video info
            video_info = supabase.table(Tables.VIDEO_UPLOADS).select("filename").eq("id", video_id).execute()
            video_name = video_info.data[0]["filename"] if video_info.data else "Unknown"
            
            error_data = {
                "id": analysis_id,
                "video_id": video_id,
                "video_name": video_name,
                "status": "failed",
                "duration_seconds": 0.0,
                "frames_processed": 0,
                "results": {},  # Empty JSONB object
                "error_message": error_message,
                "error_details": str(results.get("error_details", "")),
                "created_at": datetime.now().isoformat()
            }
            
            supabase.table(Tables.ANALYSIS_RESULTS).insert(error_data).execute()
            
            analysis_progress[analysis_id] = {
                "status": "failed",
                "progress": 0,
                "message": f"Analysis failed: {error_message}"
            }
            
            logger.error(f"Analysis failed for video {video_id}: {error_message}")
    
    except Exception as e:
        # Capture full traceback
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in background analysis: {e}\n{error_traceback}")
        
        # Update progress with error
        analysis_progress[analysis_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        }
        
        # Try to save error to database
        try:
            supabase = get_supabase()
            
            # Get video info
            try:
                video_info = supabase.table(Tables.VIDEO_UPLOADS).select("filename").eq("id", video_id).execute()
                video_name = video_info.data[0]["filename"] if video_info.data else "Unknown"
            except:
                video_name = "Unknown"
            
            error_data = {
                "id": analysis_id,
                "video_id": video_id,
                "video_name": video_name,
                "status": "failed",
                "duration_seconds": 0.0,
                "frames_processed": 0,
                "results": {},  # Empty JSONB object
                "error_message": str(e),
                "error_details": error_traceback,
                "created_at": datetime.now().isoformat()
            }
            
            supabase.table(Tables.ANALYSIS_RESULTS).insert(error_data).execute()
        except Exception as db_error:
            logger.error(f"Failed to save error to database: {db_error}")


@router.post("/{video_id}", response_model=AnalysisResponse)
async def start_analysis(
    video_id: str = PathParam(..., description="ID of the uploaded video"),
    request: AnalysisRequest = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Start video analysis for an uploaded video.
    
    The analysis runs in the background. Use the returned analysis_id to check progress.
    
    - **video_id**: ID of the uploaded video (can be in path or request body)
    - **show_visual**: Enable real-time visual display with bounding boxes (default: False)
    - **save_annotated_video**: Save video with bounding boxes to file (default: False)
    - **frame_sample_rate**: Process every Nth frame (default: 30, use 1 for all frames)
    - **confidence_threshold**: Detection confidence threshold 0.0-1.0 (default: 0.5)
    
    Returns:
    - **analysis_id**: Unique ID for this analysis
    - **status**: Initial status (processing)
    - **message**: Status message
    
    Note: Visual display (show_visual=True) only works when running locally, not in production API.
    """
    try:
        # Use request body if provided, otherwise use defaults
        if request is None:
            request = AnalysisRequest(upload_id=video_id)
        
        # Override video_id from path if different
        if request.upload_id != video_id:
            logger.warning(f"Video ID mismatch: path={video_id}, body={request.upload_id}. Using path.")
            request.upload_id = video_id
        
        # Check if video exists in database
        supabase = get_supabase()
        response = supabase.table(Tables.VIDEO_UPLOADS).select("*").eq("id", video_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
        
        video_data = response.data[0]
        video_path = Path(video_data["file_path"])
        
        # Check if video file exists
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video file not found: {video_path}")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Initialize progress
        analysis_progress[analysis_id] = {
            "status": "queued",
            "progress": 0,
            "message": "Analysis queued...",
            "visual_display": request.show_visual,
            "save_annotated": request.save_annotated_video
        }
        
        # Start background task with visual options
        background_tasks.add_task(
            run_video_analysis,
            video_id=video_id,
            analysis_id=analysis_id,
            video_path=video_path,
            show_visual=request.show_visual,
            save_annotated_video=request.save_annotated_video,
            frame_sample_rate=request.frame_sample_rate,
            confidence_threshold=request.confidence_threshold,
            enable_ai_insights=request.enable_ai_insights,
            gemini_api_key=request.gemini_api_key
        )
        
        logger.info(f"Analysis started for video {video_id}: {analysis_id} (visual={request.show_visual}, ai={request.enable_ai_insights})")
        
        message = "Video analysis started. Use /analyze/status/{analysis_id} to check progress."
        if request.show_visual:
            message += " Visual display will open in a new window."
        if request.save_annotated_video:
            message += " Annotated video will be saved to results folder."
        if request.enable_ai_insights:
            message += " AI-powered insights will be generated."
        
        return {
            "analysis_id": analysis_id,
            "video_id": video_id,
            "status": "processing",
            "message": message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@router.get("/status/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Get the status and progress of an ongoing analysis.
    
    - **analysis_id**: ID returned from POST /analyze/{video_id}
    
    Returns:
    - **status**: Current status (queued, processing, completed, failed)
    - **progress**: Progress percentage (0-100)
    - **message**: Status message
    - **result**: Full analysis results (only when completed)
    """
    try:
        # Check in-memory progress first
        if analysis_id in analysis_progress:
            progress_data = analysis_progress[analysis_id]
            
            # If completed, fetch from database
            if progress_data["status"] == "completed":
                supabase = get_supabase()
                response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
                
                if response.data:
                    result = response.data[0]
                    return {
                        "analysis_id": analysis_id,
                        "status": "completed",
                        "progress": 100,
                        "message": "Analysis completed successfully",
                        "result": result
                    }
            
            return {
                "analysis_id": analysis_id,
                **progress_data
            }
        
        # Check database for completed/failed analysis
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
        
        if response.data:
            result = response.data[0]
            status = result.get("status", "unknown")
            
            return {
                "analysis_id": analysis_id,
                "status": status,
                "progress": 100 if status == "completed" else 0,
                "message": result.get("error_message") if status == "failed" else "Analysis completed",
                "result": result if status == "completed" else None
            }
        
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis status: {str(e)}")


@router.get("/results/{analysis_id}")
async def get_analysis_results(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Get the full results of a completed analysis.
    
    - **analysis_id**: ID of the completed analysis
    
    Returns complete analysis results including:
    - Video metadata
    - Person detection statistics
    - Timeline data
    - Peak congestion frames
    - AI-generated insights
    """
    try:
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis results not found: {analysis_id}")
        
        result = response.data[0]
        
        if result.get("status") != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Analysis not completed. Status: {result.get('status')}"
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis results: {str(e)}")


@router.get("/list", response_model=AnalysisListResponse)
async def list_analyses(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None
):
    """
    List all analyses with pagination and filtering.
    
    - **limit**: Maximum number of results (default: 10)
    - **offset**: Number of results to skip (default: 0)
    - **status**: Filter by status (queued, processing, completed, failed)
    
    Returns list of analyses with metadata.
    """
    try:
        supabase = get_supabase()
        
        # Build query
        query = supabase.table(Tables.ANALYSIS_RESULTS).select("*")
        
        # Apply filters
        if status:
            query = query.eq("status", status)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        
        # Execute query
        response = query.execute()
        
        return {
            "analyses": response.data,
            "total": len(response.data),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list analyses: {str(e)}")


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str = PathParam(..., description="ID of the analysis to delete")
):
    """
    Delete an analysis and its results.
    
    - **analysis_id**: ID of the analysis to delete
    
    Returns confirmation message.
    """
    try:
        supabase = get_supabase()
        
        # Check if analysis exists
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("id").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
        
        # Delete from database
        supabase.table(Tables.ANALYSIS_RESULTS).delete().eq("id", analysis_id).execute()
        
        # Remove from in-memory progress
        if analysis_id in analysis_progress:
            del analysis_progress[analysis_id]
        
        logger.info(f"Analysis deleted: {analysis_id}")
        
        return {
            "message": "Analysis deleted successfully",
            "analysis_id": analysis_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete analysis: {str(e)}")


@router.get("/service/info")
async def get_service_info():
    """
    Get information about the analysis service configuration.
    
    Returns service configuration and model information.
    """
    try:
        service = get_analysis_service()
        return service.get_service_info()
    except Exception as e:
        logger.error(f"Error getting service info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service info: {str(e)}")


@router.get("/analytics/{analysis_id}")
async def get_enhanced_analytics(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Get enhanced analytics for a completed analysis.
    
    Returns detailed crowd analytics including:
    - Crowd density calculations
    - Spatial distribution analysis
    - Bottleneck detection
    - Time-series visualization data
    - Flow metrics
    
    - **analysis_id**: ID of the completed analysis
    """
    try:
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
        
        result = response.data[0]
        
        if result.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Analysis not completed. Status: {result.get('status')}"
            )
        
        # Extract enhanced analytics from full results
        full_results = result.get("full_results", {})
        enhanced_analytics = full_results.get("enhanced_analytics", {})
        
        if not enhanced_analytics:
            raise HTTPException(
                status_code=404,
                detail="Enhanced analytics not available for this analysis"
            )
        
        return {
            "analysis_id": analysis_id,
            "video_id": result.get("video_id"),
            "analytics": enhanced_analytics
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced analytics: {str(e)}")


@router.get("/bottlenecks/{analysis_id}")
async def get_bottleneck_analysis(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Get bottleneck analysis for a completed analysis.
    
    Returns:
    - Detected bottleneck periods
    - Severity levels
    - Duration and timing
    - Recommendations
    
    - **analysis_id**: ID of the completed analysis
    """
    try:
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
        
        result = response.data[0]
        full_results = result.get("full_results", {})
        enhanced_analytics = full_results.get("enhanced_analytics", {})
        bottleneck_analysis = enhanced_analytics.get("bottleneck_analysis", {})
        
        if not bottleneck_analysis:
            raise HTTPException(
                status_code=404,
                detail="Bottleneck analysis not available"
            )
        
        return {
            "analysis_id": analysis_id,
            "video_id": result.get("video_id"),
            "bottleneck_analysis": bottleneck_analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bottleneck analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get bottleneck analysis: {str(e)}")


@router.get("/visualization/{analysis_id}")
async def get_visualization_data(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Get visualization-ready time-series data for a completed analysis.
    
    Returns data formatted for charts and graphs:
    - Time-series person counts
    - Interval aggregations
    - Summary statistics
    
    - **analysis_id**: ID of the completed analysis
    """
    try:
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
        
        result = response.data[0]
        full_results = result.get("full_results", {})
        enhanced_analytics = full_results.get("enhanced_analytics", {})
        viz_data = enhanced_analytics.get("visualization_data", {})
        
        if not viz_data:
            raise HTTPException(
                status_code=404,
                detail="Visualization data not available"
            )
        
        return {
            "analysis_id": analysis_id,
            "video_id": result.get("video_id"),
            "visualization_data": viz_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get visualization data: {str(e)}")

