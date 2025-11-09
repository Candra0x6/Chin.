"""
Advanced Analytics Service
Enhanced crowd analytics with distribution patterns, bottleneck detection, and visualization data.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class CrowdAnalytics:
    """
    Advanced analytics for crowd data analysis.
    
    Features:
    - Crowd density calculations
    - Spatial distribution analysis
    - Bottleneck detection with severity levels
    - Time-series data for visualization
    - Statistical trend analysis
    """
    
    def __init__(
        self,
        high_density_threshold: int = 15,
        bottleneck_threshold_multiplier: float = 1.5,
        min_bottleneck_duration: int = 3  # frames
    ):
        """
        Initialize analytics service.
        
        Args:
            high_density_threshold: Person count threshold for high density
            bottleneck_threshold_multiplier: Multiplier of average for bottleneck detection
            min_bottleneck_duration: Minimum frames for bottleneck classification
        """
        self.high_density_threshold = high_density_threshold
        self.bottleneck_threshold_multiplier = bottleneck_threshold_multiplier
        self.min_bottleneck_duration = min_bottleneck_duration
        
        logger.info("CrowdAnalytics initialized")
    
    def calculate_crowd_density(
        self,
        person_count: int,
        area_sqm: float = 100.0  # Default area in square meters
    ) -> Dict:
        """
        Calculate crowd density metrics.
        
        Args:
            person_count: Number of people detected
            area_sqm: Area in square meters
            
        Returns:
            Dictionary with density metrics
        """
        density = person_count / area_sqm if area_sqm > 0 else 0
        
        # Classify density level
        if density < 0.1:
            level = "Very Low"
            severity = 1
        elif density < 0.2:
            level = "Low"
            severity = 2
        elif density < 0.4:
            level = "Moderate"
            severity = 3
        elif density < 0.6:
            level = "High"
            severity = 4
        else:
            level = "Very High"
            severity = 5
        
        return {
            "person_count": person_count,
            "area_sqm": area_sqm,
            "density_per_sqm": round(density, 3),
            "density_level": level,
            "severity_score": severity
        }
    
    def analyze_crowd_distribution(
        self,
        detections: List[Dict],
        frames_data: List[Dict],
        frame_width: int,
        frame_height: int
    ) -> Dict:
        """
        Analyze spatial distribution of people across frames.
        
        Args:
            detections: List of detection results with bounding boxes
            frames_data: List of frame metadata
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
            
        Returns:
            Distribution analysis with zones and hotspots
        """
        if not detections or not frames_data:
            return {
                "distribution_pattern": "No data",
                "zones": [],
                "hotspots": []
            }
        
        # Divide frame into zones (3x3 grid)
        zone_cols = 3
        zone_rows = 3
        zone_width = frame_width / zone_cols
        zone_height = frame_height / zone_rows
        
        # Initialize zone counters
        zone_counts = {}
        for row in range(zone_rows):
            for col in range(zone_cols):
                zone_counts[f"zone_{row}_{col}"] = 0
        
        # Count detections per zone
        total_detections_with_boxes = 0
        
        for detection in detections:
            if "detections" in detection and detection.get("detections"):
                for det in detection["detections"]:
                    bbox = det.get("bbox", [])
                    if len(bbox) == 4:
                        # Calculate center of bounding box
                        x1, y1, x2, y2 = bbox
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        # Determine zone
                        col = min(int(center_x / zone_width), zone_cols - 1)
                        row = min(int(center_y / zone_height), zone_rows - 1)
                        
                        zone_key = f"zone_{row}_{col}"
                        zone_counts[zone_key] += 1
                        total_detections_with_boxes += 1
        
        # Create zone analysis
        zones = []
        for row in range(zone_rows):
            for col in range(zone_cols):
                zone_key = f"zone_{row}_{col}"
                count = zone_counts[zone_key]
                
                # Calculate percentage
                percentage = (count / total_detections_with_boxes * 100) if total_detections_with_boxes > 0 else 0
                
                # Classify zone density
                if percentage > 20:
                    density = "Very High"
                elif percentage > 15:
                    density = "High"
                elif percentage > 10:
                    density = "Moderate"
                elif percentage > 5:
                    density = "Low"
                else:
                    density = "Very Low"
                
                zones.append({
                    "zone_id": zone_key,
                    "row": row,
                    "col": col,
                    "position": self._get_zone_name(row, col),
                    "detection_count": count,
                    "percentage": round(percentage, 1),
                    "density_level": density
                })
        
        # Identify hotspots (zones with > 15% of detections)
        hotspots = [z for z in zones if z["percentage"] > 15]
        hotspots.sort(key=lambda x: x["percentage"], reverse=True)
        
        # Determine distribution pattern
        if len(hotspots) >= 3:
            pattern = "Distributed"
        elif len(hotspots) == 2:
            pattern = "Bi-modal"
        elif len(hotspots) == 1:
            pattern = "Concentrated"
        else:
            pattern = "Uniform"
        
        return {
            "distribution_pattern": pattern,
            "total_detections_analyzed": total_detections_with_boxes,
            "zones": zones,
            "hotspots": hotspots,
            "grid_size": {"rows": zone_rows, "cols": zone_cols}
        }
    
    def detect_bottlenecks(
        self,
        detections: List[Dict],
        frames_data: List[Dict],
        fps: float = 30.0
    ) -> Dict:
        """
        Detect bottlenecks based on person count thresholds and duration.
        
        Args:
            detections: List of detection results
            frames_data: List of frame metadata
            fps: Video frames per second
            
        Returns:
            Bottleneck analysis with severity and duration
        """
        if not detections or not frames_data:
            return {
                "bottlenecks_detected": 0,
                "bottleneck_periods": [],
                "total_bottleneck_duration": 0
            }
        
        # Calculate statistics
        person_counts = [d.get("person_count", 0) for d in detections]
        avg_count = np.mean(person_counts)
        max_count = np.max(person_counts)
        
        # Bottleneck threshold
        bottleneck_threshold = avg_count * self.bottleneck_threshold_multiplier
        
        # Find bottleneck periods
        bottleneck_periods = []
        current_bottleneck = None
        
        for i, (detection, frame_data) in enumerate(zip(detections, frames_data)):
            person_count = detection.get("person_count", 0)
            timestamp = frame_data.get("timestamp", 0)
            
            # Check if bottleneck condition is met
            is_bottleneck = person_count >= bottleneck_threshold
            
            if is_bottleneck:
                if current_bottleneck is None:
                    # Start new bottleneck period
                    current_bottleneck = {
                        "start_frame": frame_data.get("frame_number"),
                        "start_timestamp": timestamp,
                        "end_frame": frame_data.get("frame_number"),
                        "end_timestamp": timestamp,
                        "peak_count": person_count,
                        "frame_count": 1,
                        "person_counts": [person_count]
                    }
                else:
                    # Continue current bottleneck
                    current_bottleneck["end_frame"] = frame_data.get("frame_number")
                    current_bottleneck["end_timestamp"] = timestamp
                    current_bottleneck["peak_count"] = max(current_bottleneck["peak_count"], person_count)
                    current_bottleneck["frame_count"] += 1
                    current_bottleneck["person_counts"].append(person_count)
            else:
                # End current bottleneck if it exists
                if current_bottleneck is not None:
                    # Only add if duration threshold is met
                    if current_bottleneck["frame_count"] >= self.min_bottleneck_duration:
                        # Calculate metrics
                        duration = current_bottleneck["end_timestamp"] - current_bottleneck["start_timestamp"]
                        avg_count_in_bottleneck = np.mean(current_bottleneck["person_counts"])
                        
                        # Determine severity
                        severity_ratio = current_bottleneck["peak_count"] / avg_count if avg_count > 0 else 1
                        if severity_ratio >= 2.0:
                            severity = "Critical"
                            severity_score = 5
                        elif severity_ratio >= 1.75:
                            severity = "High"
                            severity_score = 4
                        elif severity_ratio >= 1.5:
                            severity = "Moderate"
                            severity_score = 3
                        else:
                            severity = "Low"
                            severity_score = 2
                        
                        bottleneck_periods.append({
                            "start_time": self._format_time(current_bottleneck["start_timestamp"]),
                            "end_time": self._format_time(current_bottleneck["end_timestamp"]),
                            "duration_seconds": round(duration, 1),
                            "peak_person_count": current_bottleneck["peak_count"],
                            "average_person_count": round(avg_count_in_bottleneck, 1),
                            "severity": severity,
                            "severity_score": severity_score,
                            "frame_count": current_bottleneck["frame_count"]
                        })
                    
                    current_bottleneck = None
        
        # Handle bottleneck that extends to end of video
        if current_bottleneck is not None and current_bottleneck["frame_count"] >= self.min_bottleneck_duration:
            duration = current_bottleneck["end_timestamp"] - current_bottleneck["start_timestamp"]
            avg_count_in_bottleneck = np.mean(current_bottleneck["person_counts"])
            
            severity_ratio = current_bottleneck["peak_count"] / avg_count if avg_count > 0 else 1
            if severity_ratio >= 2.0:
                severity = "Critical"
                severity_score = 5
            elif severity_ratio >= 1.75:
                severity = "High"
                severity_score = 4
            elif severity_ratio >= 1.5:
                severity = "Moderate"
                severity_score = 3
            else:
                severity = "Low"
                severity_score = 2
            
            bottleneck_periods.append({
                "start_time": self._format_time(current_bottleneck["start_timestamp"]),
                "end_time": self._format_time(current_bottleneck["end_timestamp"]),
                "duration_seconds": round(duration, 1),
                "peak_person_count": current_bottleneck["peak_count"],
                "average_person_count": round(avg_count_in_bottleneck, 1),
                "severity": severity,
                "severity_score": severity_score,
                "frame_count": current_bottleneck["frame_count"]
            })
        
        # Calculate total bottleneck duration
        total_duration = sum(b["duration_seconds"] for b in bottleneck_periods)
        
        return {
            "bottlenecks_detected": len(bottleneck_periods),
            "bottleneck_periods": bottleneck_periods,
            "total_bottleneck_duration_seconds": round(total_duration, 1),
            "threshold_used": round(bottleneck_threshold, 1),
            "average_person_count": round(avg_count, 1),
            "max_person_count": int(max_count)
        }
    
    def create_visualization_data(
        self,
        detections: List[Dict],
        frames_data: List[Dict],
        interval_seconds: int = 10
    ) -> Dict:
        """
        Create time-series data formatted for visualization.
        
        Args:
            detections: List of detection results
            frames_data: List of frame metadata
            interval_seconds: Time interval for data aggregation
            
        Returns:
            Visualization-ready data structure
        """
        if not detections or not frames_data:
            return {
                "chart_data": [],
                "summary": {}
            }
        
        # Group data by time intervals
        intervals = []
        current_interval_start = 0
        interval_data = []
        
        for detection, frame_data in zip(detections, frames_data):
            timestamp = frame_data.get("timestamp", 0)
            person_count = detection.get("person_count", 0)
            
            # Check if we need to start a new interval
            if timestamp >= current_interval_start + interval_seconds:
                if interval_data:
                    # Calculate interval statistics
                    counts = [d["count"] for d in interval_data]
                    intervals.append({
                        "time": self._format_time(current_interval_start),
                        "timestamp": current_interval_start,
                        "average": round(np.mean(counts), 1),
                        "min": int(np.min(counts)),
                        "max": int(np.max(counts)),
                        "samples": len(interval_data)
                    })
                
                # Start new interval
                current_interval_start = int(timestamp // interval_seconds) * interval_seconds
                interval_data = []
            
            interval_data.append({
                "timestamp": timestamp,
                "count": person_count
            })
        
        # Add last interval
        if interval_data:
            counts = [d["count"] for d in interval_data]
            intervals.append({
                "time": self._format_time(current_interval_start),
                "timestamp": current_interval_start,
                "average": round(np.mean(counts), 1),
                "min": int(np.min(counts)),
                "max": int(np.max(counts)),
                "samples": len(interval_data)
            })
        
        # Calculate summary statistics
        all_counts = [d.get("person_count", 0) for d in detections]
        
        return {
            "chart_data": intervals,
            "interval_seconds": interval_seconds,
            "total_intervals": len(intervals),
            "summary": {
                "overall_average": round(np.mean(all_counts), 1),
                "overall_min": int(np.min(all_counts)),
                "overall_max": int(np.max(all_counts)),
                "std_deviation": round(np.std(all_counts), 1),
                "total_samples": len(all_counts)
            }
        }
    
    def calculate_flow_metrics(
        self,
        detections: List[Dict],
        frames_data: List[Dict],
        video_duration: float
    ) -> Dict:
        """
        Calculate flow and throughput metrics.
        
        Args:
            detections: List of detection results
            frames_data: List of frame metadata
            video_duration: Total video duration in seconds
            
        Returns:
            Flow metrics including rate of change
        """
        if not detections or len(detections) < 2:
            return {
                "flow_rate": 0,
                "trend": "Stable",
                "variability": "Low"
            }
        
        person_counts = [d.get("person_count", 0) for d in detections]
        
        # Calculate rate of change
        changes = []
        for i in range(1, len(person_counts)):
            change = person_counts[i] - person_counts[i-1]
            changes.append(change)
        
        avg_change = np.mean(changes) if changes else 0
        
        # Determine trend
        if avg_change > 0.5:
            trend = "Increasing"
        elif avg_change < -0.5:
            trend = "Decreasing"
        else:
            trend = "Stable"
        
        # Calculate variability
        std_dev = np.std(person_counts)
        mean_count = np.mean(person_counts)
        coefficient_of_variation = (std_dev / mean_count * 100) if mean_count > 0 else 0
        
        if coefficient_of_variation > 40:
            variability = "High"
        elif coefficient_of_variation > 20:
            variability = "Moderate"
        else:
            variability = "Low"
        
        return {
            "flow_rate": round(avg_change, 2),
            "trend": trend,
            "variability": variability,
            "coefficient_of_variation": round(coefficient_of_variation, 1),
            "average_count": round(mean_count, 1),
            "std_deviation": round(std_dev, 1)
        }
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to MM:SS format."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def _get_zone_name(row: int, col: int) -> str:
        """Get human-readable zone name."""
        row_names = ["Top", "Middle", "Bottom"]
        col_names = ["Left", "Center", "Right"]
        return f"{row_names[row]}-{col_names[col]}"
    
    def generate_comprehensive_report(
        self,
        detections: List[Dict],
        frames_data: List[Dict],
        video_metadata: Dict
    ) -> Dict:
        """
        Generate comprehensive analytics report.
        
        Args:
            detections: List of detection results
            frames_data: List of frame metadata
            video_metadata: Video metadata dictionary
            
        Returns:
            Complete analytics report
        """
        frame_width = video_metadata.get("width", 1920)
        frame_height = video_metadata.get("height", 1080)
        duration = video_metadata.get("duration_seconds", 0)
        fps = video_metadata.get("fps", 30.0)
        
        # Calculate all analytics
        distribution = self.analyze_crowd_distribution(
            detections, frames_data, frame_width, frame_height
        )
        
        bottlenecks = self.detect_bottlenecks(detections, frames_data, fps)
        
        viz_data = self.create_visualization_data(detections, frames_data, interval_seconds=10)
        
        flow_metrics = self.calculate_flow_metrics(detections, frames_data, duration)
        
        # Calculate average density
        person_counts = [d.get("person_count", 0) for d in detections]
        avg_count = np.mean(person_counts) if person_counts else 0
        avg_density = self.calculate_crowd_density(int(avg_count))
        
        return {
            "crowd_density": avg_density,
            "spatial_distribution": distribution,
            "bottleneck_analysis": bottlenecks,
            "visualization_data": viz_data,
            "flow_metrics": flow_metrics,
            "generated_at": datetime.now().isoformat()
        }
