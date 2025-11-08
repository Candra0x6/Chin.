"""
Simple test to debug analysis workflow
"""
import sys
import io
# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
VIDEO_PATH = Path("sample_video.mp4")

print("="*60)
print("Simple Analysis Test")
print("="*60)

# Step 1: Upload
print("\n1. Uploading video...")
with open(VIDEO_PATH, 'rb') as f:
    files = {'file': ('sample_video.mp4', f, 'video/mp4')}
    upload_response = requests.post(f"{API_URL}/upload", files=files)

print(f"Upload Status: {upload_response.status_code}")
upload_data = upload_response.json()
print(f"Upload Response: {json.dumps(upload_data, indent=2)}")

video_id = upload_data['id']
print(f"\n✓ Video uploaded: {video_id}")

# Step 2: Start analysis
print("\n2. Starting analysis...")
analyze_response = requests.post(
    f"{API_URL}/analyze/{video_id}",
    json={
        "upload_id": video_id,
        "show_visual": False,
        "save_annotated_video": False,
        "frame_sample_rate": 30,
        "confidence_threshold": 0.5,
        "enable_ai_insights": False  # Disable AI to speed up
    }
)

print(f"Analysis Status: {analyze_response.status_code}")
analysis_data = analyze_response.json()
print(f"Analysis Response: {json.dumps(analysis_data, indent=2)}")

analysis_id = analysis_data['analysis_id']
print(f"\n✓ Analysis started: {analysis_id}")

# Step 3: Poll status
print("\n3. Waiting for completion...")
for i in range(24):  # 2 minutes max (5s intervals)
    time.sleep(5)
    status_response = requests.get(f"{API_URL}/analyze/status/{analysis_id}")
    status_data = status_response.json()
    
    print(f"   [{i*5}s] Status: {status_data['status']}, Progress: {status_data['progress']}%")
    
    if status_data['status'] == 'completed':
        print("\n✓ Analysis completed!")
        print(f"\nResult data keys: {list(status_data.get('result', {}).keys())}")
        result = status_data.get('result')
        if result:
            print(f"\nResult preview:")
            print(f"  - crowd_level: {result.get('crowd_level')}")
            print(f"  - peak_count: {result.get('peak_count')}")
            print(f"  - avg_count: {result.get('avg_count')}")
            print(f"  - suggested_nurses: {result.get('suggested_nurses')}")
            print(f"  - ai_summary: {result.get('ai_summary', 'N/A')[:100]}...")
            
            # Check if results JSONB field exists
            if 'results' in result:
                print(f"\n  - results field exists (JSONB)")
                print(f"  - results keys: {list(result['results'].keys())[:10]}")
        break
    elif status_data['status'] == 'failed':
        print(f"\n✗ Analysis failed: {status_data.get('message')}")
        
        # Get error details
        error_response = requests.get(f"{API_URL}/analyze/error/{analysis_id}")
        if error_response.status_code == 200:
            error_data = error_response.json()
            print(f"\nError details:")
            print(f"  Message: {error_data.get('error_message')}")
            print(f"  Details: {error_data.get('error_details')}")
        break

print("\n" + "="*60)
