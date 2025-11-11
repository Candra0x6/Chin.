"""
Example: Using Hospital Context in Video Analysis

This script demonstrates how to submit a video analysis request
with real-time hospital staffing and resource data.
"""

import requests
import json
from typing import Dict, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
VIDEO_ID = "1a12bb90-c15b-417c-981f-e6c7ec2027fd"

# Example hospital contexts for different scenarios

HOSPITAL_CONTEXT_EMERGENCY_ROOM = {
    "staffing": {
        "total_nurses": 8,
        "total_doctors": 2,
        "available_nurses": 5,  # Some are on break/assigned
        "available_doctors": 1,
        "shift_type": "day"
    },
    "resources": {
        "total_beds": 50,
        "occupied_beds": 42,
        "available_beds": 8,
        "critical_care_beds": 10,
        "general_beds": 30,
        "observation_beds": 10
    },
    "area_sqm": 150.0,
    "location_name": "Emergency Room Waiting Area"
}

HOSPITAL_CONTEXT_TRIAGE = {
    "staffing": {
        "total_nurses": 3,
        "total_doctors": 0,
        "available_nurses": 2,
        "available_doctors": 0,
        "shift_type": "day"
    },
    "resources": {
        "total_beds": 10,
        "occupied_beds": 3,
        "available_beds": 7,
        "critical_care_beds": 0,
        "general_beds": 7,
        "observation_beds": 3
    },
    "area_sqm": 75.0,
    "location_name": "Triage Area"
}

HOSPITAL_CONTEXT_ICU = {
    "staffing": {
        "total_nurses": 12,  # ICU has higher nurse ratio
        "total_doctors": 3,
        "available_nurses": 8,
        "available_doctors": 2,
        "shift_type": "night"  # Night shift
    },
    "resources": {
        "total_beds": 20,
        "occupied_beds": 19,  # Almost full
        "available_beds": 1,
        "critical_care_beds": 20,
        "general_beds": 0,
        "observation_beds": 0
    },
    "area_sqm": 200.0,
    "location_name": "Intensive Care Unit"
}


def submit_analysis_request(
    video_id: str,
    hospital_context: Dict,
    enable_ai_insights: bool = True,
    show_visual: bool = False
) -> Dict:
    """
    Submit a video analysis request with hospital context.
    
    Args:
        video_id: ID of the uploaded video
        hospital_context: Dictionary with staffing and resource data
        enable_ai_insights: Whether to generate AI insights
        show_visual: Whether to show real-time visualization
        
    Returns:
        API response with analysis_id
    """
    
    # Prepare request body
    request_data = {
        "upload_id": video_id,
        "show_visual": show_visual,
        "save_annotated_video": False,
        "frame_sample_rate": 30,
        "confidence_threshold": 0.5,
        "enable_ai_insights": enable_ai_insights,
        "hospital_context": hospital_context
    }
    
    # Submit to API
    url = f"{API_BASE_URL}/api/analyze/{video_id}"
    
    print(f"\n🏥 Submitting analysis request to {url}")
    print(f"   Location: {hospital_context.get('location_name', 'N/A')}")
    print(f"   Available Nurses: {hospital_context['staffing']['available_nurses']}")
    print(f"   Available Beds: {hospital_context['resources']['available_beds']}")
    
    response = requests.post(url, json=request_data)
    response.raise_for_status()
    
    result = response.json()
    print(f"\n✅ Analysis queued: {result.get('analysis_id')}")
    
    return result


def check_analysis_status(analysis_id: str) -> Dict:
    """
    Check the status of an ongoing or completed analysis.
    
    Args:
        analysis_id: ID returned from submit_analysis_request
        
    Returns:
        Status response with progress and results
    """
    url = f"{API_BASE_URL}/api/analyze/status/{analysis_id}"
    
    response = requests.get(url)
    response.raise_for_status()
    
    result = response.json()
    
    status = result.get("status", "unknown")
    progress = result.get("progress", 0)
    
    print(f"\n📊 Analysis Status: {status} ({progress}%)")
    print(f"   Message: {result.get('message', 'N/A')}")
    
    if status == "completed" and result.get("result"):
        print_analysis_results(result["result"])
    
    return result


