# Discovery Engine

A complete research and original-idea discovery system with an honest backend and modern React UI.

This project intentionally does **not** fabricate sources, URLs, or claim absolute originality. It keeps a strict separation between:

- **Retrieved Evidence** — Real URLs from DuckDuckGo, never fabricated
- **AI Analysis** — Groq-generated reasoning clearly labeled as such
- **Hypotheses** — Generated from evidence with confidence scores
- **Assumptions** — Tracked and validated against sources
- **Unverified Claims** — Never presented as proven facts

---

## 🚀 Quick Start

### Run Everything

```bash
# macOS / Linux
chmod +x start.sh
./start.sh

# Windows
start.bat

# Manual (separate terminals)
python -m uvicorn discovery_engine.api:app --reload  # Terminal 1: Backend
cd frontend && npm run dev                            # Terminal 2: Frontend
```

Then open:
- **UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health

---

## 📦 Installation

### Requirements

- Python 3.10+
- Node.js 16+ with npm
- (Optional) Groq API key for AI analysis

### Setup

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# (Optional) Set up Groq for AI analysis
export GROQ_API_KEY="your_key_here"
```

---

## 🧪 Test Backend

```bash
python -m pytest -q
# Expected: 22 passed
```

---

## 🎨 What's Included

### Backend (Python)

- ✅ **FastAPI HTTP API** with full CRUD endpoints
- ✅ **SQLite Persistence** with single-connection pattern
- ✅ **DuckDuckGo Integration** for real web search (no API key needed)
- ✅ **Groq AI Analysis** for hypothesis generation and novelty assessment
- ✅ **Provider Abstraction** allowing easy addition of new retrieval/AI sources
- ✅ **Server-Sent Events** for real-time research monitoring
- ✅ **Event System** with 21+ event types for complete research workflow
- ✅ **Evidence-First Architecture** — never fabricates sources

### Frontend (React)

- ✅ **ResearchWorkspace** — Main dashboard with all tools
- ✅ **LiveStatus Monitor** — Real-time research metrics
- ✅ **SourcePanel** — All retrieved sources with clickable URLs
- ✅ **HypothesisPanel** — Generated hypotheses with novelty status
- ✅ **EventTimeline** — Chronological research activity stream
- ✅ **AnswerPanel** — Quick answer based on current research
- ✅ **Responsive Design** — Works on desktop, tablet, iPad
- ✅ **Real API Integration** — No mock data, all from backend

---

## 📖 Usage Flow

### 1. Create Research Job

Enter objective:
```
Find a genuinely novel explanation for quantum decoherence
```

Press "Create Research Job"

### 2. Start Deep Discovery

Press "Start Research"
- System ready for research queries

### 3. Search and Analyze

Enter query: `quantum decoherence mechanisms`

System automatically:
- Retrieves top 10 results from DuckDuckGo
- Analyzes sources with Groq AI
- Generates hypotheses with confidence scores
- Assesses novelty (PROBABLY_KNOWN, MODIFICATION, APPARENTLY_NOVEL, etc.)
- Emits detailed events for each action

### 4. Monitor Progress

Watch in real-time:
- ✓ Sources retrieved and analyzed
- ✓ Claims extracted
- ✓ Hypotheses generated
- ✓ Novelty assessments
- ✓ Events in timeline

### 5. Get Quick Answer

Press "Get Current Answer" to generate:
- Best current answer based on research so far
- Research continues in background
- All state preserved

### 6. Pause/Resume or Continue

- **Pause** — Pause Deep Discovery
- **Resume** — Continue research
- **Another Query** — Run more searches
- **Get Answer** — Update answer

---

## 🔍 Architecture

### Backend Endpoints

```
POST   /jobs                      → Create research job
GET    /jobs                      → List all jobs
GET    /jobs/{job_id}             → Get job details
POST   /jobs/{job_id}/start       → Start job
POST   /jobs/{job_id}/pause       → Pause job
POST   /jobs/{job_id}/resume      → Resume job
POST   /jobs/{job_id}/research    → Run research step (search + analyze)
GET    /jobs/{job_id}/events      → Stream events (Server-Sent Events)
POST   /jobs/{job_id}/answer      → Generate quick answer
POST   /jobs/{job_id}/sources     → Add manual source
POST   /jobs/{job_id}/hypotheses  → Add manual hypothesis
```

### Research Pipeline

```
User Objective
    ↓
[ResearchJob Created]
    ↓
[User enters query]
    ↓
DuckDuckGo Search (real URLs, real results)
    ↓
Groq AI Analysis (if GROQ_API_KEY set, else template fallback)
    ↓
