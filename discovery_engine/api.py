from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .database import SQLiteResearchStore
from .models import Hypothesis, ResearchJob, Source
from .research import quick_answer
from .research_service import ResearchService
from .retrieval import get_configured_retrieval_provider

app = FastAPI(title="Discovery Engine API", version="0.1.0")
store = SQLiteResearchStore("discovery_engine.db")
service = ResearchService(store)
# Load retrieval provider from environment configuration
retrieval_provider = get_configured_retrieval_provider()


class JobCreateRequest(BaseModel):
    user_objective: str = Field(..., min_length=1)
    execution_mode: str = "quick_answer"


class SourceCreateRequest(BaseModel):
    title: str
    url: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    relevant_score: float = 0.0
    source_type: str = "unknown"
    claims_extracted: List[str] = Field(default_factory=list)


class HypothesisCreateRequest(BaseModel):
    description: str
    confidence: float = 0.0
    current_status: str = "active"
    novelty_status: str = "unable_to_determine"


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/jobs")
def create_job(payload: JobCreateRequest) -> Dict[str, Any]:
    job = service.create_job(payload.user_objective, payload.execution_mode)
    return {
        "job_id": job.job_id,
        "user_objective": job.user_objective,
        "execution_mode": job.execution_mode,
        "status": job.status,
    }


@app.get("/jobs")
def list_jobs() -> List[Dict[str, Any]]:
    jobs = []
    for job in service.store._connection.execute("SELECT job_id, user_objective, execution_mode, status FROM research_jobs").fetchall():
        jobs.append({
            "job_id": job["job_id"],
            "user_objective": job["user_objective"],
            "execution_mode": job["execution_mode"],
            "status": job["status"],
        })
    return jobs


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
    try:
        job = service.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {
        "job_id": job.job_id,
        "user_objective": job.user_objective,
        "execution_mode": job.execution_mode,
        "status": job.status,
        "sources": [source.__dict__ for source in job.sources],
        "hypotheses": [hypothesis.__dict__ for hypothesis in job.hypotheses],
        "activity_events": [event.__dict__ for event in job.activity_events],
    }


@app.post("/jobs/{job_id}/start")
def start_job(job_id: str) -> Dict[str, Any]:
    try:
        job = service.start_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {"job_id": job.job_id, "status": job.status}


@app.post("/jobs/{job_id}/pause")
def pause_job(job_id: str) -> Dict[str, Any]:
    try:
        job = service.pause_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {"job_id": job.job_id, "status": job.status}


@app.post("/jobs/{job_id}/resume")
def resume_job(job_id: str) -> Dict[str, Any]:
    try:
        job = service.resume_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {"job_id": job.job_id, "status": job.status}


@app.post("/jobs/{job_id}/sources")
def add_source(job_id: str, payload: SourceCreateRequest) -> Dict[str, Any]:
    try:
        source = Source(
            title=payload.title,
            url=payload.url,
            publisher=payload.publisher,
            author=payload.author,
            publication_date=payload.publication_date,
            relevant_score=payload.relevant_score,
            source_type=payload.source_type,
            claims_extracted=payload.claims_extracted,
        )
        job = service.add_source(job_id, source)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {"job_id": job.job_id, "sources": [item.__dict__ for item in job.sources]}


@app.post("/jobs/{job_id}/hypotheses")
def add_hypothesis(job_id: str, payload: HypothesisCreateRequest) -> Dict[str, Any]:
    try:
        hypothesis = Hypothesis(
            description=payload.description,
            confidence=payload.confidence,
            current_status=payload.current_status,
            novelty_status=payload.novelty_status,
        )
        job = service.add_hypothesis(job_id, hypothesis)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {"job_id": job.job_id, "hypotheses": [item.__dict__ for item in job.hypotheses]}


@app.post("/jobs/{job_id}/research")
def run_research_step(job_id: str, payload: Dict[str, str]) -> Dict[str, Any]:
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="A non-empty query is required.")
    try:
        job = service.run_deep_discovery_step(job_id, query, retrieval_provider)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {
        "job_id": job.job_id,
        "status": job.status,
        "sources": [source.__dict__ for source in job.sources],
        "hypotheses": [hypothesis.__dict__ for hypothesis in job.hypotheses],
    }


@app.get("/jobs/{job_id}/events")
def stream_job_events(job_id: str):
    try:
        job = service.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    def event_generator():
        for event in job.activity_events:
            payload = {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "description": event.description,
                "related_object_id": event.related_object_id,
                "metadata": event.metadata,
                "job_id": job.job_id,
            }
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/jobs/{job_id}/answer")
def answer_job(job_id: str) -> Dict[str, Any]:
    try:
        job = service.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    answer = quick_answer(job)
    return {"job_id": job.job_id, "answer": answer}
