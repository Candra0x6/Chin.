"""
Tests for advanced analytics service.
"""

import pytest
import numpy as np
from app.services.analytics import CrowdAnalytics


class TestCrowdAnalytics:
    """Tests for CrowdAnalytics class."""
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance."""
        return CrowdAnalytics(
            high_density_threshold=15,
            bottleneck_threshold_multiplier=1.5,
            min_bottleneck_duration=3
        )
    
    @pytest.fixture
    def sample_detections(self):
        """Create sample detection data."""
        return [
            {"person_count": 5},
            {"person_count": 10},
            {"person_count": 15},
            {"person_count": 20},
            {"person_count": 25},
            {"person_count": 20},
            {"person_count": 15},
            {"person_count": 10},
            {"person_count": 8},
            {"person_count": 5}
        ]
    
    @pytest.fixture
    def sample_frames_data(self):
        """Create sample frame metadata."""
        return [
            {
                "frame_number": i * 30,
                "timestamp": i * 1.0,
                "timestamp_formatted": f"00:{i:02d}"
            }
            for i in range(10)
        ]
    
    def test_analytics_initialization(self, analytics_service):
        """Test analytics service initialization."""
        assert analytics_service.high_density_threshold == 15
        assert analytics_service.bottleneck_threshold_multiplier == 1.5
        assert analytics_service.min_bottleneck_duration == 3
    
    def test_calculate_crowd_density(self, analytics_service):
        """Test crowd density calculation."""
        # Low density
        result = analytics_service.calculate_crowd_density(5, 100.0)
        assert result["person_count"] == 5
        assert result["area_sqm"] == 100.0
        assert result["density_per_sqm"] == 0.05
        assert result["density_level"] == "Very Low"
        assert result["severity_score"] == 1
        
        # High density
        result = analytics_service.calculate_crowd_density(50, 100.0)
        assert result["density_level"] == "High"
        assert result["severity_score"] == 4
        
        # Very high density
        result = analytics_service.calculate_crowd_density(70, 100.0)
        assert result["density_level"] == "Very High"
        assert result["severity_score"] == 5
    
    def test_analyze_crowd_distribution(self, analytics_service):
        """Test crowd distribution analysis."""
        # Create detections with bounding boxes
        detections = [
            {
                "person_count": 2,
                "detections": [
                    {"bbox": [100, 100, 200, 300]},  # Top-left
                    {"bbox": [500, 500, 600, 700]}   # Bottom-center
                ]
            },
            {
                "person_count": 1,
                "detections": [
                    {"bbox": [100, 100, 200, 300]}   # Top-left again
                ]
            }
        ]
        
        frames_data = [
            {"frame_number": 0, "timestamp": 0},
            {"frame_number": 30, "timestamp": 1}
        ]
        
        result = analytics_service.analyze_crowd_distribution(
            detections, frames_data, 1920, 1080
        )
        
        assert "distribution_pattern" in result
        assert "zones" in result
        assert "hotspots" in result
        assert len(result["zones"]) == 9  # 3x3 grid
        assert result["total_detections_analyzed"] == 3
    
    def test_detect_bottlenecks(self, analytics_service, sample_detections, sample_frames_data):
        """Test bottleneck detection."""
        result = analytics_service.detect_bottlenecks(
            sample_detections, sample_frames_data, fps=30.0
        )
        
        assert "bottlenecks_detected" in result
        assert "bottleneck_periods" in result
        assert "total_bottleneck_duration_seconds" in result
        assert "threshold_used" in result
        assert isinstance(result["bottlenecks_detected"], int)
        
        # Should detect bottleneck where count > avg * 1.5
        # Average is 13.3, so threshold is ~20
        # Counts of 20, 25, 20 should trigger bottleneck
        assert result["bottlenecks_detected"] >= 1
    
    def test_bottleneck_severity_classification(self, analytics_service):
        """Test bottleneck severity classification."""
        # Create data with clear bottleneck
        detections = [
            {"person_count": 10},  # Normal
            {"person_count": 10},
            {"person_count": 30},  # Bottleneck start (3x average)
            {"person_count": 35},  # Peak
            {"person_count": 30},
            {"person_count": 28},  # Bottleneck end
            {"person_count": 10},  # Back to normal
        ]
        
        frames_data = [
            {"frame_number": i * 30, "timestamp": i * 1.0, "timestamp_formatted": f"00:{i:02d}"}
            for i in range(7)
        ]
        
        result = analytics_service.detect_bottlenecks(detections, frames_data)
        
        assert result["bottlenecks_detected"] > 0
        
        # Check severity classification
        if result["bottleneck_periods"]:
            bottleneck = result["bottleneck_periods"][0]
            assert "severity" in bottleneck
            assert "severity_score" in bottleneck
            assert bottleneck["severity"] in ["Critical", "High", "Moderate", "Low"]
    
    def test_create_visualization_data(self, analytics_service, sample_detections, sample_frames_data):
        """Test visualization data creation."""
        result = analytics_service.create_visualization_data(
            sample_detections, sample_frames_data, interval_seconds=3
        )
        
        assert "chart_data" in result
        assert "interval_seconds" in result
        assert "total_intervals" in result
        assert "summary" in result
        
        # Check chart data structure
        if result["chart_data"]:
            interval = result["chart_data"][0]
            assert "time" in interval
            assert "timestamp" in interval
            assert "average" in interval
            assert "min" in interval
            assert "max" in interval
            assert "samples" in interval
        
        # Check summary
        summary = result["summary"]
        assert "overall_average" in summary
        assert "overall_min" in summary
        assert "overall_max" in summary
    
    def test_calculate_flow_metrics(self, analytics_service, sample_detections, sample_frames_data):
        """Test flow metrics calculation."""
        result = analytics_service.calculate_flow_metrics(
            sample_detections, sample_frames_data, video_duration=10.0
        )
        
        assert "flow_rate" in result
        assert "trend" in result
        assert "variability" in result
        assert "coefficient_of_variation" in result
        
        # Check trend classification
        assert result["trend"] in ["Increasing", "Decreasing", "Stable"]
        assert result["variability"] in ["High", "Moderate", "Low"]
    
    def test_generate_comprehensive_report(self, analytics_service, sample_detections, sample_frames_data):
        """Test comprehensive report generation."""
        video_metadata = {
            "width": 1920,
            "height": 1080,
            "duration_seconds": 10.0,
            "fps": 30.0
        }
        
        result = analytics_service.generate_comprehensive_report(
            sample_detections, sample_frames_data, video_metadata
        )
        
        # Check all main sections
        assert "crowd_density" in result
        assert "spatial_distribution" in result
        assert "bottleneck_analysis" in result
        assert "visualization_data" in result
        assert "flow_metrics" in result
        assert "generated_at" in result
        
        # Verify structure of each section
        assert "density_level" in result["crowd_density"]
        assert "distribution_pattern" in result["spatial_distribution"]
        assert "bottlenecks_detected" in result["bottleneck_analysis"]
        assert "chart_data" in result["visualization_data"]
        assert "trend" in result["flow_metrics"]
    
    def test_empty_data_handling(self, analytics_service):
        """Test handling of empty data."""
        # Empty detections
        result = analytics_service.detect_bottlenecks([], [], fps=30.0)
        assert result["bottlenecks_detected"] == 0
        
        # Empty visualization data
        result = analytics_service.create_visualization_data([], [])
        assert result["chart_data"] == []
        
        # Empty distribution
        result = analytics_service.analyze_crowd_distribution([], [], 1920, 1080)
        assert result["distribution_pattern"] == "No data"
    
    def test_zone_naming(self, analytics_service):
        """Test zone naming convention."""
        # Test all 9 zones
        expected_names = [
            "Top-Left", "Top-Center", "Top-Right",
            "Middle-Left", "Middle-Center", "Middle-Right",
            "Bottom-Left", "Bottom-Center", "Bottom-Right"
        ]
        
        for row in range(3):
            for col in range(3):
                name = analytics_service._get_zone_name(row, col)
                assert name in expected_names
    
    def test_time_formatting(self, analytics_service):
        """Test time formatting."""
        assert analytics_service._format_time(0) == "00:00"
        assert analytics_service._format_time(30) == "00:30"
        assert analytics_service._format_time(90) == "01:30"
        assert analytics_service._format_time(3661) == "61:01"


class TestBottleneckDetection:
    """Specific tests for bottleneck detection logic."""
    
    def test_bottleneck_duration_threshold(self):
        """Test minimum duration threshold for bottlenecks."""
        analytics = CrowdAnalytics(min_bottleneck_duration=3)
        
        # Short spike (2 frames) - should NOT be detected
        detections = [
            {"person_count": 10},
            {"person_count": 30},  # Spike
            {"person_count": 30},  # Only 2 frames
            {"person_count": 10},
        ]
        
        frames_data = [
            {"frame_number": i * 30, "timestamp": i * 1.0, "timestamp_formatted": f"00:{i:02d}"}
            for i in range(4)
        ]
        
        result = analytics.detect_bottlenecks(detections, frames_data)
        
        # Should not detect bottleneck due to short duration
        assert result["bottlenecks_detected"] == 0
    
    def test_multiple_bottlenecks(self):
        """Test detection of multiple separate bottlenecks."""
        analytics = CrowdAnalytics(min_bottleneck_duration=2)
        
        # Two separate bottleneck periods
        detections = [
            {"person_count": 5},
            {"person_count": 20},  # First bottleneck
            {"person_count": 20},
            {"person_count": 5},   # Normal
            {"person_count": 5},
            {"person_count": 20},  # Second bottleneck
            {"person_count": 20},
            {"person_count": 5},
        ]
        
        frames_data = [
            {"frame_number": i * 30, "timestamp": i * 1.0, "timestamp_formatted": f"00:{i:02d}"}
            for i in range(8)
        ]
        
        result = analytics.detect_bottlenecks(detections, frames_data)
        
        # Should detect 2 separate bottlenecks
        assert result["bottlenecks_detected"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
