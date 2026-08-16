import React, { useState } from 'react';
import './AnswerPanel.css';

function AnswerPanel({ jobData }) {
  const answer = jobData?.quick_answer;

  if (!answer) {
    return (
      <div className="answer-panel panel">
        <div className="panel-header">
          <h2>📝 Current Answer</h2>
        </div>
        <div className="empty-state">
          <p>No answer generated yet.</p>
          <p className="hint">Press "Get Current Answer" to generate based on current research.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="answer-panel panel">
      <div className="panel-header">
        <h2>📝 Current Answer</h2>
      </div>
      
      <div className="answer-content">
        <div className="answer-text">
          <p>{answer}</p>
        </div>
        
        <div className="answer-context">
          <p className="context-label">Based on:</p>
          <ul className="context-list">
            <li>✓ {jobData?.sources?.length || 0} sources retrieved</li>
            <li>✓ {jobData?.hypotheses?.length || 0} hypotheses generated</li>
            <li>✓ Latest research state</li>
          </ul>
        </div>

        <div className="answer-footer">
          <p className="footer-note">
            This is the best current answer based on the research completed so far.
            Deep Discovery can continue to refine the answer.
          </p>
        </div>
      </div>
    </div>
  );
}

export default AnswerPanel;
