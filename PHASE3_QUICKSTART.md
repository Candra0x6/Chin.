# 🎥 Phase 3 Quick Start - Video Analysis

**Status:** ✅ Complete | **Date:** November 7, 2025

---

## 🚀 Quick Test (10 minutes)

### **Step 1: Start the Server**
```bash
# Activate virtual environment
venv\Scripts\activate

# Start server
python -m app.main
```

**Expected Output:**
```
🚀 HospiTwin Lite Backend Started
📁 Upload directory: uploads
📁 Results directory: results
📁 Models directory: models
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Note:** On first run, YOLOv8 will automatically download (~6MB). This takes 1-2 minutes.

---

### **Step 2: Test the Analysis API**

#### **Option A: Automated Test Script** ⭐ (Recommended)
```bash
# In a new terminal (keep server running)
venv\Scripts\activate
python test_analysis_api.py
```

This script will:
1. ✅ Create a sample video automatically
2. ✅ Upload the video
3. ✅ Start analysis
4. ✅ Monitor progress in real-time
5. ✅ Display complete results
6. ✅ Clean up test files

---

#### **Option B: Manual API Testing**

**1. Upload a Video:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_video.mp4"
```

**Response:**
```json
{
  "id": "abc123-video-id",
  "filename": "your_video.mp4",
  "status": "uploaded",
  "message": "Video uploaded successfully"
}
```

**2. Start Analysis:**
```bash
curl -X POST "http://localhost:8000/analyze/abc123-video-id"
```

**Response:**
```json
{
  "analysis_id": "xyz789-analysis-id",
  "video_id": "abc123-video-id",
  "status": "processing",
  "message": "Video analysis started..."
}
```

**3. Check Progress:**
```bash
curl "http://localhost:8000/analyze/status/xyz789-analysis-id"
```

**Response (Processing):**
```json
{
  "analysis_id": "xyz789-analysis-id",
  "status": "processing",
  "progress": 65,
  "message": "Detecting people: 58/90 frames"
}
```

**4. Get Results (when complete):**
```bash
curl "http://localhost:8000/analyze/results/xyz789-analysis-id"
```

---

#### **Option C: Browser Interface** 🌐
```
1. Open: http://localhost:8000/docs
2. Expand "POST /upload"
3. Click "Try it out"
4. Upload video file
5. Copy the video ID
6. Expand "POST /analyze/{video_id}"
7. Paste video ID and execute
8. Copy analysis ID
9. Check status with "GET /analyze/status/{analysis_id}"
```

---

## 📊 What Gets Analyzed

### **Input:** Video File
- Formats: MP4, AVI, MOV, MKV
- Max size: 100MB
- Any FPS (optimized for 30fps)

### **Processing:**
1. **Frame Extraction** (OpenCV)
   - Samples 1 frame per second
   - Extracts metadata (duration, FPS, resolution)

2. **Person Detection** (YOLOv8)
   - Detects people in each frame
   - Counts persons per frame
   - Tracks bounding boxes

3. **Analytics** (NumPy)
   - Average person count
   - Peak congestion times
   - Timeline (30-second intervals)
   - Crowd level classification

4. **Insights** (AI-ready)
   - Staff recommendations
   - Bottleneck detection
   - Summary generation

### **Output:** Complete Analysis
```json
{
  "status": "completed",
  "video_metadata": {
    "duration_seconds": 180,
    "fps": 30,
    "resolution": "1920x1080"
  },
  "statistics": {
    "average_person_count": 8.5,
    "max_person_count": 15,
    "min_person_count": 3,
    "total_detections": 450
  },
  "insights": {
    "crowd_level": "Moderate",
    "peak_congestion_time": "01:45",
    "suggested_nurses": 2,
    "bottleneck_detected": true,
    "summary": "The ER waiting area shows moderate crowd levels..."
  },
  "timeline": [...],
  "peak_congestion_frames": [...]
}
```

---

## 🧪 Testing Checklist

Run through these tests:

### **Server & Model**
- [ ] Server starts without errors
- [ ] YOLOv8 model downloads (first run only)
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Health check works: http://localhost:8000/health

### **Video Upload**
- [ ] Upload video successfully
- [ ] Get video ID
- [ ] Check upload status

### **Video Analysis**
- [ ] Start analysis with video ID
- [ ] Get analysis ID
- [ ] Progress updates correctly (0% → 100%)
- [ ] Analysis completes successfully

