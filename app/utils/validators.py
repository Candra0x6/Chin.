"""
Input validation utilities for file uploads and data validation.
"""

import os
from typing import List, Tuple
from pathlib import Path

from fastapi import UploadFile, HTTPException


class VideoValidator:
    """Validator for video file uploads."""
    
    def __init__(
        self,
        allowed_formats: List[str],
        max_size: int
    ):
        """
        Initialize video validator.
        
        Args:
            allowed_formats: List of allowed file extensions (e.g., ['mp4', 'avi'])
            max_size: Maximum file size in bytes
        """
        self.allowed_formats = [fmt.lower() for fmt in allowed_formats]
        self.max_size = max_size
    
    def validate_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Validate file extension.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is empty"
        
        # Get file extension
        file_ext = Path(filename).suffix.lower().lstrip('.')
        
        if not file_ext:
            return False, "File has no extension"
        
        if file_ext not in self.allowed_formats:
            return False, (
                f"Invalid file format. Allowed formats: "
                f"{', '.join(self.allowed_formats)}"
            )
        
        return True, ""
    
    def validate_size(self, file_size: int) -> Tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size <= 0:
            return False, "File is empty"
        
        if file_size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.0f}MB"
        
        return True, ""
    
    def validate_mime_type(self, content_type: str) -> Tuple[bool, str]:
        """
        Validate MIME type.
        
        Args:
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content_type:
            return False, "Content type not provided"
        
        valid_mime_types = [
            'video/mp4',
            'video/avi',
            'video/x-msvideo',
            'video/quicktime',
            'video/x-matroska'
        ]
        
        if content_type not in valid_mime_types:
            return False, f"Invalid content type: {content_type}"
        
        return True, ""
    
    async def validate_upload(self, file: UploadFile) -> None:
        """
        Validate uploaded file completely.
        
        Args:
            file: FastAPI UploadFile object
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate filename
        is_valid, error = self.validate_extension(file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Validate content type
        is_valid, error = self.validate_mime_type(file.content_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Read file size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer
        
        # Validate size
        is_valid, error = self.validate_size(file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Get just the filename without path
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    dangerous_chars = ['..', '/', '\\', '\0', '\n', '\r']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty after sanitization
    if not filename:
        filename = "unnamed_file"
    
    return filename


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension without dot (lowercase)
    """
    return Path(filename).suffix.lower().lstrip('.')


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
