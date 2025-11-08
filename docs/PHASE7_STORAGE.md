# Phase 7: Results & Storage API - Documentation

## 🎯 Overview

Phase 7 provides comprehensive **data retrieval, search, export, and management** capabilities for analysis results. This phase enables users to access historical data, generate reports, and maintain system hygiene through automated cleanup.

### Key Features

✅ **Results Retrieval** - Get specific or list all analyses  
✅ **Advanced Search** - Filter by multiple criteria  
✅ **Pagination & Sorting** - Handle large datasets efficiently  
✅ **Export Functionality** - Download JSON or text summaries  
✅ **Statistics** - Overall system analytics  
✅ **Cleanup Utilities** - Automated file and database maintenance  
✅ **Storage Management** - Monitor disk usage

---

## 📋 API Endpoints Summary

### Results Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/results/{id}` | Get specific analysis |
| GET | `/api/results` | List all analyses (paginated) |
| GET | `/api/results/search/advanced` | Advanced search |
| GET | `/api/results/{id}/export/json` | Export as JSON |
| GET | `/api/results/{id}/export/summary` | Export as text |
| GET | `/api/results/stats/overview` | System statistics |
| DELETE | `/api/results/{id}` | Delete analysis |

### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/results/admin/storage` | Storage information |
| POST | `/api/results/admin/cleanup` | Trigger cleanup |

---

## 📖 Detailed Endpoint Documentation

### 1. Get Analysis Result

**GET** `/api/results/{analysis_id}`

Retrieve complete analysis details for a specific ID.

#### Example Request
```bash
curl http://localhost:8000/api/results/123
```

#### Response
```json
{
  "analysis_id": 123,
  "video_id": "abc-123",
  "video_name": "hospital_lobby.mp4",
  "created_at": "2024-11-07T14:30:00",
  "status": "completed",
  "results": {
    "avg_count": 8.5,
    "peak_count": 15,
    "crowd_level": "Medium",
    "suggested_nurses": 2,
    "bottlenecks": [...],
    "ai_insights": {...}
  }
}
```

---

### 2. List Analyses (Paginated)

**GET** `/api/results`

List all analyses with pagination, filtering, and sorting.

#### Query Parameters
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 10, max: 100)
- `video_name` (string): Filter by name (partial match)
- `crowd_level` (string): Filter by level (Low, Medium, High, Very High)
- `date_from` (string): From date (YYYY-MM-DD)
- `date_to` (string): To date (YYYY-MM-DD)
- `sort_by` (string): Sort field (created_at, video_name)
- `sort_order` (string): Sort direction (asc, desc)

#### Example Requests

**Basic Pagination:**
```bash
curl "http://localhost:8000/api/results?page=1&limit=10"
```

**Filter by Crowd Level:**
```bash
curl "http://localhost:8000/api/results?crowd_level=High&limit=20"
```

**Date Range:**
```bash
curl "http://localhost:8000/api/results?date_from=2024-11-01&date_to=2024-11-07"
```

**Sorted by Newest:**
```bash
curl "http://localhost:8000/api/results?sort_by=created_at&sort_order=desc&limit=5"
```

#### Response
```json
{
  "page": 1,
  "limit": 10,
  "total": 45,
  "total_pages": 5,
  "results": [
    {
      "analysis_id": 123,
      "video_name": "hospital_lobby.mp4",
      "created_at": "2024-11-07T14:30:00",
      "crowd_level": "Medium",
      "peak_count": 15,
      "suggested_nurses": 2,
      "status": "completed"
    }
  ]
}
```

---

### 3. Advanced Search

**GET** `/api/results/search/advanced`

Search with multiple criteria and complex filters.

#### Query Parameters
- `query` (string): Text search in video name
- `min_peak_count` (int): Minimum peak people
- `max_peak_count` (int): Maximum peak people
- `crowd_levels` (string): Comma-separated levels
- `bottleneck_severity` (string): low, medium, high
- `has_ai_insights` (bool): Filter by AI insights presence
- `date_from/date_to` (string): Date range
- `page/limit` (int): Pagination

#### Example Requests

**Search by Peak Count Range:**
```bash
curl "http://localhost:8000/api/results/search/advanced?min_peak_count=10&max_peak_count=20"
```

**Multiple Crowd Levels:**
```bash
curl "http://localhost:8000/api/results/search/advanced?crowd_levels=Medium,High"
```

**With AI Insights:**
```bash
curl "http://localhost:8000/api/results/search/advanced?has_ai_insights=true"
```

**Combined Search:**
```bash
curl "http://localhost:8000/api/results/search/advanced?query=lobby&min_peak_count=5&crowd_levels=Medium,High&has_ai_insights=true"
```

