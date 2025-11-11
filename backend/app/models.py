"""
Pydantic models for request/response validation and data schemas.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class VideoUploadResponse(BaseModel):
    """Response model for video upload."""
    
    id: str = Field(..., description="Unique identifier for the analysis job")
    filename: str = Field(..., description="Original filename of uploaded video")
    path: Optional[str] = Field(None, description="Path to uploaded video file")
    status: str = Field(default="processing", description="Current status of analysis")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CrowdAnalytics(BaseModel):
    """Model for crowd analytics data."""
    
    total_people: int = Field(..., description="Total number of people detected")
    avg_density: str = Field(..., description="Average crowd density level")
    max_congestion_time: Optional[str] = Field(None, description="Time period with maximum congestion")
    peak_count: int = Field(..., description="Maximum people count in a single frame")
    avg_count: float = Field(..., description="Average people count across all frames")


class BottleneckInfo(BaseModel):
    """Model for bottleneck information."""
    
    area: str = Field(..., description="Area where bottleneck occurs")
    severity: str = Field(..., description="Severity level: Low, Medium, High, Critical")
    duration: Optional[str] = Field(None, description="Duration of bottleneck")
    recommended_action: str = Field(..., description="Suggested action to resolve bottleneck")


class StaffRecommendation(BaseModel):
    """Model for staff recommendations."""
    
    suggested_nurses: int = Field(..., description="Recommended number of nurses")
    suggested_doctors: int = Field(default=0, description="Recommended number of doctors")
    reasoning: str = Field(..., description="Explanation for recommendations")


class AnalysisResult(BaseModel):
    """Complete analysis result model."""
    
    id: str = Field(..., description="Unique identifier for this analysis")
    video_name: str = Field(..., description="Name of analyzed video")
    duration_seconds: float = Field(..., description="Video duration in seconds")
    frames_processed: int = Field(..., description="Number of frames analyzed")
    
    # Analytics data
    crowd_analytics: CrowdAnalytics
    bottleneck_info: BottleneckInfo
    staff_recommendation: StaffRecommendation
    
    # AI-generated insights
    ai_summary: str = Field(..., description="Natural language summary from AI")
    
    # Metadata
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: float = Field(..., description="Time taken to process video")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "video_name": "ER_waitingroom.mp4",
                "duration_seconds": 180.0,
                "frames_processed": 900,
                "crowd_analytics": {
                    "total_people": 27,
                    "avg_density": "High",
                    "max_congestion_time": "02:15 - 03:30",
                    "peak_count": 32,
                    "avg_count": 24.5
                },
                "bottleneck_info": {
                    "area": "Triage Room",
                    "severity": "High",
                    "duration": "75 minutes",
                    "recommended_action": "Add 1 additional nurse to triage"
                },
                "staff_recommendation": {
                    "suggested_nurses": 3,
                    "suggested_doctors": 1,
                    "reasoning": "Current crowd density requires additional staff"
                },
                "ai_summary": "The triage area is crowded between 2-3 PM. Adding 1 nurse could reduce wait time by 20%.",
                "processed_at": "2025-11-07T10:30:00Z",
                "processing_time_seconds": 12.5
            }
        }


class ChatMessage(BaseModel):
    """Model for chat messages."""
    

class HospitalStaffing(BaseModel):
    """Model for hospital staffing data."""
    
    total_nurses: int = Field(..., description="Total number of nurses on duty", ge=0)
    total_doctors: int = Field(..., description="Total number of doctors on duty", ge=0)
    available_nurses: int = Field(..., description="Currently available nurses", ge=0)
    available_doctors: int = Field(..., description="Currently available doctors", ge=0)
    shift_type: str = Field(default="day", description="Shift type: day, evening, night")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_nurses": 8,
                "total_doctors": 2,
                "available_nurses": 5,
                "available_doctors": 1,
                "shift_type": "day"
            }
        }


class HospitalResources(BaseModel):
    """Model for hospital resource data."""
    
    total_beds: int = Field(..., description="Total available beds", ge=0)
    occupied_beds: int = Field(..., description="Currently occupied beds", ge=0)
    available_beds: int = Field(..., description="Currently available beds", ge=0)
    critical_care_beds: int = Field(default=0, description="ICU/Critical care beds", ge=0)
    general_beds: int = Field(default=0, description="General ward beds", ge=0)
    observation_beds: int = Field(default=0, description="Observation/triage beds", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_beds": 50,
                "occupied_beds": 42,
                "available_beds": 8,
                "critical_care_beds": 10,
                "general_beds": 30,
                "observation_beds": 10
            }
        }


class HospitalContext(BaseModel):
    """Complete hospital context for analysis."""
    
    staffing: HospitalStaffing = Field(..., description="Current staffing information")
    resources: HospitalResources = Field(..., description="Current resource availability")
    area_sqm: float = Field(default=100.0, description="Area being monitored in square meters", ge=10.0)
    location_name: str = Field(default="Waiting Area", description="Location/area name (e.g., ER, Triage, ICU)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "staffing": {
                    "total_nurses": 8,
                    "total_doctors": 2,
                    "available_nurses": 5,
                    "available_doctors": 1,
                    "shift_type": "day"
                },
                "resources": {
                    "total_beds": 50,
                    "occupied_beds": 42,
                    "available_beds": 8,
                    "critical_care_beds": 10,
                    "general_beds": 30,
                    "observation_beds": 10
                },
                "area_sqm": 150.0,
                "location_name": "Emergency Room Waiting Area"
            }
        }


class AnalysisRequest(BaseModel):
    """Request model for starting video analysis."""
    
    upload_id: str = Field(..., description="ID of the uploaded video")
    show_visual: bool = Field(default=False, description="Show real-time visual display with bounding boxes")
    save_annotated_video: bool = Field(default=False, description="Save video with bounding boxes to file")
    frame_sample_rate: int = Field(default=30, description="Process every Nth frame (lower = more frames processed)")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Detection confidence threshold")
    enable_ai_insights: bool = Field(default=True, description="Enable AI-powered insights using Google Gemini")
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key (optional, can use env var)")
    hospital_context: Optional[HospitalContext] = Field(default=None, description="Current hospital staffing and resource data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "abc-123-def",
                "show_visual": True,
                "save_annotated_video": True,
                "frame_sample_rate": 1,
                "confidence_threshold": 0.5,
                "enable_ai_insights": True,
                "hospital_context": {
                    "staffing": {
                        "total_nurses": 8,
                        "total_doctors": 2,
                        "available_nurses": 5,
                        "available_doctors": 1,
                        "shift_type": "day"
                    },
                    "resources": {
                        "total_beds": 50,
                        "occupied_beds": 42,
                        "available_beds": 8
                    },
                    "area_sqm": 150.0,
                    "location_name": "Emergency Room"
                }
            }
        }


class ChatMessage(BaseModel):
    """Model for chat messages."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is either user or assistant."""
        if v not in ['user', 'assistant']:
            raise ValueError('Role must be either "user" or "assistant"')
        return v


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    analysis_id: str = Field(..., description="ID of the analysis to discuss")
    message: str = Field(..., description="User's question or message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous conversation history"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    response: str = Field(..., description="AI assistant's response")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Relevant analysis data used for response"
    )


class AnalysisResponse(BaseModel):
    """Response model for analysis start."""
    
    analysis_id: str = Field(..., description="Unique identifier for this analysis")
    video_id: str = Field(..., description="ID of the video being analyzed")
    status: str = Field(..., description="Analysis status")
    message: str = Field(..., description="Status message")


class AnalysisStatusResponse(BaseModel):
    """Response model for analysis status check."""
    
    analysis_id: str = Field(..., description="Analysis ID")
    status: str = Field(..., description="Current status")
    progress: int = Field(..., description="Progress percentage (0-100)")
    message: str = Field(..., description="Status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Full results when completed")


class AnalysisListResponse(BaseModel):
    """Response model for listing analyses."""
    
    analyses: List[Dict[str, Any]] = Field(..., description="List of analyses")
    total: int = Field(..., description="Total number of results")
    limit: int = Field(..., description="Results per page")
    offset: int = Field(..., description="Results offset")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
