# 🚀 Quick Start Guide

Get the Discovery Engine running in 5 minutes.

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Node.js 16+** with npm — [Download](https://nodejs.org/)
- Optional: **Groq API Key** — [Get free key](https://console.groq.com)

## Step 1: Install Dependencies

```bash
cd /workspaces/discovery-engine1726

# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

**Expected output**: No errors, all packages installed.

## Step 2: (Optional) Set Up Groq API

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

The system works without this but uses fallback templates for AI analysis.

## Step 3: Start Everything

### Option A: Automatic (Recommended)

```bash
# macOS / Linux
./start.sh

# Windows
start.bat
```

### Option B: Manual (Two Terminals)

**Terminal 1 - Backend:**
```bash
python -m uvicorn discovery_engine.api:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 4: Open the UI

Open your browser:

```
http://localhost:5173
```

You should see the Discovery Engine interface.

## Step 5: Try It Out

### 1. Enter Research Objective

Type into the objective box:
```
Find a genuinely novel explanation for X
```

Example: "Find a genuinely novel explanation for why social media affects attention spans"

### 2. Click "Create Research Job"

A new research job is created. You'll see:
- Status: QUEUED
- A set of control buttons

### 3. Click "Start Research"

Status changes to RUNNING. Now you can search.

### 4. Enter a Search Query

In the "Deep Discovery" section, type:
```
attention span social media effects
```

### 5. Click "Search"

Watch the magic happen:

1. **Sources appear** in the Sources panel (real URLs from DuckDuckGo)
2. **Hypotheses are generated** in the Hypotheses panel (from Groq AI or template)
3. **Events stream** in the Event Timeline (search_started → source_found → hypothesis_generated)
4. **Status updates** with counts of sources, hypotheses, etc.

### 6. Get an Answer

Click "Get Current Answer" to generate the best answer based on research so far.

### 7. Continue Researching

- Enter another query to search for more sources
- Click "Pause" to pause research
- Click "Resume" to continue
- Click "Get Current Answer" again to update the answer

---

## 🎯 What You'll See

### Sources Panel
```
📚 Sources [7]
  ▶ "Why Social Media Destroys Your Attention Span"
    Publisher: Medium | Relevance: 85%
    URL: https://medium.com/@user/...
```

Click to expand and see:
- Full URL (clickable)
- Author
- Publication date
- Claims extracted from the source

### Hypotheses Panel
```
💡 Hypotheses [2]
  ▶ "Social media algorithms are designed to exploit attention gaps..."
    ✅ ACTIVE
    🔀 NEW COMBINATION
    Confidence: 0.72
```

Shows hypothesis status and novelty:
- ✅ ACTIVE / ❌ REJECTED / 🔧 MODIFIED
- 🔁 PROBABLY KNOWN / 🔧 MODIFICATION / 🔀 NEW COMBINATION / ✨ APPARENTLY NOVEL

### Event Timeline
```
📋 Event Timeline [15]
  🚀 14:32:15 - Research started
  🔎 14:32:16 - Search started
  ⌨️  14:32:16 - Query issued: "attention span social media"
  📄 14:32:18 - Source found: "Why Social Media..."
  📥 14:32:18 - Source retrieved
  💾 14:32:18 - Source stored
  🧠 14:32:19 - Hypothesis generation started
  💡 14:32:20 - Hypothesis generated
```

### Current Answer
```
📝 Current Answer

Based on the research so far, social media likely affects 
attention spans through multiple mechanisms including...

Based on: 7 sources, 2 hypotheses
```

---

## 🔍 Behind the Scenes

### Real Data, Never Fabricated

✅ **Sources** come from actual DuckDuckGo search results
- Real URLs you can click and visit
- Real publication info
- Real claims from the sources

✅ **AI Analysis** is clearly AI-generated
- Not presented as fact
- Labeled as "hypothesis"
- Grounded in retrieved sources

✅ **Novelty Assessment** is honest
- Never says "100% ORIGINAL"
- Only: PROBABLY KNOWN, MODIFICATION, APPARENTLY NOVEL, or UNABLE TO DETERMINE

### Retrieval Flow

```
Your Query
    ↓
DuckDuckGo Search API
    ↓
10 Real Results with URLs
    ↓
Groq AI Analysis (if key available)
    ↓
Hypothesis Generated
    ↓
UI Shows Everything (no fabrication)
```

---

## 🛠️ Common Tasks

### Search Multiple Topics

1. Enter first query → See results
2. Enter second query → More results added
3. All results visible in Sources panel
4. System generates hypotheses from combined evidence

### Check If Backend is Running

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### View API Documentation

Open in browser:
```
http://localhost:8000/docs
```

Interactive Swagger documentation with all endpoints.

### Run Tests

```bash
python -m pytest -q
```

Expected: `22 passed`

### Clear All Research

Delete `discovery_engine.db` file (contains all saved jobs):

```bash
rm discovery_engine.db
```

Next time you start, you'll have a fresh database.

---

## ⚠️ Troubleshooting

### "Backend not found" Error

**Problem**: Frontend shows "Failed to load research job. Is the backend running?"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
python -m uvicorn discovery_engine.api:app --reload
```

### No Events Showing in Timeline

**Problem**: Event timeline is empty after searching.

**Possible causes**:
1. Browser doesn't support Server-Sent Events (try Chrome/Firefox)
2. Backend not returning events
3. Job status is not "RUNNING"

**Solution**:
- Ensure status is "RUNNING" (press "Start Research")
- Check browser console (F12) for errors
- Restart both servers

### "npm: command not found"

**Problem**: npm not installed or not in PATH

**Solution**:
```bash
# Check if Node is installed
node --version

# If not, install from https://nodejs.org/

# If installed but npm not found, reinstall Node
```

### "Cannot find module 'fastapi'"

**Problem**: Backend dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not set"

**Problem**: No AI analysis, uses template hypothesis instead

**Solution** (optional):
```bash
export GROQ_API_KEY="gsk_your_key_here"
```

If you don't have a key, sign up free at https://console.groq.com

---

## 📱 iPad / Mobile Usage

The UI is responsive and works on iPad:

1. Open http://localhost:5173 on iPad
2. All panels adapt to mobile layout
3. Scroll through Sources, Hypotheses, Events
4. Full functionality available

---

## 🎓 Understanding the Results

### Real vs Generated Content

```
✓ RETRIEVED (from DuckDuckGo)
  → Sources with real URLs
  → Claims extracted from articles
  → Author, publication date, etc.

🧠 AI-GENERATED (from Groq)
  → Hypotheses
  → Novelty assessments
  → Analysis summaries

💡 HYPOTHESIS (system generated)
  → Description (from Groq analysis)
  → Confidence score
  → Supporting sources (real URLs)
  → Novelty status (PROBABLY_KNOWN / APPARENTLY_NOVEL / etc.)
```

### Never Says "Original"

Discovery Engine is honest:

- ❌ NEVER: "This idea is 100% original"
- ❌ NEVER: "This idea has never existed before"
- ✅ INSTEAD: "APPARENTLY NOVEL based on analyzed sources"

Novelty is always qualified and uncertain.

---

## 🚀 Next Steps

1. **Explore Different Topics** — Try searches on different subjects
2. **Check Event Timeline** — See how research flows through system
3. **Review Hypotheses** — Expand each to see supporting sources
4. **Click URLs** — Verify sources are real and relevant
5. **Get Answers** — Click "Get Current Answer" multiple times
6. **Read API Docs** — Visit http://localhost:8000/docs

---

## 💡 Tips

- **Better searches = Better results** — Specific queries work best
- **Multiple searches = Richer analysis** — Search different angles
- **Real sources** — All URLs are clickable and real
- **Be patient with AI** — Groq takes ~2 seconds to analyze
- **Pause and review** — Use Pause button to examine results without continuing

---

## 📖 Learn More

- [Full README](README.md)
- [Frontend README](frontend/README.md)
- [API Documentation](http://localhost:8000/docs) (when running)

---

**Happy Researching!** 🔬
