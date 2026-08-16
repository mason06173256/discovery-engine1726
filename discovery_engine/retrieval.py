from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol, runtime_checkable


@dataclass
class RetrievalResult:
    title: str
    url: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    retrieval_timestamp: Optional[str] = None
    relevance_score: float = 0.0
    source_type: str = "unknown"
    content: str = ""
    claims: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError("A URL is required for a retrieved source.")


@runtime_checkable
class RetrievalProvider(Protocol):
    """Protocol for retrieval providers. Implementers must provide a search method that returns real retrieved results, never fabricated ones."""

    def search(self, query: str) -> List[RetrievalResult]:
        """Search for evidence and return real retrieval results. Must never fabricate sources, URLs, or evidence.
        
        Args:
            query: The search query.
            
        Returns:
            A list of real RetrievalResult objects retrieved from the provider's source.
            
        Raises:
            ValueError: If query is empty or the provider is unconfigured.
        """
        ...


class StaticRetrievalProvider:
    """Simple retrieval adapter used for testing and local-phase development. No fabricated search results are created; only provided results are accepted."""

    def __init__(self, results: Optional[List[RetrievalResult]] = None):
        self.results = results or []

    def search(self, query: str) -> List[RetrievalResult]:
        if not query or not query.strip():
            raise ValueError("A non-empty search query is required.")
        return [result for result in self.results if query.lower() in result.title.lower() or query.lower() in (result.content or "").lower()]


class UnconfiguredRetrievalProvider:
    """Placeholder provider that explicitly raises an error when used without proper configuration. Used to distinguish missing credentials from intentional static testing."""

    def __init__(self, provider_name: str = "retrieval provider"):
        self.provider_name = provider_name

    def search(self, query: str) -> List[RetrievalResult]:
        raise RuntimeError(
            f"The {self.provider_name} is not configured. Set the required environment variables "
            f"(e.g., RETRIEVAL_API_KEY, RETRIEVAL_PROVIDER_TYPE) before attempting to retrieve external evidence."
        )


def get_configured_retrieval_provider() -> RetrievalProvider:
    """Load and return a configured retrieval provider based on environment variables.
    
    Environment variables:
    - RETRIEVAL_PROVIDER_TYPE: Type of provider (e.g., 'duckduckgo', 'static', 'academic', 'patents')
      Defaults to 'duckduckgo' for real web search.
    - RETRIEVAL_API_KEY: API key for providers that require it
    - RETRIEVAL_API_URL: Base URL for the provider (if applicable)
    
    Returns:
        A configured retrieval provider instance. Defaults to DuckDuckGoRetrievalProvider for real search.
    """
    import os

    provider_type = os.getenv("RETRIEVAL_PROVIDER_TYPE", "duckduckgo").lower()

    if provider_type == "duckduckgo":
        # DuckDuckGo is the default provider—no API key required, real web search.
        return DuckDuckGoRetrievalProvider()

    if provider_type == "static":
        # Static provider for testing; can be empty for local development.
        return StaticRetrievalProvider()

    # For other providers, more sophisticated detection would go here.
    # For now, return unconfigured placeholder.
    return UnconfiguredRetrievalProvider(provider_type)


class DuckDuckGoRetrievalProvider:
    """Real web-search retrieval provider using DuckDuckGo. No API key required, does not fabricate results."""

    def __init__(self):
        self.provider_name = "DuckDuckGo"
        try:
            from ddgs import DDGS
            self.ddgs_class = DDGS
        except ImportError:
            raise RuntimeError(
                "ddgs is not installed. Install it with: pip install ddgs>=5.0.0"
            )

    def search(self, query: str) -> List[RetrievalResult]:
        """Perform a real DuckDuckGo web search and return actual results.
        
        Args:
            query: The search query.
            
        Returns:
            A list of RetrievalResult objects from DuckDuckGo search results.
            
        Raises:
            ValueError: If query is empty.
            RuntimeError: If DuckDuckGo search fails.
        """
        import os
        from datetime import datetime, timezone

        if not query or not query.strip():
            raise ValueError("A non-empty search query is required.")

        try:
            results: List[RetrievalResult] = []
            # Use DDGS to perform actual search; limit to top 10 results for efficiency
            with self.ddgs_class() as ddgs:
                search_results = list(ddgs.text(query, max_results=10))

            for result in search_results:
                # DDGS returns: title, href, body (snippet)
                retrieval_result = RetrievalResult(
                    title=result.get("title", ""),
                    url=result.get("href", ""),
                    content=result.get("body", ""),  # Snippet from DuckDuckGo
                    source_type="web_search_result",
                    publisher="DuckDuckGo",
                    relevance_score=0.75,  # Default relevance; could be enhanced later
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
                )
                results.append(retrieval_result)

            return results

        except Exception as e:
            # Gracefully handle retrieval failures
            raise RuntimeError(
                f"DuckDuckGo search failed for query '{query}': {str(e)}. "
                f"The research engine will continue without this retrieval step."
            ) from e
