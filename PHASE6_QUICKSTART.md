# Phase 6: Chat Assistant - Quick Start Guide

## ⚡ 5-Minute Setup

Get your AI chat assistant running in minutes!

---

## 🎯 What You'll Build

An interactive chat interface that lets hospital administrators:
- Ask questions about crowd analysis
- Explore "what-if" scenarios
- Get actionable recommendations
- Understand bottlenecks and solutions

---

## 📋 Prerequisites

✅ Phase 1-5 completed (video analysis + AI insights)  
✅ Python 3.8+  
✅ Google Gemini API key (optional - works without)

---

## 🚀 Setup (2 minutes)

### Step 1: Get Gemini API Key (Optional)

```bash
# Visit: https://makersuite.google.com/app/apikey
# Copy your API key

# Set environment variable
export GEMINI_API_KEY='your_api_key_here'
```

**Note:** Works without API key using rule-based mode!

---

### Step 2: Verify Installation

```bash
# Check if chat router is loaded
python -c "from app.routers import chat; print('✅ Chat module ready')"

# Check if service is available
python -c "from app.services.chat_assistant import ChatAssistant; print('✅ ChatAssistant ready')"
```

---

## 🧪 Quick Test (1 minute)

### Option A: Test Script

```bash
python test_chat_assistant.py
```

**Expected Output:**
```
================================================================================
 PHASE 6: AI CHAT ASSISTANT TEST SUITE
================================================================================

✅ Test 1: Conversation Flow - PASS
✅ Test 2: Quick Chat - PASS
✅ Test 3: Scenarios - PASS
✅ Test 4: Context Retention - PASS
✅ Test 5: Error Handling - PASS
✅ Test 6: Configuration - PASS

ALL TESTS COMPLETE ✅
```

---

### Option B: Python Quick Test

```python
from app.services.video_analysis import VideoAnalysisService
from app.services.chat_assistant import quick_chat

# 1. Analyze video
analyzer = VideoAnalysisService()
results = analyzer.analyze_video("sample_video.mp4")

# 2. Ask a question
answer = quick_chat(results, "How many nurses do we need?")
print(answer)

# Output: "Based on your crowd analysis, 2 nurses are recommended..."
```

---

## 💬 Usage Examples

### Example 1: Basic Conversation

```python
from app.services.chat_assistant import ChatAssistant

# Initialize
assistant = ChatAssistant(gemini_api_key="your_key")

# Start conversation
response = assistant.start_conversation(analysis_results)
print(response['message'])

# Ask questions
msg = assistant.send_message("Why 2 nurses?")
print(msg['response'])
```

---

### Example 2: REST API

Start the server:
```bash
uvicorn app.main:app --reload
```

Use the API:
```bash
# 1. Start conversation
curl -X POST "http://localhost:8000/api/chat/start/123"

# 2. Send message
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": 123,
    "message": "Why do you recommend 2 nurses?",
    "history": []
  }'

# 3. Get conversation summary
curl "http://localhost:8000/api/chat/history/123"
```

---

### Example 3: Multi-Turn Conversation

```python
assistant = ChatAssistant()
assistant.start_conversation(results)

history = []

# Turn 1
msg1 = assistant.send_message("What's the peak time?", history)
history.append({"role": "user", "content": "What's the peak time?"})
history.append({"role": "assistant", "content": msg1['response']})

# Turn 2 (with context!)
msg2 = assistant.send_message("Why is it so busy then?", history)
# AI remembers the peak time from Turn 1!
```

---

## 🎯 Common Questions

### Q: "Why do you recommend X nurses?"

**Response Pattern:**
```
Based on your crowd analysis:
1. Peak count: {peak} people
2. Healthcare ratio: 1 nurse per 8-10 people
3. Bottleneck severity: {severity}
4. Safety requirements: {safety_factor}

Recommendation: {X} nurses ensures patient safety and service quality.
```

---

### Q: "What if we only have 1 nurse?"

**Response Pattern:**
```
With 1 nurse during peak ({peak} people):
- Risk: Ratio becomes 1:{ratio} (below standard)
- Impact: {wait_time} longer waits, patient dissatisfaction
- Mitigation:
  1. Focus nurse at bottleneck area
  2. Implement triage system
  3. Extend hours to spread load
  4. Consider part-time support
```

---

### Q: "How can we reduce bottlenecks?"

