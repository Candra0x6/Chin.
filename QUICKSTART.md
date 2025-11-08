# 🚀 Quick Start Guide - HospiTwin Lite Backend

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- [ ] Git (optional, for version control)

## Setup Steps

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   
   Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # Copy template
   cp .env.example .env
   
   # Edit .env and add your API key
   # GEMINI_API_KEY=your_actual_api_key_here
   ```

## Running the Application

1. **Make sure virtual environment is activated**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Start the server**
   ```bash
   python -m app.main
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the application**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Testing the API

### Using cURL

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Upload Video (once Phase 2 is complete):**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_video.mp4"
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Upload video
with open("video.mp4", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/upload", files=files)
    print(response.json())
```

### Using FastAPI Interactive Docs

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

## Project Structure Overview

```
Chin/
├── app/              # Main application code
│   ├── main.py       # FastAPI app entry point
│   ├── config.py     # Configuration settings
│   ├── models.py     # Data models
│   ├── services/     # Business logic
│   ├── routers/      # API endpoints
│   └── utils/        # Utility functions
├── venv/             # Virtual environment
├── uploads/          # Uploaded videos
├── results/          # Analysis results
├── models/           # YOLO models
└── tests/            # Unit tests
```

## Common Issues

### Import Error: No module named 'app'

**Solution:** Make sure you're running from the project root:
```bash
cd d:\Vs_Code_Project\Competition\NEXT\Chin
python -m app.main
```

### Port 8000 already in use

**Solution:** Use a different port:
```bash
uvicorn app.main:app --port 8001
```

### Gemini API Error

**Solution:** 
1. Check your API key in `.env`
2. Verify internet connection
3. Check API quota limits

## Next Steps

Follow the task list in `docs/task.md` to implement:
- Phase 2: Video Upload API
- Phase 3: Video Processing & People Detection
- Phase 4: Crowd Analytics
- Phase 5: AI Recommendation Engine
- Phase 6: AI Assistant Chat
- Phase 7: Results & Storage
- Phase 8: Testing & Optimization
- Phase 9: Documentation & Deployment

## Development Workflow

1. Check task list: `docs/task.md`
2. Implement feature
3. Test locally
4. Update task list (mark as complete)
5. Commit changes

## Useful Commands

```bash
# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload

# Check code style
flake8 app/

# Format code
black app/
```

## Support

- Backend PRD: `docs/backendPRD.md`
- Task List: `docs/task.md`
- API Documentation: http://localhost:8000/docs

---

✅ **Phase 1 Complete!** Ready to implement Phase 2: Video Upload API
