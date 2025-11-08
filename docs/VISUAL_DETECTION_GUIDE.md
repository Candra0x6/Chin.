# Visual Person Detection - Real-Time Bounding Boxes

## Overview
Enhanced video analysis now includes **real-time visual feedback** with green bounding boxes around each detected person. This allows you to see exactly what the system is detecting as it processes the video, frame by frame.

## Features

### ✅ Real-Time Visual Display
- **Green bounding boxes** around each detected person
- **Person count** displayed at the top of the frame
- **Frame number** and **timestamp** shown
- **Crowd level indicator** (Low/Moderate/High/Very High) with color coding
- **Confidence scores** for each detection

### ✅ Annotated Video Saving
- Save processed video with all bounding boxes and annotations
- Output: MP4 format with same resolution as input
- Includes all overlays (boxes, text, statistics)

### ✅ Interactive Controls
- **Press 'Q'** to quit visual display (analysis continues in background)
- Auto-close when analysis completes
- Resizable window for comfortable viewing

## Visual Elements

### Bounding Boxes
```
┌─────────────────┐
│ Person 0.87     │  ← Confidence score
│                 │
│                 │  ← Green rectangle
│                 │     around person
└─────────────────┘
```

### Info Panel (Top of Screen)
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Frame: 1234 | Time: 00:41                    ┃
┃ People Detected: 15                           ┃
┃                      Crowd Level: Moderate    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Crowd Level Colors
- 🟢 **Green**: Low (< 5 people)
- 🟡 **Yellow**: Moderate (5-14 people)
- 🟠 **Orange**: High (15-24 people)
- 🔴 **Red**: Very High (≥ 25 people)

## Usage

### Method 1: Standalone Script (Recommended for Testing)

```bash
# Test with visual display
python test_visual_analysis.py
```

**Interactive Menu:**
```
Choose a test mode:
  1. Full test (visual display + save annotated video)
  2. Visual display only (no video saving)

Enter choice (1 or 2, default=1): 1
```

**What You'll See:**
1. Window opens showing video frame
2. Green boxes appear around detected persons
3. Real-time person count updates
4. Frame progresses automatically
5. Press 'Q' to quit display early
6. Analysis continues even if you quit display

### Method 2: Python Code

```python
from pathlib import Path
from app.services.video_analysis import VideoAnalysisService

# Create service with visual display
service = VideoAnalysisService(
    frame_sample_rate=1,  # Process every frame
    confidence_threshold=0.5,
    show_visual=True,  # Enable real-time display
    save_annotated_video=True,  # Save to file
    output_video_path=Path("results/annotated_video.mp4")
)

# Run analysis
results = service.analyze_video(
    video_path=Path("uploads/sample_video.mp4"),
    save_detections=True
)

print(f"Average people: {results['statistics']['average_person_count']:.1f}")
print(f"Peak people: {results['statistics']['max_person_count']}")
```

### Method 3: API Request

```bash
# Start analysis with visual display
curl -X POST "http://localhost:8000/api/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "your-video-id",
    "show_visual": true,
    "save_annotated_video": true,
    "frame_sample_rate": 1,
    "confidence_threshold": 0.5
  }'
```

**Response:**
```json
{
  "analysis_id": "abc-123-def",
  "video_id": "your-video-id",
  "status": "processing",
  "message": "Video analysis started. Visual display will open in a new window. Annotated video will be saved to results folder."
}
```

**Note:** Visual display only works when API is running locally. In production/cloud deployments, use `save_annotated_video=true` instead.

## Configuration Options

### VideoAnalysisService Parameters

```python
service = VideoAnalysisService(
    frame_sample_rate=1,           # 1=all frames, 30=1 per second at 30fps
    confidence_threshold=0.5,      # 0.0-1.0, higher=stricter detection
    show_visual=True,              # Show real-time window
    save_annotated_video=True,     # Save to file
    output_video_path=Path("...")  # Where to save
)
```

### Frame Sample Rate Guide

