# HospiTwin Lite - Backend

**Video-based Emergency Room Flow Analyzer** using AI and Computer Vision to detect patient flow bottlenecks and recommend operational improvements.

## 🎯 Overview

HospiTwin Lite analyzes hospital emergency room queue videos to:
- Detect and count people using YOLOv8
- Calculate crowd density and congestion patterns
- Identify bottlenecks in patient flow
- Provide AI-powered recommendations using Google Gemini
- Enable interactive Q&A about analysis results

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Supabase account and project ([Sign up here](https://supabase.com))

### Installation

1. **Clone the repository**
   ```bash
   cd d:\Vs_Code_Project\Competition\NEXT\Chin
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Linux/Mac)
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env and add your credentials:
   # - GEMINI_API_KEY=your_gemini_api_key
   # - SUPABASE_URL=your_supabase_project_url
   # - SUPABASE_KEY=your_supabase_anon_key
   ```

5. **Set up Supabase database**
   
   Follow the guide in `docs/SUPABASE_SETUP.md` to:
   - Create Supabase project
   - Run SQL schema
   - Verify connection

6. **Run the application**
   ```bash
   python -m app.main
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
Chin/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration and settings
│   ├── models.py                # Pydantic data models
│   ├── database.py              # Database operations
│   ├── routers/                 # API route handlers
│   │   ├── upload.py            # Video upload endpoint
│   │   ├── results.py           # Results retrieval
│   │   └── chat.py              # AI assistant chat
│   ├── services/                # Business logic
│   │   ├── video_processor.py  # Video frame extraction
│   │   ├── person_detector.py  # YOLOv8 detection
│   │   ├── analytics.py         # Crowd metrics calculation
│   │   ├── gemini_assistant.py # AI integration
│   │   └── recommendations.py   # Staff recommendations
│   └── utils/                   # Utility functions
│       ├── file_handler.py      # File operations
│       └── validators.py        # Input validation
├── models/                      # YOLO model weights
├── uploads/                     # Temporary video storage
├── results/                     # Analysis results
├── tests/                       # Unit tests
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key  # Optional

# Directories
UPLOAD_DIR=uploads
RESULTS_DIR=results
MODEL_PATH=models

# Upload Settings
MAX_UPLOAD_SIZE=104857600  # 100MB
ALLOWED_VIDEO_FORMATS=mp4,avi,mov,mkv

# Processing Settings
MAX_FRAME_RATE=5              # Process 5 frames per second
DETECTION_CONFIDENCE=0.5      # YOLOv8 confidence threshold
```

**Note:** See `docs/SUPABASE_SETUP.md` for detailed database setup instructions.

## 📖 API Usage

### 1. Upload Video for Analysis

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ER_waitingroom.mp4"
```

Response:
```json
{
  "id": "abc123",
  "filename": "ER_waitingroom.mp4",
  "status": "processing",
  "message": "Video uploaded successfully. Processing started.",
  "created_at": "2025-11-07T10:30:00Z"
}
```

### 2. Get Analysis Results

```bash
curl -X GET "http://localhost:8000/results/abc123"
```

Response:
```json
{
  "id": "abc123",
  "video_name": "ER_waitingroom.mp4",
  "crowd_analytics": {
    "total_people": 27,
    "avg_density": "High",
    "max_congestion_time": "02:15 - 03:30",
    "peak_count": 32,
    "avg_count": 24.5
  },
  "bottleneck_info": {
    "area": "Triage Room",
    "severity": "High",
    "recommended_action": "Add 1 additional nurse to triage"
  },
  "staff_recommendation": {
    "suggested_nurses": 3,
    "reasoning": "Current crowd density requires additional staff"
  },
  "ai_summary": "The triage area is crowded between 2-3 PM..."
}
```

### 3. Chat with AI Assistant

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "abc123",
    "message": "What if we only have 2 nurses?"
  }'
```

## 🧪 Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_video_processor.py
```

## 🛠️ Development

### Setting Up Development Environment

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run with auto-reload:
   ```bash
   uvicorn app.main:app --reload
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Keep functions focused and modular

## 📊 Success Metrics

- Person detection accuracy: ≥ 85%
- Processing time per 1-min video: ≤ 15 seconds
- AI insight relevance: ≥ 80%
- System uptime: 100% for MVP

## 🔍 Troubleshooting

### YOLOv8 Model Download Issues
```bash
# Manually download model
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Gemini API Errors
- Verify API key is correct in `.env`
- Check API quota limits
- Ensure internet connectivity

### Supabase Connection Errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check if database schema is created
- Ensure internet connectivity
- Review `docs/SUPABASE_SETUP.md` for setup steps

### Video Processing Errors
- Verify video format is supported
- Check file size is within limits
- Ensure OpenCV is properly installed

## 📝 License

This project is developed for the hackathon/demo purposes.

## 🤝 Contributing

1. Follow the task list in `docs/task.md`
2. Update task list after completing features
3. Write tests for new functionality
4. Update documentation

## 📧 Support

For issues and questions, please refer to the PRD document in `docs/backendPRD.md`.

---

**Built with ❤️ using FastAPI, YOLOv8, and Google Gemini**
