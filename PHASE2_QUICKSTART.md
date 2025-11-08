# 🚀 Phase 2 Complete - Quick Start Guide

## ✅ What's New

Phase 2 has been successfully implemented! You now have a fully functional video upload API.

---

## 🎯 Quick Test (5 minutes)

### 1. Start the Server
```bash
# Make sure you're in the project directory
cd d:\Vs_Code_Project\Competition\NEXT\Chin

# Activate virtual environment
venv\Scripts\activate

# Start server
python -m app.main
```

**Expected output:**
```
🚀 HospiTwin Lite Backend Started
📁 Upload directory: uploads
📁 Results directory: results
📁 Models directory: models
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test the API

**Option A: Using the Test Script** (Recommended)
```bash
# In a new terminal (keep server running)
cd d:\Vs_Code_Project\Competition\NEXT\Chin
venv\Scripts\activate
python test_upload_api.py
```

**Option B: Using the Web Interface**
```
1. Open browser: http://localhost:8000/docs
2. Click on "POST /upload"
3. Click "Try it out"
4. Click "Choose File" and select a video
5. Click "Execute"
6. See the response below
```

**Option C: Using cURL**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_video.mp4"
```

---

## 📋 Available Endpoints

### 1. **Upload Video**
```
POST /upload
```
Upload a video file (mp4, avi, mov, mkv) up to 100MB

### 2. **Check Status**
```
GET /upload/status/{video_id}
```
Get status and metadata of uploaded video

### 3. **List Uploads**
```
GET /upload/list?limit=10&offset=0
```
List all uploaded videos with pagination

### 4. **Delete Upload**
```
DELETE /upload/{video_id}
```
Delete uploaded video and its metadata

### 5. **Health Check**
```
GET /health
```
Verify API is running

---

## 🧪 Testing Checklist

Run through these tests to verify everything works:

- [ ] **Server starts** without errors
- [ ] **Health check** works: http://localhost:8000/health
- [ ] **API docs** accessible: http://localhost:8000/docs
- [ ] **Upload a video** file successfully
- [ ] **Check status** of uploaded video
- [ ] **List uploads** shows your video
- [ ] **Delete upload** removes video
- [ ] **Invalid file** (e.g., .txt) is rejected
- [ ] **Large file** (>100MB) is rejected

---

## 📊 What Gets Stored

### On Disk (uploads/ folder)
```
uploads/20251107_103045_a3f2d8c9_video.mp4
```
- Unique filename with timestamp and UUID
- Original video data preserved

### In Supabase (video_uploads table)
```json
{
  "id": "uuid-here",
  "filename": "video.mp4",
  "file_path": "uploads/20251107_103045_a3f2d8c9_video.mp4",
  "file_size": 1024000,
  "mime_type": "video/mp4",
  "status": "uploaded",
  "created_at": "2025-11-07T10:30:00Z"
}
```

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn app.main:app --port 8001
```

### "Import errors"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Upload fails with "Supabase error"
- Check `.env` has correct `SUPABASE_URL` and `SUPABASE_KEY`
- Verify Supabase database schema is created
- Run: `python test_supabase_connection.py`

### "File too large" error
- Default limit is 100MB
- Change in `.env`: `MAX_UPLOAD_SIZE=209715200` (for 200MB)

---

## 💡 Tips

### Upload from Python
```python
import requests

with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
    print(response.json())
```

### Check uploaded files
```bash
# Windows
dir uploads

# Linux/Mac
ls -lh uploads/
```

### View in Supabase
```
1. Open Supabase dashboard
2. Go to Table Editor
3. Select "video_uploads" table
4. See all uploaded videos
```

---

## 🎯 Next Steps

### Immediate
1. ✅ Test all endpoints
2. ✅ Verify Supabase integration
3. ✅ Upload sample videos

### Phase 3 (Next)
- Video frame extraction with OpenCV
- Person detection with YOLOv8
- Process uploaded videos automatically

---

## 📚 Documentation

- **API Docs:** http://localhost:8000/docs
- **Phase 2 Summary:** `docs/PHASE2_SUMMARY.md`
- **Task List:** `docs/task.md`
- **Code:**
  - Upload Router: `app/routers/upload.py`
  - Validators: `app/utils/validators.py`
  - File Handler: `app/utils/file_handler.py`

---

## ✅ Phase 2 Complete!

**What works now:**
- ✅ Video file uploads
- ✅ File validation (format, size)
- ✅ Secure file storage
- ✅ Supabase metadata storage
- ✅ Status checking
- ✅ Upload management (list, delete)
- ✅ Comprehensive error handling
- ✅ Unit tests

**What's next:**
- 🎥 Phase 3: Video Processing & People Detection

---

**Ready to process videos!** 🚀

Run `python -m app.main` to start the server!
