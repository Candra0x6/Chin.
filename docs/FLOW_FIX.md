# Upload-to-Analysis Flow Fix

**Date**: November 11, 2025  
**Issue**: Incorrect flow after video upload  
**Status**: ✅ **FIXED**

---

## 🐛 Problem

The frontend was using an **incorrect flow** after uploading videos. It was trying to navigate directly to the analysis page using the `video_id` from upload, but the backend requires a separate analysis step.

### ❌ Old (Incorrect) Flow
```
1. Upload Video → Get video_id
2. Navigate to /analysis/{video_id} ❌ Wrong!
3. Analysis page tries to fetch results with video_id (fails)
```

---

## ✅ Solution

Updated to match the **Python backend flow** from integration tests:

### ✅ New (Correct) Flow
```
1. Upload Video → Get video_id
2. Start Analysis with video_id → Get analysis_id
3. Navigate to /analysis/{analysis_id} ✓ Correct!
4. Analysis page polls status with analysis_id
5. Display results when complete
```

---

## 🔧 Changes Made

### 1. Added `analyzeVideo` Function (`lib/api.ts`)

**New Function**:
```typescript
/**
 * Start video analysis
 */
export async function analyzeVideo(
  videoId: string,
  config?: {
    show_visual?: boolean;
    save_annotated_video?: boolean;
    frame_sample_rate?: number;
    confidence_threshold?: number;
    enable_ai_insights?: boolean;
    gemini_api_key?: string;
  }
): Promise<{ analysis_id: string; message: string; status: string }>
```

**Usage**:
```typescript
const result = await analyzeVideo(videoId, {
  show_visual: false,
  save_annotated_video: false,
  frame_sample_rate: 30,
  confidence_threshold: 0.5,
  enable_ai_insights: true,
});

// result.analysis_id is the ID to use for polling and results
```

---

### 2. Updated Upload Success Handler (`app/page.tsx`)

**Before**:
```typescript
const handleUploadSuccess = (result: VideoUploadResponse) => {
  // Just navigate to /analysis/{video_id}
  router.push(`/analysis/${result.id}`);  // ❌ Wrong!
};
```

**After**:
```typescript
const handleUploadSuccess = async (result: VideoUploadResponse) => {
  try {
    toast.success('Video uploaded! Starting analysis...');
    
    // 1. Start analysis with video_id
    const analysisResult = await analyzeVideo(result.id, {
      show_visual: false,
      save_annotated_video: false,
      frame_sample_rate: 30,
      confidence_threshold: 0.5,
      enable_ai_insights: true,
    });
    
    // 2. Add to history with analysis_id
    addToHistory({
      id: analysisResult.analysis_id,  // ✓ Use analysis_id
      filename: result.filename,
      uploadedAt: new Date().toISOString(),
      status: 'processing',
    });
    
    // 3. Navigate to /analysis/{analysis_id}
    router.push(`/analysis/${analysisResult.analysis_id}`);
  } catch (error) {
    toast.error(`Failed to start analysis: ${error.message}`);
  }
};
```

---

## 📊 API Endpoints Used

### 1. Upload Video
```http
POST /api/upload
Content-Type: multipart/form-data

Response:
{
  "id": "video-uuid",
  "filename": "sample_video.mp4",
  "path": "/uploads/...",
  "status": "uploaded"
}
```

### 2. Start Analysis (NEW!)
```http
POST /api/analyze/{video_id}
Content-Type: application/json

Body:
{
  "upload_id": "video-uuid",
  "show_visual": false,
  "save_annotated_video": false,
  "frame_sample_rate": 30,
  "confidence_threshold": 0.5,
  "enable_ai_insights": true,
  "gemini_api_key": ""
}

Response:
{
  "analysis_id": "analysis-uuid",
  "message": "Analysis started",
  "status": "processing"
}
```

### 3. Poll Analysis Status
```http
GET /api/analyze/status/{analysis_id}

Response:
{
  "analysis_id": "analysis-uuid",
  "status": "processing",  // or "completed", "failed"
  "progress": 45,
  "message": "Processing video frames...",
  "result": {...}  // Only when status === "completed"
}
```

