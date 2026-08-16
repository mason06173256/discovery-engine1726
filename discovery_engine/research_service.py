from __future__ import annotations

from typing import List, Optional

from .database import ResearchStore, SQLiteResearchStore
from .events import emit_event
from .models import Event, Hypothesis, ResearchJob, Source
from .novelty import NoveltyEvaluator
from .retrieval import RetrievalProvider, RetrievalResult
from .analyzer import SourceAnalyzer


class ResearchService:
    """Operational service for creating, updating, pausing, resuming, and querying research jobs."""

    def __init__(self, store: Optional[ResearchStore] = None, analyzer: Optional[SourceAnalyzer] = None):
        self.store = store or SQLiteResearchStore("discovery_engine.db")
        self.analyzer = analyzer or SourceAnalyzer()  # Use Groq by default for AI analysis

    def create_job(self, user_objective: str, execution_mode: str = "quick_answer") -> ResearchJob:
        job = ResearchJob(user_objective=user_objective, execution_mode=execution_mode)
        emit_event(job, "research_started", "Research job created and queued.", metadata={"mode": execution_mode})
        self.store.save_job(job)
        return job

    def get_job(self, job_id: str) -> ResearchJob:
        return self.store.load_job(job_id)

    def start_job(self, job_id: str) -> ResearchJob:
        job = self.get_job(job_id)
        job.mark_started()
        emit_event(job, "research_started", "Research started.", metadata={"job_id": job.job_id})
        self.store.save_job(job)
        return job

    def pause_job(self, job_id: str) -> ResearchJob:
        job = self.get_job(job_id)
        job.mark_paused()
        emit_event(job, "research_paused", "Research paused by operator.", metadata={"job_id": job.job_id})
        self.store.save_job(job)
        return job

    def resume_job(self, job_id: str) -> ResearchJob:
        job = self.get_job(job_id)
        job.mark_resumed()
        emit_event(job, "research_resumed", "Research resumed.", metadata={"job_id": job.job_id})
        self.store.save_job(job)
        return job

    def add_source(self, job_id: str, source: Source) -> ResearchJob:
        job = self.get_job(job_id)
        job.sources.append(source)
        emit_event(job, "source_found", "Source retrieved and attached to the job.", related_object_id=source.source_id, metadata={"source_id": source.source_id, "title": source.title})
        self.store.save_job(job)
        return job

    def add_hypothesis(self, job_id: str, hypothesis: Hypothesis) -> ResearchJob:
        job = self.get_job(job_id)
        job.hypotheses.append(hypothesis)
        emit_event(job, "hypothesis_generated", "Hypothesis generated.", related_object_id=hypothesis.hypothesis_id, metadata={"confidence": hypothesis.confidence})
        self.store.save_job(job)
        return job

    def run_deep_discovery_step(self, job_id: str, query: str, retrieval_provider: RetrievalProvider) -> ResearchJob:
        job = self.get_job(job_id)
        if job.status == "queued":
            job.mark_started()

        # Emit initial search started event
        emit_event(job, "search_started", "Retrieval search cycle initiated.", metadata={"query": query})
        
        # Emit search query issued event for granular tracking
        emit_event(job, "search_query_issued", f"Search query: '{query}'", metadata={"query": query, "provider": type(retrieval_provider).__name__})
        
        # Attempt to retrieve results
        try:
            results = retrieval_provider.search(query)
        except RuntimeError as e:
            # Provider is unconfigured or errored
            emit_event(job, "provider_error", str(e), metadata={"query": query, "error": str(e)})
            self.store.save_job(job)
            return job
        
        if not results:
            emit_event(job, "search_started", "No retrieved results were returned for the query.", metadata={"query": query})
            self.store.save_job(job)
            return job

        # Process each retrieved result
        for result in results:
            # Emit source found event
            emit_event(job, "source_found", f"Source found in retrieval: {result.title}", metadata={"url": result.url, "relevance_score": result.relevance_score})
            
            # Emit source retrieved event
            emit_event(job, "source_retrieved", f"Source retrieved and processed: {result.title}", metadata={"url": result.url, "source_type": result.source_type})
            
            # Convert retrieval result to Source model (never fabricate)
            source = Source(
                title=result.title,
                url=result.url,
                publisher=result.publisher,
                author=result.author,
                publication_date=result.publication_date,
                retrieval_timestamp=result.retrieval_timestamp,
                relevant_score=result.relevance_score,
                source_type=result.source_type,
                claims_extracted=result.claims or ([result.content] if result.content else []),
            )
            job.sources.append(source)
            
            # Emit source stored event
            emit_event(job, "source_stored", f"Source persisted: {source.source_id}", related_object_id=source.source_id, metadata={"source_id": source.source_id, "url": source.url})
            
            # Emit source analyzed event
            emit_event(job, "source_analyzed", f"Source analyzed for relevance and claims.", related_object_id=source.source_id, metadata={"relevance_score": source.relevant_score})
            
            # Emit claim extracted event for each claim
            for claim in source.claims_extracted:
                emit_event(job, "claim_extracted", f"Claim extracted from {result.title}: {claim}", related_object_id=source.source_id, metadata={"source_id": source.source_id, "claim": claim})

        # Generate AI-informed hypothesis from accumulated evidence using Groq
        emit_event(job, "hypothesis_generation_started", "Using AI to analyze sources and generate hypothesis.", metadata={"source_count": len(results), "query": query})
        
        # Get sources that were just added
        new_sources = job.sources[-len(results):]
        
        # Use Groq to generate a hypothesis grounded in the retrieved sources
        try:
            hypothesis = self.analyzer.generate_hypothesis_from_sources(new_sources, query, job.user_objective)
            
            if hypothesis:
                job.hypotheses.append(hypothesis)
                emit_event(job, "hypothesis_generated", "AI-generated hypothesis from retrieved evidence using Groq.", related_object_id=hypothesis.hypothesis_id, metadata={"confidence": hypothesis.confidence, "source_count": len(results)})
            else:
                # Fallback if Groq analysis fails
                fallback_hypothesis = Hypothesis(
                    description=f"The retrieved evidence suggests a promising path for: {query}.",
                    supporting_sources=[source.source_id for source in new_sources],
                    confidence=0.65,
                    current_status="active",
                    novelty_status="unable_to_determine",
                )
                job.hypotheses.append(fallback_hypothesis)
                emit_event(job, "hypothesis_generated", "Fallback hypothesis generated (Groq analysis unavailable).", related_object_id=fallback_hypothesis.hypothesis_id, metadata={"confidence": fallback_hypothesis.confidence, "source_count": len(results)})
        except Exception as e:
            # Graceful degradation: use fallback hypothesis if AI analysis fails
            fallback_hypothesis = Hypothesis(
                description=f"The retrieved evidence suggests a promising path for: {query}.",
                supporting_sources=[source.source_id for source in new_sources],
                confidence=0.65,
                current_status="active",
                novelty_status="unable_to_determine",
            )
            job.hypotheses.append(fallback_hypothesis)
            emit_event(job, "hypothesis_generated", f"Fallback hypothesis generated (AI analysis failed: {str(e)})", related_object_id=fallback_hypothesis.hypothesis_id, metadata={"error": str(e)})


        if job.status == "running":
            job.status = "running"
        elif job.status == "paused":
            job.status = "paused"
        self.store.save_job(job)
        return job

    def run_full_research_cycle(self, job_id: str, query: str, retrieval_provider: RetrievalProvider) -> ResearchJob:
        job = self.get_job(job_id)
        if job.status == "queued":
            job.mark_started()

        emit_event(job, "search_started", "Research cycle started.", metadata={"query": query})
        self.store.save_job(job)

        job = self.run_deep_discovery_step(job_id, query, retrieval_provider)
        emit_event(job, "novelty_check_started", "Novelty evaluation started for generated hypotheses.", metadata={"hypothesis_count": len(job.hypotheses)})
        evaluator = NoveltyEvaluator()
        for hypothesis in job.hypotheses:
            hypothesis.novelty_status = evaluator.evaluate_hypothesis(hypothesis, job.sources)
            hypothesis.criticism = evaluator.critique_hypothesis(hypothesis)
        self.store.save_job(job)

        emit_event(job, "hypothesis_modified", "Hypothesis refined based on novelty and critique.", metadata={"updated_hypotheses": len(job.hypotheses)})
        self.store.save_job(job)
        return job

    def list_jobs(self) -> List[ResearchJob]:
        raise NotImplementedError("List jobs requires query support and will be implemented in a later phase.")