Hypothesis Generation (grounded in retrieved sources)
    ↓
Novelty Assessment (compared to sources)
    ↓
Events Emitted (search_started, source_found, hypothesis_generated, etc.)
    ↓
UI Updates (real-time via Server-Sent Events)
```

### Key Components

- **discovery_engine/models.py** — Domain models (ResearchJob, Source, Hypothesis, Event)
- **discovery_engine/retrieval.py** — Pluggable retrieval providers (DuckDuckGo, Static test)
- **discovery_engine/ai_providers.py** — AI provider abstraction (Groq implementation)
- **discovery_engine/analyzer.py** — Source analysis and hypothesis generation
- **discovery_engine/research_service.py** — Research orchestration logic
- **discovery_engine/api.py** — FastAPI HTTP interface
- **discovery_engine/database.py** — SQLite persistence
- **discovery_engine/events.py** — Event types and validation

---

## 🎯 Safety Guarantees

| Guarantee | Implementation |
|-----------|-----------------|
| **No Fabricated Sources** | URLs only exist when DuckDuckGo returns them |
| **No Fake Hypotheses** | Generated from actual retrieved evidence only |
| **No False Confidence** | Groq provides honest confidence scores |
| **No Proven Originality** | Never displays "100% ORIGINAL" or "PROVEN ORIGINAL" |
| **Transparent AI Reasoning** | AI analysis shown as research decision (not chain-of-thought) |
| **Evidence Tracking** | Every hypothesis linked to supporting sources |
| **Honest Novelty Assessment** | Only categorizes as: PROBABLY_KNOWN, MODIFICATION, NEW_COMBINATION, APPARENTLY_NOVEL, or UNABLE_TO_DETERMINE |

---

## ⚙️ Configuration

### Environment Variables

```bash
# Groq AI (optional, system falls back to template if not set)
export GROQ_API_KEY="gsk_your_key_here"

# Retrieval provider (default: duckduckgo)
export RETRIEVAL_PROVIDER_TYPE="duckduckgo"  # or "static" for testing

# Frontend API URL (default: http://localhost:8000)
export REACT_APP_API_URL="http://localhost:8000"
```

---

## 🧬 Development

### Running Tests

```bash
# All tests
python -m pytest -q

# Specific test file
python -m pytest tests/test_groq_research_flow.py -v

# With output
python -m pytest tests/test_foundation.py -v -s
```

### Backend Development

```bash
python -m uvicorn discovery_engine.api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Frontend Production Build

```bash
cd frontend
npm run build
npm run preview
```

---

## 📊 Test Results

```
22 passed, 3 warnings in 3.88s
```

Tests include:
- Job lifecycle (create, start, pause, resume, complete)
- Persistence (save/load jobs with all nested state)
- DuckDuckGo integration (real search, 10 results with valid URLs)
- Groq analysis (hypothesis generation, novelty assessment)
- Event emission (all event types validated)
- API endpoints (full CRUD)
- Full research flow end-to-end

---

## 🗺️ Project Structure

```
discovery-engine1726/
├── discovery_engine/          # Backend Python package
│   ├── models.py             # Domain models
│   ├── api.py                # FastAPI endpoints
│   ├── retrieval.py          # Retrieval provider abstraction
│   ├── ai_providers.py       # AI provider abstraction
│   ├── analyzer.py           # Source analysis
│   ├── research_service.py   # Business logic
│   ├── database.py           # SQLite persistence
│   ├── events.py             # Event definitions
│   └── __init__.py
├── frontend/                  # React UI
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api.js           # API client
│   │   ├── App.jsx          # Main app
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
├── tests/                     # Python tests
├── requirements.txt          # Backend dependencies
├── README.md                 # This file
├── start.sh                  # Start both (macOS/Linux)
└── start.bat                 # Start both (Windows)
```

---

## 🔮 What's Next

Potential enhancements:
- [ ] Add academic search provider (arXiv API)
- [ ] Add patent search provider (Google Patents)
- [ ] Cross-provider evidence comparison
- [ ] Iterative research refinement (AI suggests next query)
- [ ] Export results as PDF
- [ ] Search history and saved jobs
- [ ] Source credibility scoring
- [ ] Dark mode
- [ ] Advanced filtering and sorting

---

## 📝 Notes

- This is an **honest research system** — it does not pretend to prove originality
- All data comes from real sources or is clearly labeled as AI-generated
- Hypotheses are grounded in retrieved evidence
- Novelty is assessed honestly, never overstated
- Perfect for exploring ideas, not for proving they're original

---

## 🤝 Contributing

See frontend/README.md for UI development details.

---

## 📄 License

MIT
