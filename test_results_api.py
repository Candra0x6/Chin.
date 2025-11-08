"""
Test script for Results API - Phase 7
Tests retrieval, listing, search, export, and cleanup endpoints
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_VIDEO = "sample_video.mp4"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")


def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")


def test_get_analysis_result():
    """Test: Retrieve a specific analysis result"""
    print_section("Test 1: Get Analysis Result")
    
    try:
        # First, get the list of analyses to find a valid ID
        response = requests.get(f"{BASE_URL}/results", params={"limit": 1})
        
        if response.status_code != 200:
            print_result("Get Analysis Result", False, "No analyses found")
            return None
        
        data = response.json()
        if not data['results']:
            print_result("Get Analysis Result", False, "No analyses in database")
            return None
        
        analysis_id = data['results'][0]['analysis_id']
        
        # Get specific analysis
        response = requests.get(f"{BASE_URL}/results/{analysis_id}")
        
        if response.status_code == 200:
            result = response.json()
            print_result("Get Analysis Result", True, 
                        f"ID: {result['analysis_id']}, Video: {result['video_name']}")
            print(f"   Crowd Level: {result['results'].get('crowd_level')}")
            print(f"   Peak Count: {result['results'].get('peak_count')}")
            print(f"   Suggested Nurses: {result['results'].get('suggested_nurses')}")
            return analysis_id
        else:
            print_result("Get Analysis Result", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_result("Get Analysis Result", False, f"Error: {e}")
        return None


def test_list_analyses():
    """Test: List analyses with pagination"""
    print_section("Test 2: List Analyses with Pagination")
    
    try:
        # Test basic listing
        response = requests.get(f"{BASE_URL}/results", params={
            "page": 1,
            "limit": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print_result("List Analyses", True, 
                        f"Page {data['page']}/{data['total_pages']}, Total: {data['total']}")
            
            print(f"\n   First {len(data['results'])} results:")
            for i, result in enumerate(data['results'][:3], 1):
                print(f"   {i}. {result['video_name']} - {result['crowd_level']} "
                      f"(Peak: {result['peak_count']})")
            
            return True
        else:
            print_result("List Analyses", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("List Analyses", False, f"Error: {e}")
        return False


def test_filter_analyses():
    """Test: Filter analyses by crowd level"""
    print_section("Test 3: Filter Analyses")
    
    try:
        # Test filtering by crowd level
        response = requests.get(f"{BASE_URL}/results", params={
            "crowd_level": "Low",
            "limit": 10
        })
        
        if response.status_code == 200:
            data = response.json()
            print_result("Filter by Crowd Level", True, 
                        f"Found {data['total']} analyses with Low crowd level")
            
            # Test date filtering
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            response = requests.get(f"{BASE_URL}/results", params={
                "date_from": week_ago,
                "date_to": today,
                "limit": 10
            })
            
            if response.status_code == 200:
                data = response.json()
                print_result("Filter by Date Range", True, 
                            f"Found {data['total']} analyses in last 7 days")
                return True
            else:
                print_result("Filter by Date Range", False, f"Status: {response.status_code}")
                return False
        else:
            print_result("Filter by Crowd Level", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Filter Analyses", False, f"Error: {e}")
        return False


def test_search_analyses():
    """Test: Advanced search"""
    print_section("Test 4: Advanced Search")
    
    try:
        # Search by peak count range
        response = requests.get(f"{BASE_URL}/results/search/advanced", params={
            "min_peak_count": 1,
            "max_peak_count": 10,
            "limit": 10
        })
        
        if response.status_code == 200:
            data = response.json()
            print_result("Search by Peak Count", True, 
                        f"Found {data['total']} analyses with peak 1-10 people")
            
            # Search by crowd level
            response = requests.get(f"{BASE_URL}/results/search/advanced", params={
                "crowd_levels": "Low,Medium",
                "limit": 10
            })
            
            if response.status_code == 200:
                data = response.json()
                print_result("Search by Multiple Crowd Levels", True, 
                            f"Found {data['total']} analyses")
                
                if data['results']:
                    print(f"\n   Sample results:")
                    for result in data['results'][:2]:
                        print(f"   - {result['video_name']}: {result['crowd_level']} "
                              f"(Peak: {result['peak_count']})")
                
                return True
            else:
                print_result("Search by Multiple Crowd Levels", False, 
                            f"Status: {response.status_code}")
                return False
        else:
            print_result("Search by Peak Count", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Advanced Search", False, f"Error: {e}")
        return False


def test_export_json(analysis_id: int):
    """Test: Export analysis as JSON"""
    print_section("Test 5: Export to JSON")
    
    if not analysis_id:
        print_result("Export JSON", False, "No analysis ID provided")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/results/{analysis_id}/export/json")
        
        if response.status_code == 200:
            # Check if response is JSON
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                print_result("Export JSON", True, "JSON file generated")
                
                # Parse and show sample
                data = response.json()
                print(f"   Analysis ID: {data.get('analysis_id')}")
                print(f"   Video: {data.get('video_name')}")
                print(f"   Size: {len(json.dumps(data))} bytes")
                return True
            else:
                print_result("Export JSON", True, f"File downloaded ({len(response.content)} bytes)")
                return True
        else:
            print_result("Export JSON", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Export JSON", False, f"Error: {e}")
        return False


def test_export_summary(analysis_id: int):
    """Test: Export analysis summary as text"""
    print_section("Test 6: Export Summary")
    
    if not analysis_id:
        print_result("Export Summary", False, "No analysis ID provided")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/results/{analysis_id}/export/summary")
        
        if response.status_code == 200:
            content = response.text if hasattr(response, 'text') else response.content.decode()
            
            print_result("Export Summary", True, "Summary generated")
            print(f"   Length: {len(content)} characters")
            
            # Show first few lines
            lines = content.split('\n')[:10]
            print("\n   Preview:")
            for line in lines:
                if line.strip():
                    print(f"   {line[:70]}")
            
            return True
        else:
            print_result("Export Summary", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Export Summary", False, f"Error: {e}")
        return False


def test_statistics():
    """Test: Get overall statistics"""
    print_section("Test 7: Statistics Overview")
    
    try:
        response = requests.get(f"{BASE_URL}/results/stats/overview")
        
        if response.status_code == 200:
            stats = response.json()
            
            print_result("Get Statistics", True, "Statistics retrieved")
            print(f"\n   Overall Statistics:")
            print(f"   - Total Analyses: {stats['total_analyses']}")
            print(f"   - Average Peak Count: {stats['avg_peak_count']}")
            print(f"   - Total Bottlenecks: {stats['total_bottlenecks']}")
            print(f"   - Analyses with AI: {stats['analyses_with_ai_insights']}")
            
            if stats.get('analyses_by_crowd_level'):
                print(f"\n   Analyses by Crowd Level:")
                for level, count in stats['analyses_by_crowd_level'].items():
                    print(f"   - {level}: {count}")
            
            return True
        else:
            print_result("Get Statistics", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Get Statistics", False, f"Error: {e}")
        return False


def test_storage_info():
    """Test: Get storage information"""
    print_section("Test 8: Storage Information")
    
    try:
        response = requests.get(f"{BASE_URL}/results/admin/storage")
        
        if response.status_code == 200:
            storage = response.json()
            
            print_result("Get Storage Info", True, "Storage info retrieved")
            print(f"\n   Storage Statistics:")
            print(f"   - Uploads: {storage['uploads']['count']} files, "
                  f"{storage['uploads']['size_mb']} MB")
            print(f"   - Results: {storage['results']['count']} files, "
                  f"{storage['results']['size_mb']} MB")
            print(f"   - Total Size: {storage['total_size_mb']} MB")
            
            return True
        else:
            print_result("Get Storage Info", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Get Storage Info", False, f"Error: {e}")
        return False


def test_sorting():
    """Test: Sort analyses"""
    print_section("Test 9: Sorting")
    
    try:
        # Sort by date descending (newest first)
        response = requests.get(f"{BASE_URL}/results", params={
            "sort_by": "created_at",
            "sort_order": "desc",
            "limit": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print_result("Sort by Date (Newest)", True, 
                        f"Retrieved {len(data['results'])} results")
            
            if data['results']:
                print("\n   Newest analyses:")
                for result in data['results'][:3]:
                    print(f"   - {result['created_at']}: {result['video_name']}")
            
            # Sort by date ascending (oldest first)
            response = requests.get(f"{BASE_URL}/results", params={
                "sort_by": "created_at",
                "sort_order": "asc",
                "limit": 5
            })
            
            if response.status_code == 200:
                data = response.json()
                print_result("Sort by Date (Oldest)", True, 
                            f"Retrieved {len(data['results'])} results")
                
                if data['results']:
                    print("\n   Oldest analyses:")
                    for result in data['results'][:3]:
                        print(f"   - {result['created_at']}: {result['video_name']}")
                
                return True
            else:
                print_result("Sort by Date (Oldest)", False, 
                            f"Status: {response.status_code}")
                return False
        else:
            print_result("Sort by Date (Newest)", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Sorting", False, f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" PHASE 7: RESULTS & STORAGE API TEST SUITE")
    print("="*80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ Server is not responding. Please start the server:")
            print("   uvicorn app.main:app --reload")
            return
    except:
        print("\n❌ Cannot connect to server. Please start it first:")
        print("   uvicorn app.main:app --reload")
        return
    
    print("\n✅ Server is running\n")
    
    # Run tests
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Get analysis result
    analysis_id = test_get_analysis_result()
    results["total"] += 1
    if analysis_id:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 2: List analyses
    results["total"] += 1
    if test_list_analyses():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Filter analyses
    results["total"] += 1
    if test_filter_analyses():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: Search analyses
    results["total"] += 1
    if test_search_analyses():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Export JSON (only if we have an analysis ID)
    if analysis_id:
        results["total"] += 1
        if test_export_json(analysis_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test 6: Export summary (only if we have an analysis ID)
    if analysis_id:
        results["total"] += 1
        if test_export_summary(analysis_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test 7: Statistics
    results["total"] += 1
    if test_statistics():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 8: Storage info
    results["total"] += 1
    if test_storage_info():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 9: Sorting
    results["total"] += 1
    if test_sorting():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)
    print(f"\nTotal Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
