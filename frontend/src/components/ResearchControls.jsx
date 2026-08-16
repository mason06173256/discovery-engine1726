import React, { useState } from 'react';
import './ResearchControls.css';

function ResearchControls({
  jobStatus,
  isLoading,
  onStart,
  onPause,
  onResume,
  onRunResearch,
  onGetAnswer,
}) {
  const [query, setQuery] = useState('');

  const handleRunResearch = () => {
    if (query.trim()) {
      onRunResearch(query);
      setQuery('');
    }
  };

  return (
    <div className="research-controls">
      <h2>⚙️ Controls</h2>
      
      <div className="status-badge">
        <span className={`status ${jobStatus || 'queued'}`}>
          {jobStatus ? jobStatus.toUpperCase() : 'QUEUED'}
        </span>
      </div>

      <div className="controls-section">
        <h3>Job Control</h3>
        <div className="button-group">
          {jobStatus === 'queued' && (
            <button 
              className="btn btn-success"
              onClick={onStart}
              disabled={isLoading}
            >
              ▶ Start Research
            </button>
          )}
          {(jobStatus === 'running' || jobStatus === 'active') && (
            <button 
              className="btn btn-warning"
              onClick={onPause}
              disabled={isLoading}
            >
              ⏸ Pause
            </button>
          )}
          {jobStatus === 'paused' && (
            <button 
              className="btn btn-success"
              onClick={onResume}
              disabled={isLoading}
            >
              ▶ Resume
            </button>
          )}
        </div>
      </div>

      <div className="controls-section">
        <h3>Deep Discovery</h3>
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search query..."
            className="search-input"
            disabled={isLoading}
            onKeyPress={(e) => e.key === 'Enter' && handleRunResearch()}
          />
          <button 
            className="btn btn-primary btn-sm"
            onClick={handleRunResearch}
            disabled={isLoading || !query.trim()}
          >
            🔍 Search
          </button>
        </div>
      </div>

      <div className="controls-section">
        <h3>Quick Answer</h3>
        <button 
          className="btn btn-primary"
          onClick={onGetAnswer}
          disabled={isLoading}
        >
          💡 Get Current Answer
        </button>
        <p className="hint">
          Generate the best answer from current research without disrupting Deep Discovery.
        </p>
      </div>
    </div>
  );
}

export default ResearchControls;
