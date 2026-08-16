from discovery_engine.models import ResearchJob, Source, Hypothesis
from discovery_engine.events import Event
from discovery_engine.database import SQLiteResearchStore
from discovery_engine.ai_providers import GroqProvider
from discovery_engine.research import quick_answer
from discovery_engine.research_service import ResearchService
from discovery_engine.retrieval import RetrievalResult, StaticRetrievalProvider
from fastapi.testclient import TestClient
from discovery_engine.api import app


def test_research_job_tracks_core_fields():
    job = ResearchJob(
        user_objective="Find a way to improve retrieval for long-running research tasks.",
        execution_mode="quick_answer",
    )

    assert job.job_id
    assert job.user_objective.startswith("Find")
    assert job.status == "queued"
    assert job.sources == []
    assert job.hypotheses == []
    assert job.activity_events == []


def test_event_and_source_models_are_structured():
    event = Event(
        event_type="research_started",
        description="Research job started.",
        metadata={"mode": "quick_answer"},
    )

    source = Source(
        title="Sample retrieval",
        url="https://example.org/article",
        publisher="Example Press",
        retrieval_timestamp="2026-01-01T00:00:00Z",
        relevant_score=0.92,
        source_type="article",
        claims_extracted=["Evidence exists."],
    )

    assert event.event_type == "research_started"
    assert event.metadata["mode"] == "quick_answer"
    assert source.url.startswith("https://")
    assert source.relevant_score == 0.92


def test_quick_answer_uses_existing_research_state():
    job = ResearchJob(
        user_objective="Evaluate a possible AI-assisted discovery workflow.",
        execution_mode="quick_answer",
    )
    source = Source(
        title="Evidence summary",
        url="https://example.org/evidence",
        publisher="Example Press",
        retrieval_timestamp="2026-01-01T00:00:00Z",
        relevant_score=0.8,
        source_type="article",
        claims_extracted=["The current workflow depends on retrieved evidence."],
    )
    hypothesis = Hypothesis(
        description="A structured evidence-first loop improves decision quality.",
        supporting_sources=[source.source_id],
        novelty_status="modification",
        confidence=0.74,
        current_status="active",
    )
    job.sources.append(source)
    job.hypotheses.append(hypothesis)

    answer = quick_answer(job)

    assert "evidence-first" in answer.lower()
    assert "modification" in answer.lower()


def test_sqlite_store_persists_job_and_event():
    store = SQLiteResearchStore(":memory:")
    job = ResearchJob(
        user_objective="Track a basic research iteration.",
        execution_mode="deep_discovery",
    )

    store.save_job(job)
    store.record_event(job.job_id, Event(event_type="search_started", description="Search started."))

    saved = store.load_job(job.job_id)

    assert saved.user_objective == "Track a basic research iteration."
    assert saved.activity_events[0].event_type == "search_started"


def test_groq_provider_requires_env_key():
    provider = GroqProvider()
    assert provider.provider_name == "groq"

    try:
        provider.generate_text("hello")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError when GROQ_API_KEY is missing")


def test_research_service_creates_pauses_and_resumes_jobs():
    store = SQLiteResearchStore(":memory:")
    service = ResearchService(store)

    job = service.create_job("Study a better evidence workflow.", "deep_discovery")
    assert job.status == "queued"

    service.start_job(job.job_id)
    assert service.get_job(job.job_id).status == "running"

    service.pause_job(job.job_id)
    assert service.get_job(job.job_id).status == "paused"

    service.resume_job(job.job_id)
    assert service.get_job(job.job_id).status == "running"


def test_research_service_persists_sources_and_hypotheses():
    service = ResearchService(SQLiteResearchStore(":memory:"))
    job = service.create_job("Find a practical research loop.")

    source = Source(
        title="Workflow base",
        url="https://example.org/workflow-base",
        publisher="Example Press",
        retrieval_timestamp="2026-02-01T00:00:00Z",
        relevant_score=0.87,
        source_type="article",
        claims_extracted=["Evidence should remain explicit."],
    )
    hypothesis = Hypothesis(
        description="Explicit evidence tracking keeps the loop honest.",
        supporting_sources=[source.source_id],
        confidence=0.73,
    )

    service.add_source(job.job_id, source)
    service.add_hypothesis(job.job_id, hypothesis)

    saved = service.get_job(job.job_id)
    assert len(saved.sources) == 1
    assert len(saved.hypotheses) == 1
    assert saved.hypotheses[0].description == hypothesis.description


