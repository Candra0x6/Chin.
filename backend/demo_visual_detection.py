"""
Quick demo of visual person detection.

Run this to see real-time bounding boxes on a sample video.
"""

from pathlib import Path
from app.services.video_analysis import VideoAnalysisService

# Path to your video
VIDEO_PATH = Path("uploads/sample_video.mp4")
OUTPUT_PATH = Path("results/demo_output.mp4")

# Ensure paths exist
VIDEO_PATH.parent.mkdir(exist_ok=True)
OUTPUT_PATH.parent.mkdir(exist_ok=True)

print("=" * 60)
print("VISUAL PERSON DETECTION DEMO")
print("=" * 60)
print()
print("This demo will:")
print("  1. Open a window showing real-time person detection")
print("  2. Draw GREEN BOXES around each detected person")
print("  3. Show person count, frame number, and timestamp")
print("  4. Display crowd level (Low/Moderate/High/Very High)")
print("  5. Save annotated video to:", OUTPUT_PATH)
print()
print("Controls:")
print("  - Press 'Q' to quit display (analysis continues)")
print("  - Window closes automatically when complete")
print()
print("=" * 60)
print()

# Check if video exists
if not VIDEO_PATH.exists():
    print(f"❌ Error: Video not found at {VIDEO_PATH}")
    print()
    print("Please:")
    print(f"  1. Place a video file at: {VIDEO_PATH}")
    print("  2. Or update VIDEO_PATH in this script")
    print()
    exit(1)

print(f"✅ Video found: {VIDEO_PATH.name}")
print()

# Create service with visual display enabled
print("Initializing video analysis service...")
service = VideoAnalysisService(
    frame_sample_rate=1,  # Process every frame for smooth display
    confidence_threshold=0.5,
    show_visual=True,  # ⭐ Enable real-time visual display
    save_annotated_video=True,  # ⭐ Save annotated video
    output_video_path=OUTPUT_PATH
)

print("✅ Service initialized")
print()
print("Starting analysis... (window will open)")
print()

# Run analysis with progress updates
def progress(current, total, message):
    if current % 20 == 0 or current == 100:
        print(f"  [{current}%] {message}")

results = service.analyze_video(
    video_path=VIDEO_PATH,
    progress_callback=progress,
    save_detections=True
)

# Show results
print()
print("=" * 60)
print("RESULTS")
print("=" * 60)
print()

if results.get("status") == "completed":
    stats = results["statistics"]
    insights = results["insights"]
    
    print("📊 Statistics:")
    print(f"  • Frames processed: {results['processing_info']['frames_processed']}")
    print(f"  • Processing time: {results['processing_info']['processing_time_seconds']:.2f}s")
    print(f"  • Average people: {stats['average_person_count']:.1f}")
    print(f"  • Peak people: {stats['max_person_count']}")
    print()
    
    print("💡 Insights:")
    print(f"  • Crowd level: {insights['crowd_level']}")
    print(f"  • Peak time: {insights['peak_congestion_time']}")
    print(f"  • Suggested nurses: {insights['suggested_nurses']}")
    print(f"  • Bottleneck: {'Yes ⚠️' if insights['bottleneck_detected'] else 'No ✅'}")
    print()
    
    print("📹 Output:")
    print(f"  • Annotated video: {OUTPUT_PATH}")
    print()
    
    print("=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print()
    print("What you saw:")
    print("  ✓ Green boxes around each person")
    print("  ✓ Real-time person count")
    print("  ✓ Frame-by-frame detection")
    print("  ✓ Crowd level indicators")
    print()
    print("Next steps:")
    print(f"  • Watch annotated video: {OUTPUT_PATH}")
    print("  • Try with your own videos")
    print("  • Adjust confidence threshold or frame rate")
    print()
else:
    print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
    print()
