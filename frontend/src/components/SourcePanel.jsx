import React, { useState } from 'react';
import './SourcePanel.css';

function SourcePanel({ sources }) {
  const [expandedId, setExpandedId] = useState(null);

  if (!sources || sources.length === 0) {
    return (
      <div className="source-panel panel">
        <div className="panel-header">
          <h2>📚 Sources</h2>
          <span className="badge">0</span>
        </div>
        <div className="empty-state">
          <p>No sources retrieved yet.</p>
          <p className="hint">Run a research step to retrieve sources from DuckDuckGo.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="source-panel panel">
      <div className="panel-header">
        <h2>📚 Sources</h2>
        <span className="badge">{sources.length}</span>
      </div>
      
      <div className="sources-list">
        {sources.map((source, idx) => (
          <div key={source.source_id || idx} className="source-item">
            <div 
              className="source-header"
              onClick={() => setExpandedId(expandedId === source.source_id ? null : source.source_id)}
            >
              <div className="source-title-section">
                <span className="expand-icon">
                  {expandedId === source.source_id ? '▼' : '▶'}
                </span>
                <div className="source-title-group">
                  <h3 className="source-title">{source.title}</h3>
                  <p className="source-publisher">
                    {source.publisher || 'Unknown Publisher'}
                  </p>
                </div>
              </div>
              {source.relevant_score && (
                <span className="relevance-badge">
                  {Math.round(source.relevant_score * 100)}%
                </span>
              )}
            </div>

            {expandedId === source.source_id && (
              <div className="source-details">
                <div className="detail-row">
                  <span className="label">URL:</span>
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-url">
                    {source.url}
                  </a>
                </div>
                
                {source.author && (
                  <div className="detail-row">
                    <span className="label">Author:</span>
                    <span>{source.author}</span>
                  </div>
                )}
                
                {source.publication_date && (
                  <div className="detail-row">
                    <span className="label">Published:</span>
                    <span>{new Date(source.publication_date).toLocaleDateString()}</span>
                  </div>
                )}
                
                <div className="detail-row">
                  <span className="label">Retrieved:</span>
                  <span>{new Date(source.retrieval_timestamp).toLocaleString()}</span>
                </div>

                {source.source_type && (
                  <div className="detail-row">
                    <span className="label">Type:</span>
                    <span className="type-badge">{source.source_type}</span>
                  </div>
                )}

                {source.claims_extracted && source.claims_extracted.length > 0 && (
                  <div className="claims-section">
                    <span className="label">Claims Extracted:</span>
                    <ul className="claims-list">
                      {source.claims_extracted.map((claim, i) => (
                        <li key={i}>{claim}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="panel-footer">
        <p className="footer-text">
          ✓ All sources are real URLs retrieved from DuckDuckGo
        </p>
      </div>
    </div>
  );
}

export default SourcePanel;
