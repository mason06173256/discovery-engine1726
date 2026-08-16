import React, { useState } from 'react';
import './HypothesisPanel.css';

function HypothesisPanel({ hypotheses }) {
  const [expandedId, setExpandedId] = useState(null);

  if (!hypotheses || hypotheses.length === 0) {
    return (
      <div className="hypothesis-panel panel">
        <div className="panel-header">
          <h2>💡 Hypotheses</h2>
          <span className="badge">0</span>
        </div>
        <div className="empty-state">
          <p>No hypotheses generated yet.</p>
          <p className="hint">Generate hypotheses from retrieved sources.</p>
        </div>
      </div>
    );
  }

  const getNoveltyIcon = (status) => {
    switch (status) {
      case 'probably_known': return '🔁';
      case 'modification': return '🔧';
      case 'new_combination': return '🔀';
      case 'apparently_novel': return '✨';
      case 'unable_to_determine': return '❓';
      default: return '•';
    }
  };

  const getNoveltyLabel = (status) => {
    switch (status) {
      case 'probably_known': return 'PROBABLY KNOWN';
      case 'modification': return 'MODIFICATION';
      case 'new_combination': return 'NEW COMBINATION';
      case 'apparently_novel': return 'APPARENTLY NOVEL';
      case 'unable_to_determine': return 'UNABLE TO DETERMINE';
      default: return status?.toUpperCase() || 'UNKNOWN';
    }
  };

  return (
    <div className="hypothesis-panel panel">
      <div className="panel-header">
        <h2>💡 Hypotheses</h2>
        <span className="badge">{hypotheses.length}</span>
      </div>
      
      <div className="hypotheses-list">
        {hypotheses.map((hyp, idx) => (
          <div 
            key={hyp.hypothesis_id || idx} 
            className={`hypothesis-item status-${hyp.current_status}`}
          >
            <div 
              className="hypothesis-header"
              onClick={() => setExpandedId(expandedId === hyp.hypothesis_id ? null : hyp.hypothesis_id)}
            >
              <div className="hypothesis-title-section">
                <span className="expand-icon">
                  {expandedId === hyp.hypothesis_id ? '▼' : '▶'}
                </span>
                <div className="hypothesis-title-group">
                  <h3 className="hypothesis-title">{hyp.description}</h3>
                  <div className="hypothesis-badges">
                    <span className={`status-badge ${hyp.current_status}`}>
                      {hyp.current_status?.toUpperCase() || 'ACTIVE'}
                    </span>
                    <span className="novelty-badge">
                      {getNoveltyIcon(hyp.novelty_status)} {getNoveltyLabel(hyp.novelty_status)}
                    </span>
                  </div>
                </div>
              </div>
              {hyp.confidence && (
                <div className="confidence-display">
                  <span className="confidence-label">Confidence</span>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${hyp.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-value">
                    {Math.round(hyp.confidence * 100)}%
                  </span>
                </div>
              )}
            </div>

            {expandedId === hyp.hypothesis_id && (
              <div className="hypothesis-details">
                {hyp.supporting_sources && hyp.supporting_sources.length > 0 && (
                  <div className="detail-section">
                    <h4>Supporting Sources</h4>
                    <ul className="sources-list">
                      {hyp.supporting_sources.map((src, i) => (
                        <li key={i}>
                          {typeof src === 'object' ? src.title || src.url : src}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {hyp.contradicting_sources && hyp.contradicting_sources.length > 0 && (
                  <div className="detail-section warning">
                    <h4>Contradicting Sources</h4>
                    <ul className="sources-list">
                      {hyp.contradicting_sources.map((src, i) => (
                        <li key={i}>
                          {typeof src === 'object' ? src.title || src.url : src}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {hyp.criticism && hyp.criticism.length > 0 && (
                  <div className="detail-section">
                    <h4>Criticism</h4>
                    <ul className="criticism-list">
                      {hyp.criticism.map((crit, i) => (
                        <li key={i}>{crit}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {hyp.modifications && hyp.modifications.length > 0 && (
                  <div className="detail-section">
                    <h4>Modifications</h4>
                    <ul className="modifications-list">
                      {hyp.modifications.map((mod, i) => (
                        <li key={i}>{mod}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {hyp.test_results && (
                  <div className="detail-section">
                    <h4>Test Results</h4>
                    <p>{hyp.test_results}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="panel-footer">
        <p className="footer-text">
          💬 NEVER displays "PROVEN ORIGINAL" or "100% ORIGINAL"
        </p>
      </div>
    </div>
  );
}

export default HypothesisPanel;
