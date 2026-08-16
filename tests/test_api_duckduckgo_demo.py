"""Demonstration script: Research flow through FastAPI with real DuckDuckGo retrieval."""

import os
from fastapi.testclient import TestClient
from discovery_engine.api import app


def test_api_research_step_with_real_duckduckgo():
    """Demonstrate the full research flow through API using real DuckDuckGo search.
    
    This test shows:
    1. Create a research job via POST /jobs
    2. Run a research step via POST /jobs/{id}/research with real DuckDuckGo search
    3. Verify sources are stored with real URLs
    4. Verify events are recorded
    5. Get job details via GET /jobs/{id}
    """
    # Ensure we're using DuckDuckGo by default
    os.environ.pop("RETRIEVAL_PROVIDER_TYPE", None)
    
    client = TestClient(app)
    
    # Step 1: Create a research job
    job_response = client.post(
        "/jobs",
        json={
            "user_objective": "Research Python's asyncio programming model",
            "execution_mode": "deep_discovery"
        }
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["job_id"]
    print(f"✓ Created research job: {job_id}")
    
    # Step 2: Run research step with real DuckDuckGo search
    research_response = client.post(
        f"/jobs/{job_id}/research",
        json={"query": "Python asyncio concurrency"}
    )
    assert research_response.status_code == 200
    research_payload = research_response.json()
    print(f"✓ Research step completed")
    
    # Step 3: Verify sources were stored with real URLs
    sources = research_payload.get("sources", [])
    assert len(sources) > 0, "Should have retrieved sources from DuckDuckGo"
    print(f"✓ Retrieved {len(sources)} sources")
    
    for source in sources:
        assert source["url"].startswith("http"), f"Source URL must be valid: {source['url']}"
        assert source["title"], "Source must have title"
        assert source["relevant_score"] > 0, "Source must have relevance score"
        print(f"  - {source['title'][:60]}... ({source['url'][:50]}...)")
    
    # Step 4: Verify events were recorded
    hypotheses = research_payload.get("hypotheses", [])
    assert len(hypotheses) > 0, "Should have generated hypotheses from evidence"
    print(f"✓ Generated {len(hypotheses)} hypothesis/hypotheses from evidence")
    
    # Step 5: Get job details to see full event log
    details_response = client.get(f"/jobs/{job_id}")
    assert details_response.status_code == 200
    job_details = details_response.json()
    
    activity_events = job_details.get("activity_events", [])
    assert len(activity_events) > 0, "Should have recorded activity events"
    
    event_types = set()
    for event in activity_events:
        event_types.add(event["event_type"])
    
    print(f"✓ Recorded {len(activity_events)} activity events")
    print(f"  Event types: {', '.join(sorted(event_types))}")
    
    # Verify key events are present
    assert "search_started" in event_types, "Should have search_started event"
    assert "source_found" in event_types, "Should have source_found events"
    assert "hypothesis_generated" in event_types, "Should have hypothesis_generated event"
    
    print("\n✓ Full research flow through FastAPI with real DuckDuckGo search successful!")
    return job_id, sources, hypotheses, activity_events


if __name__ == "__main__":
    job_id, sources, hypotheses, events = test_api_research_step_with_real_duckduckgo()
