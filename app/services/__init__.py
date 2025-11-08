"""Services package for video processing, detection, and analytics."""

from .video_processor import VideoProcessor
from .person_detector import PersonDetector, DetectionStats
from .video_analysis import VideoAnalysisService
from .analytics import CrowdAnalytics

__all__ = [
    "VideoProcessor",
    "PersonDetector",
    "DetectionStats",
    "VideoAnalysisService",
    "CrowdAnalytics",
]

