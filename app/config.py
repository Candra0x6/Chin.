"""
Configuration module for HospiTwin Lite application.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    gemini_api_key: Optional[str] = None
    
    # Database Configuration (PostgreSQL via Supabase)
    db_user: str
    db_password: str
    db_host: str
    db_port: str = "5432"
    db_name: str
    
    # Legacy Supabase Configuration (for backward compatibility)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # Directory Configuration
    upload_dir: str = "uploads"
    results_dir: str = "results"
    model_path: str = "models"
    
    # Application Configuration
    max_upload_size: int = 104857600  # 100MB
    allowed_video_formats: str = "mp4,avi,mov,mkv"
    
    # Processing Configuration
    max_frame_rate: int = 5  # Frames per second to process
    detection_confidence: float = 0.5  # YOLOv8 confidence threshold
    
    # Gemini AI Configuration (optional)
    gemini_model: str = "gemini-1.5-flash"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048
    
    # General Configuration (optional)
    debug: bool = False
    log_level: str = "INFO"
    default_confidence_threshold: float = 0.5
    default_frame_sample_rate: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # Allow extra fields from .env
    )
    
    @property
    def allowed_formats_list(self) -> List[str]:
        """Convert allowed formats string to list."""
        return [fmt.strip().lower() for fmt in self.allowed_video_formats.split(",")]
    
    def get_upload_path(self) -> Path:
        """Get and ensure upload directory exists."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_results_path(self) -> Path:
        """Get and ensure results directory exists."""
        path = Path(self.results_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_model_path(self) -> Path:
        """Get and ensure models directory exists."""
        path = Path(self.model_path)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
