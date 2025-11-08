

# 🏥 **HospiTwin Lite – Video-based Emergency Room Flow Analyzer**

### 📄 **Product Requirement Document (PRD)**

**Version:** 1.0
**Focus:** Backend (Python-based, simple, free tools)
**Goal:** Prototype / MVP for hackathon or internal demo

---

## 1️⃣ **Product Overview**

> **HospiTwin Lite** is a simplified AI backend that analyzes hospital emergency room (ER) queue videos to detect patient flow bottlenecks and recommend operational improvements using video analytics and AI insights.

**Core Idea:**
From a single video input (e.g., ER waiting area), the system uses **computer vision (YOLO + OpenCV)** to count people and detect crowded areas, then provides **AI-generated insights** using **Gemini** based on those metrics.

---

## 2️⃣ **Main Objectives**

* Automatically analyze ER crowd and patient flow from video.
* Detect **bottlenecks** and estimate **needed staff or resources**.
* Allow users to ask **“what if”** questions via an AI assistant (Gemini).
* Run locally or on any free-tier environment (no paid infrastructure).

---

## 3️⃣ **User Flow**

```
1️⃣ User uploads a video of ER queue
     ↓
2️⃣ System processes the video:
       - Detects number of people
       - Calculates average waiting density
       - Estimates bottleneck areas
     ↓
3️⃣ System generates a structured output (JSON):
       {
         "total_people": 23,
         "avg_density": "High",
         "suggested_nurses": 3,
         "bottleneck_area": "Triage Room"
       }
     ↓
4️⃣ AI (Gemini) reads the JSON → creates human-friendly insights:
       "The triage area is overcrowded. Consider adding 1 nurse."
     ↓
5️⃣ User can chat with the AI assistant:
       “What if there are only 2 nurses?”
     ↓
6️⃣ AI responds with new recommendations.
```

---

## 4️⃣ **Core Features**

| #     | Feature                           | Description                                                 | Technology                       |
| ----- | --------------------------------- | ----------------------------------------------------------- | -------------------------------- |
| **1** | 🧾 **Video Upload API**           | Upload ER queue video (MP4, AVI, etc.)                      | FastAPI + Python Multipart       |
| **2** | 🎥 **People Detection**           | Detects & counts people frame-by-frame                      | OpenCV + YOLOv8 (Ultralytics)    |
| **3** | 📊 **Crowd Analytics**            | Calculates crowd density & duration of congestion           | Pandas + NumPy                   |
| **4** | ⚙️ **Bottleneck Identification**  | Determines where & when congestion occurs                   | Simple threshold logic           |
| **5** | 💡 **AI Recommendation Engine**   | Suggests staff or flow changes                              | Rule-based + Gemini LLM          |
| **6** | 🧠 **AI Assistant Chat**          | User asks follow-up Qs, Gemini answers based on output data | Gemini API                       |
| **7** | 📁 **Result API**                 | Returns structured JSON of detected insights                | FastAPI endpoint `/results/{id}` |
| **8** | 🧮 **Metrics Storage**            | Saves analysis results and chat history                     | Supabase (PostgreSQL)            |

---

## 5️⃣ **Technical Architecture**

```
┌─────────────────────────────┐
│         Frontend UI         │
│  (upload video)  │
└──────────────┬──────────────┘
               │
         (Video Upload)
               │
┌──────────────▼──────────────┐
│         FastAPI App         │
│  /upload → process → result │
├──────────────┬──────────────┤
│ YOLOv8 Model │  OpenCV      │ ← detect persons
│ Pandas/NumPy │  Analyzer    │ ← compute metrics
└──────────────┴──────────────┘
               │
       (Generate JSON Output)
               │
┌──────────────▼──────────────┐
│ Gemini Insight Assistant    │
│ “Explain bottlenecks, Q&A”  │
└─────────────────────────────┘
```

---

## 6️⃣ **Technology Stack (Free & Simple)**

| Layer             | Tool / Library                       | Notes                             |
| ----------------- | ------------------------------------ | --------------------------------- |
| Backend Framework | **FastAPI**                          | Lightweight, async, easy docs     |
| File Upload       | **python-multipart**                 | For receiving video files         |
| Video Processing  | **OpenCV + MoviePy**                 | Extract frames, track people      |
| Object Detection  | **YOLOv8 (Ultralytics)**             | Free pretrained "person" model    |
| Data Analysis     | **Pandas, NumPy**                    | Calculate crowd & density metrics |
| AI Assistant      | **Gemini API (google-generativeai)** | Natural-language insights         |
| Database          | **Supabase (PostgreSQL)**            | Store results and chat history    |
| Server            | **Uvicorn**                          | Local or cloud run                |
| Env Management    | **venv / conda**                     | Clean dependency setup            |

---

## 7️⃣ **Example Output (JSON)**

```json
{
  "video_name": "ER_waitingroom.mp4",
  "total_people": 27,
  "avg_density": "High",
  "max_congestion_time": "02:15 - 03:30",
  "bottleneck_area": "Triage Room",
  "suggested_nurses": 3,
  "ai_summary": "The triage area is crowded between 2-3 PM. Adding 1 nurse could reduce wait time by 20%."
}
```

---

## 8️⃣ **AI Assistant Sample Q&A**

**User:** “What if we only have 2 nurses available?”
**AI (Gemini):**

> “If nurse count drops to 2, average patient wait time could increase by 35%. Suggest prioritizing triage for critical cases.”

**User:** “When was the crowd the highest?”
**AI:**

> “Between 14:00 and 15:30, with 27 people simultaneously in the triage area.”

---

## 9️⃣ **Success Metrics**

| Metric                             | Target                  |
| ---------------------------------- | ----------------------- |
| Average person detection accuracy  | ≥ 85%                   |
| Processing time per 1-min video    | ≤ 15 seconds            |
| AI insight relevance (manual eval) | ≥ 80% “useful” feedback |
| System uptime (local test)         | 100% for MVP            |

---

## 🔟 **Why This Version Works**

* ✅ **Minimal paid services required** (Supabase free tier available)
* ✅ **Scalable cloud database** with Supabase
* ✅ **Simple open-source tools** for processing
* ✅ **Actionable insights directly from video**
* ✅ **Real-time capable with PostgreSQL**
* ✅ **Beginner-friendly for Python devs**

