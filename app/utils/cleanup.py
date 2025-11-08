"""
Cleanup Utilities - Phase 7
Handles cleanup of old uploads, expired sessions, and temporary files
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import logging

from app.config import settings
from app.database import get_supabase

logger = logging.getLogger(__name__)


class CleanupManager:
    """
    Manager for cleaning up old files and data
    """
    
    def __init__(self, retention_days: int = 30):
        """
        Initialize cleanup manager
        
        Args:
            retention_days: Number of days to retain files (default: 30)
        """
        self.retention_days = retention_days
        self.cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    def cleanup_old_uploads(self) -> Dict[str, any]:
        """
        Remove uploaded video files older than retention period
        
        Returns:
            {
                "files_removed": 5,
                "space_freed_mb": 245.6,
                "files": ["video1.mp4", ...]
            }
        """
        upload_dir = settings.get_upload_path()
        
        if not upload_dir.exists():
            logger.warning(f"Upload directory does not exist: {upload_dir}")
            return {"files_removed": 0, "space_freed_mb": 0, "files": []}
        
        files_removed = []
        total_size = 0
        
        try:
            for file_path in upload_dir.glob("*"):
                if file_path.is_file():
                    # Check file age
                    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if modified_time < self.cutoff_date:
                        # Record size before deletion
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        
                        # Delete file
                        file_path.unlink()
                        files_removed.append(file_path.name)
                        logger.info(f"Removed old upload: {file_path.name}")
            
            return {
                "files_removed": len(files_removed),
                "space_freed_mb": round(total_size / (1024 * 1024), 2),
                "files": files_removed
            }
            
        except Exception as e:
            logger.error(f"Error during upload cleanup: {e}")
            raise
    
    def cleanup_old_results(self) -> Dict[str, any]:
        """
        Remove exported result files older than retention period
        
        Returns:
            {
                "files_removed": 3,
                "space_freed_mb": 1.2,
                "files": ["result1.json", ...]
            }
        """
        results_dir = settings.get_results_path()
        
        if not results_dir.exists():
            logger.warning(f"Results directory does not exist: {results_dir}")
            return {"files_removed": 0, "space_freed_mb": 0, "files": []}
        
        files_removed = []
        total_size = 0
        
        try:
            for file_path in results_dir.glob("*"):
                if file_path.is_file():
                    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if modified_time < self.cutoff_date:
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        
                        file_path.unlink()
                        files_removed.append(file_path.name)
                        logger.info(f"Removed old result: {file_path.name}")
            
            return {
                "files_removed": len(files_removed),
                "space_freed_mb": round(total_size / (1024 * 1024), 2),
                "files": files_removed
            }
            
        except Exception as e:
            logger.error(f"Error during results cleanup: {e}")
            raise
    
    def cleanup_orphaned_files(self) -> Dict[str, any]:
        """
        Remove files that have no corresponding database entry
        
        Returns:
            {
                "uploads_orphaned": 2,
                "results_orphaned": 1
            }
        """
        try:
            supabase = get_supabase()
            
            # Get all analysis results from database
            response = supabase.table("ANALYSIS_RESULTS").select("video_id, video_name").execute()
            
            # Create set of valid video names
            valid_videos = set()
            for item in response.data:
                if item.get('video_name'):
                    valid_videos.add(item['video_name'])
            
            # Check upload directory
            upload_dir = settings.get_upload_path()
            uploads_removed = 0
            
            if upload_dir.exists():
                for file_path in upload_dir.glob("*"):
                    if file_path.is_file() and file_path.name not in valid_videos:
                        file_path.unlink()
                        uploads_removed += 1
                        logger.info(f"Removed orphaned upload: {file_path.name}")
            
            return {
                "uploads_orphaned": uploads_removed,
                "message": f"Removed {uploads_removed} orphaned files"
            }
            
        except Exception as e:
            logger.error(f"Error during orphaned file cleanup: {e}")
            raise
    
    def cleanup_old_database_records(self, days: int = 90) -> Dict[str, any]:
        """
        Archive or delete old analysis records from database
        
        Args:
            days: Records older than this will be removed (default: 90)
        
        Returns:
            {
                "records_removed": 5,
                "cutoff_date": "2024-01-01"
            }
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff.strftime("%Y-%m-%d")
            
            supabase = get_supabase()
            
            # Get old records
            response = supabase.table("ANALYSIS_RESULTS").select("id").lt("created_at", cutoff_str).execute()
            
            old_records = len(response.data)
            
            # Delete old records
            if old_records > 0:
                supabase.table("ANALYSIS_RESULTS").delete().lt("created_at", cutoff_str).execute()
                logger.info(f"Removed {old_records} old database records")
            
            return {
                "records_removed": old_records,
                "cutoff_date": cutoff_str
            }
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
            raise
    
    def get_storage_stats(self) -> Dict[str, any]:
        """
        Get current storage statistics
        
        Returns:
            {
                "uploads": {"count": 10, "size_mb": 1024.5},
                "results": {"count": 5, "size_mb": 2.3},
                "total_size_mb": 1026.8
            }
        """
        def get_dir_stats(directory: Path) -> Dict[str, any]:
            if not directory.exists():
                return {"count": 0, "size_mb": 0}
            
            files = list(directory.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            return {
                "count": len([f for f in files if f.is_file()]),
                "size_mb": round(total_size / (1024 * 1024), 2)
            }
        
        upload_stats = get_dir_stats(settings.get_upload_path())
        results_stats = get_dir_stats(settings.get_results_path())
        
        return {
            "uploads": upload_stats,
            "results": results_stats,
            "total_size_mb": round(upload_stats["size_mb"] + results_stats["size_mb"], 2)
        }
    
    def cleanup_all(self) -> Dict[str, any]:
        """
        Run all cleanup operations
        
        Returns:
            Summary of all cleanup operations
        """
        logger.info("Starting comprehensive cleanup...")
        
        results = {
            "started_at": datetime.now().isoformat(),
            "retention_days": self.retention_days,
            "operations": {}
        }
        
        # Cleanup old uploads
        try:
            results["operations"]["uploads"] = self.cleanup_old_uploads()
        except Exception as e:
            results["operations"]["uploads"] = {"error": str(e)}
        
        # Cleanup old results
        try:
            results["operations"]["results"] = self.cleanup_old_results()
        except Exception as e:
            results["operations"]["results"] = {"error": str(e)}
        
        # Cleanup orphaned files
        try:
            results["operations"]["orphaned"] = self.cleanup_orphaned_files()
        except Exception as e:
            results["operations"]["orphaned"] = {"error": str(e)}
        
        # Get final storage stats
        try:
            results["storage_after"] = self.get_storage_stats()
        except Exception as e:
            results["storage_after"] = {"error": str(e)}
        
        results["completed_at"] = datetime.now().isoformat()
        
        logger.info("Cleanup completed")
        return results


# Convenience functions

def cleanup_old_files(retention_days: int = 30) -> Dict[str, any]:
    """
    Quick cleanup of old files
    
    Args:
        retention_days: Days to retain files
    
    Returns:
        Cleanup summary
    """
    manager = CleanupManager(retention_days=retention_days)
    return manager.cleanup_all()


def get_storage_info() -> Dict[str, any]:
    """
    Get current storage information
    
    Returns:
        Storage statistics
    """
    manager = CleanupManager()
    return manager.get_storage_stats()


# Add cleanup endpoint to results router
def setup_cleanup_endpoints(router):
    """
    Add cleanup endpoints to a router
    
    Usage:
        from app.utils.cleanup import setup_cleanup_endpoints
        setup_cleanup_endpoints(router)
    """
    from fastapi import HTTPException, Query
    
    @router.post("/admin/cleanup")
    async def trigger_cleanup(
        retention_days: int = Query(30, description="Days to retain files")
    ):
        """
        Manually trigger cleanup of old files
        
        Admin endpoint to clean up:
        - Old uploaded videos
        - Old exported results
        - Orphaned files
        
        Args:
            retention_days: Files older than this will be removed
        
        Returns:
            Cleanup summary
        """
        try:
            result = cleanup_old_files(retention_days=retention_days)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cleanup failed: {str(e)}"
            )
    
    @router.get("/admin/storage")
    async def get_storage():
        """
        Get current storage statistics
        
        Returns storage info for:
        - Uploads directory
        - Results directory
        - Total size
        """
        try:
            return get_storage_info()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get storage info: {str(e)}"
            )
