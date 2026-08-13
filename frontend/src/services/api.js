/**
 * API Client for APOGEE Backend
 * Handles all HTTP requests to FastAPI backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health Monitor API
export const healthAPI = {
  getStatus: async (spacecraftId = '25544') => {
    const response = await apiClient.get(`/api/health/status`, {
      params: { spacecraft_id: spacecraftId }
    });
    return response.data;
  },

  getAlerts: async (spacecraftId = '25544', limit = 50) => {
    const response = await apiClient.get(`/api/health/alerts`, {
      params: { spacecraft_id: spacecraftId, limit }
    });
    return response.data;
  },

  injectFault: async (faultType, metric, durationSeconds = 60) => {
    const response = await apiClient.post(`/api/health/inject-fault`, null, {
      params: {
        fault_type: faultType,
        metric: metric,
        duration_seconds: durationSeconds
      }
    });
    return response.data;
  },
};

// Debris Risk API
export const debrisAPI = {
  refresh: async (spacecraftId = '25544') => {
    const response = await apiClient.post(`/api/debris/refresh`, null, {
      params: { spacecraft_id: spacecraftId }
    });
    return response.data;
  },

  getRisks: async (spacecraftId = '25544', minRiskScore = 0, limit = 50) => {
    const response = await apiClient.get(`/api/debris/risks`, {
      params: {
        spacecraft_id: spacecraftId,
        min_risk_score: minRiskScore,
        limit: limit
      }
    });
    return response.data;
  },

  getObjects: async (limit = 100) => {
    const response = await apiClient.get(`/api/debris/objects`, {
      params: { limit }
    });
    return response.data;
  },
};

// Discovery Module API
export const discoveryAPI = {
  getCandidates: async (minConfidence = 0.0, onlyLikelyPlanets = false) => {
    const response = await apiClient.get(`/api/discovery/candidates`, {
      params: {
        min_confidence: minConfidence,
        only_likely_planets: onlyLikelyPlanets
      }
    });
    return response.data;
  },

  getCandidate: async (ticId) => {
    const response = await apiClient.get(`/api/discovery/candidates/${ticId}`);
    return response.data;
  },

  getLightcurve: async (ticId) => {
    const response = await apiClient.get(`/api/discovery/candidates/${ticId}/lightcurve`);
    return response.data;
  },
};

// General API
export const generalAPI = {
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
