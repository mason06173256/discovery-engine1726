from __future__ import annotations

import argparse
from typing import Optional

from discovery_engine.database import SQLiteResearchStore
from discovery_engine.events import emit_event
from discovery_engine.models import Hypothesis, ResearchJob, Source
from discovery_engine.research import DeepDiscoveryLoop, quick_answer


def build_demo_job() -> ResearchJob:
    job = ResearchJob(
        user_objective="Evaluate whether a structured evidence-first workflow improves research quality.",
        execution_mode="quick_answer",
    )

    source = Source(
        title="Evidence first workflow",
        url="https://example.org/evidence/workflow",
        publisher="Research Lab",
        author="A. Researcher",
        publication_date="2026-01-15",
        relevant_score=0.88,
        source_type="article",
        claims_extracted=[
            "Research quality improves when evidence and hypotheses remain distinct.",
            "A workflow with explicit evidence tracking reduces unsupported claims.",
        ],
    )

    hypothesis = Hypothesis(
        description="A structured evidence-first loop improves decision quality and reduces unsupported conclusions.",
        supporting_sources=[source.source_id],
        novelty_status="modification",
        confidence=0.81,
        current_status="active",
    )

    job.sources.append(source)
    job.hypotheses.append(hypothesis)
    emit_event(job, "source_found", "Example source was added to the job.", related_object_id=source.source_id, metadata={"source_id": source.source_id})
    emit_event(job, "hypothesis_generated", "Example hypothesis was created.", related_object_id=hypothesis.hypothesis_id, metadata={"confidence": hypothesis.confidence})
    return job


def run_demo() -> None:
    job = build_demo_job()
    print("Job ID:", job.job_id)
    print("Quick answer:")
    print(quick_answer(job))

    store = SQLiteResearchStore("discovery_engine.db")
    store.save_job(job)
    print("Saved job to SQLite database.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Discovery Engine backend demo")
    parser.add_argument("--demo", action="store_true", help="run a minimal quick-answer demo")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        print("Discovery Engine ready. Use --demo to run a quick answer example.")


if __name__ == "__main__":
    main()
