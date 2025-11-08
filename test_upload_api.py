"""
Manual test script for video upload API.
Creates a sample video file and uploads it to test the endpoint.
"""

import sys
import requests
from pathlib import Path


def create_sample_video(filename: str = "sample_test.mp4", size_kb: int = 100) -> Path:
    """
    Create a sample video file for testing.
    
    Args:
        filename: Name of file to create
        size_kb: Size of file in KB
        
    Returns:
        Path to created file
    """
    file_path = Path(filename)
    
    # Create a fake video file with random content
    content = b"FAKE VIDEO DATA " * (size_kb * 64)  # Approximate KB
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    print(f"✓ Created sample video: {filename} ({len(content) / 1024:.1f} KB)")
    return file_path


def test_upload_api(base_url: str = "http://localhost:8000"):
    """
    Test the video upload API.
    
    Args:
        base_url: Base URL of the API
    """
    print(f"\n{'='*60}")
    print("  🎬 Testing Video Upload API")
    print(f"{'='*60}\n")
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        print(f"   Make sure the server is running: python -m app.main")
        return
    
    # Test 2: Create sample video
    print("\n2. Creating sample video file...")
    video_path = create_sample_video("test_upload.mp4", size_kb=100)
    
    # Test 3: Upload video
    print("\n3. Uploading video...")
    try:
        with open(video_path, 'rb') as f:
            files = {
                'file': ('test_video.mp4', f, 'video/mp4')
            }
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Upload successful!")
            print(f"   Video ID: {data['id']}")
            print(f"   Filename: {data['filename']}")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            
            video_id = data['id']
            
            # Test 4: Check upload status
            print("\n4. Checking upload status...")
            response = requests.get(f"{base_url}/upload/status/{video_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✅ Status retrieved successfully")
                print(f"   Status: {status_data['status']}")
                print(f"   File size: {status_data['file_size']} bytes")
            else:
                print(f"   ⚠️  Status check failed: {response.status_code}")
            
            # Test 5: List uploads
            print("\n5. Listing recent uploads...")
            response = requests.get(f"{base_url}/upload/list?limit=5")
            if response.status_code == 200:
                list_data = response.json()
                print(f"   ✅ Found {list_data['count']} videos")
                for video in list_data['videos'][:3]:
                    print(f"      - {video['filename']} ({video['status']})")
            else:
                print(f"   ⚠️  List failed: {response.status_code}")
            
            # Test 6: Delete upload (optional - uncomment to test)
            # print("\n6. Deleting uploaded video...")
            # response = requests.delete(f"{base_url}/upload/{video_id}")
            # if response.status_code == 200:
            #     print(f"   ✅ Video deleted successfully")
            # else:
            #     print(f"   ⚠️  Delete failed: {response.status_code}")
            
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
    
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
    
    finally:
        # Cleanup test file
        if video_path.exists():
            video_path.unlink()
            print(f"\n✓ Cleaned up test file")
    
    print(f"\n{'='*60}")
    print("  Test Complete!")
    print(f"{'='*60}\n")


def test_invalid_uploads(base_url: str = "http://localhost:8000"):
    """Test invalid upload scenarios."""
    print(f"\n{'='*60}")
    print("  🧪 Testing Invalid Upload Scenarios")
    print(f"{'='*60}\n")
    
    # Test 1: Invalid file format
    print("1. Testing invalid file format (.txt)...")
    txt_file = Path("test.txt")
    txt_file.write_text("This is not a video")
    
    try:
        with open(txt_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 400:
            print(f"   ✅ Correctly rejected: {response.json()['detail']}")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    finally:
        txt_file.unlink()
    
    # Test 2: Empty file
    print("\n2. Testing empty file...")
    empty_file = Path("empty.mp4")
    empty_file.write_bytes(b"")
    
    try:
        with open(empty_file, 'rb') as f:
            files = {'file': ('empty.mp4', f, 'video/mp4')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 400:
            print(f"   ✅ Correctly rejected: {response.json()['detail']}")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    finally:
        empty_file.unlink()
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("\n🏥 HospiTwin Lite - Upload API Test")
    print(f"Testing API at: {base_url}\n")
    
    # Run tests
    test_upload_api(base_url)
    test_invalid_uploads(base_url)
    
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("- Check uploaded files in: uploads/")
    print("- View API docs: http://localhost:8000/docs")
    print("- Check Supabase dashboard for metadata")
