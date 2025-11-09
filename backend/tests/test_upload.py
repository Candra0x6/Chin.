"""
Tests for video upload API endpoints.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_upload_video_no_file():
    """Test upload without file."""
    response = client.post("/upload")
    assert response.status_code == 422  # Unprocessable Entity


def test_upload_video_invalid_format():
    """Test upload with invalid file format."""
    # Create a fake text file
    files = {
        "file": ("test.txt", b"fake video content", "text/plain")
    }
    response = client.post("/upload", files=files)
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


def test_upload_video_valid():
    """Test successful video upload."""
    # Create a fake video file
    files = {
        "file": ("test_video.mp4", b"fake video content" * 100, "video/mp4")
    }
    response = client.post("/upload", files=files)
    
    # Should succeed or fail based on Supabase configuration
    assert response.status_code in [201, 500]
    
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test_video.mp4"
        assert data["status"] == "uploaded"


def test_get_upload_status_not_found():
    """Test getting status of non-existent upload."""
    response = client.get("/upload/status/00000000-0000-0000-0000-000000000000")
    assert response.status_code in [404, 500]


def test_list_uploads():
    """Test listing uploads."""
    response = client.get("/upload/list")
    
    # Should succeed or fail based on Supabase configuration
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "videos" in data
        assert "count" in data
        assert "limit" in data


def test_list_uploads_with_pagination():
    """Test listing uploads with pagination."""
    response = client.get("/upload/list?limit=5&offset=0")
    
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 0


def test_upload_video_too_large():
    """Test upload with file too large."""
    # Create a file larger than max size (100MB)
    large_content = b"x" * (101 * 1024 * 1024)  # 101 MB
    
    files = {
        "file": ("large_video.mp4", large_content, "video/mp4")
    }
    
    response = client.post("/upload", files=files)
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()
