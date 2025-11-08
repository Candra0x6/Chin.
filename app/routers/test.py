"""
Test API Router
Provides endpoints for running integration tests via web interface
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any

router = APIRouter(prefix="/test", tags=["Testing"])


@router.post("/integration")
async def run_integration_tests() -> JSONResponse:
    """
    Run the complete integration test suite
    
    Returns:
        JSONResponse: Test results including output and summary
    """
    try:
        # Path to integration test file
        test_file = Path(__file__).parent.parent.parent / "tests" / "test_integration.py"
        
        if not test_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Integration test file not found: {test_file}"
            )
        
        # Run the test suite
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += "\n\n=== ERRORS ===\n" + result.stderr
        
        # Try to parse summary from output
        summary = parse_test_summary(output)
        
        return JSONResponse(
            content={
                "success": result.returncode == 0,
                "output": output,
                "summary": summary,
                "return_code": result.returncode
            }
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Test execution timeout (exceeded 5 minutes)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run integration tests: {str(e)}"
        )


@router.get("/status")
async def test_api_status() -> Dict[str, Any]:
    """
    Check if test API is available
    
    Returns:
        Dict: Status information
    """
    test_file = Path(__file__).parent.parent.parent / "tests" / "test_integration.py"
    sample_video = Path(__file__).parent.parent.parent / "sample_video.mp4"
    
    return {
        "status": "available",
        "test_file_exists": test_file.exists(),
        "sample_video_exists": sample_video.exists(),
        "test_file_path": str(test_file),
        "sample_video_path": str(sample_video)
    }


def parse_test_summary(output: str) -> Dict[str, Any]:
    """
    Parse test summary from output
    
    Args:
        output: Test output text
        
    Returns:
        Dict containing test statistics
    """
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            # Parse summary section
            if "Total Tests:" in line:
                summary["total"] = int(line.split(":")[-1].strip())
            elif "Passed:" in line:
                summary["passed"] = int(line.split(":")[-1].strip())
            elif "Failed:" in line:
                summary["failed"] = int(line.split(":")[-1].strip())
            
            # Parse individual test results
            if "✅ PASS" in line or "❌ FAIL" in line:
                passed = "✅ PASS" in line
                test_name = line.split("-")[-1].strip() if "-" in line else line
                summary["tests"].append({
                    "name": test_name,
                    "passed": passed
                })
    
    except Exception:
        # If parsing fails, return empty summary
        pass
    
    return summary


@router.get("/results")
async def get_latest_test_results() -> JSONResponse:
    """
    Get the latest test results from saved JSON file
    
    Returns:
        JSONResponse: Latest test results
    """
    try:
        results_dir = Path(__file__).parent.parent.parent / "results"
        
        if not results_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="No test results found. Run tests first."
            )
        
        # Find most recent results file
        result_files = sorted(
            results_dir.glob("integration_test_results_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not result_files:
            raise HTTPException(
                status_code=404,
                detail="No test results found. Run tests first."
            )
        
        # Read the latest results
        with open(result_files[0], 'r') as f:
            results = json.load(f)
        
        return JSONResponse(content={
            "timestamp": result_files[0].stem.split('_')[-1],
            "results": results
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read test results: {str(e)}"
        )


@router.delete("/results")
async def clear_test_results() -> Dict[str, str]:
    """
    Clear all saved test results
    
    Returns:
        Dict: Success message
    """
    try:
        results_dir = Path(__file__).parent.parent.parent / "results"
        
        if not results_dir.exists():
            return {"message": "No results to clear"}
        
        # Delete all result files
        deleted_count = 0
        for result_file in results_dir.glob("integration_test_results_*.json"):
            result_file.unlink()
            deleted_count += 1
        
        return {
            "message": f"Cleared {deleted_count} test result file(s)"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear test results: {str(e)}"
        )
