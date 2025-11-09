"""
Results API Router - Phase 7
Handles retrieval, listing, search, and export of analysis results
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import uuid

from app.database import get_supabase
from app.models import AnalysisResult
from app.utils.cleanup import setup_cleanup_endpoints


def validate_uuid(uuid_string: str, field_name: str = "ID") -> None:
    """Validate UUID format and raise 404 if invalid"""
    try:
        uuid.UUID(uuid_string)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=404,
            detail=f"Invalid {field_name} format"
        )

router = APIRouter(prefix="/api/results", tags=["results"])

# Add cleanup endpoints
setup_cleanup_endpoints(router)


# ============================================================================
# RETRIEVAL ENDPOINTS
# ============================================================================

@router.get("/{analysis_id}", response_model=Dict[str, Any])
async def get_analysis_result(analysis_id: str):
    """
    Retrieve a specific analysis result by ID
    
    Returns complete analysis including:
    - Video metadata
    - Crowd statistics
    - Density analysis
    - Bottleneck detection
    - Spatial distribution
    - Flow analysis
    - AI insights (if available)
    - Enhanced analytics
    
    Args:
        analysis_id: The unique identifier of the analysis
        
    Returns:
        Complete analysis result dictionary
        
    Raises:
        HTTPException 404: Analysis not found
        HTTPException 500: Database error
    """
    # Validate UUID format first
    validate_uuid(analysis_id, "Analysis ID")
    
    try:
        supabase = get_supabase()
        
        # Query Supabase for the analysis result
        response = supabase.table("ANALYSIS_RESULTS").select("*").eq("id", analysis_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis with ID {analysis_id} not found"
            )
        
        result = response.data[0]
        
        # Parse JSON fields if they're stored as strings
        if isinstance(result.get('results'), str):
            result['results'] = json.loads(result['results'])
        
        return {
            "analysis_id": result['id'],
            "video_id": result.get('video_id'),
            "video_name": result.get('video_name'),
            "created_at": result.get('created_at'),
            "status": result.get('status', 'completed'),
            "results": result['results']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )


@router.get("", response_model=Dict[str, Any])
async def list_analysis_results(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Results per page (max 100)"),
    video_name: Optional[str] = Query(None, description="Filter by video name (partial match)"),
    crowd_level: Optional[str] = Query(None, description="Filter by crowd level (Low, Medium, High, Very High)"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Sort field (created_at, video_name)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)")
):
    """
    List all analysis results with pagination and filtering
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Results per page (default: 10, max: 100)
    - video_name: Filter by video name (partial match)
    - crowd_level: Filter by crowd level
    - date_from: Filter results from date (inclusive)
    - date_to: Filter results to date (inclusive)
    - sort_by: Sort field (created_at or video_name)
    - sort_order: Sort direction (asc or desc)
    
    Returns:
        {
            "page": 1,
            "limit": 10,
            "total": 45,
            "total_pages": 5,
            "results": [...]
        }
    """
    try:
        supabase = get_supabase()
        
        # Start building the query
        query = supabase.table("ANALYSIS_RESULTS").select("*", count="exact")
        
        # Apply filters
        if video_name:
            query = query.ilike("video_name", f"%{video_name}%")
        
        if crowd_level:
            query = query.eq("results->>crowd_level", crowd_level)
        
        if date_from:
            query = query.gte("created_at", date_from)
        
        if date_to:
            # Add one day to include the entire end date
            end_date = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            query = query.lt("created_at", end_date.strftime("%Y-%m-%d"))
        
        # Apply sorting
        ascending = (sort_order.lower() == "asc")
        query = query.order(sort_by, desc=not ascending)
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        
        # Get total count
        total_count = response.count if hasattr(response, 'count') else len(response.data)
        total_pages = (total_count + limit - 1) // limit
        
        # Format results
        results = []
        for item in response.data:
            # Parse results JSON if needed
            results_data = item.get('results')
            if isinstance(results_data, str):
                results_data = json.loads(results_data)
            
            results.append({
                "analysis_id": item['id'],
                "video_id": item.get('video_id'),
                "video_name": item.get('video_name'),
                "created_at": item.get('created_at'),
                "crowd_level": results_data.get('crowd_level') if results_data else None,
                "peak_count": results_data.get('peak_count') if results_data else None,
                "suggested_nurses": results_data.get('suggested_nurses') if results_data else None,
                "status": item.get('status', 'completed')
            })
        
        return {
            "page": page,
            "limit": limit,
            "total": total_count,
            "total_pages": total_pages,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list analyses: {str(e)}"
        )


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@router.get("/search/advanced", response_model=Dict[str, Any])
async def search_analyses(
    query: Optional[str] = Query(None, description="Search in video name and results"),
    min_peak_count: Optional[int] = Query(None, description="Minimum peak count"),
    max_peak_count: Optional[int] = Query(None, description="Maximum peak count"),
    crowd_levels: Optional[str] = Query(None, description="Comma-separated crowd levels"),
    bottleneck_severity: Optional[str] = Query(None, description="Bottleneck severity (low, medium, high)"),
    has_ai_insights: Optional[bool] = Query(None, description="Filter by AI insights presence"),
    date_from: Optional[str] = Query(None, description="From date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="To date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Advanced search with multiple criteria
    
    Search Parameters:
    - query: Text search in video name
    - min_peak_count: Minimum peak people count
    - max_peak_count: Maximum peak people count
    - crowd_levels: Comma-separated levels (e.g., "Medium,High")
    - bottleneck_severity: Filter by bottleneck severity
    - has_ai_insights: Filter by presence of AI insights
    - date_from/date_to: Date range filter
    - page/limit: Pagination
    
    Returns:
        {
            "page": 1,
            "total": 15,
            "results": [...]
        }
    """
    try:
        supabase = get_supabase()
        
        # Start query
        db_query = supabase.table("ANALYSIS_RESULTS").select("*", count="exact")
        
        # Text search
        if query:
            db_query = db_query.ilike("video_name", f"%{query}%")
        
        # Date range
        if date_from:
            db_query = db_query.gte("created_at", date_from)
        if date_to:
            end_date = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            db_query = db_query.lt("created_at", end_date.strftime("%Y-%m-%d"))
        
        # Execute query
        db_query = db_query.order("created_at", desc=True)
        offset = (page - 1) * limit
        db_query = db_query.range(offset, offset + limit - 1)
        
        response = db_query.execute()
        
        # Post-processing filters (for JSON fields)
        filtered_results = []
        for item in response.data:
            results_data = item.get('results')
            if isinstance(results_data, str):
                results_data = json.loads(results_data)
            
            # Skip if no results data
            if not results_data:
                continue
            
            # Apply JSON field filters
            if min_peak_count is not None and results_data.get('peak_count', 0) < min_peak_count:
                continue
            
            if max_peak_count is not None and results_data.get('peak_count', 999) > max_peak_count:
                continue
            
            if crowd_levels:
                level_list = [l.strip() for l in crowd_levels.split(',')]
                if results_data.get('crowd_level') not in level_list:
                    continue
            
            if bottleneck_severity:
                bottlenecks = results_data.get('bottlenecks', [])
                if not any(b.get('severity', '').lower() == bottleneck_severity.lower() for b in bottlenecks):
                    continue
            
            if has_ai_insights is not None:
                has_insights = 'ai_insights' in results_data and results_data['ai_insights']
                if has_insights != has_ai_insights:
                    continue
            
            # Add to filtered results
            filtered_results.append({
                "analysis_id": item['id'],
                "video_id": item.get('video_id'),
                "video_name": item.get('video_name'),
                "created_at": item.get('created_at'),
                "crowd_level": results_data.get('crowd_level'),
                "peak_count": results_data.get('peak_count'),
                "avg_count": results_data.get('avg_count'),
                "suggested_nurses": results_data.get('suggested_nurses'),
                "bottleneck_count": len(results_data.get('bottlenecks', [])),
                "has_ai_insights": 'ai_insights' in results_data
            })
        
        return {
            "page": page,
            "limit": limit,
            "total": len(filtered_results),
            "results": filtered_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/{analysis_id}/export/json")
async def export_analysis_json(analysis_id: str):
    """
    Export analysis result as JSON file
    
    Args:
        analysis_id: The analysis ID to export
        
    Returns:
        JSON file download
    """
    # Validate UUID format first
    validate_uuid(analysis_id, "Analysis ID")
    
    try:
        # Get the analysis result
        supabase = get_supabase()
        response = supabase.table("ANALYSIS_RESULTS").select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        result = response.data[0]
        
        # Parse results if needed
        results_data = result.get('results')
        if isinstance(results_data, str):
            results_data = json.loads(results_data)
        
        # Convert datetime to string for JSON serialization
        created_at = result.get('created_at')
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        
        # Create export data
        export_data = {
            "analysis_id": result['id'],
            "video_name": result.get('video_name'),
            "created_at": created_at,
            "results": results_data
        }
        
        # Save to temp file
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        filename = f"analysis_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/{analysis_id}/export/summary")
async def export_analysis_summary(analysis_id: str):
    """
    Export analysis result as formatted summary text
    """
    # Validate UUID format first
    validate_uuid(analysis_id, "Analysis ID")
    
    try:
        # Get the analysis result
        supabase = get_supabase()
        response = supabase.table("ANALYSIS_RESULTS").select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        result = response.data[0]
        results_data = result.get('results')
        if isinstance(results_data, str):
            results_data = json.loads(results_data)
        
        # Generate summary text
        summary = f"""
================================================================================
Chin  - ANALYSIS SUMMARY
================================================================================

Analysis ID: {result['id']}
Video Name: {result.get('video_name', 'N/A')}
Analysis Date: {result.get('created_at', 'N/A')}

--------------------------------------------------------------------------------
CROWD STATISTICS
--------------------------------------------------------------------------------
Average People Count: {results_data.get('avg_count', 0):.1f}
Peak Count: {results_data.get('peak_count', 0)}
Total People Detected: {results_data.get('total_people', 0)}
Crowd Level: {results_data.get('crowd_level', 'N/A')}

Peak Congestion Time: {results_data.get('peak_congestion_time', 'N/A')}

--------------------------------------------------------------------------------
STAFFING RECOMMENDATION
--------------------------------------------------------------------------------
Suggested Nurses: {results_data.get('suggested_nurses', 0)}

Rationale:
{results_data.get('reasoning', 'Standard healthcare staffing ratios applied')}

--------------------------------------------------------------------------------
BOTTLENECK ANALYSIS
--------------------------------------------------------------------------------
Number of Bottlenecks Detected: {len(results_data.get('bottlenecks', []))}
"""
        
        # Add bottleneck details
        if results_data.get('bottlenecks'):
            for i, bottleneck in enumerate(results_data['bottlenecks'], 1):
                summary += f"\nBottleneck {i}:\n"
                summary += f"  Time Range: {bottleneck.get('start_time', 'N/A')} - {bottleneck.get('end_time', 'N/A')}\n"
                summary += f"  Severity: {bottleneck.get('severity', 'N/A')}\n"
                summary += f"  Average Count: {bottleneck.get('avg_count', 0):.1f}\n"
        
        # Add AI insights if available
        if results_data.get('ai_insights'):
            summary += "\n" + "="*80 + "\n"
            summary += "AI INSIGHTS\n"
            summary += "="*80 + "\n"
            summary += results_data['ai_insights'].get('summary', 'No summary available')
            summary += "\n"
        
        summary += "\n" + "="*80 + "\n"
        summary += "Generated by Chin  - Emergency Room Flow Analyzer\n"
        summary += "="*80 + "\n"
        
        # Save to file
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        filename = f"summary_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = results_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(summary)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="text/plain"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/stats/overview")
async def get_statistics_overview():
    """
    Get overall statistics across all analyses
    
    Returns:
        {
            "total_analyses": 45,
            "analyses_by_crowd_level": {...},
            "avg_peak_count": 12.5,
            "total_bottlenecks": 67,
            "analyses_with_ai_insights": 30
        }
    """
    try:
        supabase = get_supabase()
        
        # Get all analyses
        response = supabase.table("ANALYSIS_RESULTS").select("*").execute()
        
        total_analyses = len(response.data)
        crowd_levels = {}
        peak_counts = []
        total_bottlenecks = 0
        ai_insights_count = 0
        
        for item in response.data:
            results_data = item.get('results')
            if isinstance(results_data, str):
                results_data = json.loads(results_data)
            
            if not results_data:
                continue
            
            # Count crowd levels
            level = results_data.get('crowd_level', 'Unknown')
            crowd_levels[level] = crowd_levels.get(level, 0) + 1
            
            # Collect peak counts
            peak = results_data.get('peak_count', 0)
            if peak:
                peak_counts.append(peak)
            
            # Count bottlenecks
            bottlenecks = results_data.get('bottlenecks', [])
            total_bottlenecks += len(bottlenecks)
            
            # Check AI insights
            if results_data.get('ai_insights'):
                ai_insights_count += 1
        
        avg_peak = sum(peak_counts) / len(peak_counts) if peak_counts else 0
        
        return {
            "total_analyses": total_analyses,
            "analyses_by_crowd_level": crowd_levels,
            "avg_peak_count": round(avg_peak, 2),
            "total_bottlenecks": total_bottlenecks,
            "analyses_with_ai_insights": ai_insights_count,
            "avg_bottlenecks_per_analysis": round(total_bottlenecks / total_analyses, 2) if total_analyses > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )

# ============================================================================
# DELETE ENDPOINT
# ============================================================================


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Delete a specific analysis result
    """
    # Validate UUID format first
    validate_uuid(analysis_id, "Analysis ID")
    
    try:
        supabase = get_supabase()
        
        # Check if exists
        response = supabase.table("ANALYSIS_RESULTS").select("id").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Delete from database
        supabase.table("ANALYSIS_RESULTS").delete().eq("id", analysis_id).execute()
        
        return {
            "message": f"Analysis {analysis_id} deleted successfully",
            "analysis_id": analysis_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )
