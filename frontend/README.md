# Discovery Engine UI

A modern React-based interface for the Discovery Engine research system. The UI connects directly to the FastAPI backend and provides real-time monitoring of the research process using Server-Sent Events.

## Getting Started

### Prerequisites

- **Node.js 16+** and npm
- **Python 3.10+** (for the backend)
- Discovery Engine backend running on `http://localhost:8000`

### Installation

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Backend must be installed. Ensure the backend is running:

```bash
# In a separate terminal, from the project root
python -m uvicorn discovery_engine.api:app --reload --host 0.0.0.0 --port 8000
```

### Development

1. Start the backend (if not already running):

```bash
python -m uvicorn discovery_engine.api:app --reload
```

2. In another terminal, start the frontend development server:

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:5173`

### Production Build

```bash
cd frontend
npm run build
npm run preview
```

## UI Architecture

### Components

- **ResearchWorkspace** — Main container managing job state and orchestration
- **ObjectiveInput** — Research objective entry and job creation
- **ResearchControls** — Job lifecycle controls (Start, Pause, Resume, Get Answer)
- **LiveStatus** — Real-time research metrics (elapsed time, source count, hypothesis count)
- **SourcePanel** — Display of all retrieved sources with metadata
- **HypothesisPanel** — Generated hypotheses with novelty assessment
- **EventTimeline** — Chronological event stream from backend
- **AnswerPanel** — Current best answer based on research

### API Integration

The UI connects to the Discovery Engine backend via:

- **REST endpoints** for job management and operations
- **Server-Sent Events (SSE)** for real-time event streaming
- **No mocking** — all data comes directly from the backend

### Key Features

✅ **Real-time Updates** — Live event stream shows research progress  
✅ **No Fabricated Data** — All sources, hypotheses, and events are real  
✅ **Evidence-Based** — Clearly distinguishes retrieved data from AI reasoning  
✅ **Responsive Design** — Works on desktop, tablet, and iPad  
✅ **Modular Architecture** — Easy to extend with new components  

## Usage Flow

1. **Create Research Job**
   - Enter objective: "Find a genuinely novel explanation for X"
   - Press "Create Research Job"

2. **Start Research**
   - Press "Start Research" to enter active mode
   - Research status changes to "RUNNING"

3. **Deep Discovery**
   - Enter search queries to retrieve sources from DuckDuckGo
   - System automatically analyzes sources with Groq AI
   - Hypotheses are generated and displayed in real-time

4. **Monitor Progress**
   - Watch event timeline for research actions
   - View all retrieved sources with URLs
   - See generated hypotheses with novelty status

5. **Get Quick Answer**
   - Press "Get Current Answer" to generate answer based on research so far
   - Research continues in background
   - Press again to update answer

6. **Pause/Resume**
   - Press "Pause" to pause Deep Discovery
   - Press "Resume" to continue

## Research Transparency

The UI clearly distinguishes:

- **Retrieved Evidence** — Real URLs from DuckDuckGo (marked with ✓)
- **AI Analysis** — Groq-generated insights (in hypotheses)
- **System Events** — All research actions with timestamps
- **Hypotheses** — Generated from evidence, never fabricated

Novelty status never shows "PROVEN ORIGINAL" or "100% ORIGINAL" — only honest assessments:
- PROBABLY KNOWN
- MODIFICATION
- NEW COMBINATION
- APPARENTLY NOVEL
- UNABLE TO DETERMINE

## API Endpoints Used

The frontend communicates with:

```
POST   /jobs                      → Create research job
GET    /jobs                      → List all jobs
GET    /jobs/{job_id}             → Get job details
POST   /jobs/{job_id}/start       → Start job
POST   /jobs/{job_id}/pause       → Pause job
POST   /jobs/{job_id}/resume      → Resume job
POST   /jobs/{job_id}/research    → Run research step
GET    /jobs/{job_id}/events      → Stream events (SSE)
POST   /jobs/{job_id}/answer      → Generate quick answer
```

## Environment Variables

Optional configuration:

```bash
REACT_APP_API_URL=http://localhost:8000
```

Default: `http://localhost:8000`

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Works well on iPad with responsive design.

## Development Notes

### Styling

- All styling is done with CSS files (no CSS-in-JS)
- Color scheme: Purple gradient (#667eea to #764ba2)
- Responsive breakpoints: 1400px, 1024px, 768px

### State Management

- React hooks for local component state
- Parent-child component communication via props
- Backend as source of truth for all data

### Real-time Updates

- Server-Sent Events (SSE) for live event stream
- Auto-refresh job data every 2 seconds
- Auto-scroll to latest event in timeline

## Troubleshooting

**Backend not found**
- Ensure backend is running on port 8000
- Check: `curl http://localhost:8000/health`

**No events showing**
- Verify SSE support in your browser
- Check browser console for errors
- Ensure job status is "running" before expecting events

**Styles not loading**
- Clear browser cache (Ctrl+Shift+Del)
- Restart dev server

## Future Enhancements

- [ ] Export research results as PDF
- [ ] Search history and saved jobs
- [ ] Advanced filtering and sorting
- [ ] Hypothesis comparison view
- [ ] Source credibility scoring
- [ ] Dark mode

## License

Same as Discovery Engine main project
