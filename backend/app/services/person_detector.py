"""
Person Detector Service
YOLOv8-based person detection for video analysis.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
import torch

# CRITICAL FIX for PyTorch 2.6+ compatibility
# Must patch BEFORE importing ultralytics
import ultralytics.nn.tasks as tasks

# Store original torch_safe_load function
_original_torch_safe_load = tasks.torch_safe_load

def _patched_torch_safe_load(file, *args, **kwargs):
    """
    Patched version of torch_safe_load that uses weights_only=False
    for YOLOv8 model loading compatibility with PyTorch 2.6+.
    """
    try:
        # Use weights_only=False for YOLOv8 models (they are from trusted source)
        return torch.load(file, map_location='cpu', weights_only=False), file
    except Exception as e:
        logger.error(f"Failed to load model weights: {e}")
        raise

# Apply patch
tasks.torch_safe_load = _patched_torch_safe_load

from ultralytics import YOLO
import numpy as np

logger = logging.getLogger(__name__)
logger.info("Applied PyTorch 2.6 compatibility patch for YOLOv8 model loading")


class PersonDetector:
    """
    Detects people in video frames using YOLOv8.
    
    Features:
    - Automatic model download and caching
    - GPU acceleration if available
    - Person-only detection (class 0 in COCO dataset)
    - Configurable confidence threshold
    - Bounding box and count extraction
    """
    
    def __init__(
        self,
        model_name: str = "yolov8n.pt",  # nano model (fastest)
        confidence_threshold: float = 0.5,
        device: Optional[str] = None,
        model_dir: Optional[Path] = None
    ):
        """
        Initialize the PersonDetector.
        
        Args:
            model_name: YOLOv8 model variant (yolov8n/s/m/l/x.pt)
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            device: Device to run model on ('cpu', 'cuda', or None for auto)
            model_dir: Directory to store/load model weights
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model_dir = model_dir or Path("models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # COCO class ID for person (must be set before loading model)
        self.person_class_id = 0
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Initializing PersonDetector with {model_name} on {self.device}")
        
        # Load model
        self.model = self._load_model()
        
        logger.info("PersonDetector initialized successfully")
    
    def _load_model(self) -> YOLO:
        """
        Load YOLOv8 model.
        Downloads model if not cached.
        
        Returns:
            Loaded YOLO model
        """
        try:
            # YOLOv8 will automatically download if not found
            model = YOLO(self.model_name)
            
            # Move to device
            model.to(self.device)
            
            logger.info(f"Model loaded: {self.model_name}")
            logger.info(f"Model classes: {len(model.names)} (person is class {self.person_class_id})")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def detect_persons(
        self,
        frame: np.ndarray,
        return_boxes: bool = True
    ) -> Dict:
        """
        Detect people in a single frame.
        
        Args:
            frame: Input frame (BGR format from OpenCV)
            return_boxes: Whether to return bounding box coordinates
            
        Returns:
            Dictionary containing:
            {
                "person_count": int,
                "detections": [
                    {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": float,
                        "class_id": int,
                        "class_name": str
                    }
                ] (if return_boxes=True)
            }
        """
        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                classes=[self.person_class_id],  # Only detect persons
                verbose=False
            )
            
            # Extract results
            result = results[0]  # First (and only) image
            boxes = result.boxes
            
            person_count = len(boxes)
            
            output = {
                "person_count": person_count,
                "confidence_threshold": self.confidence_threshold
            }
            
            if return_boxes and person_count > 0:
                detections = []
                
                for box in boxes:
                    # Get box coordinates (x1, y1, x2, y2)
                    coords = box.xyxy[0].cpu().numpy()
                    
                    detection = {
                        "bbox": coords.tolist(),  # [x1, y1, x2, y2]
                        "confidence": float(box.conf[0].cpu().numpy()),
                        "class_id": int(box.cls[0].cpu().numpy()),
                        "class_name": self.model.names[int(box.cls[0])]
                    }
                    
                    detections.append(detection)
                
                output["detections"] = detections
            
            return output
            
        except Exception as e:
            logger.error(f"Error detecting persons: {e}")
            return {
                "person_count": 0,
                "error": str(e)
            }
    
    def detect_batch(
        self,
        frames: List[np.ndarray],
        return_boxes: bool = False
    ) -> List[Dict]:
        """
        Detect people in multiple frames (batch processing).
        
        Args:
            frames: List of input frames
            return_boxes: Whether to return bounding box coordinates
            
        Returns:
            List of detection results for each frame
        """
        try:
            # Run batch inference
            results = self.model(
                frames,
                conf=self.confidence_threshold,
                classes=[self.person_class_id],
                verbose=False,
                stream=True  # Memory efficient streaming
            )
            
            batch_results = []
            
            for result in results:
                boxes = result.boxes
                person_count = len(boxes)
                
                output = {
                    "person_count": person_count,
                    "confidence_threshold": self.confidence_threshold
                }
                
                if return_boxes and person_count > 0:
                    detections = []
                    
                    for box in boxes:
                        coords = box.xyxy[0].cpu().numpy()
                        
                        detection = {
                            "bbox": coords.tolist(),
                            "confidence": float(box.conf[0].cpu().numpy()),
                            "class_id": int(box.cls[0].cpu().numpy()),
                            "class_name": self.model.names[int(box.cls[0])]
                        }
                        
                        detections.append(detection)
                    
                    output["detections"] = detections
                
                batch_results.append(output)
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Error in batch detection: {e}")
            return [{"person_count": 0, "error": str(e)}] * len(frames)
    
    def analyze_frame_with_visualization(
        self,
        frame: np.ndarray
    ) -> Tuple[np.ndarray, Dict]:
        """
        Detect people and return annotated frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (annotated_frame, detection_result)
        """
        try:
            # Run inference with visualization
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                classes=[self.person_class_id],
                verbose=False
            )
            
            result = results[0]
            
            # Get annotated frame
            annotated_frame = result.plot()
            
            # Get detection data
            boxes = result.boxes
            person_count = len(boxes)
            
            detection_result = {
                "person_count": person_count,
                "confidence_threshold": self.confidence_threshold
            }
            
            return annotated_frame, detection_result
            
        except Exception as e:
            logger.error(f"Error in visualization: {e}")
            return frame, {"person_count": 0, "error": str(e)}
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "person_class_id": self.person_class_id,
            "total_classes": len(self.model.names),
            "cuda_available": torch.cuda.is_available(),
            "model_type": str(type(self.model))
        }
    
    def update_confidence_threshold(self, new_threshold: float):
        """
        Update confidence threshold.
        
        Args:
            new_threshold: New confidence threshold (0.0-1.0)
        """
        if 0.0 <= new_threshold <= 1.0:
            self.confidence_threshold = new_threshold
            logger.info(f"Confidence threshold updated to {new_threshold}")
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    @staticmethod
    def calculate_bbox_area(bbox: List[float]) -> float:
        """
        Calculate area of bounding box.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            Area in pixels
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        return width * height
    
    @staticmethod
    def calculate_bbox_center(bbox: List[float]) -> Tuple[float, float]:
        """
        Calculate center point of bounding box.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            (center_x, center_y)
        """
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y


class DetectionStats:
    """
    Helper class for calculating detection statistics across frames.
    """
    
    @staticmethod
    def calculate_statistics(detections: List[Dict]) -> Dict:
        """
        Calculate statistics from multiple frame detections.
        
        Args:
            detections: List of detection results from multiple frames
            
        Returns:
            Dictionary with statistics
        """
        if not detections:
            return {
                "total_frames": 0,
                "average_person_count": 0,
                "max_person_count": 0,
                "min_person_count": 0,
                "total_detections": 0
            }
        
        person_counts = [d.get("person_count", 0) for d in detections]
        
        return {
            "total_frames": len(detections),
            "average_person_count": np.mean(person_counts),
            "max_person_count": np.max(person_counts),
            "min_person_count": np.min(person_counts),
            "total_detections": np.sum(person_counts),
            "std_person_count": np.std(person_counts),
            "median_person_count": np.median(person_counts)
        }
    
    @staticmethod
    def find_peak_frames(
        detections: List[Dict],
        frames_data: List[Dict],
        top_n: int = 5
    ) -> List[Dict]:
        """
        Find frames with highest person counts.
        
        Args:
            detections: List of detection results
            frames_data: List of frame metadata
            top_n: Number of top frames to return
            
        Returns:
            List of top N frames with highest person counts
        """
        if not detections or not frames_data:
            return []
        
        # Combine detections with frame data
        combined = []
        for detection, frame_data in zip(detections, frames_data):
            combined.append({
                "frame_number": frame_data.get("frame_number"),
                "timestamp": frame_data.get("timestamp"),
                "timestamp_formatted": frame_data.get("timestamp_formatted"),
                "person_count": detection.get("person_count", 0)
            })
        
        # Sort by person count and get top N
        sorted_frames = sorted(combined, key=lambda x: x["person_count"], reverse=True)
        
        return sorted_frames[:top_n]
