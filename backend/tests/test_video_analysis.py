"""
Tests for video processing and person detection services.
"""

import pytest
import numpy as np
from pathlib import Path
import cv2
import tempfile
import os

from app.services.video_processor import VideoProcessor
from app.services.person_detector import PersonDetector, DetectionStats


class TestVideoProcessor:
    """Tests for VideoProcessor class."""
    
    @pytest.fixture
    def sample_video(self):
        """Create a sample video file for testing."""
        # Create temporary video file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(temp_path), fourcc, 30.0, (640, 480))
        
        # Write 90 frames (3 seconds at 30fps)
        for i in range(90):
            # Create a simple frame with changing color
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:, :] = (i * 2, 100, 150)
            out.write(frame)
        
        out.release()
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    def test_video_processor_init(self):
        """Test VideoProcessor initialization."""
        processor = VideoProcessor(frame_sample_rate=30, max_frames=100)
        
        assert processor.frame_sample_rate == 30
        assert processor.max_frames == 100
        assert processor.target_size is None
    
    def test_get_video_metadata(self, sample_video):
        """Test video metadata extraction."""
        processor = VideoProcessor()
        metadata = processor.get_video_metadata(sample_video)
        
        assert metadata['fps'] == 30.0
        assert metadata['total_frames'] == 90
        assert metadata['width'] == 640
        assert metadata['height'] == 480
        assert metadata['duration_seconds'] == 3.0
        assert 'estimated_frames_to_process' in metadata
    
    def test_extract_frames(self, sample_video):
        """Test frame extraction."""
        processor = VideoProcessor(frame_sample_rate=30)  # 1 frame per second
        frames_data = processor.extract_frames(sample_video)
        
        assert len(frames_data) == 3  # 3 frames from 3-second video
        
        for frame_data in frames_data:
            assert 'frame_number' in frame_data
            assert 'timestamp' in frame_data
            assert 'frame' in frame_data
            assert isinstance(frame_data['frame'], np.ndarray)
            assert frame_data['frame'].shape == (480, 640, 3)
    
    def test_extract_frames_with_max_limit(self, sample_video):
        """Test frame extraction with max frames limit."""
        processor = VideoProcessor(frame_sample_rate=15, max_frames=2)
        frames_data = processor.extract_frames(sample_video)
        
        assert len(frames_data) <= 2
    
    def test_extract_single_frame(self, sample_video):
        """Test single frame extraction."""
        processor = VideoProcessor()
        frame = processor.extract_single_frame(sample_video, frame_number=10)
        
        assert frame is not None
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (480, 640, 3)
    
    def test_frame_summary(self, sample_video):
        """Test frame summary generation."""
        processor = VideoProcessor(frame_sample_rate=30)
        frames_data = processor.extract_frames(sample_video)
        
        summary = processor.create_frame_summary(frames_data)
        
        assert summary['total_frames_processed'] == len(frames_data)
        assert 'time_span' in summary
        assert 'average_frame_interval_seconds' in summary
    
    def test_invalid_video_path(self):
        """Test error handling for invalid video path."""
        processor = VideoProcessor()
        
        with pytest.raises(ValueError):
            processor.get_video_metadata(Path("nonexistent.mp4"))


class TestPersonDetector:
    """Tests for PersonDetector class."""
    
    @pytest.fixture
    def sample_frame(self):
        """Create a sample frame for testing."""
        # Create a simple test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some color to make it less empty
        frame[:, :] = (100, 150, 200)
        return frame
    
    def test_person_detector_init(self):
        """Test PersonDetector initialization."""
        detector = PersonDetector(
            model_name="yolov8n.pt",
            confidence_threshold=0.5
        )
        
        assert detector.model_name == "yolov8n.pt"
        assert detector.confidence_threshold == 0.5
        assert detector.person_class_id == 0
        assert detector.model is not None
    
    def test_detect_persons(self, sample_frame):
        """Test person detection on a frame."""
        detector = PersonDetector(confidence_threshold=0.5)
        result = detector.detect_persons(sample_frame, return_boxes=True)
        
        assert 'person_count' in result
        assert 'confidence_threshold' in result
        assert isinstance(result['person_count'], int)
        assert result['person_count'] >= 0
    
    def test_detect_batch(self, sample_frame):
        """Test batch person detection."""
        detector = PersonDetector(confidence_threshold=0.5)
        frames = [sample_frame, sample_frame, sample_frame]
        
        results = detector.detect_batch(frames, return_boxes=False)
        
        assert len(results) == 3
        for result in results:
            assert 'person_count' in result
            assert isinstance(result['person_count'], int)
    
    def test_update_confidence_threshold(self):
        """Test confidence threshold update."""
        detector = PersonDetector(confidence_threshold=0.5)
        
        detector.update_confidence_threshold(0.7)
        assert detector.confidence_threshold == 0.7
        
        with pytest.raises(ValueError):
            detector.update_confidence_threshold(1.5)  # Invalid threshold
    
    def test_get_model_info(self):
        """Test model info retrieval."""
        detector = PersonDetector()
        info = detector.get_model_info()
        
        assert 'model_name' in info
        assert 'device' in info
        assert 'confidence_threshold' in info
        assert 'person_class_id' in info
        assert info['person_class_id'] == 0
    
    def test_calculate_bbox_area(self):
        """Test bounding box area calculation."""
        bbox = [100, 100, 200, 200]
        area = PersonDetector.calculate_bbox_area(bbox)
        
        assert area == 10000  # 100 x 100
    
    def test_calculate_bbox_center(self):
        """Test bounding box center calculation."""
        bbox = [100, 100, 200, 200]
        center_x, center_y = PersonDetector.calculate_bbox_center(bbox)
        
        assert center_x == 150
        assert center_y == 150


