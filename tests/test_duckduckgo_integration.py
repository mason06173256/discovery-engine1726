"""Integration test demonstrating real DuckDuckGo retrieval through the API."""

from discovery_engine import ResearchService, DuckDuckGoRetrievalProvider
from discovery_engine.database import SQLiteResearchStore


def test_duckduckgo_retrieval_direct():
    """Test that DuckDuckGo provider performs real web search and stores results."""
    provider = DuckDuckGoRetrievalProvider()
    
    # Perform a real search
    results = provider.search("Python programming language")
    
    # Verify results are real (not fabricated)
    assert len(results) > 0, "DuckDuckGo should return search results"
    
    # Verify each result has required fields
    for result in results:
        assert result.title, "Each result must have a title"
        assert result.url, "Each result must have a URL"
        assert result.url.startswith("http"), "URL must be a valid web address"
        assert result.source_type == "web_search_result", "Source type must indicate it's from web search"
        assert result.publisher == "DuckDuckGo", "Publisher must be DuckDuckGo"
        assert result.retrieval_timestamp, "Retrieval timestamp must be recorded"
        assert result.content, "Content/snippet must be present"


def test_research_service_with_duckduckgo():
    """Test that research service properly stores DuckDuckGo results in database."""
    service = ResearchService(SQLiteResearchStore(":memory:"))
    provider = DuckDuckGoRetrievalProvider()
    
    # Create a research job
    job = service.create_job("Find information about web search technologies", "deep_discovery")
    
    # Run research step with real DuckDuckGo search
    updated_job = service.run_deep_discovery_step(job.job_id, "web search", provider)
    
    # Verify sources were stored
    assert len(updated_job.sources) > 0, "DuckDuckGo results should be stored as sources"
    
    # Verify each source has real data (not fabricated)
    for source in updated_job.sources:
        assert source.url, "Source URL must be present"
        assert source.url.startswith("http"), "Source URL must be valid"
        assert source.title, "Source title must be present"
        assert source.retrieval_timestamp, "Retrieval timestamp must be recorded"
    
    # Verify events were recorded
    assert len(updated_job.activity_events) > 0, "Research step should emit events"
    
    # Check for expected event types
    event_types = {event.event_type for event in updated_job.activity_events}
    assert "search_started" in event_types, "Should have search_started event"
    assert "source_found" in event_types, "Should have source_found event"
    assert "hypothesis_generated" in event_types, "Should have hypothesis_generated event"
    
    # Verify hypothesis was generated from actual evidence
    assert len(updated_job.hypotheses) > 0, "Hypothesis should be generated from retrieved evidence"
    hypothesis = updated_job.hypotheses[0]
    assert hypothesis.supporting_sources, "Hypothesis should reference supporting sources"
    assert hypothesis.description, "Hypothesis should have a description"


if __name__ == "__main__":
    test_duckduckgo_retrieval_direct()
    print("✓ DuckDuckGo direct retrieval test passed")
    
    test_research_service_with_duckduckgo()
    print("✓ Research service with DuckDuckGo test passed")
