from __future__ import annotations

from typing import Any, Dict, Optional

from .models import Event, ResearchJob, utc_now_iso

VALID_EVENT_TYPES = {
    "research_started",
    "search_started",
    "search_query_issued",
    "source_found",
    "source_retrieved",
    "source_stored",
    "source_analyzed",
    "claim_extracted",
    "hypothesis_generation_started",
    "hypothesis_generated",
    "novelty_check_started",
    "hypothesis_rejected",
    "hypothesis_modified",
    "experiment_started",
    "experiment_completed",
    "research_paused",
    "research_resumed",
    "answer_generated",
    "research_completed",
    "provider_unconfigured",
    "provider_error",
}


def emit_event(
    job: ResearchJob,
    event_type: str,
    description: str,
    related_object_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Event:
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")
    event = Event(
        event_type=event_type,
        description=description,
        related_object_id=related_object_id,
        metadata=metadata or {},
        timestamp=utc_now_iso(),
    )
    job.add_event(event)
    return event


def record_event(
    job: ResearchJob,
    event_type: str,
    description: str,
    related_object_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Event:
    return emit_event(job, event_type, description, related_object_id, metadata)
