from __future__ import annotations

from typing import Any, Dict, List, Optional

from .events import emit_event
from .models import Event, Experiment, Hypothesis, ResearchJob, Source
from .novelty import NoveltyEvaluator


class DeepDiscoveryLoop:
    """Stateful long-running discovery loop scaffold for future retrieval integration."""

    def __init__(self, store: Optional[Any] = None):
        self.store = store

    def start(self, job: ResearchJob) -> ResearchJob:
        emit_event(job, "research_started", "Research job started.", metadata={"mode": job.execution_mode})
        job.status = "running"
        self._persist(job)
        return job

    def pause(self, job: ResearchJob) -> ResearchJob:
        emit_event(job, "research_paused", "Research job paused.", metadata={"status": job.status})
        job.mark_paused()
        self._persist(job)
        return job

    def resume(self, job: ResearchJob) -> ResearchJob:
        emit_event(job, "research_resumed", "Research job resumed.", metadata={"status": job.status})
        job.mark_resumed()
        self._persist(job)
        return job

    def step(self, job: ResearchJob) -> ResearchJob:
        if not job.hypotheses:
            job.hypotheses.append(
                Hypothesis(
                    description="A structured evidence-first loop improves answer quality.",
                    supporting_sources=[source.source_id for source in job.sources],
                    novelty_status="modification",
                    confidence=0.65,
                    current_status="active",
                )
            )
        evaluator = NoveltyEvaluator()
        for hypothesis in job.hypotheses:
            hypothesis.novelty_status = evaluator.evaluate_hypothesis(hypothesis, job.sources)
            hypothesis.criticism = evaluator.critique_hypothesis(hypothesis)
        self._persist(job)
        return job

    def complete(self, job: ResearchJob) -> ResearchJob:
        emit_event(job, "research_completed", "Research job completed.", metadata={"discoveries": len(job.discoveries)})
        job.mark_completed()
        self._persist(job)
        return job

    def _persist(self, job: ResearchJob) -> None:
        if self.store is not None:
            self.store.save_job(job)


def quick_answer(job: ResearchJob) -> str:
    """Return the best available answer using current retrieved evidence and active hypotheses."""
    if not job.sources and not job.hypotheses:
        return "No retrieved evidence or active hypotheses are available yet. More research is required before a substantive answer can be formed."

    evidence_summary = "; ".join(source.claims_extracted[0] if source.claims_extracted else source.title for source in job.sources)
    active_hypotheses = ", ".join(hypothesis.description for hypothesis in job.hypotheses if hypothesis.current_status != "rejected")

    if not active_hypotheses:
        return f"Based on the retrieved evidence ({evidence_summary}), the current state does not support a confident answer yet."

    best_hypothesis = max(job.hypotheses, key=lambda h: h.confidence, default=None)
    if best_hypothesis is None:
        return f"Current evidence suggests a need for more investigation. Retrieved findings include: {evidence_summary}"

    answer = (
        f"Using the retrieved evidence and active hypotheses, the most promising direction is: "
        f"{best_hypothesis.description}. This is a {best_hypothesis.novelty_status} hypothesis with confidence "
        f"{best_hypothesis.confidence:.2f}. Evidence reviewed: {evidence_summary}."
    )
    emit_event(job, "answer_generated", "Answer generated from current state.", metadata={"answer": answer})
    return answer
