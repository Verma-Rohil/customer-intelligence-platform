/**
 * Centralized API client for FastAPI backend communication.
 * All fetch calls route through here for consistent error handling.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error ${response.status}: ${errorBody}`);
  }
  
  return response.json();
}

export const api = {
  // Health
  health: () => request('/health'),

  // Model Info
  modelInfo: () => request('/model-info'),

  // Churn Prediction
  predictChurn: (features) =>
    request('/predict-churn', {
      method: 'POST',
      body: JSON.stringify(features),
    }),

  // Customer Segmentation
  segmentCustomer: (features) =>
    request('/segment', {
      method: 'POST',
      body: JSON.stringify(features),
    }),

  // Campaign Simulation
  simulateCampaign: (payload) =>
    request('/simulate-campaign', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Executive Summary (KPIs, distributions)
  executiveSummary: () => request('/api/executive-summary'),

  // Feature Importance from XGBoost
  featureImportance: () => request('/api/feature-importance'),

  // Segment data for deep dive
  segmentData: () => request('/api/segment-data'),
};