#### Response
```json
{
  "page": 1,
  "total": 15,
  "results": [
    {
      "analysis_id": 123,
      "video_name": "hospital_lobby.mp4",
      "crowd_level": "Medium",
      "peak_count": 15,
      "avg_count": 8.5,
      "suggested_nurses": 2,
      "bottleneck_count": 2,
      "has_ai_insights": true
    }
  ]
}
```

---

### 4. Export to JSON

**GET** `/api/results/{analysis_id}/export/json`

Download complete analysis as JSON file.

#### Example
```bash
curl -O "http://localhost:8000/api/results/123/export/json"
```

#### Downloaded File
```json
{
  "analysis_id": 123,
  "video_name": "hospital_lobby.mp4",
  "created_at": "2024-11-07T14:30:00",
  "results": {
    "avg_count": 8.5,
    "peak_count": 15,
    ...full analysis data...
  }
}
```

---

### 5. Export Summary

**GET** `/api/results/{analysis_id}/export/summary`

Download human-readable text summary.

#### Example
```bash
curl -O "http://localhost:8000/api/results/123/export/summary"
```

#### Downloaded File (summary_123_20241107_143000.txt)
```
================================================================================
HOSPITWIN LITE - ANALYSIS SUMMARY
================================================================================

Analysis ID: 123
Video Name: hospital_lobby.mp4
Analysis Date: 2024-11-07T14:30:00

--------------------------------------------------------------------------------
CROWD STATISTICS
--------------------------------------------------------------------------------
Average People Count: 8.5
Peak Count: 15
Total People Detected: 256
Crowd Level: Medium

Peak Congestion Time: 14:30:00 - 15:00:00

--------------------------------------------------------------------------------
STAFFING RECOMMENDATION
--------------------------------------------------------------------------------
Suggested Nurses: 2

Rationale:
Based on healthcare staffing ratios (1:8-10) and crowd density analysis...

--------------------------------------------------------------------------------
BOTTLENECK ANALYSIS
--------------------------------------------------------------------------------
Number of Bottlenecks Detected: 2

Bottleneck 1:
  Time Range: 14:30:00 - 14:45:00
  Severity: High
  Average Count: 12.3
...
```

---

### 6. Statistics Overview

**GET** `/api/results/stats/overview`

Get system-wide statistics across all analyses.

#### Example
```bash
curl http://localhost:8000/api/results/stats/overview
```

#### Response
```json
{
  "total_analyses": 45,
  "analyses_by_crowd_level": {
    "Low": 20,
    "Medium": 15,
    "High": 8,
    "Very High": 2
  },
  "avg_peak_count": 12.5,
  "total_bottlenecks": 67,
  "analyses_with_ai_insights": 30,
  "avg_bottlenecks_per_analysis": 1.49
}
```

---

### 7. Storage Information

**GET** `/api/results/admin/storage`

Get current storage usage statistics.

#### Example
```bash
curl http://localhost:8000/api/results/admin/storage
```

#### Response
```json
{
  "uploads": {
    "count": 15,
    "size_mb": 1024.5
  },
  "results": {
    "count": 8,
    "size_mb": 3.2
  },
  "total_size_mb": 1027.7
}
```

---

### 8. Trigger Cleanup

**POST** `/api/results/admin/cleanup`

Manually trigger cleanup of old files.

#### Query Parameters
- `retention_days` (int): Files older than this will be removed (default: 30)

#### Example
```bash
curl -X POST "http://localhost:8000/api/results/admin/cleanup?retention_days=30"
```

#### Response
```json
{
  "started_at": "2024-11-07T14:30:00",
  "retention_days": 30,
  "operations": {
    "uploads": {
      "files_removed": 5,
      "space_freed_mb": 245.6,
      "files": ["old_video1.mp4", "old_video2.mp4", ...]
    },
    "results": {
      "files_removed": 3,
      "space_freed_mb": 1.2,
      "files": ["result1.json", ...]
    },
    "orphaned": {
      "uploads_orphaned": 2,
      "message": "Removed 2 orphaned files"
    }
  },
  "storage_after": {
    "uploads": {"count": 10, "size_mb": 778.9},
    "results": {"count": 5, "size_mb": 2.0},
    "total_size_mb": 780.9
  },
  "completed_at": "2024-11-07T14:30:05"
}
```

---

### 9. Delete Analysis

**DELETE** `/api/results/{analysis_id}`

Delete a specific analysis from the database.

#### Example
```bash
curl -X DELETE http://localhost:8000/api/results/123
```

#### Response
```json
{
  "message": "Analysis 123 deleted successfully",
  "analysis_id": 123
}
```

---

## 🐍 Python SDK Usage

### Example 1: List Recent Analyses

