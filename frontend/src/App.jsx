import React, { useState, useEffect } from 'react';
import ResearchWorkspace from './components/ResearchWorkspace';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🔬 Discovery Engine</h1>
        <p className="subtitle">Research and Original-Idea Discovery System</p>
      </header>
      <main className="app-main">
        <ResearchWorkspace />
      </main>
    </div>
  );
}

export default App;
