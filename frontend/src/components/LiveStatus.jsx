import React, { useState, useEffect } from 'react';
import './LiveStatus.css';

function LiveStatus({ jobData, startTime, eventCount }) {
  const [elapsed, setElapsed] = useState('0s');

  useEffect(() => {
    if (!startTime) return;

    const updateElapsed = () => {
      const now = new Date();
      const diff = Math.floor((now - startTime) / 1000);
      
      if (diff < 60) {
        setElapsed(`${diff}s`);
      } else if (diff < 3600) {
        const mins = Math.floor(diff / 60);
        const secs = diff % 60;
        setElapsed(`${mins}m ${secs}s`);
      } else {
        const hours = Math.floor(diff / 3600);
        const mins = Math.floor((diff % 3600) / 60);
        setElapsed(`${hours}h ${mins}m`);
      }
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  const sources = jobData?.sources || [];
  const hypotheses = jobData?.hypotheses || [];
  const rejectedHypotheses = hypotheses.filter(h => h.current_status === 'rejected').length;
  const survivingHypotheses = hypotheses.length - rejectedHypotheses;

  // Extract search events to count searches
  const searchEventCount = eventCount || 0;

  return (
    <div className="live-status">
      <h2>📊 Research Status</h2>
      
      <div className="status-grid">
        <div className="status-item">
          <div className="status-label">Elapsed Time</div>
          <div className="status-value">{elapsed}</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">Sources Found</div>
          <div className="status-value">{sources.length}</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">Hypotheses</div>
          <div className="status-value">{hypotheses.length}</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">Rejected</div>
          <div className="status-value rejected">{rejectedHypotheses}</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">Surviving</div>
          <div className="status-value success">{survivingHypotheses}</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">Events</div>
          <div className="status-value">{eventCount}</div>
        </div>
      </div>

      {jobData?.hypotheses && jobData.hypotheses.length > 0 && (
        <div className="phase-info">
          <h3>Current Phase</h3>
          <p>Analyzing sources and generating hypotheses</p>
        </div>
      )}
    </div>
  );
}

export default LiveStatus;
