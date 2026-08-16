import React, { useState } from 'react';
import './ObjectiveInput.css';

function ObjectiveInput({ onSubmit, isLoading, error, initialValue, isDisabled }) {
  const [objective, setObjective] = useState(initialValue || '');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (objective.trim() && !isDisabled && !isLoading) {
      onSubmit(objective);
    }
  };

  return (
    <div className="objective-input">
      <h2>🎯 Research Objective</h2>
      {!isDisabled ? (
        <form onSubmit={handleSubmit}>
          <textarea
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder="Find a genuinely novel explanation for..."
            className="objective-textarea"
            disabled={isLoading}
            required
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isLoading || !objective.trim()}
          >
            {isLoading ? 'Creating Job...' : 'Create Research Job'}
          </button>
        </form>
      ) : (
        <div className="objective-display">
          <p>{objective}</p>
        </div>
      )}
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default ObjectiveInput;
