# Phase 5: AI-Powered Insights with Google Gemini

## 📋 Overview

Phase 5 introduces **AI-powered natural language insights** using Google Gemini, transforming raw crowd analytics data into actionable recommendations for hospital administrators.

### What's New in Phase 5

✅ **Gemini AI Integration**
- Natural language summary generation
- Context-aware staff recommendations  
- Bottleneck identification with explanations
- Priority action suggestions

✅ **Intelligent Fallback**
- Automatic rule-based mode when API unavailable
- Consistent output format regardless of mode
- No analysis failures due to AI service issues

✅ **Seamless Integration**
- AI insights generated automatically after analytics
- Optional API key configuration
- Enable/disable via API parameters

---

## 🏗️ Architecture

### Components Created

#### 1. **GeminiAssistant Service** (`app/services/gemini_assistant.py`)

Main AI service that:
- Configures Google Gemini API client
- Builds comprehensive prompts from analytics data
- Parses AI responses into structured format
- Provides rule-based fallback logic
- Handles errors gracefully

**Key Methods:**
```python
def generate_insights(analysis_results, include_recommendations=True) -> Dict
def _generate_ai_insights(stats, insights, enhanced, video_meta, include_recommendations) -> Dict
def _generate_rule_based_insights(stats, insights, enhanced, video_meta, include_recommendations) -> Dict
def _build_insights_prompt(stats, insights, enhanced, video_meta, include_recommendations) -> str
def _parse_ai_response(ai_text, stats, insights, enhanced) -> Dict
def get_model_info() -> Dict
```

#### 2. **VideoAnalysisService Integration** (`app/services/video_analysis.py`)

Enhanced to:
- Accept AI insights parameters in `__init__`
- Create `GeminiAssistant` instance if enabled
- Generate AI insights after enhanced analytics (Step 5.5)
- Add `ai_insights` to results dictionary
- Handle AI generation errors without failing analysis

**New Parameters:**
```python
enable_ai_insights: bool = True
gemini_api_key: Optional[str] = None
```

#### 3. **API Models & Endpoints** (`app/models.py`, `app/routers/analysis.py`)

Updated:
- `AnalysisRequest` model with `enable_ai_insights` and `gemini_api_key` fields
- `get_analysis_service()` to accept and pass AI parameters
- `run_video_analysis()` background task with AI configuration
- `start_analysis()` endpoint to include AI in status message

---

## 🔑 API Key Setup

### Option 1: Environment Variable (Recommended)

1. **Get API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Set Environment Variable:**

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

3. **Add to .env file (persistent):**
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048
```

### Option 2: API Parameter

Pass directly in API request:
```json
{
  "upload_id": "video-123",
  "enable_ai_insights": true,
  "gemini_api_key": "your_api_key_here"
}
```

⚠️ **Security Note:** Prefer environment variables over hardcoding keys in requests.

---

## 🚀 Usage

### 1. Python Service (Direct)

```python
from app.services.video_analysis import VideoAnalysisService
from pathlib import Path

# With Gemini API
service = VideoAnalysisService(
    frame_sample_rate=30,
    confidence_threshold=0.5,
    enable_ai_insights=True,
    gemini_api_key="your_key"  # Or None to use env var
)

results = service.analyze_video(
    video_path=Path("video.mp4"),
    save_detections=True
)

# Access AI insights
ai_insights = results.get("ai_insights", {})
print(ai_insights["ai_summary"])
print(ai_insights["key_findings"])
print(ai_insights["staff_suggestions"])
```

### 2. REST API

**Start Analysis with AI:**
```bash
curl -X POST "http://localhost:8000/api/analyze/video-123" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "video-123",
    "enable_ai_insights": true,
    "frame_sample_rate": 30,
    "confidence_threshold": 0.5
  }'
```

**Response:**
```json
{
  "analysis_id": "abc-def-ghi",
  "status": "processing",
  "message": "Video analysis started. AI-powered insights will be generated."
}
```

**Get Results:**
```bash
curl "http://localhost:8000/api/analyze/results/abc-def-ghi"
```

### 3. Test Script

```bash
# Set API key (optional)
export GEMINI_API_KEY="your_key"

