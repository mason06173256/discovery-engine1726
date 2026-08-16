"""Pytest configuration and fixtures for Discovery Engine tests."""

import os
import pytest
from discovery_engine.retrieval import StaticRetrievalProvider, RetrievalResult


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment before any tests run."""
    # Set default retrieval provider to static for testing
    os.environ.setdefault("RETRIEVAL_PROVIDER_TYPE", "static")
    
    # Optionally, configure a mock retrieval provider with test data
    # This can be set per-test if needed


@pytest.fixture
def static_retrieval_provider_with_test_data():
    """Provide a static retrieval provider with pre-configured test data."""
    return StaticRetrievalProvider(
        [
            RetrievalResult(
                title="Evidence first systems",
                url="https://example.org/evidence-first",
                publisher="Research Lab",
                content="Explicit evidence boundaries reduce unsupported claims.",
                relevance_score=0.92,
                source_type="article",
            ),
            RetrievalResult(
                title="Modular research architectures",
                url="https://example.org/modular-research",
                publisher="Research Institute",
                content="Modular systems enable incremental research and hypothesis testing.",
                relevance_score=0.85,
                source_type="paper",
            ),
        ]
    )
