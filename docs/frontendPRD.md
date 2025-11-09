
# 🏥 **Chin  Frontend – Next.js PRD**

### 📄 **Product Requirement Document (Frontend)**

**Version:** 1.0
**Goal:** Enable hospital users to upload ER queue videos, view automated AI analysis results, and chat with an AI assistant (Gemini).

---

## 1️⃣ **Product Overview**

> **Chin  Frontend** provides a web interface for hospital managers to upload short ER queue videos, visualize analysis results, and interact with an AI assistant that explains and recommends actions.

**Core Objectives:**

* Upload a short ER video (waiting room or triage area).
* Display detected crowd metrics and bottleneck analysis results.
* Provide a chat interface with Gemini to ask follow-up “what-if” questions.

All of this runs **locally or on free hosting (e.g., Vercel)** and connects directly to your Python backend.

---

## 2️⃣ **User Flow**

```
1️⃣ User opens Chin  web app
     ↓
2️⃣ Uploads ER video (MP4, max 2 minutes)
     ↓
3️⃣ System uploads video → FastAPI backend processes it
     ↓
4️⃣ After analysis completes:
       - Shows total people detected
       - Highlights bottleneck stage
       - Shows AI summary insight
     ↓
5️⃣ User interacts with Gemini Chat Assistant:
       “What if I reduce staff to 2?”
       “When was the crowd highest?”
     ↓
6️⃣ Gemini replies with insights based on backend results
```

---

## 3️⃣ **Core Features**

| #     | Feature                       | Description                                         | Example UI / Function                             |
| ----- | ----------------------------- | --------------------------------------------------- | ------------------------------------------------- |
| **1** | 📁 **Video Upload Component** | Allows user to upload short MP4/AVI video           | “Upload Video” button + progress bar              |
| **2** | ⏳ **Processing Status**       | Shows upload progress & processing spinner          | “Analyzing video…” loader                         |
| **3** | 📊 **Result Dashboard**       | Displays backend analysis (JSON → charts + text)    | Total people, bottleneck area, recommended nurses |
| **4** | 🧠 **AI Insight Panel**       | Shows Gemini’s summary automatically after analysis | “The triage room was most crowded from 2–3 PM.”   |
| **5** | 💬 **AI Chat Interface**      | User can ask follow-up questions                    | “What if more patients arrive?”                   |
| **6** | 🧾 **History (optional)**     | Stores previous analyses locally                    | LocalStorage-based log (no backend DB)            |

---

## 4️⃣ **Interface Design (Simple MVP)**

### 🎨 **Layout Overview**

```
---------------------------------------------------------
|  🏥 Chin                                     |
---------------------------------------------------------
| [ Upload Video Button ]  [ Progress Bar ]             |
---------------------------------------------------------
| 📊 Analysis Results:                                  |
|   - Total People: 27                                  |
|   - Bottleneck: Triage Room                           |
|   - Suggested Nurses: 3                               |
|   - Summary: "Add 1 nurse to reduce wait time by 20%" |
---------------------------------------------------------
| 💬 Gemini Assistant:                                  |
|   [User:] What if there are only 2 nurses?            |
|   [Gemini:] Wait time may increase by 35%.            |
---------------------------------------------------------
```

---

## 5️⃣ **Technology Stack (Free & Beginner Friendly)**

| Layer          | Tech                                 | Why                                          |
| -------------- | ------------------------------------ | -------------------------------------------- |
| Framework      | **Next.js (latest)**                 | Free, easy deploy on Vercel, fast API routes |
| Styling        | **Tailwind CSS**                     | Easy responsive UI with prebuilt classes     |
| State Mgmt     | **React Hooks / Context API**        | Lightweight, no Redux needed                 |
| Charting       | **Recharts / Chart.js**              | Free and simple for small analytics          |
| File Upload    | **Axios / fetch API**                | To send videos to FastAPI backend            |
| Chat Interface | **React Chat UI / custom component** | Lightweight chat panel                       |
| AI API         | **Gemini API (via backend)**         | Simple integration for LLM responses         |
| Deployment     | **Vercel (Free)**                    | Deploy frontend easily                       |

---

## 6️⃣ **Frontend–Backend Integration**

| Endpoint            | Method | Description                                  |
| ------------------- | ------ | -------------------------------------------- |
| `/api/upload`       | `POST` | Upload video → Backend stores + processes    |
| `/api/status/{id}`  | `GET`  | Check progress (optional for longer runs)    |
| `/api/results/{id}` | `GET`  | Fetch JSON analysis results                  |
| `/api/chat`         | `POST` | Send user question to Gemini + return answer |

All endpoints call the Python FastAPI backend hosted locally or on Render/Heroku (free tiers).

---

## 7️⃣ **Frontend Folder Structure**

```
hospi_frontend/
│
├── pages/
│   ├── index.js              # Upload page + dashboard
│   ├── chat.js               # Gemini chat view
│
├── components/
│   ├── UploadBox.js          # Video upload UI
│   ├── ResultPanel.js        # Shows analysis metrics
│   ├── ChatAssistant.js      # Gemini chat interface
│   └── Loader.js             # Simple spinner
│
├── lib/
│   └── api.js                # Fetch & upload functions
│
├── styles/
│   └── globals.css           # Tailwind styles
│
└── package.json
```

---

## 8️⃣ **Example Dependencies (`package.json`)**

```json
{
  "dependencies": {
    "next": "latest",
    "react": "latest",
    "react-dom": "latest",
    "axios": "latest",
    "chart.js": "latest",
    "react-chat-ui": "latest",
    "tailwindcss": "latest"
  }
}
```

---

## 9️⃣ **Expected User Experience**

✅ Uploads video easily (drag & drop or click).
✅ Sees clear visual results after 10–15 seconds.
✅ Reads short AI-generated summary.
✅ Asks questions naturally to Gemini.
✅ All runs locally or with free-tier hosting.

---

## 🔟 **Success Metrics**

| Metric                                 | Target         |
| -------------------------------------- | -------------- |
| Upload success rate                    | ≥ 95%          |
| Video processing time display accuracy | ±2 seconds     |
| User satisfaction with chat responses  | ≥ 80% positive |
| Deployment ease (Vercel build success) | 100%           |

---

## 💡 **Why This Frontend Works**

* Minimalistic → perfect for MVP or demo.
* No complex database or auth needed.
* Connects easily to Python backend.
* All techs are **free**, **open-source**, and **well-documented**.
* Easy to expand later (real-time dashboard, camera streaming, etc.).