# Run tests
python test_ai_insights.py
```

Tests include:
1. **Gemini AI Mode** (if key available)
2. **Rule-Based Fallback** (no key)
3. **AI Disabled Mode**

---

## 📊 AI Insights Output Format

### Response Structure

```json
{
  "ai_insights": {
    "ai_summary": "Executive summary (2-3 sentences)",
    "key_findings": [
      "Finding 1",
      "Finding 2",
      "Finding 3"
    ],
    "recommendations": [
      "Recommendation 1",
      "Recommendation 2"
    ],
    "staff_suggestions": {
      "suggested_nurses": 2,
      "reasoning": "Detailed explanation..."
    },
    "bottleneck_areas": [
      "Area 1 description",
      "Time period description"
    ],
    "priority_actions": [
      "Action 1",
      "Action 2"
    ],
    "generated_by": "gemini-ai",
    "generated_at": "2024-01-15T10:30:00"
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `ai_summary` | string | Executive summary of crowd situation |
| `key_findings` | array | 3-5 most important observations |
| `recommendations` | array | Long-term operational improvements |
| `staff_suggestions` | object | Staffing recommendations with reasoning |
| `bottleneck_areas` | array | Critical areas/times requiring attention |
| `priority_actions` | array | Immediate steps to take |
| `generated_by` | string | `"gemini-ai"` or `"rule-based"` |
| `generated_at` | string | ISO timestamp |

---

## 🧠 Prompt Engineering

### Prompt Structure

The AI prompt includes:

1. **Context Setting:**
   - Role: Healthcare operations analyst
   - Specialty: Emergency room flow optimization

2. **Video Information:**
   - Duration, resolution, frames analyzed
   - Processing configuration

3. **Crowd Statistics:**
   - Average/peak/min counts
   - Total detections

4. **Density Analysis:**
   - Density level and per sqm metrics
   - Severity score (1-5)

5. **Bottleneck Analysis:**
   - Number detected, threshold used
   - Critical periods with timestamps
   - Peak counts and durations

6. **Spatial Distribution:**
   - Distribution pattern
   - Hotspot zones

7. **Flow Metrics:**
   - Trend (increasing/stable/decreasing)
   - Variability and coefficient
   - Flow rate

8. **Expected Output:**
   - Executive summary
   - Key findings
   - Bottleneck areas
   - Staff recommendations with reasoning
   - Priority actions
   - Long-term recommendations

### Prompt Example

```
You are an expert healthcare operations analyst specializing in emergency room flow optimization.
Analyze the following hospital waiting area video analysis results and provide actionable insights.

VIDEO INFORMATION:
- Duration: 00:01:30
- Resolution: 1920x1080
- Total frames analyzed: 90

CROWD STATISTICS:
- Average people count: 12.5
- Peak people count: 18
- Minimum people count: 8
- Total detections: 1125

CROWD DENSITY ANALYSIS:
- Density level: High
- Density per sqm: 0.156
- Severity score: 4/5

[... additional sections ...]

Please provide:
1. **Executive Summary** (2-3 sentences): Overall assessment
2. **Key Findings** (3-5 bullet points): Most important observations
3. **Bottleneck Areas**: Specific locations or times requiring attention
4. **Staff Recommendations**: 
   - Current suggestion: 2 nurse(s)
   - Provide detailed reasoning for staffing levels
   - Consider peak times and bottleneck periods
5. **Priority Actions** (numbered list): Immediate steps to improve flow
6. **Long-term Recommendations**: Operational improvements

Format your response clearly with these sections. Be specific, actionable, and data-driven.
```

---

## 🔧 Configuration

### Environment Variables

```env
# Required for AI mode
GEMINI_API_KEY=your_api_key_here

# Optional configurations
GEMINI_MODEL=gemini-1.5-flash    # or gemini-1.5-pro
GEMINI_TEMPERATURE=0.7            # 0.0-1.0 (creativity)
GEMINI_MAX_TOKENS=2048            # Response length
```

### Model Options

| Model | Speed | Quality | Cost | Use Case |
|-------|-------|---------|------|----------|
| `gemini-1.5-flash` | ⚡ Fast | ✅ Good | 💰 Low | Production (recommended) |
| `gemini-1.5-pro` | 🐌 Slower | 🌟 Excellent | 💰💰 Higher | High-quality analysis |

### Temperature Settings

- **0.0-0.3:** Deterministic, factual responses
- **0.4-0.7:** Balanced creativity and consistency (recommended: **0.7**)
- **0.8-1.0:** More creative, varied responses

---

## 🛡️ Error Handling

### Graceful Degradation

The system never fails analysis due to AI issues:

```python
# AI generation error handling
try:
    ai_insights = self.gemini_assistant.generate_insights(results)
    results["ai_insights"] = ai_insights
except Exception as e:
    logger.error(f"Error generating AI insights: {e}")
    results["ai_insights"] = {
        "error": "AI insights generation failed",
        "message": str(e)
    }
```

### Fallback Modes

1. **Gemini API Available:** Uses AI generation
2. **No API Key:** Rule-based insights automatically
3. **API Error:** Catches exception, uses rule-based
4. **Parsing Error:** Returns raw AI text with basic structure
5. **Complete Failure:** Returns minimal insights from statistics

### Error Response

```json
{
  "ai_insights": {
    "error": "AI insights generation failed",
    "message": "API key invalid or quota exceeded"
  }
}
```

---

## 📈 Performance

### Timing Breakdown

| Step | Duration | % of Total |
|------|----------|-----------|
| Frame extraction | 10-20s | 30% |
| Person detection | 20-40s | 50% |
| Enhanced analytics | 1-2s | 3% |
| **AI insights** | **2-5s** | **7%** |
| Result compilation | 1s | 2% |
| **TOTAL** | **35-70s** | **100%** |

### Token Usage

Typical prompt + response:
- **Input:** ~800-1200 tokens
- **Output:** ~500-800 tokens
- **Total:** ~1300-2000 tokens per analysis

Cost estimate (gemini-1.5-flash):
- ~$0.0003-0.0005 per analysis
- Very cost-effective for production use

---

## 🧪 Testing

### Test Script: `test_ai_insights.py`

**Run all tests:**
```bash
python test_ai_insights.py
```

**Test Coverage:**

1. **Test 1: Gemini AI Mode**
   - Requires: `GEMINI_API_KEY` environment variable
   - Tests: API connection, prompt generation, response parsing
   - Output: Full AI insights with all sections

2. **Test 2: Rule-Based Fallback**
   - Requires: No API key
   - Tests: Fallback logic, consistent output format
   - Output: Rule-based insights

3. **Test 3: AI Disabled**
   - Tests: `enable_ai_insights=False` parameter
   - Output: No AI insights in results

**Expected Output:**
```
================================================================================
 PHASE 5: AI-POWERED INSIGHTS TEST SUITE
================================================================================

✅ GEMINI_API_KEY found in environment
   Key: AIzaSyBa...Xd9k

--------------------------------------------------------------------------------

================================================================================
Test 1: AI Insights with Google Gemini
================================================================================

📹 Analyzing video: sample_video.mp4
🤖 AI insights: Enabled
🔑 API key: Provided

[  0%] Extracting video metadata...
[ 10%] Extracting frames...
[ 50%] Detecting people in frames...
[ 92%] Generating enhanced analytics...
[ 95%] Generating AI insights...
[100%] Analysis complete!

================================================================================
✅ ANALYSIS COMPLETE
================================================================================

📊 Statistics:
   - Average people: 12.5
   - Peak count: 18
   - Crowd level: High

================================================================================
🤖 AI-POWERED INSIGHTS
================================================================================
Generated by: gemini-ai
Generated at: 2024-01-15T10:30:00

📝 Executive Summary:
   Analysis of 00:01:30 video reveals high crowd levels with an average of 12.5 people...

🔍 Key Findings (5):
   1. Average occupancy: 12.5 people (High density)
   2. Peak congestion: 18 people at 00:00:45
   3. Detected 3 bottleneck period(s) requiring attention
   4. Crowd concentration in: Center, Entry zones
   5. Crowd flow trend: Increasing with high variability

👥 Staff Recommendations:
   - Suggested nurses: 2
   - Reasoning: Based on average crowd of 12.5 people and high density level...

⚠️  Bottleneck Areas (3):
   1. Center zone
   2. Entry zone
   3. Time 00:00:40 - 00:00:50 (Critical)

🎯 Priority Actions (5):
   1. Deploy 2 nurse(s) to waiting area
   2. Focus resources during peak time: 00:00:45
   3. Station personnel in Center, Entry areas
   4. Review scheduling to accommodate increasing demand
   5. Implement flexible staffing model

💡 Recommendations (4):
   1. Increase staffing immediately to handle high crowd density
   2. Address bottleneck periods with additional staff during peak times
   3. Position staff strategically in high-density zones
   4. Prepare for continued growth - consider long-term capacity planning

================================================================================
```

---

## 🔍 Troubleshooting

### Issue: "No AI insights generated"

**Symptoms:**
- `ai_insights` missing from results
- No error message

**Solutions:**
1. Check `enable_ai_insights=True` in service initialization
2. Verify API key set: `echo $GEMINI_API_KEY`
3. Check logs for initialization messages
4. Ensure `google-generativeai` package installed

### Issue: "API key invalid"

**Symptoms:**
```json
{
  "error": "AI insights generation failed",
  "message": "API key not valid"
}
```

**Solutions:**
1. Verify key at: https://makersuite.google.com/app/apikey
2. Check no extra spaces: `export GEMINI_API_KEY="key"` (not `"key "`)
3. Regenerate API key if necessary
4. Ensure key has proper permissions

### Issue: "Rule-based fallback always used"

**Symptoms:**
- `generated_by: "rule-based"` even with API key

**Solutions:**
1. Check `google-generativeai` package version: `pip show google-generativeai`
2. Upgrade if needed: `pip install --upgrade google-generativeai`
3. Check network connectivity to Google APIs
4. Verify firewall allows HTTPS to `generativelanguage.googleapis.com`
5. Check Python logs for initialization errors

### Issue: "AI response too long"

**Symptoms:**
- Truncated responses
- Missing sections

**Solutions:**
1. Increase `GEMINI_MAX_TOKENS`: `export GEMINI_MAX_TOKENS=4096`
2. Use `gemini-1.5-pro` for longer outputs
3. Reduce prompt complexity (fewer analytics sections)

### Issue: "Slow AI generation"

**Symptoms:**
- AI step takes >10 seconds

**Solutions:**
1. Switch to `gemini-1.5-flash` (faster)
2. Reduce `max_output_tokens` to 1024-1536
3. Check network latency to Google servers
4. Consider caching for repeated analyses

---

## 📝 Example Use Cases

### 1. Real-time Monitoring Dashboard

Display AI summary for administrators:
```python
results = service.analyze_video(video_path)
summary = results["ai_insights"]["ai_summary"]
actions = results["ai_insights"]["priority_actions"]

# Show in dashboard
print(f"Current Situation: {summary}")
print("Recommended Actions:")
for i, action in enumerate(actions, 1):
    print(f"  {i}. {action}")
```

### 2. Staffing Automation

Auto-adjust staff based on AI recommendations:
```python
staff = results["ai_insights"]["staff_suggestions"]
nurses_needed = staff["suggested_nurses"]
reasoning = staff["reasoning"]

# Send alert to management
send_alert(
    level="info",
    message=f"Recommend {nurses_needed} nurses: {reasoning}"
)
```

### 3. Report Generation

Generate PDF reports with AI insights:
```python
ai_insights = results["ai_insights"]

report = PDFReport()
report.add_section("Executive Summary", ai_insights["ai_summary"])
report.add_list("Key Findings", ai_insights["key_findings"])
report.add_list("Recommendations", ai_insights["recommendations"])
report.save("crowd_analysis_report.pdf")
```

### 4. Historical Analysis

Compare AI insights over time:
```python
# Analyze multiple videos
insights_history = []
for video in videos:
    results = service.analyze_video(video)
    insights_history.append(results["ai_insights"])

# Trend analysis
avg_nurses = np.mean([i["staff_suggestions"]["suggested_nurses"] 
                      for i in insights_history])
print(f"Average staffing need: {avg_nurses:.1f} nurses")
```

---

## 🎯 Best Practices

### 1. API Key Management

✅ **DO:**
- Store in environment variables
- Use `.env` file (add to `.gitignore`)
- Rotate keys periodically
- Use separate keys for dev/prod

❌ **DON'T:**
- Hardcode in source code
- Commit to version control
- Share keys in chat/email
- Use same key across projects

### 2. Error Handling

✅ **DO:**
- Always have fallback logic
- Log errors for debugging
- Continue analysis on AI failure
- Provide meaningful error messages

❌ **DON'T:**
- Fail entire analysis on AI error
- Expose raw API errors to users
- Retry infinitely on quota errors
- Ignore error logs

### 3. Prompt Design

✅ **DO:**
- Include all relevant analytics data
- Specify expected output format
- Use clear section headers
- Request actionable recommendations

❌ **DON'T:**
- Send minimal data (poor insights)
- Use ambiguous instructions
- Expect specific JSON format (parse flexibly)
- Request medical diagnoses

### 4. Cost Optimization

✅ **DO:**
- Use `gemini-1.5-flash` for production
- Set reasonable `max_tokens` (2048)
- Cache repeated analyses
- Monitor token usage

❌ **DON'T:**
- Use `gemini-1.5-pro` unnecessarily
- Set `max_tokens` >4096
- Regenerate for same video
- Ignore quota limits

---

## 📚 API Reference

### GeminiAssistant Class

```python
class GeminiAssistant:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    )
```

### Methods

#### `generate_insights(analysis_results, include_recommendations=True) -> Dict`

Generate AI insights from analysis results.

**Parameters:**
- `analysis_results` (Dict): Complete video analysis results
- `include_recommendations` (bool): Include staff recommendations

**Returns:**
- Dict with `ai_summary`, `key_findings`, `recommendations`, etc.

**Example:**
```python
assistant = GeminiAssistant(api_key="your_key")
insights = assistant.generate_insights(results, include_recommendations=True)
```

#### `get_model_info() -> Dict`

Get configuration information.

**Returns:**
```python
{
    "model_name": "gemini-1.5-flash",
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "gemini_available": True,
    "model_initialized": True,
    "mode": "gemini-ai"
}
```

### Convenience Function

#### `generate_quick_insights(analysis_results, api_key=None) -> Dict`

Quick one-line insights generation.

**Example:**
```python
from app.services.gemini_assistant import generate_quick_insights

insights = generate_quick_insights(results, api_key="your_key")
```

---

## 🔗 Integration with Other Phases

### Phase 4 → Phase 5

Phase 5 consumes Phase 4 enhanced analytics:
- Crowd density metrics
- Bottleneck analysis
- Spatial distribution
- Flow metrics

All feed into AI prompt for comprehensive insights.

### Phase 5 → Phase 6

Phase 6 (AI Assistant Chat) will use Phase 5 insights:
- Answer questions about recommendations
- Explain reasoning behind staff suggestions
- Discuss bottleneck areas
- "What-if" scenario analysis

---

## 🚦 Next Steps

### Phase 6: AI Assistant Chat

Create interactive chat endpoint:
- `/api/chat` - Ask questions about analysis
- Conversation context management
- Reference Phase 5 insights in responses
- Handle follow-up questions

**Features:**
- "Why do you recommend 2 nurses?"
- "What if we only have 1 nurse available?"
- "How can we reduce bottlenecks?"
- "Show me the most critical time periods"

---

## 📖 Additional Resources

- **Google Gemini API Docs:** https://ai.google.dev/docs
- **API Key Management:** https://makersuite.google.com/app/apikey
- **Pricing:** https://ai.google.dev/pricing
- **Rate Limits:** https://ai.google.dev/docs/rate_limits

---

## ✅ Phase 5 Checklist

- [x] Created `GeminiAssistant` service
- [x] Integrated AI insights into analysis pipeline
- [x] Added API key configuration (env vars)
- [x] Built comprehensive prompt templates
- [x] Implemented rule-based fallback
- [x] Added error handling and graceful degradation
- [x] Updated API models and endpoints
- [x] Created test script with 3 modes
- [x] Documented architecture and usage
- [x] Validated with sample video

**Status:** ✅ Phase 5 Complete!

**Next:** Phase 6 - AI Assistant Chat Interface