def test_api_job_lifecycle_and_state_updates():
    client = TestClient(app)

    response = client.post(
        "/jobs",
        json={"user_objective": "Improve the evidence-first workflow.", "execution_mode": "deep_discovery"},
    )
    assert response.status_code == 200
    job = response.json()
    job_id = job["job_id"]

    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["user_objective"] == "Improve the evidence-first workflow."

    start_response = client.post(f"/jobs/{job_id}/start")
    assert start_response.status_code == 200
    assert start_response.json()["status"] == "running"

    source_payload = {
        "title": "Workflow design patterns",
        "url": "https://example.org/patterns",
        "publisher": "Example Press",
        "relevant_score": 0.91,
        "source_type": "article",
        "claims_extracted": ["Clear evidence boundaries help research quality."],
    }
    source_response = client.post(f"/jobs/{job_id}/sources", json=source_payload)
    assert source_response.status_code == 200
    assert len(source_response.json()["sources"]) == 1

    hypothesis_payload = {
        "description": "Evidence boundaries improve trust in research outputs.",
        "confidence": 0.76,
        "current_status": "active",
        "novelty_status": "modification",
    }
    hypothesis_response = client.post(f"/jobs/{job_id}/hypotheses", json=hypothesis_payload)
    assert hypothesis_response.status_code == 200
    assert len(hypothesis_response.json()["hypotheses"]) == 1

    answer_response = client.post(f"/jobs/{job_id}/answer")
    assert answer_response.status_code == 200
    assert "evidence" in answer_response.json()["answer"].lower()


def test_retrieval_provider_and_deep_discovery_step():
    provider = StaticRetrievalProvider(
        [
            RetrievalResult(
                title="Evidence first systems",
                url="https://example.org/evidence-first",
                publisher="Research Lab",
                content="Explicit evidence boundaries reduce unsupported claims.",
                relevance_score=0.92,
                source_type="article",
            )
        ]
    )
    results = provider.search("evidence first systems")
    assert len(results) == 1
    assert results[0].url.startswith("https://")

    service = ResearchService(SQLiteResearchStore(":memory:"))
    job = service.create_job("Find a better evidence-first research workflow.", "deep_discovery")
    next_job = service.run_deep_discovery_step(job.job_id, "evidence first systems", provider)

    assert next_job.status in {"running", "paused", "completed"}
    assert len(next_job.sources) >= 1
    assert len(next_job.hypotheses) >= 1


def test_api_lists_jobs_and_runs_research_step():
    from discovery_engine import api
    
    # Configure the API's retrieval provider with test data for this test
    test_provider = StaticRetrievalProvider(
        [
            RetrievalResult(
                title="Evidence first systems",
                url="https://example.org/evidence-first",
                publisher="Research Lab",
                content="Explicit evidence boundaries reduce unsupported claims.",
                relevance_score=0.92,
                source_type="article",
            )
        ]
    )
    original_provider = api.retrieval_provider
    api.retrieval_provider = test_provider
    
    try:
        client = TestClient(app)

        first = client.post(
            "/jobs",
            json={"user_objective": "Improve evidence-first review in research tasks.", "execution_mode": "deep_discovery"},
        )
        assert first.status_code == 200
        job_id = first.json()["job_id"]

        list_response = client.get("/jobs")
        assert list_response.status_code == 200
        assert any(item["job_id"] == job_id for item in list_response.json())

        research_response = client.post(
            f"/jobs/{job_id}/research",
            json={"query": "evidence first systems"},
        )
        assert research_response.status_code == 200
        payload = research_response.json()
        assert payload["job_id"] == job_id
        assert len(payload["sources"]) >= 1
        assert len(payload["hypotheses"]) >= 1
    finally:
        # Restore the original provider
        api.retrieval_provider = original_provider


def test_api_streams_job_events():
    client = TestClient(app)
    job = client.post(
        "/jobs",
        json={"user_objective": "Track research progress live.", "execution_mode": "quick_answer"},
    ).json()
    job_id = job["job_id"]

    client.post(f"/jobs/{job_id}/start")
    with client.stream("GET", f"/jobs/{job_id}/events") as response:
        body = response.read()

    assert response.status_code == 200
    assert b"research_started" in body
    assert b"job_id" in body


def test_deep_discovery_cycle_generates_critiqued_hypotheses():
    provider = StaticRetrievalProvider(
        [
            RetrievalResult(
                title="Evidence first systems",
                url="https://example.org/evidence-first",
                publisher="Research Lab",
                content="Explicit evidence boundaries reduce unsupported claims.",
                relevance_score=0.92,
                source_type="article",
            )
        ]
    )
    service = ResearchService(SQLiteResearchStore(":memory:"))
    job = service.create_job("Build a better evidence-first workflow.", "deep_discovery")

    updated = service.run_full_research_cycle(job.job_id, "evidence first systems", provider)

    assert len(updated.sources) >= 1
    assert len(updated.hypotheses) >= 1
    assert updated.hypotheses[0].novelty_status in {"modification", "probably_known", "unable_to_determine"}
    assert updated.hypotheses[0].criticism
