import React, { useEffect, useRef } from 'react';
import './EventTimeline.css';

function EventTimeline({ events }) {
  const containerRef = useRef(null);

  // Auto-scroll to latest event
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [events]);

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'research_started': return '🚀';
      case 'search_started': return '🔎';
      case 'search_query_issued': return '⌨️';
      case 'source_found': return '📄';
      case 'source_retrieved': return '📥';
      case 'source_stored': return '💾';
      case 'source_analyzed': return '🔬';
      case 'claim_extracted': return '✂️';
      case 'hypothesis_generation_started': return '🧠';
      case 'hypothesis_generated': return '💡';
      case 'novelty_check_started': return '🔍';
      case 'hypothesis_rejected': return '❌';
      case 'hypothesis_modified': return '🔧';
      case 'experiment_started': return '🧪';
      case 'experiment_completed': return '✅';
      case 'research_paused': return '⏸';
      case 'research_resumed': return '▶️';
      case 'answer_generated': return '📝';
      case 'research_completed': return '🏁';
      case 'provider_error': return '⚠️';
      default: return '•';
    }
  };

  const getEventLabel = (eventType) => {
    switch (eventType) {
      case 'research_started': return 'Research started';
      case 'search_started': return 'Search started';
      case 'search_query_issued': return 'Query issued';
      case 'source_found': return 'Source found';
      case 'source_retrieved': return 'Source retrieved';
      case 'source_stored': return 'Source stored';
      case 'source_analyzed': return 'Source analyzed';
      case 'claim_extracted': return 'Claim extracted';
      case 'hypothesis_generation_started': return 'Hypothesis generation started';
      case 'hypothesis_generated': return 'Hypothesis generated';
      case 'novelty_check_started': return 'Novelty check started';
      case 'hypothesis_rejected': return 'Hypothesis rejected';
      case 'hypothesis_modified': return 'Hypothesis modified';
      case 'experiment_started': return 'Experiment started';
      case 'experiment_completed': return 'Experiment completed';
      case 'research_paused': return 'Research paused';
      case 'research_resumed': return 'Research resumed';
      case 'answer_generated': return 'Answer generated';
      case 'research_completed': return 'Research completed';
      case 'provider_error': return 'Provider error';
      default: return eventType?.replace(/_/g, ' ') || 'Event';
    }
  };

  if (!events || events.length === 0) {
    return (
      <div className="event-timeline panel">
        <div className="panel-header">
          <h2>📋 Event Timeline</h2>
          <span className="badge">0</span>
        </div>
        <div className="empty-state">
          <p>Waiting for research events...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="event-timeline panel">
      <div className="panel-header">
        <h2>📋 Event Timeline</h2>
        <span className="badge">{events.length}</span>
      </div>
      
      <div className="events-container" ref={containerRef}>
        <div className="timeline">
          {events.map((event, idx) => (
            <div key={idx} className="timeline-item">
              <div className="timeline-marker">
                <span className="event-icon">{getEventIcon(event.event_type)}</span>
              </div>
              <div className="timeline-content">
                <div className="event-header">
                  <span className="event-type">
                    {getEventLabel(event.event_type)}
                  </span>
                  <span className="event-time">
                    {event.timestamp 
                      ? new Date(event.timestamp).toLocaleTimeString()
                      : 'just now'}
                  </span>
                </div>
                {event.description && (
                  <p className="event-description">{event.description}</p>
                )}
                {event.metadata && Object.keys(event.metadata).length > 0 && (
                  <div className="event-metadata">
                    {Object.entries(event.metadata).map(([key, val]) => (
                      <span key={key} className="metadata-item">
                        <span className="metadata-key">{key}:</span>
                        <span className="metadata-value">
                          {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                        </span>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default EventTimeline;
