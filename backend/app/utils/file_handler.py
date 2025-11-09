"""
File handling utilities for saving, reading, and managing uploaded files.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime

from fastapi import UploadFile
from app.utils.validators import sanitize_filename


class FileHandler:
    """Handle file operations for uploads and storage."""
    
    def __init__(self, upload_dir: str):
        """
        Initialize file handler.
        
        Args:
            upload_dir: Directory path for storing uploads
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename to avoid collisions.
        
        Args:
            original_filename: Original filename from upload
            
        Returns:
            Unique filename with UUID prefix
        """
        # Sanitize the original filename
        safe_filename = sanitize_filename(original_filename)
        
        # Generate unique ID
        unique_id = uuid.uuid4().hex[:8]
        
        # Get timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Split filename and extension
        name_parts = safe_filename.rsplit('.', 1)
        name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else 'mp4'
        
        # Create unique filename
        unique_filename = f"{timestamp}_{unique_id}_{name}.{extension}"
        
        return unique_filename
    
    async def save_upload_file(
        self,
        upload_file: UploadFile,
        custom_filename: Optional[str] = None
    ) -> tuple[str, Path]:
        """
        Save uploaded file to disk.
        
        Args:
            upload_file: FastAPI UploadFile object
            custom_filename: Optional custom filename (will be sanitized)
            
        Returns:
            Tuple of (filename, full_path)
        """
        # Generate filename
        if custom_filename:
            filename = sanitize_filename(custom_filename)
        else:
            filename = self.generate_unique_filename(upload_file.filename)
        
        # Full path
        file_path = self.upload_dir / filename
        
        # Save file in chunks to handle large files
        try:
            with open(file_path, 'wb') as buffer:
                # Reset file pointer
                await upload_file.seek(0)
                
                # Write in chunks
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = await upload_file.read(chunk_size)
                    if not chunk:
                        break
                    buffer.write(chunk)
            
            return filename, file_path
            
        except Exception as e:
            # Clean up partial file if error occurs
            if file_path.exists():
                file_path.unlink()
            raise Exception(f"Failed to save file: {str(e)}")
    
    def get_file_size(self, file_path: Path) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        return file_path.stat().st_size if file_path.exists() else 0
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete file from uploads directory.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.upload_dir / filename
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists.
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if exists, False otherwise
        """
        file_path = self.upload_dir / filename
        return file_path.exists()
    
    def get_file_path(self, filename: str) -> Path:
        """
        Get full path for a filename.
        
        Args:
            filename: Name of file
            
        Returns:
            Full Path object
        """
        return self.upload_dir / filename
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """
        Delete files older than specified days.
        
        Args:
            days: Number of days to keep files
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        current_time = datetime.now().timestamp()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        for file_path in self.upload_dir.glob('*'):
            if file_path.is_file():
                file_time = file_path.stat().st_mtime
                if file_time < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
        
        return deleted_count
    
    def get_directory_size(self) -> int:
        """
        Calculate total size of uploads directory.
        
        Returns:
            Total size in bytes
        """
        total_size = 0
        for file_path in self.upload_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size


def copy_file(source: Path, destination: Path) -> None:
    """
    Copy file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def move_file(source: Path, destination: Path) -> None:
    """
    Move file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
