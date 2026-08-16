from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Optional

from .models import Event, Hypothesis, ResearchJob, Source, Experiment


class ResearchStore(ABC):
    @abstractmethod
    def save_job(self, job: ResearchJob) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_job(self, job_id: str) -> ResearchJob:
        raise NotImplementedError

    @abstractmethod
    def record_event(self, job_id: str, event: Event) -> None:
        raise NotImplementedError


class SQLiteResearchStore(ResearchStore):
    def __init__(self, database_path: str = "discovery_engine.db"):
        self.database_path = database_path
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return self._connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_jobs (
                    job_id TEXT PRIMARY KEY,
                    user_objective TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT,
                    last_update_time TEXT,
                    completion_time TEXT,
                    sources TEXT,
                    hypotheses TEXT,
                    rejected_hypotheses TEXT,
                    experiments TEXT,
                    discoveries TEXT,
                    activity_events TEXT
                )
                """
            )
            connection.commit()

    @staticmethod
    def _json_loads(value: Optional[str], default: Any = None) -> Any:
        if value in (None, ""):
            return default if default is not None else []
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default if default is not None else []

    @staticmethod
    def _json_dumps(value: Any) -> str:
        return json.dumps(value, default=str)

    def save_job(self, job: ResearchJob) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO research_jobs (
                    job_id, user_objective, execution_mode, status, start_time,
                    last_update_time, completion_time, sources, hypotheses,
                    rejected_hypotheses, experiments, discoveries, activity_events
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    user_objective = excluded.user_objective,
                    execution_mode = excluded.execution_mode,
                    status = excluded.status,
                    start_time = excluded.start_time,
                    last_update_time = excluded.last_update_time,
                    completion_time = excluded.completion_time,
                    sources = excluded.sources,
                    hypotheses = excluded.hypotheses,
                    rejected_hypotheses = excluded.rejected_hypotheses,
                    experiments = excluded.experiments,
                    discoveries = excluded.discoveries,
                    activity_events = excluded.activity_events
                """,
                (
                    job.job_id,
                    job.user_objective,
                    job.execution_mode,
                    job.status,
                    job.start_time,
                    job.last_update_time,
                    job.completion_time,
                    self._json_dumps([source.__dict__ for source in job.sources]),
                    self._json_dumps([hypothesis.__dict__ for hypothesis in job.hypotheses]),
                    self._json_dumps([hypothesis.__dict__ for hypothesis in job.rejected_hypotheses]),
                    self._json_dumps([experiment.__dict__ for experiment in job.experiments]),
                    self._json_dumps(job.discoveries),
                    self._json_dumps([event.__dict__ for event in job.activity_events]),
                ),
            )
            connection.commit()

    def load_job(self, job_id: str) -> ResearchJob:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM research_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Research job not found: {job_id}")

        sources = [Source(**source_data) for source_data in self._json_loads(row["sources"], [])]
        hypotheses = [Hypothesis(**hypothesis_data) for hypothesis_data in self._json_loads(row["hypotheses"], [])]
        rejected = [Hypothesis(**hypothesis_data) for hypothesis_data in self._json_loads(row["rejected_hypotheses"], [])]
        experiments = [Experiment(**experiment_data) for experiment_data in self._json_loads(row["experiments"], [])]
        events = [Event(**event_data) for event_data in self._json_loads(row["activity_events"], [])]

        job = ResearchJob(
            user_objective=row["user_objective"],
            execution_mode=row["execution_mode"],
            job_id=row["job_id"],
            status=row["status"],
            start_time=row["start_time"],
            last_update_time=row["last_update_time"],
            completion_time=row["completion_time"],
            sources=sources,
            hypotheses=hypotheses,
            rejected_hypotheses=rejected,
            experiments=experiments,
            discoveries=self._json_loads(row["discoveries"], []),
            activity_events=events,
        )
        return job

    def record_event(self, job_id: str, event: Event) -> None:
        job = self.load_job(job_id)
        job.activity_events.append(event)
        job.last_update_time = event.timestamp
        self.save_job(job)
