from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

VALID_EXECUTION_MODES = {"quick_answer", "deep_discovery"}
VALID_HYPOTHESIS_STATUSES = {
    "active",
    "rejected",
    "modified",
    "tested",
    "archived",
}
VALID_NOVELTY_STATUSES = {
    "known",
    "probably_known",
    "modification",
    "new_combination",
    "apparently_novel",
    "unable_to_determine",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Event:
    event_type: str
    description: str
    timestamp: str = field(default_factory=utc_now_iso)
    related_object_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaimRecord:
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_type: str = "unverified_claim"
    content: str = ""
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Source:
    title: str
    url: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    retrieval_timestamp: Optional[str] = None
    relevant_score: float = 0.0
    source_type: str = "unknown"
    claims_extracted: List[str] = field(default_factory=list)
    hypotheses_used: List[str] = field(default_factory=list)
    source_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not self.retrieval_timestamp:
            self.retrieval_timestamp = utc_now_iso()
        if not self.url:
            raise ValueError("A source URL is required and must come from an actual retrieval system.")


@dataclass
class Hypothesis:
    description: str
    creation_timestamp: str = field(default_factory=utc_now_iso)
    supporting_sources: List[str] = field(default_factory=list)
    contradicting_sources: List[str] = field(default_factory=list)
    novelty_status: str = "unable_to_determine"
    confidence: float = 0.0
    current_status: str = "active"
    criticism: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    test_results: List[str] = field(default_factory=list)
    hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if self.novelty_status not in VALID_NOVELTY_STATUSES:
            raise ValueError(f"Unsupported novelty status: {self.novelty_status}")
        if self.current_status not in VALID_HYPOTHESIS_STATUSES:
            raise ValueError(f"Unsupported hypothesis status: {self.current_status}")
        self.confidence = max(0.0, min(1.0, float(self.confidence)))


@dataclass
class Experiment:
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    started_at: str = field(default_factory=utc_now_iso)
    completed_at: Optional[str] = None
    status: str = "planned"
    result_summary: str = ""
    related_hypothesis_id: Optional[str] = None


@dataclass
class ResearchJob:
    user_objective: str
    execution_mode: str = "quick_answer"
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "queued"
    start_time: Optional[str] = None
    last_update_time: Optional[str] = None
    completion_time: Optional[str] = None
    sources: List[Source] = field(default_factory=list)
    hypotheses: List[Hypothesis] = field(default_factory=list)
    rejected_hypotheses: List[Hypothesis] = field(default_factory=list)
    experiments: List[Experiment] = field(default_factory=list)
    discoveries: List[Dict[str, Any]] = field(default_factory=list)
    activity_events: List[Event] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.execution_mode not in VALID_EXECUTION_MODES:
            raise ValueError(f"Unsupported execution mode: {self.execution_mode}")
        if not self.start_time:
            self.start_time = utc_now_iso()
        if not self.last_update_time:
            self.last_update_time = self.start_time
        if self.user_objective is None:
            raise ValueError("A user objective is required for every research job.")

    def add_event(self, event: Event) -> Event:
        self.activity_events.append(event)
        self.last_update_time = utc_now_iso()
        return event

    def mark_started(self) -> None:
        self.status = "running"
        self.start_time = self.start_time or utc_now_iso()
        self.last_update_time = utc_now_iso()

    def mark_completed(self) -> None:
        self.status = "completed"
        self.completion_time = utc_now_iso()
        self.last_update_time = self.completion_time

    def mark_paused(self) -> None:
        self.status = "paused"
        self.last_update_time = utc_now_iso()

    def mark_resumed(self) -> None:
        self.status = "running"
        self.last_update_time = utc_now_iso()
