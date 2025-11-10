"""
Video Analysis Service
Main pipeline combining video processing and person detection.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json
import numpy as np
import cv2
import os

from .video_processor import VideoProcessor
from .person_detector import PersonDetector, DetectionStats
from .analytics import CrowdAnalytics
from .gemini_assistant import GeminiAssistant

logger = logging.getLogger(__name__)


class VideoAnalysisService:
    """
    Main service for analyzing videos to detect people and generate insights.
    
    Combines:
    - Video frame extraction (VideoProcessor)
    - Person detection (PersonDetector)
    - Statistics calculation (DetectionStats)
    """
    
    def __init__(
        self,
        frame_sample_rate: int = 30,  # Process every Nth frame (30 = ~1 per second at 30fps)
        confidence_threshold: float = 0.5,
        max_frames: Optional[int] = None,
        device: Optional[str] = None,
        show_visual: bool = False,  # Enable real-time visual display
        save_annotated_video: bool = False,  # Save video with bounding boxes
        output_video_path: Optional[Path] = None,  # Path for annotated video
        enable_ai_insights: bool = True,  # Enable AI insights generation
        gemini_api_key: Optional[str] = None  # Gemini API key (or from env)
    ):
        """
        Initialize the VideoAnalysisService.
        
        Args:
            frame_sample_rate: Process every Nth frame
            confidence_threshold: Person detection confidence threshold
            max_frames: Maximum frames to process (None = all)
            device: Device for YOLO model ('cpu', 'cuda', or None for auto)
            show_visual: Show real-time visual display with bounding boxes
            save_annotated_video: Save annotated video to file
            output_video_path: Path to save annotated video
            enable_ai_insights: Enable AI-powered insights generation
            gemini_api_key: Google Gemini API key (or load from GEMINI_API_KEY env var)
        """
        self.video_processor = VideoProcessor(
            frame_sample_rate=frame_sample_rate,
            max_frames=max_frames
        )
        
        self.person_detector = PersonDetector(
            confidence_threshold=confidence_threshold,
            device=device
        )
        
        self.analytics = CrowdAnalytics()
        
        # Visual display settings
        self.show_visual = show_visual
        self.save_annotated_video = save_annotated_video
        self.output_video_path = output_video_path
        self.video_writer = None
        
        # AI insights settings
        self.enable_ai_insights = enable_ai_insights
        self.gemini_assistant = None
        
        if enable_ai_insights:
            # Get API key from parameter or environment
            api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
            
            # Initialize Gemini assistant
            self.gemini_assistant = GeminiAssistant(
                api_key=api_key,
                model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
                max_output_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
            )
            
            logger.info(f"AI insights enabled: {self.gemini_assistant.get_model_info()['mode']}")
        else:
            logger.info("AI insights disabled")
        
        logger.info("VideoAnalysisService initialized")
    
    def analyze_video(
        self,
        video_path: Path,
        progress_callback: Optional[Callable] = None,
        save_detections: bool = True
    ) -> Dict:
        """
        Analyze video to detect people frame-by-frame.
        
        Args:
            video_path: Path to video file
            progress_callback: Optional callback(current, total, status_message)
            save_detections: Whether to save detailed detection data
            
        Returns:
            Complete analysis results dictionary
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting video analysis: {video_path.name}")
            
            # Step 1: Extract video metadata
            if progress_callback:
                progress_callback(0, 100, "Extracting video metadata...")
            
            metadata = self.video_processor.get_video_metadata(video_path)
            logger.info(f"Video metadata: {metadata['duration_formatted']} duration, {metadata['fps']:.1f} fps")
            
            # Step 2: Extract frames
            if progress_callback:
                progress_callback(10, 100, "Extracting frames...")
            
            frames_data = self._extract_frames_with_progress(
                video_path,
                progress_callback
            )
            
            if not frames_data:
                raise ValueError("No frames extracted from video")
            
            logger.info(f"Extracted {len(frames_data)} frames")
            
            # Step 3: Detect people in frames
            if progress_callback:
                progress_callback(50, 100, "Detecting people in frames...")
            
            detections = self._detect_people_in_frames(
                frames_data,
                progress_callback
            )
            
            logger.info(f"Person detection complete for {len(detections)} frames")
            
            # Step 4: Calculate statistics
            if progress_callback:
                progress_callback(90, 100, "Calculating statistics...")
            
            statistics = DetectionStats.calculate_statistics(detections)
            peak_frames = DetectionStats.find_peak_frames(detections, frames_data, top_n=5)
            
            # Step 5: Compile results
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            results = {
                "status": "completed",
                "video_metadata": metadata,
                "processing_info": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "processing_time_seconds": processing_time,
                    "frames_processed": len(frames_data),
                    "frame_sample_rate": self.video_processor.frame_sample_rate,
                    "confidence_threshold": self.person_detector.confidence_threshold
                },
                "statistics": statistics,
                "peak_congestion_frames": peak_frames,
                "timeline": self._generate_timeline(frames_data, detections)
            }
            
           
            
            # Add insights
            results["insights"] = self._generate_insights(results)
            
            # Add Phase 4: Enhanced analytics (90-95%)
            if progress_callback:
                progress_callback(92, 100, "Generating enhanced analytics...")
            
            results["enhanced_analytics"] = self.analytics.generate_comprehensive_report(
                detections, frames_data, metadata
            )
            
            # Phase 5: AI-powered insights (95-98%)
            if self.enable_ai_insights and self.gemini_assistant:
                if progress_callback:
                    progress_callback(95, 100, "Generating AI insights...")
                
                try:
                    ai_insights = self.gemini_assistant.generate_insights(
                        results,
                        include_recommendations=True
                    )
                    results["ai_insights"] = ai_insights
                    logger.info(f"AI insights generated: {ai_insights.get('generated_by', 'unknown')}")
                except Exception as e:
                    logger.error(f"Error generating AI insights: {e}")
                    # Don't fail the entire analysis - continue without AI insights
                    results["ai_insights"] = {
                        "error": "AI insights generation failed",
                        "message": str(e)
                    }
            
            if progress_callback:
                progress_callback(100, 100, "Analysis complete!")
            
            logger.info(f"Video analysis completed in {processing_time:.2f}s")
            logger.info(f"Average person count: {statistics['average_person_count']:.1f}")
            logger.info(f"Peak person count: {statistics['max_person_count']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "video_path": str(video_path)
            }
    
    def _extract_frames_with_progress(
        self,
        video_path: Path,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Extract frames with progress tracking."""
        frames = []
        
        def frame_progress(current, total, frame_data):
            frames.append(frame_data)
            if progress_callback:
                # Map to 10-50% of total progress
                progress = 10 + int((current / total) * 40)
                progress_callback(progress, 100, f"Extracting frames: {current}/{total}")
        
        self.video_processor.extract_frames(video_path, progress_callback=frame_progress)
        
        return frames
    
    def _detect_people_in_frames(
        self,
        frames_data: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """Detect people in all frames with progress tracking and visual display."""
        detections = []
        total_frames = len(frames_data)
        
        # Initialize video writer if saving annotated video
        if self.save_annotated_video and self.output_video_path and frames_data:
            first_frame = frames_data[0]["frame"]
            height, width = first_frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(self.output_video_path),
                fourcc,
                30.0,  # FPS
                (width, height)
            )
            logger.info(f"Saving annotated video to: {self.output_video_path}")
        
        # Create window for visual display
        if self.show_visual:
            cv2.namedWindow('Person Detection - Press Q to quit', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Person Detection - Press Q to quit', 1280, 720)
            logger.info("Real-time visual display enabled - Press 'Q' to quit")
        
        for idx, frame_data in enumerate(frames_data):
            frame = frame_data["frame"].copy()  # Make a copy for annotation
            
            # Detect people with bounding boxes
            detection = self.person_detector.detect_persons(frame, return_boxes=True)
            detections.append(detection)
            
            # Draw bounding boxes and info on frame
            annotated_frame = self._draw_detections(
                frame,
                detection,
                frame_data["frame_number"],
                frame_data["timestamp_formatted"]
            )
            
            # Show visual display
            if self.show_visual:
                cv2.imshow('Person Detection - Press Q to quit', annotated_frame)
                
                # Wait 1ms and check for 'q' key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    logger.info("User requested to quit visual display")
                    self.show_visual = False  # Stop showing but continue processing
            
            # Save to video file
            if self.video_writer is not None:
                self.video_writer.write(annotated_frame)
            
            if progress_callback and (idx % 10 == 0 or idx == total_frames - 1):
                # Map to 50-90% of total progress
                progress = 50 + int((idx / total_frames) * 40)
                progress_callback(
                    progress, 
                    100, 
                    f"Detecting people: {idx + 1}/{total_frames}"
                )
        
        # Cleanup
        if self.show_visual:
            cv2.destroyAllWindows()
        
        if self.video_writer is not None:
            self.video_writer.release()
            logger.info(f"Annotated video saved successfully")
        
        return detections
    
    def _format_frame_detections(
        self,
        frames_data: List[Dict],
        detections: List[Dict]
    ) -> List[Dict]:
        """Format frame-by-frame detection data."""
        formatted = []
        
        for frame_data, detection in zip(frames_data, detections):
            formatted.append({
                "frame_number": frame_data["frame_number"],
                "timestamp": frame_data["timestamp"],
                "timestamp_formatted": frame_data["timestamp_formatted"],
                "person_count": detection.get("person_count", 0)
            })
        
        return formatted
    
    def _generate_timeline(
        self,
        frames_data: List[Dict],
        detections: List[Dict],
        interval_seconds: int = 30
    ) -> List[Dict]:
        """
        Generate timeline summary with aggregated counts per time interval.
        
        Args:
            frames_data: List of frame data
            detections: List of detection results
            interval_seconds: Time interval for aggregation
            
        Returns:
            List of time intervals with statistics
        """
        if not frames_data or not detections:
            return []
        
        timeline = []
        current_interval_start = 0
        interval_detections = []
        
        for frame_data, detection in zip(frames_data, detections):
            timestamp = frame_data["timestamp"]
            
            # Check if we need to start a new interval
            if timestamp >= current_interval_start + interval_seconds:
                if interval_detections:
                    # Calculate stats for current interval
                    person_counts = [d.get("person_count", 0) for d in interval_detections]
                    timeline.append({
                        "interval_start": current_interval_start,
                        "interval_end": current_interval_start + interval_seconds,
                        "interval_formatted": f"{self._format_time(current_interval_start)} - {self._format_time(current_interval_start + interval_seconds)}",
                        "average_person_count": float(np.mean(person_counts)),
                        "max_person_count": int(np.max(person_counts)),
                        "min_person_count": int(np.min(person_counts)),
                        "frames_in_interval": len(interval_detections)
                    })
                
                # Start new interval
                current_interval_start = int(timestamp // interval_seconds) * interval_seconds
                interval_detections = []
            
            interval_detections.append(detection)
        
        # Add last interval
        if interval_detections:
            person_counts = [d.get("person_count", 0) for d in interval_detections]
            timeline.append({
                "interval_start": current_interval_start,
                "interval_end": current_interval_start + interval_seconds,
                "interval_formatted": f"{self._format_time(current_interval_start)} - {self._format_time(current_interval_start + interval_seconds)}",
                "average_person_count": float(np.mean(person_counts)),
                "max_person_count": int(np.max(person_counts)),
                "min_person_count": int(np.min(person_counts)),
                "frames_in_interval": len(interval_detections)
            })
        
        return timeline
    
    def _generate_insights(self, results: Dict) -> Dict:
        """
        Generate human-readable insights from analysis results.
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Insights dictionary
        """
        stats = results.get("statistics", {})
        timeline = results.get("timeline", [])
        peak_frames = results.get("peak_congestion_frames", [])
        
        avg_count = stats.get("average_person_count", 0)
        max_count = stats.get("max_person_count", 0)
        
        # Determine crowd level
        if avg_count < 5:
            crowd_level = "Low"
        elif avg_count < 15:
            crowd_level = "Moderate"
        elif avg_count < 25:
            crowd_level = "High"
        else:
            crowd_level = "Very High"
        
        # Find peak congestion period
        peak_period = "N/A"
        if peak_frames:
            peak_period = peak_frames[0].get("timestamp_formatted", "N/A")
        
        # Calculate suggested staff
        suggested_nurses = max(1, int(np.ceil(avg_count / 10)))
        
        insights = {
            "crowd_level": crowd_level,
            "average_person_count": round(avg_count, 1),
            "peak_person_count": max_count,
            "peak_congestion_time": peak_period,
            "suggested_nurses": suggested_nurses,
            "bottleneck_detected": max_count > avg_count * 1.5,  # Peak > 150% of average
            "summary": self._generate_summary_text(
                crowd_level, 
                avg_count, 
                max_count, 
                peak_period,
                suggested_nurses
            )
        }
        
        return insights
    
    @staticmethod
    def _generate_summary_text(
        crowd_level: str,
        avg_count: float,
        max_count: int,
        peak_time: str,
        suggested_nurses: int
    ) -> str:
        """Generate human-readable summary text."""
        summary = f"The ER waiting area shows {crowd_level.lower()} crowd levels with an average of {avg_count:.1f} people. "
        
        if max_count > 0:
            summary += f"Peak congestion of {max_count} people occurred at {peak_time}. "
        
        summary += f"Recommended staffing: {suggested_nurses} nurse(s) for optimal flow."
        
        return summary
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to MM:SS format."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _draw_detections(
        self,
        frame: np.ndarray,
        detection: Dict,
        frame_number: int,
        timestamp: str
    ) -> np.ndarray:
        """
        Draw bounding boxes and information on frame.
        
        Args:
            frame: Original frame
            detection: Detection results with bounding boxes
            frame_number: Current frame number
            timestamp: Formatted timestamp
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        person_count = detection.get("person_count", 0)
        detections_list = detection.get("detections", [])
        
        # Draw bounding boxes for each detected person
        for det in detections_list:
            bbox = det.get("bbox", [])
            confidence = det.get("confidence", 0.0)
            
            if len(bbox) == 4:
                x1, y1, x2, y2 = map(int, bbox)
                
                # Draw green bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw confidence label
                label = f"Person {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                
                # Draw label background
                cv2.rectangle(
                    annotated,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    (0, 255, 0),
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    annotated,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1
                )
        
        # Draw info panel at top
        info_panel_height = 80
        overlay = annotated.copy()
        cv2.rectangle(overlay, (0, 0), (annotated.shape[1], info_panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)
        
        # Draw statistics
        cv2.putText(
            annotated,
            f"Frame: {frame_number} | Time: {timestamp}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        cv2.putText(
            annotated,
            f"People Detected: {person_count}",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Draw crowd level indicator
        if person_count < 5:
            crowd_level = "Low"
            color = (0, 255, 0)  # Green
        elif person_count < 15:
            crowd_level = "Moderate"
            color = (0, 255, 255)  # Yellow
        elif person_count < 25:
            crowd_level = "High"
            color = (0, 165, 255)  # Orange
        else:
            crowd_level = "Very High"
            color = (0, 0, 255)  # Red
        
        cv2.putText(
            annotated,
            f"Crowd Level: {crowd_level}",
            (annotated.shape[1] - 300, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )
        
        return annotated
    
    def get_service_info(self) -> Dict:
        """Get information about the analysis service configuration."""
        return {
            "video_processor": {
                "frame_sample_rate": self.video_processor.frame_sample_rate,
                "max_frames": self.video_processor.max_frames,
                "target_size": self.video_processor.target_size
            },
            "person_detector": self.person_detector.get_model_info(),
            "visual_display": {
                "show_visual": self.show_visual,
                "save_annotated_video": self.save_annotated_video,
                "output_video_path": str(self.output_video_path) if self.output_video_path else None
            }
        }
