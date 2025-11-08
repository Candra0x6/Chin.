"""
Test script for visual person detection with real-time bounding boxes.

This script demonstrates the enhanced video analysis with:
- Real-time visual display with green bounding boxes around detected persons
- Frame-by-frame person count display
- Crowd level indicators
- Optional: Save annotated video to file

Usage:
    python test_visual_analysis.py

Requirements:
    - A video file to analyze
    - YOLOv8 model downloaded (will auto-download if not present)
    - Press 'Q' to quit the visual display early (analysis will continue)
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.video_analysis import VideoAnalysisService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_visual_analysis():
    """Test video analysis with real-time visual display."""
    
    # Configuration
    video_path = project_root / "uploads" / "sample_video.mp4"
    output_video_path = project_root / "results" / "annotated_video.mp4"
    
    # Check if video exists
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        logger.info("Please place a video file at: uploads/sample_video.mp4")
        logger.info("Or modify the video_path variable in this script")
        return
    
    logger.info("=" * 60)
    logger.info("VISUAL PERSON DETECTION TEST")
    logger.info("=" * 60)
    logger.info(f"Video: {video_path.name}")
    logger.info(f"Output: {output_video_path}")
    logger.info("")
    logger.info("Features:")
    logger.info("  ✓ Real-time visual display with bounding boxes")
    logger.info("  ✓ Green rectangles around each detected person")
    logger.info("  ✓ Frame number and timestamp display")
    logger.info("  ✓ Person count and crowd level indicators")
    logger.info("  ✓ Save annotated video to file")
    logger.info("")
    logger.info("Controls:")
    logger.info("  - Press 'Q' to quit visual display (analysis continues)")
    logger.info("  - Window will auto-close when analysis completes")
    logger.info("=" * 60)
    logger.info("")
    
    # Create service with visual display enabled
    service = VideoAnalysisService(
        frame_sample_rate=1,  # Process every frame for smooth display
        confidence_threshold=0.5,
        show_visual=True,  # Enable real-time display
        save_annotated_video=True,  # Save annotated video
        output_video_path=output_video_path
    )
    
    logger.info("Starting analysis with visual display...")
    logger.info("A window will open showing real-time person detection")
    logger.info("")
    
    # Progress callback
    def progress_callback(current, total, message):
        logger.info(f"Progress: {current}% - {message}")
    
    # Run analysis
    results = service.analyze_video(
        video_path=video_path,
        progress_callback=progress_callback,
        save_detections=True
    )
    
    # Display results
    logger.info("")
    logger.info("=" * 60)
    logger.info("ANALYSIS RESULTS")
    logger.info("=" * 60)
    
    if results.get("status") == "completed":
        stats = results.get("statistics", {})
        insights = results.get("insights", {})
        
        logger.info("")
        logger.info("📊 STATISTICS:")
        logger.info(f"  • Total frames processed: {results['processing_info']['frames_processed']}")
        logger.info(f"  • Processing time: {results['processing_info']['processing_time_seconds']:.2f} seconds")
        logger.info(f"  • Average people count: {stats['average_person_count']:.1f}")
        logger.info(f"  • Peak people count: {stats['max_person_count']}")
        logger.info(f"  • Min people count: {stats['min_person_count']}")
        
        logger.info("")
        logger.info("💡 INSIGHTS:")
        logger.info(f"  • Crowd level: {insights['crowd_level']}")
        logger.info(f"  • Peak congestion time: {insights['peak_congestion_time']}")
        logger.info(f"  • Suggested nurses: {insights['suggested_nurses']}")
        logger.info(f"  • Bottleneck detected: {'Yes' if insights['bottleneck_detected'] else 'No'}")
        
        logger.info("")
        logger.info(f"📝 Summary: {insights['summary']}")
        
        # Enhanced analytics
        if "enhanced_analytics" in results:
            enhanced = results["enhanced_analytics"]
            
            logger.info("")
            logger.info("🔬 ENHANCED ANALYTICS:")
            
            if "crowd_density" in enhanced:
                density = enhanced["crowd_density"]
                logger.info(f"  • Density level: {density.get('density_level', 'N/A')}")
                logger.info(f"  • Density per sqm: {density.get('density_per_sqm', 0):.3f}")
            
            if "bottleneck_analysis" in enhanced:
                bottleneck = enhanced["bottleneck_analysis"]
                logger.info(f"  • Bottlenecks detected: {bottleneck.get('bottlenecks_detected', 0)}")
                
                if bottleneck.get("bottleneck_periods"):
                    logger.info("  • Bottleneck periods:")
                    for period in bottleneck["bottleneck_periods"][:3]:  # Show top 3
                        logger.info(f"    - {period['start_time']} to {period['end_time']}")
                        logger.info(f"      Severity: {period['severity']} (score: {period['severity_score']:.1f})")
                        logger.info(f"      Peak count: {period['peak_count']}")
            
            if "spatial_distribution" in enhanced:
                spatial = enhanced["spatial_distribution"]
                logger.info(f"  • Distribution pattern: {spatial.get('distribution_pattern', 'N/A')}")
                if spatial.get("hotspots"):
                    logger.info(f"  • Hotspots: {', '.join(spatial['hotspots'])}")
            
            if "flow_metrics" in enhanced:
                flow = enhanced["flow_metrics"]
                logger.info(f"  • Crowd trend: {flow.get('trend', 'N/A')}")
                logger.info(f"  • Variability: {flow.get('variability', 'N/A')}")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ ANALYSIS COMPLETE")
        logger.info("=" * 60)
        logger.info(f"📹 Annotated video saved to: {output_video_path}")
        logger.info("")
        logger.info("What you saw:")
        logger.info("  ✓ Green bounding boxes around each detected person")
        logger.info("  ✓ Real-time person count at the top")
        logger.info("  ✓ Frame number and timestamp")
        logger.info("  ✓ Crowd level indicator (Low/Moderate/High/Very High)")
        logger.info("")
        logger.info("You can now:")
        logger.info("  • Review the annotated video: results/annotated_video.mp4")
        logger.info("  • Use the analysis results for further processing")
        logger.info("  • Share the annotated video to demonstrate detection capability")
        
    else:
        logger.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
    
    logger.info("")


def test_visual_analysis_without_saving():
    """Test video analysis with visual display only (no video saving)."""
    
    video_path = project_root / "uploads" / "sample_video.mp4"
    
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return
    
    logger.info("=" * 60)
    logger.info("VISUAL DISPLAY ONLY (No Video Saving)")
    logger.info("=" * 60)
    logger.info("This mode shows real-time detection without saving annotated video")
    logger.info("Faster processing, no output file created")
    logger.info("=" * 60)
    logger.info("")
    
    # Create service with visual display but no saving
    service = VideoAnalysisService(
        frame_sample_rate=1,
        confidence_threshold=0.5,
        show_visual=True,
        save_annotated_video=False
    )
    
    def progress_callback(current, total, message):
        if current % 10 == 0 or current == 100:
            logger.info(f"Progress: {current}% - {message}")
    
    results = service.analyze_video(
        video_path=video_path,
        progress_callback=progress_callback
    )
    
    if results.get("status") == "completed":
        logger.info("")
        logger.info("✅ Analysis complete (visual display only)")
        stats = results.get("statistics", {})
        logger.info(f"Average people: {stats.get('average_person_count', 0):.1f}")
        logger.info(f"Peak people: {stats.get('max_person_count', 0)}")


if __name__ == "__main__":
    print("\n")
    print("=" * 60)
    print("VIDEO ANALYSIS WITH REAL-TIME VISUAL DISPLAY")
    print("=" * 60)
    print("")
    print("Choose a test mode:")
    print("  1. Full test (visual display + save annotated video)")
    print("  2. Visual display only (no video saving)")
    print("")
    
    choice = input("Enter choice (1 or 2, default=1): ").strip() or "1"
    
    if choice == "1":
        test_visual_analysis()
    elif choice == "2":
        test_visual_analysis_without_saving()
    else:
        print("Invalid choice. Running full test...")
        test_visual_analysis()
