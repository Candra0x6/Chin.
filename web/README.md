# Chin  Frontend - Next.js Application

> Emergency Room Flow Analyzer - Web Interface

This is the frontend web application for Chin , built with Next.js, TypeScript, and Tailwind CSS. It provides a user-friendly interface for uploading ER queue videos, viewing AI-powered analysis results, and interacting with an AI assistant.

## 🚀 Features

- **Video Upload**: Upload and manage ER queue videos
- **Analysis Dashboard**: View crowd statistics, bottleneck detection, and staffing recommendations
- **AI Chat Assistant**: Interactive chat powered by Gemini AI
- **Data Visualization**: Charts and graphs for analysis insights
- **Export Capabilities**: Download results as JSON or text summaries

## 📋 Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running (see [backend README](../backend/README.md))

## 🛠️ Installation

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Configure Environment

Copy the example environment file and update with your backend API URL:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```bash
# Backend API URL (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Maximum file upload size in bytes (100MB)
NEXT_PUBLIC_MAX_FILE_SIZE=104857600

# Allowed video formats
NEXT_PUBLIC_ALLOWED_FORMATS=video/mp4,video/avi,video/mov,video/x-matroska
```

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Production Build

```bash
npm run build
npm start
```

## 📁 Project Structure

```
web/
├── app/                 # Next.js app directory
│   ├── page.tsx        # Main page
│   └── ...
├── components/          # React components (to be created)
├── lib/                 # Utility libraries
│   ├── api.ts          # API client for backend communication
│   ├── config.ts       # Configuration management
│   ├── types.ts        # TypeScript type definitions
│   └── validators.ts   # Input validation utilities
├── public/             # Static assets
├── .env.local          # Local environment variables (not in git)
├── .env.example        # Environment template
└── package.json        # Dependencies
```

## 🔌 API Integration

The frontend communicates with the FastAPI backend using a centralized API client (`lib/api.ts`).

### Available API Functions

**Video Upload:**
- `uploadVideo(file, onProgress)` - Upload video with progress tracking
- `getUploadStatus(videoId)` - Check upload status
- `deleteVideo(videoId)` - Delete uploaded video
- `listUploads(limit, offset, statusFilter)` - List all uploads

**Analysis Results:**
- `getAnalysisResult(analysisId)` - Get analysis details
- `listAnalysisResults(params)` - List analyses with filters
- `deleteAnalysis(analysisId)` - Delete analysis
- `getStatisticsOverview()` - Get overall statistics
- `exportAnalysisJson(analysisId)` - Export as JSON
- `exportAnalysisSummary(analysisId)` - Export as text

**AI Chat:**
- `startChat(analysisId)` - Start chat conversation
- `sendChatMessage(request)` - Send message
- `getChatHistory(analysisId)` - Get conversation history
- `clearChat(analysisId)` - Clear conversation

**Health Check:**
- `checkHealth()` - Check backend health
- `isApiReachable()` - Verify API connectivity

### Usage Example

```typescript
import { uploadVideo, getAnalysisResult } from '@/lib/api';
import { validateVideoFile } from '@/lib/validators';

// Upload a video
async function handleUpload(file: File) {
  const validation = validateVideoFile(file);
  if (!validation.isValid) {
    alert(validation.error);
    return;
  }

  try {
    const result = await uploadVideo(file, (progress) => {
      console.log('Upload progress:', progress);
    });
    console.log('Video uploaded:', result.id);
  } catch (error) {
    console.error('Upload failed:', error);
  }
}

// Get analysis results
async function fetchAnalysis(analysisId: string) {
  try {
    const analysis = await getAnalysisResult(analysisId);
    console.log('Crowd level:', analysis.results.crowd_level);
    console.log('Peak count:', analysis.results.peak_count);
  } catch (error) {
    console.error('Failed to fetch analysis:', error);
  }
}
```

## 🔒 Security

- Input validation for all file uploads
- File type and size restrictions
- XSS protection through input sanitization
- Type-safe API communication
- Environment-based configuration

## 🧪 Testing

```bash
npm run lint       # Run ESLint
npm run build      # Test production build
```

## 📦 Dependencies

### Core
- **Next.js** (v16.0.1) - React framework
- **React** (v19.2.0) - UI library
- **TypeScript** (v5) - Type safety

### UI & Styling
- **Tailwind CSS** (v4) - Utility-first CSS
- **Three.js** (v0.181.1) - 3D graphics
- **GSAP** (v3.13.0) - Animations

### Data & API
- **Axios** (v1.13.2) - HTTP client
- **Recharts** (v3.4.1) - Charts and graphs

## 🚢 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Add environment variables in project settings
4. Deploy!

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- AWS Amplify
- DigitalOcean App Platform
- Self-hosted with Docker

## 📖 Documentation

- [Frontend PRD](../docs/frontendPRD.md) - Product requirements
- [Phase 1 Integration](../docs/PHASE1_INTEGRATION_COMPLETE.md) - API integration details
- [Frontend Tasks](../docs/FRONTEND_TASKS.md) - Development roadmap
- [Backend API](../backend/README.md) - Backend documentation

## 🤝 Contributing

1. Follow TypeScript guidelines in [docs/Typescript.md](../docs/Typescript.md)
2. Ensure all components are properly typed
3. Test API integration before committing
4. Update documentation for new features

## 📝 License

Part of the Chin  project.

---

**Current Status:** Phase 1 Complete ✅ (API Integration)
**Next Phase:** Phase 2 - Core Components Development
