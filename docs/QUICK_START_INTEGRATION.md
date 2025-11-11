# 🚀 Quick Start Guide - Frontend Integration

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] Backend API running at `http://localhost:8000`
- [ ] Git repository cloned
- [ ] Terminal/Command Prompt open

## 5-Minute Setup

### Step 1: Navigate to Web Directory
```bash
cd web
```

### Step 2: Install Dependencies
```bash
npm install
```
*Expected: 418 packages installed, 0 vulnerabilities*

### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local if backend URL is different
# Default: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Verify Backend is Running
```bash
# In a new terminal, test backend
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "directories": {...}
}
```

### Step 5: Start Development Server
```bash
npm run dev
```

**✅ Success!** Frontend running at [http://localhost:3000](http://localhost:3000)

---

## Test the Integration

### Test 1: API Connection
Create `test-connection.js` in web root:

```javascript
// test-connection.js
const axios = require('axios');

async function testAPI() {
  try {
    const response = await axios.get('http://localhost:8000/health');
    console.log('✅ Backend is healthy:', response.data);
  } catch (error) {
    console.error('❌ Backend not reachable:', error.message);
  }
}

testAPI();
```

Run:
```bash
node test-connection.js
```

### Test 2: API Client
Create a test page in Next.js:

```typescript
// app/test/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { checkHealth, isApiReachable } from '@/lib/api';

export default function TestPage() {
  const [status, setStatus] = useState('Testing...');

  useEffect(() => {
    async function test() {
      const reachable = await isApiReachable();
      if (reachable) {
        const health = await checkHealth();
        setStatus(`✅ Backend healthy: ${health.status}`);
      } else {
        setStatus('❌ Backend not reachable');
      }
    }
    test();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">API Connection Test</h1>
      <p className="mt-4">{status}</p>
    </div>
  );
}
```

Visit: [http://localhost:3000/test](http://localhost:3000/test)

---

## Common Issues & Solutions

### Issue 1: "Cannot connect to server"
**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start backend:
cd ../backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

### Issue 2: "CORS Error"
**Solution:** Backend already has CORS configured for all origins. If still getting errors:
```python
# backend/app/main.py - verify this exists:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: "Module not found" errors
**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue 4: TypeScript errors
**Solution:**
```bash
# Check all files
npm run build

# Fix common issues
# - Ensure all imports use @/lib/* paths
# - Check type definitions are imported
```

---

## Usage Examples

### Example 1: Upload Video
```typescript
import { uploadVideo } from '@/lib/api';
import { validateVideoFile } from '@/lib/validators';

async function handleUpload(file: File) {
  // Validate
  const validation = validateVideoFile(file);
  if (!validation.isValid) {
    alert(validation.error);
    return;
  }

  // Upload
  try {
    const result = await uploadVideo(file, (progress) => {
      const percent = (progress.loaded / (progress.total || 1)) * 100;
      console.log(`Upload: ${percent.toFixed(0)}%`);
    });

    console.log('✅ Uploaded:', result.id);
    return result.id;
  } catch (error) {
    console.error('❌ Upload failed:', error);
  }
}
```

### Example 2: Get Analysis
```typescript
import { getAnalysisResult } from '@/lib/api';

async function displayAnalysis(analysisId: string) {
  try {
    const analysis = await getAnalysisResult(analysisId);
    
    console.log('Results:');
    console.log('- Crowd Level:', analysis.results.crowd_level);
    console.log('- Peak Count:', analysis.results.peak_count);
    console.log('- Avg Count:', analysis.results.avg_count);
    console.log('- Suggested Nurses:', analysis.results.suggested_nurses);
    
    return analysis;
  } catch (error) {
    console.error('❌ Failed:', error);
  }
}
```

### Example 3: Chat with AI
```typescript
import { startChat, sendChatMessage } from '@/lib/api';

async function chat(analysisId: string, question: string) {
  try {
    // Start session
    const session = await startChat(analysisId);
    console.log('Welcome:', session.message);
    
    // Ask question
    const response = await sendChatMessage({
      analysis_id: analysisId,
      message: question,
      conversation_history: []
    });
    
    console.log('AI:', response.response);
    return response;
  } catch (error) {
    console.error('❌ Chat failed:', error);
  }
}

// Usage
chat('analysis-uuid-here', 'Why 3 nurses?');
```

---

## Project Structure

```
web/
├── app/                    # Next.js pages
├── components/             # React components (to be created)
├── lib/                    # Utilities
│   ├── api.ts             # ✅ API client
│   ├── config.ts          # ✅ Configuration
│   ├── types.ts           # ✅ Type definitions
│   └── validators.ts      # ✅ Validation
├── public/                # Static assets
├── .env.local             # ✅ Your config
├── .env.example           # ✅ Template
└── package.json           # ✅ Dependencies
```

---

## Development Workflow

### 1. Start Both Servers
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd web
npm run dev
```

### 2. Make Changes
- Edit files in `web/`
- Hot reload applies changes automatically
- Check browser console for errors

### 3. Test Changes
- Use browser DevTools Network tab
- Check API requests/responses
- Verify data in backend database

### 4. Build for Production
```bash
npm run build
npm start
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_MAX_FILE_SIZE` | `104857600` | Max upload size (100MB) |
| `NEXT_PUBLIC_ALLOWED_FORMATS` | `video/mp4,video/avi,...` | Allowed formats |
| `NEXT_PUBLIC_APP_NAME` | `Chin` | Application name |
| `NEXT_PUBLIC_APP_VERSION` | `1.0.0` | App version |
| `NEXT_PUBLIC_DEBUG` | `false` | Enable debug logs |

---

## API Endpoints Quick Reference

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `uploadVideo()` | `POST /api/upload` | Upload video |
| `getAnalysisResult()` | `GET /api/results/{id}` | Get analysis |
| `startChat()` | `POST /api/chat/start/{id}` | Start chat |
| `sendChatMessage()` | `POST /api/chat/message` | Send message |
| `checkHealth()` | `GET /health` | Health check |

Full list: See `lib/api.ts`

---

## Next Steps

1. **Create Components** (Phase 2)
   - UploadBox component
   - ResultPanel component
   - ChatAssistant component

2. **Build Pages** (Phase 4)
   - Main upload/dashboard page
   - Chat interface page

3. **Add Visualizations** (Phase 5)
   - Integration with Recharts
   - Create chart components

---

## Need Help?

- **Documentation:** See `docs/PHASE1_INTEGRATION_COMPLETE.md`
- **Backend API:** See `backend/README.md`
- **Type Definitions:** See `lib/types.ts`
- **Examples:** See `docs/PHASE1_SUMMARY.md`

---

**Status:** ✅ Phase 1 Complete - Ready for Component Development
**Support:** Check documentation or backend API docs at `http://localhost:8000/docs`