def print_analysis_results(results: Dict):
    """Pretty print analysis results with hospital analytics."""
    
    print("\n" + "="*70)
    print("📋 ANALYSIS RESULTS")
    print("="*70)
    
    # Basic statistics
    stats = results.get("statistics", {})
    print(f"\n📊 Crowd Statistics:")
    print(f"   Average People: {stats.get('average_person_count', 0):.1f}")
    print(f"   Peak Count: {stats.get('max_person_count', 0)}")
    print(f"   Min Count: {stats.get('min_person_count', 0)}")
    
    # Hospital Analytics
    hospital_analytics = results.get("hospital_analytics", {})
    if hospital_analytics:
        print(f"\n🏥 Hospital Analytics:")
        print(f"   Location: {hospital_analytics.get('location', 'N/A')}")
        print(f"   Overall Status: {hospital_analytics.get('overall_status', 'N/A')}")
        print(f"   Capacity Score: {hospital_analytics.get('capacity_score', 'N/A')}/100")
        
        # Staffing recommendations
        staffing = hospital_analytics.get("staffing_analysis", {})
        if staffing:
            print(f"\n👨‍⚕️ Staffing Recommendations:")
            print(f"   Recommended Nurses: {staffing.get('recommended_nurses', 'N/A')}")
            print(f"   Additional Needed: {staffing.get('additional_nurses_needed', 0)}")
            print(f"   Predicted Wait Time: {staffing.get('predicted_wait_time_minutes', 'N/A')} min")
            print(f"   Probability of Waiting: {staffing.get('probability_waiting', 'N/A'):.1%}")
            print(f"   System Utilization: {staffing.get('system_utilization', 'N/A'):.1%}")
            print(f"   Algorithm: {staffing.get('algorithm', 'N/A')}")
        
        # Bed analysis
        beds = hospital_analytics.get("bed_analysis", {})
        if beds:
            print(f"\n🛏️ Bed Analysis:")
            print(f"   Estimated Waiting Patients: {beds.get('estimated_waiting_patients', 'N/A'):.1f}")
            print(f"   Current Occupancy: {beds.get('current_occupancy_rate', 'N/A'):.1%}")
            print(f"   Projected Occupancy: {beds.get('projected_occupancy_rate', 'N/A'):.1%}")
            print(f"   Additional Beds Needed: {beds.get('additional_capacity_needed', 0)}")
            print(f"   Urgency: {beds.get('urgency_level', 'N/A')}")
        
        # Alerts
        alerts = hospital_analytics.get("critical_alerts", [])
        if alerts:
            print(f"\n⚠️ Critical Alerts:")
            for alert in alerts:
                print(f"   • {alert}")
        
        # Summary
        summary = hospital_analytics.get("summary", "")
        if summary:
            print(f"\n📝 Summary:")
            print(f"   {summary}")
    
    # AI Insights
    ai_insights = results.get("ai_insights", {})
    if ai_insights and "error" not in ai_insights:
        print(f"\n🤖 AI Insights ({ai_insights.get('generated_by', 'unknown')}):")
        print(f"   {ai_insights.get('ai_summary', 'N/A')[:200]}...")
        
        findings = ai_insights.get("key_findings", [])
        if findings:
            print(f"\n   Key Findings:")
            for finding in findings[:3]:
                print(f"   • {finding}")
        
        actions = ai_insights.get("priority_actions", [])
        if actions:
            print(f"\n   Priority Actions:")
            for action in actions[:3]:
                print(f"   • {action}")
    
    print("\n" + "="*70)


def main():
    """Main example demonstrating the hospital context API."""
    
    print("\n🚀 Hospital Analytics Integration Example\n")
    
    # Scenario 1: Emergency Room with moderate load
    print("\n--- Scenario 1: Emergency Room ---")
    try:
        response = submit_analysis_request(
            video_id=VIDEO_ID,
            hospital_context=HOSPITAL_CONTEXT_EMERGENCY_ROOM,
            enable_ai_insights=True
        )
        analysis_id = response.get("analysis_id")
        print(f"Analysis ID: {analysis_id}")
        
        # In a real scenario, you would poll the status endpoint
        # status_response = check_analysis_status(analysis_id)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the backend is running.")
        print("   Run: python -m uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Scenario 2: Triage Area
    print("\n--- Scenario 2: Triage Area ---")
    response = submit_analysis_request(
        video_id=VIDEO_ID,
        hospital_context=HOSPITAL_CONTEXT_TRIAGE
    )
    
    # Scenario 3: ICU (Night Shift - Critical)
    print("\n--- Scenario 3: ICU (Night Shift) ---")
    response = submit_analysis_request(
        video_id=VIDEO_ID,
        hospital_context=HOSPITAL_CONTEXT_ICU
    )
    
    print("\n\n📌 Note:")
    print("   • Use check_analysis_status() to poll for completed results")
    print("   • Results include hospital_analytics with Erlang C calculations")
    print("   • AI insights are contextualized to hospital capacity")
    print("   • Set enable_ai_insights=False to skip AI generation for faster processing")


if __name__ == "__main__":
    main()
