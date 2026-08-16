import React, { useState, useEffect } from 'react';
import { jobsApi, eventsApi } from '../api';
import ObjectiveInput from './ObjectiveInput';
import ResearchControls from './ResearchControls';
import LiveStatus from './LiveStatus';
import SourcePanel from './SourcePanel';
import HypothesisPanel from './HypothesisPanel';
import EventTimeline from './EventTimeline';
import AnswerPanel from './AnswerPanel';
import './ResearchWorkspace.css';

function ResearchWorkspace() {
  const [jobId, setJobId] = useState(null);
  const [jobData, setJobData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [eventSource, setEventSource] = useState(null);
  const [events, setEvents] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Load job data
  useEffect(() => {
    if (!jobId) return;

    const loadJob = async () => {
      try {
        const response = await jobsApi.getJob(jobId);
        setJobData(response.data);
      } catch (err) {
        console.error('Failed to load job:', err);
        setError('Failed to load research job');
      }
    };

    loadJob();
    const interval = autoRefresh ? setInterval(loadJob, 2000) : null;
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId, autoRefresh]);

  // Subscribe to events
  useEffect(() => {
    if (!jobId) return;

    let es = null;
    const subscribeToEvents = async () => {
      es = eventsApi.subscribeToEvents(
        jobId,
        (event) => {
          setEvents((prev) => [...prev, event]);
        },
        () => {
          console.log('Event stream closed');
        }
      );
      setEventSource(es);
    };

    subscribeToEvents();

    return () => {
      if (es) {
        eventsApi.closeConnection(es);
      }
    };
  }, [jobId]);

  // Create new job
  const handleCreateJob = async (objective) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await jobsApi.createJob(objective, 'iterative');
      setJobId(response.data.job_id);
      setJobData(response.data);
      setStartTime(new Date());
      setEvents([]);
    } catch (err) {
      console.error('Failed to create job:', err);
      setError('Failed to create research job. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };

  // Start job
  const handleStartJob = async () => {
    if (!jobId) return;
    setIsLoading(true);
    try {
      const response = await jobsApi.startJob(jobId);
      setJobData(response.data);
    } catch (err) {
      console.error('Failed to start job:', err);
      setError('Failed to start research job');
    } finally {
      setIsLoading(false);
    }
  };

  // Pause job
  const handlePauseJob = async () => {
    if (!jobId) return;
    setIsLoading(true);
    try {
      const response = await jobsApi.pauseJob(jobId);
      setJobData(response.data);
    } catch (err) {
      console.error('Failed to pause job:', err);
      setError('Failed to pause research job');
    } finally {
      setIsLoading(false);
    }
  };

  // Resume job
  const handleResumeJob = async () => {
    if (!jobId) return;
    setIsLoading(true);
    try {
      const response = await jobsApi.resumeJob(jobId);
      setJobData(response.data);
    } catch (err) {
      console.error('Failed to resume job:', err);
      setError('Failed to resume research job');
    } finally {
      setIsLoading(false);
    }
  };

  // Run research step
  const handleRunResearch = async (query) => {
    if (!jobId) return;
    setIsLoading(true);
    try {
      const response = await jobsApi.runResearch(jobId, query);
      setJobData(response.data);
    } catch (err) {
      console.error('Failed to run research:', err);
      setError('Failed to run research step');
    } finally {
      setIsLoading(false);
    }
  };

  // Get quick answer
  const handleGetAnswer = async () => {
    if (!jobId) return;
    setIsLoading(true);
    try {
      const response = await jobsApi.getAnswer(jobId);
      setJobData(response.data);
    } catch (err) {
      console.error('Failed to get answer:', err);
      setError('Failed to generate answer');
    } finally {
      setIsLoading(false);
    }
  };

  if (!jobId) {
    return (
      <div className="research-workspace">
        <ObjectiveInput onSubmit={handleCreateJob} isLoading={isLoading} error={error} />
      </div>
    );
  }

  return (
    <div className="research-workspace active">
      <div className="workspace-grid">
        {/* Left Column: Objective and Controls */}
        <div className="workspace-left">
          <div className="workspace-section">
            <ObjectiveInput 
              initialValue={jobData?.user_objective} 
              isDisabled={true}
            />
          </div>

          <div className="workspace-section">
            <ResearchControls
              jobStatus={jobData?.status}
              isLoading={isLoading}
              onStart={handleStartJob}
              onPause={handlePauseJob}
              onResume={handleResumeJob}
              onRunResearch={handleRunResearch}
              onGetAnswer={handleGetAnswer}
            />
          </div>

          <div className="workspace-section">
            <LiveStatus 
              jobData={jobData}
              startTime={startTime}
              eventCount={events.length}
            />
          </div>
        </div>

        {/* Right Column: Data Panels */}
        <div className="workspace-right">
          <div className="panels-container">
            <SourcePanel sources={jobData?.sources || []} />
            <HypothesisPanel hypotheses={jobData?.hypotheses || []} />
          </div>
        </div>
      </div>

      {/* Bottom: Event Timeline and Answer */}
      <div className="workspace-bottom">
        <div className="panels-row">
          <EventTimeline events={events} />
          <AnswerPanel jobData={jobData} />
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
    </div>
  );
}

export default ResearchWorkspace;
