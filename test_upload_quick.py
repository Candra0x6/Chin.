"""
Quick test to verify upload endpoint works correctly
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_VIDEO = Path("sample_video.mp4")

def test_upload():
    print("Testing upload endpoint...")
    
    if not TEST_VIDEO.exists():
        print(f"❌ Test video not found: {TEST_VIDEO}")
        print("\nPlease create a sample video file:")
        print("  ffmpeg -f lavfi -i testsrc=duration=10:size=320x240:rate=30 sample_video.mp4")
        return False
    
    # Test upload
    with open(TEST_VIDEO, 'rb') as f:
        files = {'file': (TEST_VIDEO.name, f, 'video/mp4')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Expected: 201")
    
    if response.status_code == 201:
        print("✅ Upload successful!")
        data = response.json()
        print(f"\nResponse:")
        print(json.dumps(data, indent=2, default=str))
        
        video_id = data.get('id')
        
        # Test getting upload status
        print(f"\nChecking upload status...")
        status_response = requests.get(f"{BASE_URL}/api/upload/status/{video_id}")
        print(f"Status Code: {status_response.status_code}")
        
        if status_response.status_code == 200:
            print("✅ Upload found in database!")
            print(json.dumps(status_response.json(), indent=2, default=str))
            return True
        else:
            print("❌ Upload not found in database")
            print(status_response.text)
            return False
    else:
        print("❌ Upload failed!")
        print(response.text)
        return False

if __name__ == "__main__":
    # Check server
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            print("✅ Server is running\n")
            test_upload()
        else:
            print("❌ Server health check failed")
    except Exception as e:
        print("❌ Server is not running!")
        print("Please start it: uvicorn app.main:app --reload")