| Value | Description | Use Case |
|-------|-------------|----------|
| 1 | Every frame | Smooth visual display, slower |
| 10 | Every 10th frame | Balanced performance |
| 30 | ~1 per second | Fast processing, less smooth |

### Confidence Threshold Guide

| Value | Detections | False Positives |
|-------|------------|-----------------|
| 0.3 | High | More likely |
| 0.5 | Balanced | Moderate |
| 0.7 | Strict | Less likely |

## Output Files

### Annotated Video
- **Location:** `results/annotated_{video_id}.mp4`
- **Format:** MP4 (H.264 codec)
- **Resolution:** Same as input video
- **FPS:** 30 (configurable)
- **Size:** ~2-3x larger than input (due to annotations)

### What's Included
✅ Green bounding boxes around persons
✅ Confidence scores for each detection
✅ Frame number and timestamp overlay
✅ Real-time person count
✅ Crowd level indicator
✅ Info panel with statistics

## Performance Considerations

### Real-Time Display
- **Overhead:** Adds ~10-20% processing time
- **CPU Usage:** Moderate increase for rendering
- **Recommended:** Local testing only

### Video Saving
- **Overhead:** Adds ~30-40% processing time
- **Disk Space:** Requires space for output video
- **Recommended:** Production use for sharing results

### Optimization Tips

**For Fastest Processing (no visual):**
```python
service = VideoAnalysisService(
    frame_sample_rate=30,
    show_visual=False,
    save_annotated_video=False
)
```

**For Smooth Visual Display:**
```python
service = VideoAnalysisService(
    frame_sample_rate=1,  # All frames
    show_visual=True,
    save_annotated_video=False  # Skip saving for speed
)
```

**For Production Sharing:**
```python
service = VideoAnalysisService(
    frame_sample_rate=1,
    show_visual=False,  # No display in production
    save_annotated_video=True,  # Save for later review
    output_video_path=Path("results/annotated.mp4")
)
```

## Troubleshooting

### Issue: Window Doesn't Open

**Possible Causes:**
- Running on headless server (no display)
- OpenCV GUI issues
- `show_visual=False` in configuration

**Solutions:**
1. Verify you're running locally with a display
2. Check OpenCV installation: `pip install opencv-python`
3. Set `show_visual=True` in service initialization
4. Use `save_annotated_video=True` as alternative

### Issue: Window Opens but No Video

**Possible Causes:**
- Video file not found
- Unsupported video format
- Corrupted video file

**Solutions:**
1. Verify video path is correct
2. Check video format (MP4/AVI recommended)
3. Try different video file
4. Check logs for error messages

### Issue: Bounding Boxes Not Visible

**Possible Causes:**
- Low confidence threshold
- No persons detected
- Model loading issue

**Solutions:**
1. Lower `confidence_threshold` to 0.3
2. Verify video contains visible persons
3. Check YOLOv8 model is downloaded
4. Review detection logs

### Issue: Slow Performance

**Possible Causes:**
- Processing every frame (`frame_sample_rate=1`)
- Large video resolution
- CPU-only processing (no GPU)

**Solutions:**
1. Increase `frame_sample_rate` to 10 or 30
2. Reduce video resolution before processing
3. Use GPU if available (CUDA-enabled device)
4. Close other applications

### Issue: "Press Q to Quit" Doesn't Work

**Possible Causes:**
- Window not in focus
- Keyboard input not captured

**Solutions:**
1. Click on the video window first
2. Press 'Q' or 'q' (case insensitive)
3. Wait a moment for processing
4. Close terminal to force stop

## Examples

### Example 1: Quick Visual Check
```python
# Fast visual preview of detections
service = VideoAnalysisService(
    frame_sample_rate=10,  # Every 10th frame
    show_visual=True,
    save_annotated_video=False
)

results = service.analyze_video(Path("test.mp4"))
```

### Example 2: Full Analysis + Save
```python
# Complete analysis with saved video
service = VideoAnalysisService(
    frame_sample_rate=1,  # All frames
    show_visual=True,
    save_annotated_video=True,
    output_video_path=Path("results/demo.mp4")
)

results = service.analyze_video(Path("hospital_video.mp4"))
```

