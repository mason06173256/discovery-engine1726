import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Research Job Operations
export const jobsApi = {
  createJob: (userObjective, executionMode = 'iterative') => 
    api.post('/jobs', { user_objective: userObjective, execution_mode: executionMode }),
  
  listJobs: () => 
    api.get('/jobs'),
  
  getJob: (jobId) => 
    api.get(`/jobs/${jobId}`),
  
  startJob: (jobId) => 
    api.post(`/jobs/${jobId}/start`),
  
  pauseJob: (jobId) => 
    api.post(`/jobs/${jobId}/pause`),
  
  resumeJob: (jobId) => 
    api.post(`/jobs/${jobId}/resume`),
  
  runResearch: (jobId, query) => 
    api.post(`/jobs/${jobId}/research`, { query }),
  
  getAnswer: (jobId) => 
    api.post(`/jobs/${jobId}/answer`),
  
  addSource: (jobId, sourceData) => 
    api.post(`/jobs/${jobId}/sources`, sourceData),
  
  addHypothesis: (jobId, hypothesisData) => 
    api.post(`/jobs/${jobId}/hypotheses`, hypothesisData),
};

// Server-Sent Events for live updates
export const eventsApi = {
  subscribeToEvents: (jobId, onEvent, onError) => {
    const eventSource = new EventSource(`${API_BASE_URL}/jobs/${jobId}/events`);
    
    eventSource.addEventListener('event', (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent(data);
      } catch (e) {
        console.error('Failed to parse event:', e);
      }
    });
    
    eventSource.addEventListener('error', () => {
      onError();
      eventSource.close();
    });
    
    return eventSource;
  },
  
  closeConnection: (eventSource) => {
    if (eventSource) {
      eventSource.close();
    }
  }
};

export default api;