**Response Pattern:**
```
Bottleneck reduction strategies:
1. Increase staff during peak: {peak_time}
2. Position staff at hotspots: {zones}
3. Implement express lanes for simple cases
4. Adjust scheduling based on patterns
5. Use spatial data to optimize flow

Priority: Address {highest_severity} bottleneck first.
```

---

### Q: "When are peak times?"

**Response Pattern:**
```
Peak periods in your analysis:
- Primary peak: {time1} ({count1} people avg)
- Secondary peak: {time2} ({count2} people avg)
- Off-peak: {time3} ({count3} people avg)

Focus resources during primary peak for maximum impact.
```

---

## 🛠️ Configuration

### Basic Configuration

```python
# Default settings (works out of the box)
assistant = ChatAssistant()

# Custom configuration
assistant = ChatAssistant(
    gemini_api_key="your_key",
    model_name="gemini-1.5-flash"
)
```

---

### Environment Variables

```bash
# Optional - defaults work fine
export GEMINI_API_KEY='your_key'
export GEMINI_MODEL='gemini-1.5-flash'
export CHAT_TEMPERATURE='0.8'
export CHAT_MAX_TOKENS='1024'
```

---

## 📊 Response Modes

### 1. Gemini AI Mode (with API key)
- **Response Time:** 2-4 seconds
- **Quality:** High - context-aware, detailed
- **Use Case:** Production with budget

**Indicator:** `"generated_by": "gemini-ai"`

---

### 2. Rule-Based Mode (no API key)
- **Response Time:** 50-100 ms
- **Quality:** Good - pattern matching
- **Use Case:** Demo, testing, budget-free

**Indicator:** `"generated_by": "rule-based"`

---

### 3. Error Fallback Mode
- **Response Time:** 10-20 ms
- **Quality:** Basic - generic responses
- **Use Case:** Last resort

**Indicator:** `"generated_by": "error-fallback"`

---

## 🎨 Integration Examples

### Frontend Integration (React)

```javascript
// Start conversation
const startChat = async (analysisId) => {
  const response = await fetch(`/api/chat/start/${analysisId}`, {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data.message); // Welcome message
  return data.session_id;
};

// Send message
const sendMessage = async (analysisId, message, history) => {
  const response = await fetch('/api/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysisId, message, history })
  });
  const data = await response.json();
  return data.response;
};

// Usage
const sessionId = await startChat(123);
const answer = await sendMessage(123, "Why 2 nurses?", []);
```

---

### CLI Integration

```bash
#!/bin/bash
# chat.sh - Simple CLI chat interface

ANALYSIS_ID=123

# Start conversation
curl -s -X POST "http://localhost:8000/api/chat/start/$ANALYSIS_ID"

# Send message
read -p "You: " message
curl -s -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d "{\"analysis_id\": $ANALYSIS_ID, \"message\": \"$message\", \"history\": []}"
```

---

## 🔧 Troubleshooting

### Issue: "No API key provided"

**Fix:**
```bash
export GEMINI_API_KEY='your_key'
```
Or use rule-based mode (it still works!).

---

### Issue: "Session not found"

**Fix:**
```python
# Start conversation first
response = requests.post(f"/api/chat/start/{analysis_id}")
# Then send messages
```

---

### Issue: "Generic responses"

**Fix:**
- Verify analysis results are complete
- Pass conversation history for context
- Restart conversation if needed

---

### Issue: "Slow responses"

**Check:**
- Internet connection (for Gemini API)
- API rate limits
- Use rule-based mode for instant responses

---

## 📈 Performance Tips

### 1. Session Reuse
```python
# ❌ Don't create new assistant per message
assistant = ChatAssistant()  # Loses context!

# ✅ Reuse assistant for conversation
global_assistant = ChatAssistant()
```

---

### 2. History Management
```python
# ❌ Don't send full history every time (slow)
send_message(msg, history_all_1000_messages)

# ✅ Send recent history (last 10 messages)
send_message(msg, history[-10:])
```

---

### 3. Caching
```python
# Cache common questions
cache = {
    "why 2 nurses": "Based on healthcare ratios...",
    "peak time": "Peak period is 2-3 PM..."
}

if message in cache:
    return cache[message]
```

---

## 🎯 Real-World Scenarios

### Scenario 1: Morning Briefing

**Hospital administrator's morning routine:**

```python
# Check yesterday's analysis
results = get_analysis(yesterday_video_id)

# Quick questions
q1 = quick_chat(results, "What was peak time yesterday?")
q2 = quick_chat(results, "Any bottlenecks to address?")
q3 = quick_chat(results, "Staffing recommendation for today?")

# Email to team
email_body = f"""
Good morning team,

Yesterday's Analysis:
- Peak Time: {q1}
- Bottlenecks: {q2}
- Today's Staffing: {q3}

See full analysis: {dashboard_link}
"""
```