```python
import requests

response = requests.get("http://localhost:8000/api/results", params={
    "page": 1,
    "limit": 10,
    "sort_by": "created_at",
    "sort_order": "desc"
})

data = response.json()
print(f"Total analyses: {data['total']}")

for analysis in data['results']:
    print(f"{analysis['video_name']}: {analysis['crowd_level']} "
          f"(Peak: {analysis['peak_count']})")
```

---

### Example 2: Search High-Crowd Analyses

```python
response = requests.get(
    "http://localhost:8000/api/results/search/advanced",
    params={
        "crowd_levels": "High,Very High",
        "min_peak_count": 15,
        "has_ai_insights": True
    }
)

results = response.json()['results']
print(f"Found {len(results)} high-crowd analyses")

for r in results:
    print(f"- {r['video_name']}: Peak {r['peak_count']}, "
          f"{r['bottleneck_count']} bottlenecks")
```

---

### Example 3: Export and Save Reports

```python
from pathlib import Path

analysis_id = 123

# Export JSON
response = requests.get(f"http://localhost:8000/api/results/{analysis_id}/export/json")
Path("reports").mkdir(exist_ok=True)
with open(f"reports/analysis_{analysis_id}.json", "wb") as f:
    f.write(response.content)

# Export summary
response = requests.get(f"http://localhost:8000/api/results/{analysis_id}/export/summary")
with open(f"reports/summary_{analysis_id}.txt", "wb") as f:
    f.write(response.content)

print("✅ Reports exported successfully")
```

---

### Example 4: Automated Weekly Cleanup

```python
import schedule
import time

def weekly_cleanup():
    """Run cleanup every week"""
    response = requests.post(
        "http://localhost:8000/api/results/admin/cleanup",
        params={"retention_days": 30}
    )
    
    result = response.json()
    print(f"Cleanup completed:")
    print(f"  - Uploads removed: {result['operations']['uploads']['files_removed']}")
    print(f"  - Space freed: {result['operations']['uploads']['space_freed_mb']} MB")

# Schedule weekly cleanup (Sundays at 2 AM)
schedule.every().sunday.at("02:00").do(weekly_cleanup)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

---

## 🔧 Cleanup Manager

### CleanupManager Class

The `CleanupManager` class provides comprehensive cleanup utilities.

#### Methods

##### `cleanup_old_uploads()`
Remove uploaded videos older than retention period.

```python
from app.utils.cleanup import CleanupManager

manager = CleanupManager(retention_days=30)
result = manager.cleanup_old_uploads()

print(f"Removed {result['files_removed']} files")
print(f"Freed {result['space_freed_mb']} MB")
```

##### `cleanup_old_results()`
Remove exported result files.

```python
result = manager.cleanup_old_results()
```

##### `cleanup_orphaned_files()`
Remove files with no database entry.

```python
result = manager.cleanup_orphaned_files()
print(f"Removed {result['uploads_orphaned']} orphaned files")
```

##### `get_storage_stats()`
Get current storage usage.

```python
stats = manager.get_storage_stats()
print(f"Total storage: {stats['total_size_mb']} MB")
```

##### `cleanup_all()`
Run all cleanup operations.

```python
result = manager.cleanup_all()
```

---

## 📊 Response Models

### AnalysisListItem
```python
{
  "analysis_id": int,
  "video_id": str,
  "video_name": str,
  "created_at": str,  # ISO 8601
  "crowd_level": str,  # Low, Medium, High, Very High
  "peak_count": int,
  "suggested_nurses": int,
  "status": str  # completed, processing, failed
}
```

### PaginatedResponse
```python
{
  "page": int,
  "limit": int,
  "total": int,
  "total_pages": int,
  "results": [AnalysisListItem]
}
```

### StatisticsOverview
```python
{
  "total_analyses": int,
  "analyses_by_crowd_level": dict,
  "avg_peak_count": float,
  "total_bottlenecks": int,
  "analyses_with_ai_insights": int,
  "avg_bottlenecks_per_analysis": float
}
```

---

## 🎯 Use Cases

### Use Case 1: Daily Operations Dashboard

Hospital administrator checks daily statistics:

```python
# Get today's analyses
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
response = requests.get("http://localhost:8000/api/results", params={
    "date_from": today,
    "date_to": today,
    "sort_by": "created_at",
    "sort_order": "desc"
})

analyses = response.json()['results']
print(f"Today's analyses: {len(analyses)}")

for analysis in analyses:
    if analysis['crowd_level'] in ['High', 'Very High']:
        print(f"⚠️  {analysis['video_name']}: {analysis['crowd_level']} "
              f"(Peak: {analysis['peak_count']})")
```

---

### Use Case 2: Monthly Report Generation

Generate monthly report with all high-crowd incidents:

```python
from datetime import datetime, timedelta