### **Results**
- [ ] Results stored in Supabase
- [ ] Full results retrievable via API
- [ ] Results contain all expected fields
- [ ] Insights make sense

### **Additional Endpoints**
- [ ] List analyses works
- [ ] Service info accessible
- [ ] Delete analysis works

---

## 🐛 Troubleshooting

### **Server Won't Start**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn app.main:app --port 8001
```

### **YOLOv8 Download Fails**
```bash
# Check internet connection
# Model downloads from GitHub (~6MB)
# Wait 1-2 minutes for first download
```

### **Analysis Fails**
```bash
# Check video file format (must be MP4, AVI, MOV, or MKV)
# Check video file size (max 100MB)
# Check logs in terminal for errors
```

### **Out of Memory**
```python
# Reduce frame sample rate in config
# In app/routers/analysis.py:
analysis_service = VideoAnalysisService(
    frame_sample_rate=60,  # Process every 2 seconds instead of 1
    max_frames=100  # Limit total frames
)
```

### **GPU Not Detected**
```python
# Check CUDA installation
import torch
print(torch.cuda.is_available())  # Should print True

# If False, YOLOv8 will use CPU (slower but works)
```

---

## 💡 Performance Tips

### **Faster Processing**
1. **Increase Frame Sample Rate:** Process fewer frames
   ```python
   frame_sample_rate=60  # Every 2 seconds instead of 1
   ```

2. **Use GPU:** Ensure CUDA is installed for 5-10x speedup

3. **Limit Frames:** For quick tests
   ```python
   max_frames=50  # Only process first 50 frames
   ```

### **Better Accuracy**
1. **Lower Confidence Threshold:**
   ```python
   confidence_threshold=0.3  # Detect more people (may have false positives)
   ```

2. **Process More Frames:**
   ```python
   frame_sample_rate=15  # 2 frames per second
   ```

---

## 📈 Expected Processing Times

| Video Duration | Frames | Processing Time (CPU) | Processing Time (GPU) |
|----------------|--------|----------------------|----------------------|
| 5 seconds      | 5      | 2-3 seconds          | 1-2 seconds          |
| 30 seconds     | 30     | 10-15 seconds        | 3-5 seconds          |
| 2 minutes      | 120    | 40-60 seconds        | 10-15 seconds        |
| 5 minutes      | 300    | 90-120 seconds       | 25-35 seconds        |

**Note:** Times assume 30 FPS video with frame_sample_rate=30 (1 frame/second)

---

## 🎯 Example Output

### **Sample Analysis Results**

**Video:** 3-minute ER waiting room footage

```json
{
  "video_metadata": {
    "duration_seconds": 180,
    "fps": 30,
    "total_frames": 5400,
    "frames_processed": 180
  },
  "statistics": {
    "average_person_count": 12.5,
    "max_person_count": 23,
    "min_person_count": 5,
    "total_detections": 2250
  },
  "insights": {
    "crowd_level": "High",
    "peak_congestion_time": "02:15",
    "suggested_nurses": 3,
    "bottleneck_detected": true,
    "summary": "The ER waiting area shows high crowd levels with an average of 12.5 people. Peak congestion of 23 people occurred at 02:15. Recommended staffing: 3 nurse(s) for optimal flow."
  }
}
```

---

## 🔗 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/analyze/{video_id}` | Start analysis |
| GET | `/analyze/status/{analysis_id}` | Check progress |
| GET | `/analyze/results/{analysis_id}` | Get full results |
| GET | `/analyze/list` | List all analyses |
| DELETE | `/analyze/{analysis_id}` | Delete analysis |
| GET | `/analyze/service/info` | Service configuration |

---

## 📚 Documentation

- **Full Phase 3 Summary:** `docs/PHASE3_SUMMARY.md`
- **API Documentation:** http://localhost:8000/docs
- **Task List:** `docs/task.md`

---

## ✅ Phase 3 Complete!

**What Works:**
- ✅ Video frame extraction (OpenCV)
- ✅ Person detection (YOLOv8)
- ✅ Real-time progress tracking
- ✅ Comprehensive analytics
- ✅ AI-ready insights
- ✅ Supabase storage
- ✅ Complete API
- ✅ Automated testing

**What's Next:**
- 🎯 Phase 4: Enhanced Crowd Analytics
- 🤖 Phase 5: AI Recommendation Engine (Gemini)
- 💬 Phase 6: AI Assistant Chat

---

**Ready to analyze videos!** 🎥✨

Run `python test_analysis_api.py` to see it in action!
