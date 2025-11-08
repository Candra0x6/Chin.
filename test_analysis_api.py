"""
Manual test script for video analysis API.

Tests the complete Phase 3 functionality:
- Video upload
- Analysis start
- Progress tracking
- Result retrieval
"""

import requests
import time
import cv2
import numpy as np
from pathlib import Path
import tempfile


BASE_URL = "http://localhost:8000"


def create_sample_video(duration_seconds: int = 5) -> Path:
    """
    Create a sample video file for testing.
    
    Args:
        duration_seconds: Video duration in seconds
        
    Returns:
        Path to created video file
    """
    print(f"📹 Creating sample video ({duration_seconds}s)...")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_path = Path(temp_file.name)
    temp_file.close()
    
    # Video properties
    fps = 30
    width, height = 640, 480
    total_frames = duration_seconds * fps
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(temp_path), fourcc, float(fps), (width, height))
    
    # Create frames with moving "people" (colored rectangles)
    for i in range(total_frames):
        # Create white background
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Add some "people" as colored rectangles
        num_people = 5 + int(5 * np.sin(i / 30))  # Vary between 0-10 people
        
        for j in range(num_people):
            x = (50 + j * 100) % (width - 100)
            y = (100 + i * 2) % (height - 150)
            
            # Draw rectangle as "person"
            color = (50 + j * 30, 100, 200)
            cv2.rectangle(frame, (x, y), (x + 80, y + 120), color, -1)
        
        out.write(frame)
    
    out.release()
    
    print(f"✅ Sample video created: {temp_path}")
    print(f"   Duration: {duration_seconds}s, Resolution: {width}x{height}, FPS: {fps}")
    
    return temp_path


