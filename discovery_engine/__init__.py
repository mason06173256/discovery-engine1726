"""Discovery Engine backend foundation."""

from .models import ClaimRecord, Event, Hypothesis, ResearchJob, Source, Experiment
from .events import emit_event, record_event
from .database import ResearchStore, SQLiteResearchStore
from .ai_providers import AIProvider, GroqProvider
from .novelty import NoveltyEvaluator
from .retrieval import RetrievalResult, RetrievalProvider, StaticRetrievalProvider, UnconfiguredRetrievalProvider, DuckDuckGoRetrievalProvider, get_configured_retrieval_provider
from .research import DeepDiscoveryLoop, quick_answer
from .research_service import ResearchService
from .analyzer import SourceAnalyzer

__all__ = [
    "ClaimRecord",
    "Event",
    "Hypothesis",
    "ResearchJob",
    "Source",
    "Experiment",
    "emit_event",
    "record_event",
    "ResearchStore",
    "SQLiteResearchStore",
    "AIProvider",
    "GroqProvider",
    "NoveltyEvaluator",
    "RetrievalResult",
    "RetrievalProvider",
    "StaticRetrievalProvider",
    "UnconfiguredRetrievalProvider",
    "DuckDuckGoRetrievalProvider",
    "get_configured_retrieval_provider",
    "DeepDiscoveryLoop",
    "ResearchService",
    "SourceAnalyzer",
    "quick_answer",
]
