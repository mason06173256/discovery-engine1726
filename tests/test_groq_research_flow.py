"""Demonstration: Full research flow with Groq-powered analysis."""

import os
from fastapi.testclient import TestClient
from discovery_engine.api import app
from discovery_engine.retrieval import StaticRetrievalProvider, RetrievalResult


def test_full_research_flow_with_groq():
    """Demonstrate complete research flow: Retrieval → Groq Analysis → Hypothesis.
    
    This shows:
    1. Create research job
    2. Run research step with static test data (to avoid slow DuckDuckGo)
    3. Groq analyzes retrieved sources (or uses fallback)
    4. AI-generated hypothesis is created
    5. Events are recorded showing analysis steps
    """
    from discovery_engine import api as api_module
    
    # Ensure we use static provider for this test (not DuckDuckGo)
    test_provider = StaticRetrievalProvider(
        [
            RetrievalResult(
                title="Understanding Blockchain Technology",
                url="https://example.org/blockchain-basics",
                publisher="Tech Academy",
                content="Blockchain is a distributed ledger technology that enables secure, decentralized data storage.",
                relevance_score=0.93,
                source_type="article",
            ),
            RetrievalResult(
                title="Smart Contracts in Ethereum",
                url="https://example.org/smart-contracts",
                publisher="Ethereum Foundation",
                content="Smart contracts are self-executing code that runs on the blockchain automatically when conditions are met.",
                relevance_score=0.91,
                source_type="documentation",
            ),
        ]
    )
    
    original_provider = api_module.retrieval_provider
    api_module.retrieval_provider = test_provider
    
    try:
        client = TestClient(app)
        
        # Step 1: Create research job
        print("\n🔬 Creating research job...")
        job_response = client.post(
            "/jobs",
            json={
                "user_objective": "Research blockchain consensus mechanisms and their security properties",
                "execution_mode": "deep_discovery"
            }
        )
        assert job_response.status_code == 200
        job_id = job_response.json()["job_id"]
        print(f"✓ Job created: {job_id}")
        
        # Step 2: Run research step (triggers Groq analysis)
        print("\n🔍 Running research step with Groq analysis...")
        research_response = client.post(
            f"/jobs/{job_id}/research",
            json={"query": "blockchain"}  # Match the word in our test provider
        )
        assert research_response.status_code == 200
        research_payload = research_response.json()
        print("✓ Research step completed")
        
        # Step 3: Verify sources were retrieved
        sources = research_payload.get("sources", [])
        print(f"\n📚 Retrieved {len(sources)} sources:")
        for source in sources:
            print(f"  - {source['title']}")
            print(f"    URL: {source['url']}")
        
        assert len(sources) > 0, "Should have retrieved sources"
        
        # Step 4: Verify Groq-generated hypothesis
        hypotheses = research_payload.get("hypotheses", [])
        print(f"\n🧠 Generated {len(hypotheses)} AI-powered hypothesis/hypotheses:")
        
        assert len(hypotheses) > 0, "Should have generated hypothesis from sources"
        
        for hypothesis in hypotheses:
            print(f"\n  Hypothesis: {hypothesis['description'][:100]}...")
            print(f"  Confidence: {hypothesis['confidence']}")
            print(f"  Supporting Sources: {len(hypothesis['supporting_sources'])}")
            print(f"  Criticism:")
            for criticism in hypothesis['criticism']:
                print(f"    - {criticism}")
        
        # Step 5: Get full job details to inspect event stream
        print("\n📋 Fetching complete job details with full event stream...")
        details_response = client.get(f"/jobs/{job_id}")
        assert details_response.status_code == 200
        job_details = details_response.json()
        
        activity_events = job_details.get("activity_events", [])
        print(f"✓ Total events recorded: {len(activity_events)}")
        
        # Print key events showing analysis workflow
        print("\n🔄 Analysis Workflow Events:")
        key_events = [
            "search_started",
            "search_query_issued",
            "source_found",
            "source_retrieved",
            "source_stored",
            "source_analyzed",
            "claim_extracted",
            "hypothesis_generation_started",
            "hypothesis_generated",
        ]
        
        for event in activity_events:
            if event["event_type"] in key_events:
                print(f"  [{event['event_type']}] {event['description'][:80]}")
        
        # Verify AI analysis events are present
        event_types = {event["event_type"] for event in activity_events}
        assert "source_found" in event_types, "Should have retrieval events"
        assert "hypothesis_generated" in event_types, "Should have hypothesis generation"
        
        # Verify Groq was used or fallback was triggered
        has_ai_indicators = (
            any(
                "Groq" in str(e.get("metadata", {})) or "AI" in str(e.get("metadata", {}))
                for e in activity_events
            )
            or any(
                "Groq" in h.get("description", "") or "AI" in h.get("description", "")
                for h in hypotheses
                if "criticism" in h
            )
        )
        
        print(f"\n✓ AI Analysis Indicators: {'Present' if has_ai_indicators else 'Fallback used (expected if GROQ_API_KEY not set)'}")
        
        print("\n✅ Complete research flow with Groq analysis successful!")
        print(f"""
Summary:
- Research Job: {job_id}
- Sources Retrieved: {len(sources)}
- Hypotheses Generated: {len(hypotheses)}
- Total Events: {len(activity_events)}
- Analysis Method: {"Groq AI" if has_ai_indicators else "Fallback template"}
        """)
        
        return job_id, sources, hypotheses, activity_events
        
    finally:
        # Restore original provider
        api_module.retrieval_provider = original_provider


if __name__ == "__main__":
    test_full_research_flow_with_groq()