def test_health_check():
    """Test API health check."""
    print("\n🏥 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Directories: {data['directories']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_upload_video(video_path: Path):
    """
    Test video upload.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Video ID if successful, None otherwise
    """
    print("\n📤 Testing video upload...")
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (video_path.name, f, 'video/mp4')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            video_id = data['id']
            print("✅ Video uploaded successfully")
            print(f"   Video ID: {video_id}")
            print(f"   Filename: {data['filename']}")
            print(f"   Status: {data['status']}")
            return video_id
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None


def test_start_analysis(video_id: str):
    """
    Test starting video analysis.
    
    Args:
        video_id: ID of uploaded video
        
    Returns:
        Analysis ID if successful, None otherwise
    """
    print("\n🔬 Testing analysis start...")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze/{video_id}")
        
        if response.status_code == 200:
            data = response.json()
            analysis_id = data['analysis_id']
            print("✅ Analysis started successfully")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   Video ID: {data['video_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            return analysis_id
        else:
            print(f"❌ Analysis start failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Analysis start error: {e}")
        return None


def test_check_analysis_status(analysis_id: str, max_wait: int = 300):
    """
    Test checking analysis status and wait for completion.
    
    Args:
        analysis_id: ID of the analysis
        max_wait: Maximum seconds to wait for completion
        
    Returns:
        True if completed successfully, False otherwise
    """
    print(f"\n⏱️ Checking analysis status (max wait: {max_wait}s)...")
    
    start_time = time.time()
    last_progress = -1
    
    try:
        while time.time() - start_time < max_wait:
            response = requests.get(f"{BASE_URL}/analyze/status/{analysis_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                progress = data.get('progress', 0)
                message = data.get('message', '')
                
                # Print progress if changed
                if progress != last_progress:
                    print(f"   Progress: {progress}% - {message}")
                    last_progress = progress
                
                if status == "completed":
                    print("✅ Analysis completed successfully!")
                    
                    # Print results summary
                    if 'result' in data and data['result']:
                        result = data['result']
                        print(f"\n📊 Analysis Results:")
                        print(f"   Total People: {result.get('total_people', 'N/A')}")
                        print(f"   Avg Density: {result.get('avg_density', 'N/A')}")
                        print(f"   Peak Time: {result.get('peak_congestion_time', 'N/A')}")
                        print(f"   Suggested Nurses: {result.get('suggested_nurses', 'N/A')}")
                        print(f"   Processing Time: {result.get('processing_time_seconds', 'N/A')}s")
                        
                        if 'ai_summary' in result:
                            print(f"\n💡 AI Summary:")
                            print(f"   {result['ai_summary']}")
                    
                    return True
                
                elif status == "failed":
                    print(f"❌ Analysis failed: {message}")
                    return False
                
                # Wait before next check
                time.sleep(2)
            
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        
        print(f"⏱️ Timeout: Analysis did not complete within {max_wait}s")
        return False
    
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False


def test_get_analysis_results(analysis_id: str):
    """
    Test getting full analysis results.
    
    Args:
        analysis_id: ID of the analysis
    """
    print(f"\n📥 Testing result retrieval...")
    
    try:
        response = requests.get(f"{BASE_URL}/analyze/results/{analysis_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Results retrieved successfully")
            
            # Print detailed results
            print(f"\n📈 Detailed Results:")
            print(f"   Status: {data.get('status')}")
            print(f"   Video ID: {data.get('video_id')}")
            
            # Full results
            full_results = data.get('full_results', {})
            if full_results:
                video_meta = full_results.get('video_metadata', {})
                print(f"\n   Video Metadata:")
                print(f"     Duration: {video_meta.get('duration_formatted')}")
                print(f"     FPS: {video_meta.get('fps')}")
                print(f"     Resolution: {video_meta.get('width')}x{video_meta.get('height')}")
                
                stats = full_results.get('statistics', {})
                print(f"\n   Statistics:")
                print(f"     Total Frames: {stats.get('total_frames')}")
                print(f"     Avg Person Count: {stats.get('average_person_count', 0):.2f}")
                print(f"     Max Person Count: {stats.get('max_person_count')}")
                print(f"     Min Person Count: {stats.get('min_person_count')}")
                
                insights = full_results.get('insights', {})
                print(f"\n   Insights:")
                print(f"     Crowd Level: {insights.get('crowd_level')}")
                print(f"     Bottleneck Detected: {insights.get('bottleneck_detected')}")
            
            return True
        else:
            print(f"❌ Result retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Result retrieval error: {e}")
        return False


def test_list_analyses():
    """Test listing all analyses."""
    print(f"\n📋 Testing analysis listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/analyze/list?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            analyses = data.get('analyses', [])
            print(f"✅ Retrieved {len(analyses)} analyses")
            
            for i, analysis in enumerate(analyses[:3]):  # Show first 3
                print(f"\n   Analysis {i+1}:")
                print(f"     ID: {analysis.get('id')}")
                print(f"     Status: {analysis.get('status')}")
                print(f"     Video ID: {analysis.get('video_id')}")
                print(f"     Created: {analysis.get('created_at')}")
            
            return True
        else:
            print(f"❌ List failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ List error: {e}")
        return False


def test_service_info():
    """Test getting service information."""
    print(f"\n🔧 Testing service info...")
    
    try:
        response = requests.get(f"{BASE_URL}/analyze/service/info")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Service info retrieved")
            
            processor = data.get('video_processor', {})
            print(f"\n   Video Processor:")
            print(f"     Frame Sample Rate: {processor.get('frame_sample_rate')}")
            print(f"     Max Frames: {processor.get('max_frames')}")
            
            detector = data.get('person_detector', {})
            print(f"\n   Person Detector:")
            print(f"     Model: {detector.get('model_name')}")
            print(f"     Device: {detector.get('device')}")
            print(f"     Confidence: {detector.get('confidence_threshold')}")
            print(f"     CUDA Available: {detector.get('cuda_available')}")
            
            return True
        else:
            print(f"❌ Service info failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Service info error: {e}")
        return False


def run_complete_test():
    """Run complete end-to-end test."""
    print("=" * 60)
    print("🚀 PHASE 3 - Video Analysis API Test")
    print("=" * 60)
    
    # Step 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Make sure the server is running.")
        return
    
    # Step 2: Service info
    test_service_info()
    
    # Step 3: Create sample video
    video_path = create_sample_video(duration_seconds=5)
    
    try:
        # Step 4: Upload video
        video_id = test_upload_video(video_path)
        if not video_id:
            return
        
        # Step 5: Start analysis
        analysis_id = test_start_analysis(video_id)
        if not analysis_id:
            return
        
        # Step 6: Monitor progress
        if not test_check_analysis_status(analysis_id, max_wait=300):
            return
        
        # Step 7: Get full results
        test_get_analysis_results(analysis_id)
        
        # Step 8: List analyses
        test_list_analyses()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    
    finally:
        # Cleanup
        if video_path.exists():
            video_path.unlink()
            print(f"\n🧹 Cleaned up test video: {video_path}")


if __name__ == "__main__":
    run_complete_test()
