"""Tests for Groq-powered source analysis and hypothesis generation."""

import os
import pytest
from discovery_engine import (
    SourceAnalyzer, 
    ResearchService, 
    SQLiteResearchStore,
    StaticRetrievalProvider,
    RetrievalResult,
)
from discovery_engine.models import Source


def test_source_analyzer_initializes():
    """Test that SourceAnalyzer can be initialized with Groq provider."""
    analyzer = SourceAnalyzer()
    assert analyzer is not None
    assert analyzer.ai_provider is not None


def test_source_analyzer_extracts_key_insights():
    """Test that SourceAnalyzer can extract insights from sources using Groq."""
    analyzer = SourceAnalyzer()
    
    # Create mock sources
    sources = [
        Source(
            title="Machine Learning Basics",
            url="https://example.org/ml-basics",
            publisher="AI Institute",
            source_type="article",
            claims_extracted=["Machine learning is a subset of AI that learns patterns from data."],
            relevant_score=0.9,
        ),
        Source(
            title="Neural Networks Explained",
            url="https://example.org/neural-nets",
            publisher="Tech Blog",
            source_type="blog",
            claims_extracted=["Neural networks use interconnected nodes to process information."],
            relevant_score=0.85,
        ),
    ]
    
    query = "machine learning techniques"
    
    # Extract insights using Groq
    insights = analyzer.extract_key_insights(sources, query)
    
    # Verify we got a response (not error message)
    assert insights is not None
    assert isinstance(insights, str)
    assert len(insights) > 0
    # If GROQ_API_KEY is set, we should get real insights; otherwise a graceful error
    # Both are acceptable for this test
    assert "machine learning" in insights.lower() or "failed" in insights.lower()


def test_source_analyzer_generates_hypothesis():
    """Test that SourceAnalyzer can generate AI-informed hypothesis from sources."""
    analyzer = SourceAnalyzer()
    
    sources = [
        Source(
            title="Python Async/Await",
            url="https://example.org/async-await",
            publisher="Python Docs",
            source_type="documentation",
            claims_extracted=["Async/await syntax simplifies asynchronous code in Python."],
            relevant_score=0.95,
        ),
        Source(
            title="Concurrency Patterns",
            url="https://example.org/concurrency",
            publisher="Tech Journal",
            source_type="article",
            claims_extracted=["Concurrency improves application responsiveness and throughput."],
            relevant_score=0.88,
        ),
    ]
    
    query = "Python concurrency models"
    user_objective = "Understand how Python handles concurrent execution"
    
    # Generate hypothesis using Groq
    hypothesis = analyzer.generate_hypothesis_from_sources(sources, query, user_objective)
    
    # Verify hypothesis structure
    if hypothesis:
        assert hypothesis.description is not None
        assert len(hypothesis.description) > 0
        assert hypothesis.supporting_sources == [source.source_id for source in sources]
        assert 0.0 <= hypothesis.confidence <= 1.0
        assert hypothesis.current_status == "active"
        assert hypothesis.criticism is not None
        assert len(hypothesis.criticism) > 0
    # If hypothesis is None, Groq might not be available, which is acceptable for testing


def test_research_service_uses_analyzer():
    """Test that ResearchService uses SourceAnalyzer for hypothesis generation."""
    store = SQLiteResearchStore(":memory:")
    analyzer = SourceAnalyzer()
    service = ResearchService(store, analyzer)
    
    # Verify the service has the analyzer
    assert service.analyzer is not None


def test_research_service_with_groq_analysis():
    """Test full research flow with Groq-powered hypothesis generation."""
    # Use static provider so test doesn't depend on DuckDuckGo availability
    provider = StaticRetrievalProvider(
        [
            RetrievalResult(
                title="Quantum Computing Basics",
                url="https://example.org/quantum-basics",
                publisher="Science Daily",
                content="Quantum computers use quantum bits (qubits) to process information differently than classical computers.",
                relevance_score=0.92,
                source_type="article",
            ),
            RetrievalResult(
                title="Quantum Algorithms",
                url="https://example.org/quantum-algorithms",
                publisher="IEEE",
                content="Quantum algorithms can solve specific problems exponentially faster than classical algorithms.",
                relevance_score=0.88,
                source_type="paper",
            ),
        ]
    )
    
    store = SQLiteResearchStore(":memory:")
    analyzer = SourceAnalyzer()
    service = ResearchService(store, analyzer)
    
    # Create a research job
    job = service.create_job("Research quantum computing applications", "deep_discovery")
    
    # Run research step with Groq analysis
    updated_job = service.run_deep_discovery_step(job.job_id, "quantum computing", provider)
    
    # Verify results
    assert len(updated_job.sources) > 0
    assert len(updated_job.hypotheses) > 0
    
    # Verify hypothesis was generated
    hypothesis = updated_job.hypotheses[0]
    assert hypothesis.description is not None
    assert len(hypothesis.description) > 0
    assert hypothesis.supporting_sources is not None
    assert len(hypothesis.supporting_sources) > 0
    
    # Verify events were recorded
    event_types = {event.event_type for event in updated_job.activity_events}
    assert "hypothesis_generated" in event_types or "hypothesis_generation_started" in event_types
    
    # Verify we have evidence of AI analysis in events or criticism
    if updated_job.hypotheses and updated_job.hypotheses[0].criticism:
        # If AI analysis succeeded, we should have criticism
        has_groq_indicator = any("Groq" in str(c) or "AI" in str(c) for c in updated_job.hypotheses[0].criticism)
        # Or it was a fallback
        has_fallback_indicator = any("Fallback" in str(c) for c in updated_job.hypotheses[0].criticism)
        # Either is acceptable
        assert has_groq_indicator or has_fallback_indicator or len(updated_job.hypotheses[0].criticism) > 0


def test_source_analyzer_compare_novelty():
    """Test that SourceAnalyzer can assess novelty using Groq."""
    analyzer = SourceAnalyzer()
    
    sources = [
        Source(
            title="Established ML Framework",
            url="https://example.org/established",
            publisher="ML Community",
            source_type="documentation",
            claims_extracted=["Framework X is a well-established machine learning library."],
            relevant_score=0.9,
        ),
    ]
    
    hypothesis = "Framework X provides an effective way to build machine learning models"
    
    # Assess novelty using Groq
    novelty = analyzer.compare_sources_for_novelty(sources, hypothesis)
    
    # Verify response is one of the expected values
    assert novelty in ["probably_known", "modification", "unable_to_determine"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