class TestDetectionStats:
    """Tests for DetectionStats helper class."""
    
    def test_calculate_statistics(self):
        """Test statistics calculation from detections."""
        detections = [
            {"person_count": 5},
            {"person_count": 10},
            {"person_count": 15},
            {"person_count": 8},
            {"person_count": 12}
        ]
        
        stats = DetectionStats.calculate_statistics(detections)
        
        assert stats['total_frames'] == 5
        assert stats['average_person_count'] == 10.0
        assert stats['max_person_count'] == 15
        assert stats['min_person_count'] == 5
        assert stats['total_detections'] == 50
    
    def test_calculate_statistics_empty(self):
        """Test statistics calculation with empty input."""
        stats = DetectionStats.calculate_statistics([])
        
        assert stats['total_frames'] == 0
        assert stats['average_person_count'] == 0
    
    def test_find_peak_frames(self):
        """Test finding peak congestion frames."""
        detections = [
            {"person_count": 5},
            {"person_count": 20},
            {"person_count": 15},
            {"person_count": 25},
            {"person_count": 10}
        ]
        
        frames_data = [
            {"frame_number": i, "timestamp": i * 0.5, "timestamp_formatted": f"00:{i:02d}"}
            for i in range(5)
        ]
        
        peak_frames = DetectionStats.find_peak_frames(detections, frames_data, top_n=3)
        
        assert len(peak_frames) == 3
        assert peak_frames[0]['person_count'] == 25  # Highest
        assert peak_frames[1]['person_count'] == 20  # Second highest
        assert peak_frames[2]['person_count'] == 15  # Third highest


# Integration tests
class TestVideoAnalysisIntegration:
    """Integration tests for video analysis pipeline."""
    
    @pytest.fixture
    def sample_video_with_content(self):
        """Create a video with more realistic content."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(temp_path), fourcc, 30.0, (640, 480))
        
        # Create 60 frames (2 seconds)
        for i in range(60):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        
        yield temp_path
        
        if temp_path.exists():
            temp_path.unlink()
    
    def test_full_processing_pipeline(self, sample_video_with_content):
        """Test the complete video processing pipeline."""
        # Initialize services
        processor = VideoProcessor(frame_sample_rate=30, max_frames=5)
        detector = PersonDetector(confidence_threshold=0.5)
        
        # Extract metadata
        metadata = processor.get_video_metadata(sample_video_with_content)
        assert metadata is not None
        
        # Extract frames
        frames_data = processor.extract_frames(sample_video_with_content)
        assert len(frames_data) > 0
        assert len(frames_data) <= 5  # Respects max_frames
        
        # Detect people in frames
        detections = []
        for frame_data in frames_data:
            detection = detector.detect_persons(frame_data['frame'])
            detections.append(detection)
        
        assert len(detections) == len(frames_data)
        
        # Calculate statistics
        stats = DetectionStats.calculate_statistics(detections)
        assert stats['total_frames'] == len(frames_data)
        assert stats['average_person_count'] >= 0
        
        print(f"\n✅ Pipeline test completed successfully!")
        print(f"   Frames processed: {len(frames_data)}")
        print(f"   Average person count: {stats['average_person_count']:.1f}")
        print(f"   Peak person count: {stats['max_person_count']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