### Example 3: Production Mode
```python
# No visual, just save annotated video
service = VideoAnalysisService(
    frame_sample_rate=5,  # Balance speed/quality
    show_visual=False,  # No display
    save_annotated_video=True,
    output_video_path=Path("results/output.mp4")
)

results = service.analyze_video(Path("input.mp4"))
```

## Technical Details

### Drawing Pipeline
1. **Frame Copy:** Original frame copied to preserve data
2. **Detection:** YOLOv8 processes frame with bounding boxes
3. **Box Drawing:** Green rectangles drawn at coordinates
4. **Label Addition:** Confidence scores added above boxes
5. **Info Panel:** Statistics overlay at top
6. **Display/Save:** Frame shown and/or saved to video

### Color Scheme
```python
# Bounding box: Green
box_color = (0, 255, 0)

# Crowd levels:
low_color = (0, 255, 0)      # Green
moderate_color = (0, 255, 255)  # Yellow
high_color = (0, 165, 255)   # Orange
very_high_color = (0, 0, 255)  # Red

# Text: White on semi-transparent black
text_color = (255, 255, 255)
background_color = (0, 0, 0)
```

### Video Writer Settings
```python
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30.0
size = (frame_width, frame_height)
```

## Integration with Existing Features

### ✅ All Calculations Preserved
Visual display does **NOT** affect:
- Person count statistics
- Crowd analytics
- Bottleneck detection
- Flow metrics
- Spatial distribution
- Enhanced analytics
- AI insights

### ✅ Additional Data
Visual display **ADDS**:
- Bounding box coordinates in results
- Confidence scores per detection
- Visual confirmation of detections

## Best Practices

### For Development/Testing
1. ✅ Use `show_visual=True` to verify detections
2. ✅ Set `frame_sample_rate=1` for smooth playback
3. ✅ Keep videos short (< 1 minute)
4. ✅ Use `save_annotated_video=False` for speed

### For Demos/Presentations
1. ✅ Use both `show_visual=True` and `save_annotated_video=True`
2. ✅ Process entire video (`frame_sample_rate=1`)
3. ✅ Share annotated video file
4. ✅ Use high-quality input videos

### For Production
1. ✅ Use `show_visual=False` (no GUI on servers)
2. ✅ Use `save_annotated_video=True` for review
3. ✅ Optimize `frame_sample_rate` for speed
4. ✅ Store annotated videos for auditing

## Comparison

| Feature | No Visual | Visual Display | Save Annotated |
|---------|-----------|----------------|----------------|
| **Speed** | Fastest | Slower | Slowest |
| **Real-time Feedback** | ❌ | ✅ | ❌ |
| **Saved Output** | ❌ | ❌ | ✅ |
| **Server Compatible** | ✅ | ❌ | ✅ |
| **Demo Friendly** | ❌ | ✅ | ✅ |
| **Disk Space** | Minimal | Minimal | High |

## FAQ

**Q: Can I use visual display in a Docker container?**
A: No, requires X11 forwarding or local display. Use `save_annotated_video` instead.

**Q: Will visual display slow down processing?**
A: Yes, adds ~10-20% overhead for rendering and display.

**Q: Can I change the bounding box color?**
A: Yes, modify `box_color` in `_draw_detections()` method.

**Q: Does pressing 'Q' stop the analysis?**
A: No, only closes display window. Analysis continues in background.

**Q: Can I save annotated video without showing display?**
A: Yes, set `show_visual=False` and `save_annotated_video=True`.

**Q: What video formats are supported?**
A: MP4, AVI, MOV, MKV (any format OpenCV can read).

**Q: Can I adjust the info panel size/position?**
A: Yes, modify `_draw_detections()` method in video_analysis.py.

---

**Updated:** November 7, 2025
**Status:** ✅ Implemented and Tested
**Next:** Phase 5 - AI Recommendation Engine with Gemini
