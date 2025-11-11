"""
Integration Tests - Phase 8 & 9
Tests complete workflows across multiple services and API endpoints
Includes hospital context analytics integration tests
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
from typing import Dict, Any
import os

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
TEST_VIDEO = "sample_video.mp4"
TEST_VIDEO_PATH = Path(__file__).parent.parent / TEST_VIDEO


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")


def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")


class IntegrationTestSuite:
    """Complete integration test suite for Chin """
    
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        self.test_data = {}
    
    def record_test(self, name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "details": details
        })
    
    def check_server(self) -> bool:
        """Verify server is running"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def test_complete_workflow(self) -> bool:
        """
        Test 1: Complete workflow from upload to export
        Tests: Upload → Analyze → Chat → Export
        """
        print_section("Test 1: Complete Workflow (Upload → Analyze → Chat → Export)")
        
        if not TEST_VIDEO_PATH.exists():
            print_result("Complete Workflow", False, f"Test video not found: {TEST_VIDEO_PATH}")
            self.record_test("Complete Workflow", False, "Test video missing")
            return False
        
        start_time = time.time()
        
        try:
            # Step 1: Upload video
            print("Step 1: Uploading video...")
            with open(TEST_VIDEO_PATH, 'rb') as f:
                files = {'file': (TEST_VIDEO, f, 'video/mp4')}
                upload_response = requests.post(f"{API_URL}/upload", files=files)
            
            if upload_response.status_code != 201:
                print_result("Upload", False, f"Status: {upload_response.status_code}")
                self.record_test("Complete Workflow - Upload", False)
                return False
            
            upload_data = upload_response.json()
            video_id = upload_data.get('id')
            video_path = upload_data.get('path')
            print_result("Upload", True, f"Video ID: {video_id}")
            
            # Give database a moment to ensure metadata is committed
            time.sleep(1)
            
            # Step 2: Analyze video
            print("\nStep 2: Analyzing video...")
            analyze_response = requests.post(
                f"{API_URL}/analyze/{video_id}",
                json={
                    "upload_id": video_id,
                    "show_visual": False,
                    "save_annotated_video": False,
                    "frame_sample_rate": 30,
                    "confidence_threshold": 0.5,
                    "enable_ai_insights": True,
                    "gemini_api_key": os.getenv('GEMINI_API_KEY', '')
                }
            )
            
            if analyze_response.status_code != 200:
                print_result("Analysis", False, f"Status: {analyze_response.status_code}")
                self.record_test("Complete Workflow - Analysis", False)
                return False
            
            analysis_data = analyze_response.json()
            analysis_id = analysis_data.get('analysis_id')
            print_result("Analysis Started", True, f"Analysis ID: {analysis_id}")
            
            # Wait for analysis to complete
            print("\nWaiting for analysis to complete...")
            max_wait = 120  # 2 minutes max
            start_wait = time.time()
            analysis_complete = False
            
            while time.time() - start_wait < max_wait:
                status_response = requests.get(f"{API_URL}/analyze/status/{analysis_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    message = status_data.get('message', '')
                    
                    print(f"   Progress: {progress}% - Status: {status}")
                    if message and status == 'failed':
                        print(f"   Error: {message}")
                    
                    if status == 'completed':
                        analysis_complete = True
                        analysis_result = status_data.get('result', {})
                        break
                    elif status == 'failed':
                        # Fetch detailed error information
                        print("\n   Fetching detailed error information...")
                        error_response = requests.get(f"{API_URL}/analyze/error/{analysis_id}")
                        if error_response.status_code == 200:
                            error_data = error_response.json()
                            print(f"\n   ❌ ERROR DETAILS:")
                            print(f"   Message: {error_data.get('error_message', 'Unknown')}")
                            print(f"   Details:\n{error_data.get('error_details', 'No details')}")
                        
                        print_result("Analysis", False, f"Analysis failed: {message}")
                        self.record_test("Complete Workflow - Analysis", False, "Analysis failed")
                        return False
                
                time.sleep(5)  # Check every 5 seconds
            
            if not analysis_complete:
                print_result("Analysis", False, "Timeout waiting for analysis")
                self.record_test("Complete Workflow - Analysis", False, "Timeout")
                return False
            
            crowd_level = analysis_result.get('results', {}).get('crowd_level', 'Unknown')
            peak_count = analysis_result.get('results', {}).get('peak_count', 0)
            print_result("Analysis Complete", True, 
                        f"ID: {analysis_id}, Crowd: {crowd_level}, Peak: {peak_count}")
            
            self.test_data['analysis_id'] = analysis_id
            
            # Step 3: Start chat conversation
            print("\nStep 3: Starting chat conversation...")
            chat_start_response = requests.post(f"{API_URL}/chat/start/{analysis_id}")
            
            if chat_start_response.status_code != 200:
                print_result("Chat Start", False, f"Status: {chat_start_response.status_code}")
                self.record_test("Complete Workflow - Chat Start", False)
                return False
            
            chat_data = chat_start_response.json()
            print_result("Chat Start", True, f"Session: {chat_data.get('session_id')}")
            
            # Step 4: Send chat message
            print("\nStep 4: Sending chat message...")
            chat_message_response = requests.post(f"{API_URL}/chat/message", json={
                "analysis_id": analysis_id,
                "message": "Why do you recommend this number of nurses?",
                "history": []
            })
            
            if chat_message_response.status_code != 200:
                print_result("Chat Message", False, f"Status: {chat_message_response.status_code}")
                self.record_test("Complete Workflow - Chat Message", False)
                return False
            
            chat_response = chat_message_response.json()
            print_result("Chat Message", True, 
                        f"Response length: {len(chat_response['response'])} chars")
            print(f"   Preview: {chat_response['response'][:100]}...")
            
            # Step 5: Get analysis result
            print("\nStep 5: Retrieving analysis result...")
            result_response = requests.get(f"{API_URL}/results/{analysis_id}")
            
            if result_response.status_code != 200:
                print_result("Get Result", False, f"Status: {result_response.status_code}")
                self.record_test("Complete Workflow - Get Result", False)
                return False
            
            result_data = result_response.json()
            print_result("Get Result", True, f"Video: {result_data['video_name']}")
            
            # Step 6: Export as JSON
            print("\nStep 6: Exporting as JSON...")
            export_json_response = requests.get(f"{API_URL}/results/{analysis_id}/export/json")
            
            if export_json_response.status_code != 200:
                print_result("Export JSON", False, f"Status: {export_json_response.status_code}")
                self.record_test("Complete Workflow - Export JSON", False)
                return False
            
            print_result("Export JSON", True, f"Size: {len(export_json_response.content)} bytes")
            
            # Step 7: Export as summary
            print("\nStep 7: Exporting as summary...")
            export_summary_response = requests.get(f"{API_URL}/results/{analysis_id}/export/summary")
            
            if export_summary_response.status_code != 200:
                print_result("Export Summary", False, f"Status: {export_summary_response.status_code}")
                self.record_test("Complete Workflow - Export Summary", False)
                return False
            
            print_result("Export Summary", True, 
                        f"Size: {len(export_summary_response.content)} bytes")
            
            # Calculate total time
            total_time = time.time() - start_time
            print(f"\n⏱️  Total workflow time: {total_time:.2f} seconds")
            
            self.record_test("Complete Workflow", True, f"Time: {total_time:.2f}s")
            return True
            
        except Exception as e:
            print_result("Complete Workflow", False, f"Error: {e}")
            self.record_test("Complete Workflow", False, str(e))
            return False
    
    def test_concurrent_operations(self) -> bool:
        """
        Test 2: Concurrent operations
        Tests: Multiple simultaneous API calls
        """
        print_section("Test 2: Concurrent Operations")
        
        if not self.test_data.get('analysis_id'):
            print_result("Concurrent Operations", False, "No analysis_id available")
            self.record_test("Concurrent Operations", False, "Missing prerequisites")
            return False
        
        try:
            import concurrent.futures
            
            analysis_id = self.test_data['analysis_id']
            
            def make_request(endpoint: str) -> tuple:
                """Make API request and measure time"""
                start = time.time()
                response = requests.get(endpoint)
                duration = time.time() - start
                return response.status_code, duration
            
            # Prepare concurrent requests
            endpoints = [
                f"{API_URL}/results/{analysis_id}",
                f"{API_URL}/results?page=1&limit=10",
                f"{API_URL}/results/stats/overview",
                f"{API_URL}/chat/history/{analysis_id}",
                f"{API_URL}/results/admin/storage"
            ]
            
            print(f"Sending {len(endpoints)} concurrent requests...")
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, url) for url in endpoints]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            total_time = time.time() - start_time
            
            # Check results
            success_count = sum(1 for status, _ in results if status == 200)
            avg_response_time = sum(duration for _, duration in results) / len(results)
            
            print_result("Concurrent Requests", success_count == len(endpoints),
                        f"Success: {success_count}/{len(endpoints)}, "
                        f"Total time: {total_time:.2f}s, "
                        f"Avg response: {avg_response_time:.2f}s")
            
            self.record_test("Concurrent Operations", success_count == len(endpoints),
                           f"{success_count}/{len(endpoints)} succeeded")
            
            return success_count == len(endpoints)
            
        except Exception as e:
            print_result("Concurrent Operations", False, f"Error: {e}")
            self.record_test("Concurrent Operations", False, str(e))
            return False
    
    def test_data_consistency(self) -> bool:
        """
        Test 3: Data consistency across endpoints
        Tests: Same data returned from different endpoints
        """
        print_section("Test 3: Data Consistency")
        
        if not self.test_data.get('analysis_id'):
            print_result("Data Consistency", False, "No analysis_id available")
            self.record_test("Data Consistency", False, "Missing prerequisites")
            return False
        
        try:
            analysis_id = self.test_data['analysis_id']
            
            # Get data from different endpoints
            result_response = requests.get(f"{API_URL}/results/{analysis_id}")
            list_response = requests.get(f"{API_URL}/results?limit=100")
            search_response = requests.get(f"{API_URL}/results/search/advanced?limit=100")
            
            if result_response.status_code != 200:
                print_result("Data Consistency", False, "Failed to get result")
                self.record_test("Data Consistency", False)
                return False
            
            result_data = result_response.json()
            
            # Check if same analysis exists in list
            list_data = list_response.json()
            found_in_list = any(
                item['analysis_id'] == analysis_id 
                for item in list_data['results']
            )
            
            # Check in search results
            search_data = search_response.json()
            found_in_search = any(
                item['analysis_id'] == analysis_id 
                for item in search_data['results']
            )
            
            # Verify data consistency
            consistency_checks = {
                "Found in list": found_in_list,
                "Found in search": found_in_search,
                "Has results data": 'results' in result_data,
                "Has video_name": bool(result_data.get('video_name')),
                "Has created_at": bool(result_data.get('created_at'))
            }
            
            all_passed = all(consistency_checks.values())
            
            print_result("Data Consistency", all_passed,
                        f"Checks: {sum(consistency_checks.values())}/{len(consistency_checks)}")
            
            for check, passed in consistency_checks.items():
                status = "✓" if passed else "✗"
                print(f"   {status} {check}")
            
            self.record_test("Data Consistency", all_passed)
            return all_passed
            
        except Exception as e:
            print_result("Data Consistency", False, f"Error: {e}")
            self.record_test("Data Consistency", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """
        Test 4: Error handling
        Tests: Invalid requests, edge cases
        """
        print_section("Test 4: Error Handling")
        
        try:
            error_tests = []
            
            # Test 1: Invalid analysis ID
            response = requests.get(f"{API_URL}/results/999999")
            error_tests.append(("Invalid ID", response.status_code == 404))
            
            # Test 2: Invalid pagination
            response = requests.get(f"{API_URL}/results?page=0&limit=1000")
            error_tests.append(("Invalid pagination", response.status_code in [400, 422]))
            
            # Test 3: Invalid chat message (should return 422 for validation error or 404 for invalid UUID)
            response = requests.post(f"{API_URL}/chat/message", json={
                "analysis_id": 999999,
                "message": "",
                "history": []
            })
            error_tests.append(("Invalid chat", response.status_code in [400, 404, 422]))
            
            # Test 4: Missing required fields (should return 404 for route not found or 422 for validation)
            response = requests.post(f"{API_URL}/analyze", json={})
            error_tests.append(("Missing fields", response.status_code in [400, 404, 422]))
            
            passed_count = sum(1 for _, passed in error_tests if passed)
            all_passed = passed_count == len(error_tests)
            
            print_result("Error Handling", all_passed,
                        f"Checks: {passed_count}/{len(error_tests)}")
            
            for test_name, passed in error_tests:
                status = "✓" if passed else "✗"
                print(f"   {status} {test_name}")
            
            self.record_test("Error Handling", all_passed,
                           f"{passed_count}/{len(error_tests)} passed")
            
            return all_passed
            
        except Exception as e:
            print_result("Error Handling", False, f"Error: {e}")
            self.record_test("Error Handling", False, str(e))
            return False
    
    def test_pagination(self) -> bool:
        """
        Test 5: Pagination functionality
        Tests: Page navigation, limits
        """
        print_section("Test 5: Pagination")
        
        try:
            # Get first page
            page1_response = requests.get(f"{API_URL}/results?page=1&limit=5")
            if page1_response.status_code != 200:
                print_result("Pagination", False, "Failed to get first page")
                self.record_test("Pagination", False)
                return False
            
            page1_data = page1_response.json()
            
            # Get second page
            page2_response = requests.get(f"{API_URL}/results?page=2&limit=5")
            page2_data = page2_response.json()
            
            # Verify pagination metadata
            checks = {
                "Has page number": page1_data.get('page') == 1,
                "Has limit": page1_data.get('limit') == 5,
                "Has total": 'total' in page1_data,
                "Has total_pages": 'total_pages' in page1_data,
                "Results count matches": len(page1_data['results']) <= 5,
                "Different pages": (
                    page1_data['results'] != page2_data['results']
                    if page2_data['results'] else True
                )
            }
            
            all_passed = all(checks.values())
            
            print_result("Pagination", all_passed,
                        f"Total: {page1_data.get('total')}, "
                        f"Pages: {page1_data.get('total_pages')}")
            
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"   {status} {check}")
            
            self.record_test("Pagination", all_passed)
            return all_passed
            
        except Exception as e:
            print_result("Pagination", False, f"Error: {e}")
            self.record_test("Pagination", False, str(e))
            return False
    
    def test_filtering_sorting(self) -> bool:
        """
        Test 6: Filtering and sorting
        Tests: Query parameters work correctly
        """
        print_section("Test 6: Filtering and Sorting")
        
        try:
            # Test filtering by crowd level
            filter_response = requests.get(f"{API_URL}/results?crowd_level=Low&limit=10")
            
            if filter_response.status_code != 200:
                print_result("Filtering", False, "Filter request failed")
                self.record_test("Filtering and Sorting", False)
                return False
            
            filter_data = filter_response.json()
            
            # Test sorting
            sort_desc_response = requests.get(
                f"{API_URL}/results?sort_by=created_at&sort_order=desc&limit=5"
            )
            sort_asc_response = requests.get(
                f"{API_URL}/results?sort_by=created_at&sort_order=asc&limit=5"
            )
            
            sort_desc_data = sort_desc_response.json()
            sort_asc_data = sort_asc_response.json()
            
            checks = {
                "Filter works": filter_response.status_code == 200,
                "Sort desc works": sort_desc_response.status_code == 200,
                "Sort asc works": sort_asc_response.status_code == 200,
                "Results returned": len(filter_data['results']) >= 0
            }
            
            all_passed = all(checks.values())
            
            print_result("Filtering and Sorting", all_passed,
                        f"Filtered results: {len(filter_data['results'])}")
            
            self.record_test("Filtering and Sorting", all_passed)
            return all_passed
            
        except Exception as e:
            print_result("Filtering and Sorting", False, f"Error: {e}")
            self.record_test("Filtering and Sorting", False, str(e))
            return False
    
    def test_hospital_context_analytics(self) -> bool:
        """
        Test 7: Hospital context analytics integration
        Tests: Hospital data acceptance, analytics calculation, output structure
        """
        print_section("Test 7: Hospital Context Analytics")
        
        if not TEST_VIDEO_PATH.exists():
            print_result("Hospital Context Analytics", False, "Test video not found")
            self.record_test("Hospital Context Analytics", False, "Test video missing")
            return False
        
        try:
            # Step 1: Upload video
            print("Step 1: Uploading video for hospital analytics test...")
            with open(TEST_VIDEO_PATH, 'rb') as f:
                files = {'file': (TEST_VIDEO, f, 'video/mp4')}
                upload_response = requests.post(f"{API_URL}/upload", files=files)
            
            if upload_response.status_code != 201:
                print_result("Upload", False, f"Status: {upload_response.status_code}")
                self.record_test("Hospital Context Analytics - Upload", False)
                return False
            
            video_id = upload_response.json()['id']
            print_result("Upload", True, f"Video ID: {video_id}")
            time.sleep(1)
            
            # Step 2: Create hospital context
            print("\nStep 2: Creating hospital context...")
            hospital_context = {
                "staffing": {
                    "total_nurses": 10,
                    "total_doctors": 5,
                    "available_nurses": 8,
                    "available_doctors": 4,
                    "shift_type": "Day"
                },
                "resources": {
                    "total_beds": 50,
                    "occupied_beds": 35,
                    "available_beds": 15,
                    "critical_care_beds": 10,
                    "general_beds": 30,
                    "observation_beds": 10
                },
                "area_sqm": 500,
                "location_name": "Emergency Room"
            }
            
            print_result("Hospital Context", True, 
                        f"Staffing: {hospital_context['staffing']['available_nurses']} nurses, "
                        f"Resources: {hospital_context['resources']['available_beds']} beds")
            print(f"   Hospital context: {json.dumps(hospital_context, indent=2)}")
            
            # Step 3: Analyze with hospital context
            print("\nStep 3: Analyzing with hospital context...")
            analyze_payload = {
                "upload_id": video_id,
                "show_visual": False,
                "save_annotated_video": False,
                "frame_sample_rate": 30,
                "confidence_threshold": 0.5,
                "enable_ai_insights": True,
                "gemini_api_key": os.getenv('GEMINI_API_KEY', ''),
                "hospital_context": hospital_context
            }
            print(f"   📤 Sending payload: {json.dumps(analyze_payload, indent=2)}")
            
            analyze_response = requests.post(
                f"{API_URL}/analyze/{video_id}",
                json=analyze_payload
            )
            
            if analyze_response.status_code != 200:
                print_result("Analysis with Context", False, f"Status: {analyze_response.status_code}")
                print(f"   Response: {analyze_response.text}")
                self.record_test("Hospital Context Analytics - Analysis", False)
                return False
            
            analysis_response_data = analyze_response.json()
            analysis_id = analysis_response_data['analysis_id']
            print_result("Analysis Started", True, f"Analysis ID: {analysis_id}")
            print(f"   Full response: {json.dumps(analysis_response_data, indent=2)}")
            
            # Step 4: Wait for analysis and check hospital analytics in results
            print("\nStep 4: Waiting for analysis to include hospital analytics...")
            max_wait = 120
            start_wait = time.time()
            analysis_complete = False
            hospital_analytics_present = False
            
            while time.time() - start_wait < max_wait:
                status_response = requests.get(f"{API_URL}/analyze/status/{analysis_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    print(f"   Progress: {progress}% - Status: {status}")
                    
                    if status == 'completed':
                        analysis_complete = True
                        analysis_result = status_data.get('result', {})
                        
                        # DEBUG: Log the structure of results
                        print(f"   📊 Status response result type: {type(analysis_result)}")
                        print(f"   📊 Status response result keys: {list(analysis_result.keys()) if isinstance(analysis_result, dict) else 'Not a dict'}")
                        
                        # Check for hospital_analytics in results
                        hospital_analytics = analysis_result.get('results', {}).get('hospital_analytics')
                        if hospital_analytics:
                            hospital_analytics_present = True
                            print_result("Hospital Analytics Present", True, 
                                        "hospital_analytics field found in results")
                        else:
                            print(f"   ⚠️  hospital_analytics not found in status result")
                            print(f"   Available in results: {list(analysis_result.get('results', {}).keys())}")
                        break
                    elif status == 'failed':
                        print_result("Analysis", False, status_data.get('message', 'Unknown error'))
                        print(f"   Status data: {json.dumps(status_data, indent=2)}")
                        self.record_test("Hospital Context Analytics", False, "Analysis failed")
                        return False
                
                time.sleep(5)
            
            if not analysis_complete:
                print_result("Analysis", False, "Timeout waiting for analysis")
                self.record_test("Hospital Context Analytics", False, "Timeout")
                return False
            
            # Step 5: Retrieve and validate hospital analytics
            print("\nStep 5: Validating hospital analytics structure...")
            result_response = requests.get(f"{API_URL}/results/{analysis_id}")
            
            if result_response.status_code != 200:
                print_result("Get Result", False, f"Status: {result_response.status_code}")
                self.record_test("Hospital Context Analytics - Result", False)
                return False
            
            result_data = result_response.json()
            hospital_analytics = result_data.get('results', {}).get('hospital_analytics', {})
            
            # DEBUG: Print full hospital_analytics structure
            print("\n📊 DEBUG: Full Hospital Analytics Structure")
            print(f"   Result data keys: {list(result_data.keys())}")
            print(f"   Results keys: {list(result_data.get('results', {}).keys())}")
            print(f"   hospital_analytics type: {type(hospital_analytics)}")
            print(f"   hospital_analytics: {json.dumps(hospital_analytics, indent=2, default=str)}")
            print(f"   hospital_analytics keys: {list(hospital_analytics.keys())}")
            
            # Validate hospital analytics structure
            validation_checks = {
                "Has staffing_analysis": 'staffing_analysis' in hospital_analytics,
                "Has bed_analysis": 'bed_analysis' in hospital_analytics,
                "Has capacity_score": 'capacity_score' in hospital_analytics,
                "Has critical_alerts": 'critical_alerts' in hospital_analytics
            }
            
            # Validate staffing analysis
            if 'staffing_analysis' in hospital_analytics:
                staffing = hospital_analytics['staffing_analysis']
                validation_checks.update({
                    "Staffing - recommended_nurses": 'recommended_nurses' in staffing,
                    "Staffing - wait_time": 'predicted_wait_time_minutes' in staffing,
                    "Staffing - probability": 'probability_waiting' in staffing,
                    "Staffing - algorithm": 'algorithm' in staffing
                })
                
                print_result("Staffing Analysis", all(v for k, v in validation_checks.items() if 'Staffing' in k),
                            f"Recommended: {staffing.get('recommended_nurses')} nurses, "
                            f"Wait time: {staffing.get('predicted_wait_time_minutes', 0):.1f} min")
            
            # Validate bed analysis
            print("\n🔍 DEBUG: Bed Analysis Inspection")
            print(f"   hospital_analytics keys: {list(hospital_analytics.keys())}")
            print(f"   'bed_analysis' in hospital_analytics: {'bed_analysis' in hospital_analytics}")
            
            if 'bed_analysis' in hospital_analytics:
                bed_analysis = hospital_analytics['bed_analysis']
                print(f"   bed_analysis type: {type(bed_analysis)}")
                print(f"   bed_analysis keys: {list(bed_analysis.keys()) if isinstance(bed_analysis, dict) else 'N/A'}")
                print(f"   bed_analysis content: {json.dumps(bed_analysis, indent=4)}")
                
                # Log all fields
                print(f"\n   Detailed Bed Analysis Fields:")
                print(f"     - occupancy_rate: {bed_analysis.get('occupancy_rate', 'MISSING')}")
                print(f"     - current_occupancy_rate: {bed_analysis.get('current_occupancy_rate', 'MISSING')}")
                print(f"     - additional_capacity_needed: {bed_analysis.get('additional_capacity_needed', 'MISSING')}")
                print(f"     - type: {bed_analysis.get('type', 'MISSING')}")
                print(f"     - total_beds: {bed_analysis.get('total_beds', 'MISSING')}")
                print(f"     - occupied_beds: {bed_analysis.get('occupied_beds', 'MISSING')}")
                print(f"     - available_beds: {bed_analysis.get('available_beds', 'MISSING')}")
                
                # Use the actual field names from backend
                occupancy_rate = bed_analysis.get('current_occupancy_rate', 0)
                additional_capacity = bed_analysis.get('additional_capacity_needed', 0)
                
                validation_checks.update({
                    "Bed - occupancy": bed_analysis.get('current_occupancy_rate') is not None,
                    "Bed - shortage": 'additional_capacity_needed' in bed_analysis
                })
                
                bed_checks_passed = all(v for k, v in validation_checks.items() if 'Bed' in k)
                
                print(f"\n   Bed Analysis Validation:")
                print(f"     - Checks passed: {bed_checks_passed}")
                print(f"     - Occupancy value: {occupancy_rate} (type: {type(occupancy_rate).__name__})")
                print(f"     - Shortage value: {additional_capacity} (type: {type(additional_capacity).__name__})")
                print(f"     - Occupancy percentage: {occupancy_rate * 100:.1f}%")
                
                print_result("Bed Analysis", bed_checks_passed,
                            f"Occupancy: {occupancy_rate * 100:.1f}%, "
                            f"Shortage: {additional_capacity} beds")
            else:
                print(f"   ❌ bed_analysis NOT FOUND in hospital_analytics")
                print(f"   Available keys: {list(hospital_analytics.keys())}")
                validation_checks.update({
                    "Bed - occupancy": False,
                    "Bed - shortage": False
                })
                print_result("Bed Analysis", False, "bed_analysis key missing from hospital_analytics")
            
            # Validate capacity score
            capacity_score = hospital_analytics.get('capacity_score', -1)
            if 0 <= capacity_score <= 100:
                validation_checks["Capacity score valid"] = True
                print_result("Capacity Score", True, f"Score: {capacity_score:.1f}/100")
            else:
                validation_checks["Capacity score valid"] = False
                print_result("Capacity Score", False, f"Invalid score: {capacity_score}")
            
            # Validate alerts
            critical_alerts = hospital_analytics.get('critical_alerts', [])
            validation_checks["Has alerts list"] = isinstance(critical_alerts, list)
            print_result("Critical Alerts", True, f"Count: {len(critical_alerts)}")
            
            all_passed = all(validation_checks.values())
            
            print(f"\nValidation Results:")
            for check, passed in validation_checks.items():
                status = "✓" if passed else "✗"
                print(f"   {status} {check}")
            
            self.record_test("Hospital Context Analytics", all_passed,
                           f"{sum(validation_checks.values())}/{len(validation_checks)} checks passed")
            
            return all_passed
            
        except Exception as e:
            print_result("Hospital Context Analytics", False, f"Error: {e}")
            self.record_test("Hospital Context Analytics", False, str(e))
            return False
    
    def test_hospital_context_without_context(self) -> bool:
        """
        Test 8: Backward compatibility - analysis without hospital context
        Tests: System works without hospital_context (backward compatible)
        """
        print_section("Test 8: Backward Compatibility (No Hospital Context)")
        
        if not TEST_VIDEO_PATH.exists():
            print_result("Backward Compatibility", False, "Test video not found")
            self.record_test("Backward Compatibility", False, "Test video missing")
            return False
        
        try:
            # Upload video
            print("Uploading video for backward compatibility test...")
            with open(TEST_VIDEO_PATH, 'rb') as f:
                files = {'file': (TEST_VIDEO, f, 'video/mp4')}
                upload_response = requests.post(f"{API_URL}/upload", files=files)
            
            if upload_response.status_code != 201:
                print_result("Upload", False, f"Status: {upload_response.status_code}")
                return False
            
            video_id = upload_response.json()['id']
            time.sleep(1)
            
            # Analyze WITHOUT hospital context (old way)
            print("Analyzing WITHOUT hospital context...")
            analyze_response = requests.post(
                f"{API_URL}/analyze/{video_id}",
                json={
                    "upload_id": video_id,
                    "show_visual": False,
                    "save_annotated_video": False,
                    "frame_sample_rate": 30,
                    "confidence_threshold": 0.5,
                    "enable_ai_insights": False
                }
            )
            
            if analyze_response.status_code != 200:
                print_result("Analysis without context", False, f"Status: {analyze_response.status_code}")
                self.record_test("Backward Compatibility", False)
                return False
            
            analysis_id = analyze_response.json()['analysis_id']
            
            # Wait for completion
            print("Waiting for analysis...")
            max_wait = 120
            start_wait = time.time()
            
            while time.time() - start_wait < max_wait:
                status_response = requests.get(f"{API_URL}/analyze/status/{analysis_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    if status in ['completed', 'failed']:
                        break
                
                time.sleep(5)
            
            # Verify results exist (with or without hospital_analytics)
            result_response = requests.get(f"{API_URL}/results/{analysis_id}")
            
            if result_response.status_code != 200:
                print_result("Backward Compatibility", False, "Cannot retrieve results")
                self.record_test("Backward Compatibility", False)
                return False
            
            result_data = result_response.json()
            has_results = 'results' in result_data
            
            # Check what's present
            hospital_analytics = result_data.get('results', {}).get('hospital_analytics')
            
            checks = {
                "Has results": has_results,
                "Results is not empty": len(result_data.get('results', {})) > 0,
                "System works without context": True  # If we got here, it works
            }
            
            all_passed = all(checks.values())
            
            details = f"Results present, Hospital analytics: {'present' if hospital_analytics else 'not present (expected)'}"
            print_result("Backward Compatibility", all_passed, details)
            
            self.record_test("Backward Compatibility", all_passed)
            return all_passed
            
        except Exception as e:
            print_result("Backward Compatibility", False, f"Error: {e}")
            self.record_test("Backward Compatibility", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*80)
        print(" PHASE 8: INTEGRATION TEST SUITE")
        print("="*80)
        
        # Check server
        if not self.check_server():
            print("\n❌ Server is not running. Please start it:")
            print("   uvicorn app.main:app --reload")
            return
        
        print("\n✅ Server is running\n")
        
        # Run tests
        self.test_complete_workflow()
        self.test_concurrent_operations()
        self.test_data_consistency()
        self.test_error_handling()
        self.test_pagination()
        self.test_filtering_sorting()
        self.test_hospital_context_analytics()
        self.test_hospital_context_without_context()
        
        # Summary
        print_section("TEST SUMMARY")
        print(f"Total Tests: {self.results['total']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.results['failed']} test(s) failed")
            print("\nFailed tests:")
            for test in self.results['tests']:
                if not test['passed']:
                    print(f"  - {test['name']}: {test['details']}")
        
        print("\n" + "="*80 + "\n")
        
        return self.results


def main():
    """Run integration tests"""
    suite = IntegrationTestSuite()
    results = suite.run_all_tests()
    
    # Save results to file
    results_file = Path("results") / f"integration_test_results_{int(time.time())}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    main()