---

### Scenario 2: Real-Time Decision

**During shift, unexpected crowd:**

```
Admin: "Current crowd is 20 people. How many nurses needed?"
AI: "With 20 people, recommend 2-3 nurses. Your historical peak 
     was 15 people with 2 nurses. Consider adding 1 nurse now."

Admin: "What if I only have 2 available?"
AI: "With 2 nurses for 20 people:
     - Position 1 at reception bottleneck
     - Position 1 in waiting area hotspot
     - Implement triage to prioritize urgent cases
     - Monitor queue length every 15 minutes"
```

---

### Scenario 3: Budget Meeting

**Justifying staffing costs:**

```
CFO: "Why do we need 3 nurses? Can't we manage with 2?"

Admin: [Opens chat with last month's data]
       "What would happen if we reduced from 3 to 2 nurses?"

AI: "Analysis of last month:
     - Average peak: 25 people
     - With 3 nurses: 8:1 ratio ✅ (within standard)
     - With 2 nurses: 12.5:1 ratio ❌ (below standard)
     
     Impact of reduction:
     - 40% longer wait times
     - Increased patient complaints
     - Safety compliance risk
     - Staff burnout
     
     Recommendation: Maintain 3 nurses during peak hours,
     2 nurses during off-peak saves 25% vs full reduction."

[Admin shares screenshot in presentation]
```

---

## 🚀 Next Steps

### Phase 6 Complete ✅

You can now:
- ✅ Chat with analysis results
- ✅ Explore scenarios
- ✅ Get recommendations
- ✅ Understand bottlenecks

### Phase 7: Results & Storage API

Next features:
- 📊 List all analyses
- 🔍 Search and filter
- 📄 Export to PDF/JSON
- 📈 Historical trends
- 🗃️ Chat history persistence

---

## 📚 Resources

### Documentation
- [Full Phase 6 Documentation](./docs/PHASE6_CHAT.md)
- [API Reference](./docs/backendPRD.md)
- [Phase 5: AI Insights](./docs/PHASE5_AI_INSIGHTS.md)

### Test Files
- `test_chat_assistant.py` - Comprehensive test suite
- `app/services/chat_assistant.py` - Service implementation
- `app/routers/chat.py` - API endpoints

### Support
- Check logs: `tail -f app.log`
- Test endpoint: `curl http://localhost:8000/api/chat/sessions`
- Validate setup: `python test_chat_assistant.py`

---

## 💡 Pro Tips

### Tip 1: Start Simple
```python
# Begin with quick_chat for testing
answer = quick_chat(results, "Staffing recommendation?")
# Then upgrade to full conversation when needed
```

---

### Tip 2: Use Rule-Based for Demos
```python
# No API key needed for demos!
assistant = ChatAssistant()  # Works instantly
# Fast responses, no costs
```

---

### Tip 3: Preset Questions
```python
# Provide users with suggested questions
suggestions = [
    "Why do you recommend X nurses?",
    "What if we only have 1 nurse?",
    "When are the peak times?",
    "How can we reduce bottlenecks?",
    "Where should we position staff?"
]
```

---

### Tip 4: Context Retention
```python
# Always pass history for follow-ups
msg1 = send_message("What's the peak time?", [])
msg2 = send_message("Why then?", history)  # Remembers context!
```

---

### Tip 5: Batch Analysis
```python
# Analyze multiple videos, chat with each
for video_id in video_ids:
    results = analyze_video(video_id)
    summary = quick_chat(results, "Key findings?")
    report.append(summary)
```

---

## 🎓 Summary

**Phase 6** turns complex data into conversations! 

✅ **Easy Setup** - 5 minutes to running chat  
✅ **No API Required** - Rule-based mode works great  
✅ **Natural Language** - Ask questions like a human  
✅ **Context-Aware** - Remembers conversation flow  
✅ **Production Ready** - RESTful API with error handling  

**Cost:** ~$0.002 per 10-turn conversation (with API)  
**Speed:** 2-4s (AI) or 50ms (rule-based)  
**Accuracy:** High with comprehensive context  

---

**Ready to chat?** Run `python test_chat_assistant.py` 🚀

---

*Last Updated: January 15, 2024*  
*Version: 1.0.0*  
*Next: Phase 7 - Results & Storage API*