### 4. Get Results
```http
GET /api/results/{analysis_id}

Response:
{
  "analysis_id": "analysis-uuid",
  "video_name": "sample_video.mp4",
  "created_at": "2025-11-11T...",
  "results": {
    "avg_count": 12.5,
    "peak_count": 25,
    "crowd_level": "High",
    "suggested_nurses": 8,
    ...
  }
}
```

---

## 🎯 User Experience Flow

### Step-by-Step UX
1. **User uploads video**
   - Toast: "Video uploaded! Starting analysis..."
   - Loading spinner shown

2. **System starts analysis**
   - Backend processes video with YOLOv8
   - Returns `analysis_id`

3. **Redirect to analysis page**
   - Toast: "Analysis started! Redirecting..."
   - Navigate to `/analysis/{analysis_id}`

4. **Analysis page polls status**
   - Shows progress bar (0-100%)
   - Shows status messages
   - Updates every 3 seconds

5. **Display results**
   - When status === "completed"
   - Shows crowd statistics, charts, recommendations

---

## 🧪 Testing

### Manual Test
```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload

# 2. Start frontend
cd web
npm run dev

# 3. Upload a video
# - Go to http://localhost:3000
# - Click upload
# - Select sample_video.mp4
# - Verify:
#   ✓ Toast shows "Video uploaded! Starting analysis..."
#   ✓ Toast shows "Analysis started! Redirecting..."
#   ✓ URL changes to /analysis/{analysis_id}
#   ✓ Progress bar shows 0-100%
#   ✓ Results display when complete
```

### Integration Test
The Python integration test (`tests/test_integration.py`) already tests this flow:

```python
# 1. Upload
upload_response = requests.post(f"{API_URL}/upload", files=files)
video_id = upload_response.json()['id']

# 2. Analyze
analyze_response = requests.post(
    f"{API_URL}/analyze/{video_id}",
    json={...}
)
analysis_id = analyze_response.json()['analysis_id']

# 3. Poll status
status_response = requests.get(f"{API_URL}/analyze/status/{analysis_id}")

# 4. Get results
result_response = requests.get(f"{API_URL}/results/{analysis_id}")
```

---

## 📝 Key Points

### Important IDs
- **`video_id`**: Returned from `/api/upload`, used to **start** analysis
- **`analysis_id`**: Returned from `/api/analyze/{video_id}`, used for **everything else**

### Always Use `analysis_id` For:
- ✅ Polling status: `/api/analyze/status/{analysis_id}`
- ✅ Getting results: `/api/results/{analysis_id}`
- ✅ Starting chat: `/api/chat/start/{analysis_id}`
- ✅ Exporting data: `/api/results/{analysis_id}/export/...`

### Only Use `video_id` For:
- ✅ Starting analysis: `/api/analyze/{video_id}`
- ✅ Deleting upload: `/api/upload/{video_id}`

---

## 🚀 Benefits of This Fix

1. **Correct Flow** - Matches backend implementation
2. **Better UX** - Users see analysis progress immediately
3. **Error Handling** - Proper error messages if analysis fails to start
4. **Consistent** - Uses same pattern as Python integration tests
5. **Scalable** - Can easily add analysis configuration options

---

## 🔄 Migration Notes

### For Existing Users
If users have bookmarked URLs with old `video_id` format:
- Old: `/analysis/{video_id}` ❌ Will fail
- New: `/analysis/{analysis_id}` ✅ Works correctly

**Solution**: The analysis page (`app/analysis/[id]/page.tsx`) already handles this by checking if the ID is valid. If not found, it shows an error.

### For Developers
When adding new features that interact with analysis:
- ✅ **Always use** `analysis_id` (from `/api/analyze/{video_id}` response)
- ❌ **Never use** `video_id` for anything except starting analysis

---

## ✅ Verification Checklist

- [x] Added `analyzeVideo` function to API client
- [x] Updated `handleUploadSuccess` to call `analyzeVideo`
- [x] Changed navigation to use `analysis_id` instead of `video_id`
- [x] Added proper error handling with toasts
- [x] Tested build - no TypeScript errors
- [x] Updated toast messages for better UX
- [x] History entries use `analysis_id`

---

**Status**: ✅ **COMPLETE**  
**Build**: ✅ **PASSING**  
**Ready for**: Testing with real backend