# Get last month's date range
today = datetime.now()
first_day = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
last_day = today.replace(day=1) - timedelta(days=1)

response = requests.get("http://localhost:8000/api/results/search/advanced", params={
    "crowd_levels": "High,Very High",
    "date_from": first_day.strftime("%Y-%m-%d"),
    "date_to": last_day.strftime("%Y-%m-%d"),
    "limit": 100
})

high_crowd_analyses = response.json()['results']

# Export each as summary
for analysis in high_crowd_analyses:
    response = requests.get(
        f"http://localhost:8000/api/results/{analysis['analysis_id']}/export/summary"
    )
    filename = f"monthly_report_{analysis['analysis_id']}.txt"
    with open(filename, "wb") as f:
        f.write(response.content)

print(f"✅ Generated {len(high_crowd_analyses)} reports")
```

---

### Use Case 3: Capacity Planning

Analyze historical trends for capacity planning:

```python
# Get statistics
response = requests.get("http://localhost:8000/api/results/stats/overview")
stats = response.json()

print("=== CAPACITY PLANNING REPORT ===")
print(f"Total Analyses: {stats['total_analyses']}")
print(f"Average Peak Count: {stats['avg_peak_count']}")
print(f"Average Bottlenecks: {stats['avg_bottlenecks_per_analysis']}")

print("\nCrowd Level Distribution:")
for level, count in stats['analyses_by_crowd_level'].items():
    percentage = (count / stats['total_analyses']) * 100
    print(f"  {level}: {count} ({percentage:.1f}%)")

# Recommendation
if stats['avg_peak_count'] > 15:
    print("\n⚠️  Recommendation: Consider increasing base staffing")
if stats['avg_bottlenecks_per_analysis'] > 2:
    print("⚠️  Recommendation: Review operational workflows")
```

---

## ✅ Best Practices

### 1. Pagination

Always use pagination for large datasets:

```python
# ❌ Don't: Load all results at once
response = requests.get("http://localhost:8000/api/results?limit=1000")

# ✅ Do: Paginate through results
page = 1
while True:
    response = requests.get("http://localhost:8000/api/results", params={
        "page": page,
        "limit": 50
    })
    data = response.json()
    
    # Process results
    for result in data['results']:
        process(result)
    
    if page >= data['total_pages']:
        break
    page += 1
```

---

### 2. Error Handling

Always handle API errors gracefully:

```python
try:
    response = requests.get(f"http://localhost:8000/api/results/{analysis_id}")
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Analysis not found")
    else:
        print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

### 3. Caching

Cache frequently accessed data:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100, ttl=3600)  # Cache for 1 hour
def get_analysis(analysis_id: int):
    response = requests.get(f"http://localhost:8000/api/results/{analysis_id}")
    return response.json()
```

---

### 4. Scheduled Cleanup

Set up automated cleanup:

```python
# Add to cron: 0 2 * * 0 (Every Sunday at 2 AM)
import subprocess

result = subprocess.run([
    "curl", "-X", "POST",
    "http://localhost:8000/api/results/admin/cleanup?retention_days=30"
], capture_output=True)

if result.returncode == 0:
    print("✅ Cleanup completed")
else:
    print("❌ Cleanup failed")
```

---

## 🔮 Future Enhancements

Phase 7.1:
- [ ] PDF export with charts
- [ ] Bulk export (multiple analyses)
- [ ] Scheduled reports via email
- [ ] Data archival to cloud storage

Phase 7.2:
- [ ] Historical trend analysis
- [ ] Comparative reports (week-over-week)
- [ ] Predictive analytics
- [ ] Dashboard widgets API

---

## 🆘 Troubleshooting

### Issue: "Analysis not found"

**Solution:** Verify the analysis ID exists:
```bash
curl http://localhost:8000/api/results | jq '.results[].analysis_id'
```

### Issue: "No results returned"

**Solution:** Check filters are not too restrictive:
```bash
# Remove filters gradually
curl "http://localhost:8000/api/results?page=1&limit=100"
```

### Issue: "Slow search performance"

**Solution:** Add database indexes (Supabase):
```sql
CREATE INDEX idx_created_at ON ANALYSIS_RESULTS(created_at);
CREATE INDEX idx_video_name ON ANALYSIS_RESULTS(video_name);
```

---

## 📚 Related Documentation

- [Phase 5: AI Insights](./PHASE5_AI_INSIGHTS.md)
- [Phase 6: Chat Assistant](./PHASE6_CHAT.md)
- [Backend API Reference](./backendPRD.md)
- [Quick Start](../PHASE7_QUICKSTART.md)

---

**Phase 7 Complete!** 🎉  
Next: Phase 8 - Testing & Optimization

---

*Last Updated: November 7, 2024*  
*Version: 1.0.0*
