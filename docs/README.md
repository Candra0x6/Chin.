# Developer Documentation

## 📚 Overview

This directory contains comprehensive developer documentation for the Chin  project, including interactive API testing capabilities.

## 🌐 Web-Based Documentation

### Access the Documentation

Open `docs/index.html` in your web browser to access the interactive developer documentation portal.

**Features:**
- 📖 **Project Overview** - Complete project introduction and tech stack
- 🏗️ **System Architecture** - Detailed architecture diagrams and data flow
- 🔌 **API Reference** - Complete REST API documentation with examples
- 🧪 **Integration Tests** - Interactive test runner with real-time results
- 🚀 **Quick Start Guide** - Step-by-step setup instructions

### Opening the Documentation

#### Option 1: Direct File Access
```bash
# On Windows
start docs/index.html

# On macOS
open docs/index.html

# On Linux
xdg-open docs/index.html
```

#### Option 2: Using Python HTTP Server
```bash
# Navigate to project root
cd path/to/Chin-

# Start a local web server
python -m http.server 8080

# Open in browser
# http://localhost:8080/docs/index.html
```

#### Option 3: Using VS Code Live Server
1. Install "Live Server" extension in VS Code
2. Right-click on `docs/index.html`
3. Select "Open with Live Server"

## 🧪 Interactive Testing

The documentation includes an **Interactive Test Runner** that allows you to run integration tests directly from your browser.

### Prerequisites

1. **Backend server must be running:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Test video must exist:**
   - Ensure `sample_video.mp4` is in the project root
   - Or use your own test video

3. **Database must be accessible:**
   - PostgreSQL running and migrated
   - Proper credentials in `.env` file

### Running Tests from Web Interface

1. Open `docs/index.html` in your browser
2. Navigate to the "🧪 Integration Tests" tab
3. Click "▶️ Run All Tests" button
4. Watch real-time test execution and results

### Test Coverage

The integration test suite includes:

| Test # | Name | Description | Steps/Checks |
|--------|------|-------------|--------------|
| 1 | Complete Workflow | Full cycle from upload to export | 7 steps |
| 2 | Concurrent Operations | Multiple simultaneous API calls | 5 endpoints |
| 3 | Data Consistency | Same data across endpoints | 5 checks |
| 4 | Error Handling | Invalid requests and edge cases | 4 scenarios |
| 5 | Pagination | Page navigation and limits | 6 checks |
| 6 | Filtering & Sorting | Query parameters | 4 scenarios |

## 📡 Test API Endpoints

The backend provides REST endpoints for running tests programmatically:

### Run Integration Tests
```bash
POST /api/test/integration
```

**Response:**
```json
{
  "success": true,
  "output": "Test execution output...",
  "summary": {
    "total": 6,
    "passed": 5,
    "failed": 1,
    "tests": [...]
  },
  "return_code": 0
}
```

### Get Test Status
```bash
GET /api/test/status
```

**Response:**
```json
{
  "status": "available",
  "test_file_exists": true,
  "sample_video_exists": true,
  "test_file_path": "/path/to/test_integration.py",
  "sample_video_path": "/path/to/sample_video.mp4"
}
```

### Get Latest Test Results
```bash
GET /api/test/results
```

**Response:**
```json
{
  "timestamp": "1699459200",
  "results": {
    "total": 6,
    "passed": 5,
    "failed": 1,
    "tests": [...]
  }
}
```

### Clear Test Results
```bash
DELETE /api/test/results
```

## 🔧 Running Tests via Command Line

### Run All Integration Tests
```bash
python tests/test_integration.py
```

### Run Specific Test Categories

Edit `test_integration.py` and comment out tests you don't want to run:

```python
# Run only specific tests
suite.test_complete_workflow()
# suite.test_concurrent_operations()  # Commented out
# suite.test_data_consistency()       # Commented out
```

### View Saved Test Results
```bash
# Results are saved to results/ directory
cat results/integration_test_results_*.json
```

## 📊 Understanding Test Results

### Success Indicators
- ✅ `PASS` - Test completed successfully
- 🎉 All tests passed - 100% success rate
- Green status badges in web interface

### Failure Indicators
- ❌ `FAIL` - Test encountered an error
- ⚠️ Partial success - Some checks failed
- Red status badges in web interface

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Server not running | Backend server offline | Start server: `uvicorn app.main:app --reload` |
| Test video not found | Missing `sample_video.mp4` | Add video file to project root |
| Database connection error | PostgreSQL not accessible | Check DATABASE_URL in `.env` |
| Analysis timeout | Video too long/large | Use shorter test video (< 2 minutes) |
| Gemini API error | Invalid API key | Set GEMINI_API_KEY in `.env` |

## 📖 Additional Documentation Files

### Backend PRD
`docs/backendPRD.md` - Complete backend product requirements:
- Product overview and objectives
- Technical architecture
- Technology stack
- Core features and endpoints
- Success metrics

### Frontend PRD
`docs/frontendPRD.md` - Frontend specifications:
- User interface design
- Component structure
- Frontend-backend integration
- Technology stack (Next.js)
- Deployment guidelines

### Python Documentation
`docs/python.md` - Python-specific documentation:
- Code style guidelines
- Module structure
- Dependency management
- Development best practices

### Task Tracking
`docs/task.md` - Project task list and progress tracking

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run integration tests
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: |
        python tests/test_integration.py
```

## 🔐 Security Considerations

### For Development
- Documentation is served locally - no external access
- Test API endpoints are for development only
- Don't commit API keys or sensitive data

### For Production
- Remove or protect `/api/test/*` endpoints
- Implement authentication for documentation access
- Use environment-specific configurations
- Enable CORS restrictions

## 📞 Support

### Getting Help
1. Check the Quick Start guide in `docs/index.html`
2. Review API documentation at `http://localhost:8000/docs`
3. Check troubleshooting section in web docs
4. Review test output for specific error messages

### Contributing
When adding new features:
1. Update API documentation in `docs/index.html`
2. Add integration tests in `tests/test_integration.py`
3. Update this README if needed
4. Run full test suite before committing

## 📝 License

This documentation is part of the Chin  project.

---

**Last Updated:** November 8, 2025
**Version:** 1.0.0
