"""
Video Processor Service
Handles video frame extraction and preprocessing using OpenCV.
"""

import cv2
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Processes video files to extract frames for analysis.
    
    Features:
    - Frame extraction with configurable sampling rate
    - Video metadata extraction (fps, duration, resolution)
    - Frame preprocessing (resizing, normalization)
    - Memory-efficient frame iteration
    """
    
    def __init__(
        self,
        frame_sample_rate: int = 30,  # Process every Nth frame
        target_size: Optional[Tuple[int, int]] = None,  # Resize frames (width, height)
        max_frames: Optional[int] = None  # Limit number of frames to process
    ):
        """
        Initialize the VideoProcessor.
        
        Args:
            frame_sample_rate: Process every Nth frame (1 = every frame, 30 = 1 per second at 30fps)
            target_size: Optional target size for resizing frames (width, height)
            max_frames: Optional maximum number of frames to process
        """
        self.frame_sample_rate = frame_sample_rate
        self.target_size = target_size
        self.max_frames = max_frames
        
    def get_video_metadata(self, video_path: Path) -> Dict:
        """
        Extract metadata from video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video metadata
            
        Raises:
            ValueError: If video cannot be opened
        """
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        
        try:
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            # Extract metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            metadata = {
                "fps": fps,
                "total_frames": frame_count,
                "width": width,
                "height": height,
                "duration_seconds": duration,
                "duration_formatted": self._format_duration(duration),
                "codec": int(cap.get(cv2.CAP_PROP_FOURCC)),
                "file_size_mb": video_path.stat().st_size / (1024 * 1024)
            }
            
            # Calculate estimated frames to process
            estimated_frames = frame_count // self.frame_sample_rate
            if self.max_frames:
                estimated_frames = min(estimated_frames, self.max_frames)
            metadata["estimated_frames_to_process"] = estimated_frames
            
            logger.info(f"Video metadata extracted: {video_path.name} - {duration:.1f}s, {fps:.1f}fps, {width}x{height}")
            
            return metadata
            
        finally:
            cap.release()
    
    def extract_frames(
        self, 
        video_path: Path,
        progress_callback: Optional[callable] = None
    ) -> List[Dict]:
        """
        Extract frames from video file.
        
        Args:
            video_path: Path to video file
            progress_callback: Optional callback function(current, total, frame_data)
            
        Returns:
            List of dictionaries containing frame data:
            [{
                "frame_number": int,
                "timestamp": float (seconds),
                "frame": numpy.ndarray (BGR image),
                "original_size": (width, height),
                "processed_size": (width, height)
            }]
            
        Raises:
            ValueError: If video cannot be opened
        """
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        frames_data = []
        
        try:
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_idx = 0
            processed_count = 0
            
            logger.info(f"Starting frame extraction: {video_path.name}")
            logger.info(f"Total frames: {total_frames}, Sample rate: every {self.frame_sample_rate} frame(s)")
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Sample frames based on sample rate
                if frame_idx % self.frame_sample_rate == 0:
                    timestamp = frame_idx / fps if fps > 0 else 0
                    original_size = (frame.shape[1], frame.shape[0])  # (width, height)
                    
                    # Resize if target size is specified
                    processed_frame = frame
                    if self.target_size:
                        processed_frame = cv2.resize(frame, self.target_size)
                    
                    processed_size = (processed_frame.shape[1], processed_frame.shape[0])
                    
                    frame_data = {
                        "frame_number": frame_idx,
                        "timestamp": timestamp,
                        "timestamp_formatted": self._format_duration(timestamp),
                        "frame": processed_frame,
                        "original_size": original_size,
                        "processed_size": processed_size
                    }
                    
                    frames_data.append(frame_data)
                    processed_count += 1
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(processed_count, total_frames // self.frame_sample_rate, frame_data)
                    
                    # Check max frames limit
                    if self.max_frames and processed_count >= self.max_frames:
                        logger.info(f"Reached max frames limit: {self.max_frames}")
                        break
                
                frame_idx += 1
            
            logger.info(f"Frame extraction complete: {processed_count} frames extracted from {total_frames} total frames")
            
            return frames_data
            
        finally:
            cap.release()
    
    def extract_single_frame(
        self, 
        video_path: Path,
        frame_number: int = 0
    ) -> Optional[np.ndarray]:
        """
        Extract a single frame from video.
        
        Args:
            video_path: Path to video file
            frame_number: Frame number to extract (0-based)
            
        Returns:
            Frame as numpy array or None if extraction fails
        """
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        
        try:
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            
            if ret:
                # Resize if target size is specified
                if self.target_size:
                    frame = cv2.resize(frame, self.target_size)
                return frame
            
            return None
            
        finally:
            cap.release()
    
    def save_frame(
        self,
        frame: np.ndarray,
        output_path: Path,
        quality: int = 95
    ) -> bool:
        """
        Save frame to file.
        
        Args:
            frame: Frame as numpy array
            output_path: Path to save frame
            quality: JPEG quality (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            logger.info(f"Frame saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
            return False
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def get_frame_at_timestamp(
        self,
        video_path: Path,
        timestamp: float
    ) -> Optional[np.ndarray]:
        """
        Extract frame at specific timestamp.
        
        Args:
            video_path: Path to video file
            timestamp: Timestamp in seconds
            
        Returns:
            Frame as numpy array or None if extraction fails
        """
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        
        try:
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            # Convert timestamp to frame number
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            
            if ret:
                # Resize if target size is specified
                if self.target_size:
                    frame = cv2.resize(frame, self.target_size)
                return frame
            
            return None
            
        finally:
            cap.release()
    
    def create_frame_summary(self, frames_data: List[Dict]) -> Dict:
        """
        Create summary statistics from extracted frames.
        
        Args:
            frames_data: List of frame data dictionaries
            
        Returns:
            Summary dictionary
        """
        if not frames_data:
            return {
                "total_frames_processed": 0,
                "time_span": "00:00 - 00:00",
                "average_frame_interval": 0
            }
        
        first_timestamp = frames_data[0]["timestamp"]
        last_timestamp = frames_data[-1]["timestamp"]
        
        avg_interval = (last_timestamp - first_timestamp) / len(frames_data) if len(frames_data) > 1 else 0
        
        return {
            "total_frames_processed": len(frames_data),
            "time_span": f"{self._format_duration(first_timestamp)} - {self._format_duration(last_timestamp)}",
            "first_frame_number": frames_data[0]["frame_number"],
            "last_frame_number": frames_data[-1]["frame_number"],
            "average_frame_interval_seconds": avg_interval,
            "frame_size": frames_data[0]["processed_size"]
        }
