/**
 * APOGEE API Client
 * Centralized API communication for all modules
 */

const API_BASE_URL = 'http://localhost:8000/api';

class ApiClient {
  /**
   * Generic fetch wrapper with error handling
   */
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ==================== DEBRIS RISK MODULE ====================

  /**
   * Get conjunction risk analysis for spacecraft
   */
  async getConjunctionRisks(spacecraftId = '25544') {
    return this.request(`/debris/risks?spacecraft_id=${spacecraftId}`);
  }

  /**
   * Get tracked objects near spacecraft
   */
  async getTrackedObjects(spacecraftId = '25544') {
    return this.request(`/debris/tracked-objects?spacecraft_id=${spacecraftId}`);
  }

  /**
   * Trigger background computation of conjunction risks
   */
  async computeConjunctionRisks(spacecraftId = '25544') {
    return this.request(`/debris/compute?spacecraft_id=${spacecraftId}`, {
      method: 'POST',
    });
  }

  // ==================== HEALTH MONITOR MODULE ====================

  /**
   * Get current health status snapshot
   */
  async getHealthStatus(spacecraftId = '25544') {
    return this.request(`/health/status?spacecraft_id=${spacecraftId}`);
  }

  /**
   * Get unified alerts feed (health + debris)
   */
  async getUnifiedAlerts(spacecraftId = '25544', limit = 50) {
    return this.request(`/health/alerts?spacecraft_id=${spacecraftId}&limit=${limit}`);
  }

  /**
   * Inject synthetic fault for demo
   */
  async injectFault(faultType, metric, durationSeconds = 60, spacecraftId = '25544') {
    return this.request(
      `/health/inject-fault?fault_type=${faultType}&metric=${metric}&duration_seconds=${durationSeconds}&spacecraft_id=${spacecraftId}`,
      { method: 'POST' }
    );
  }

  /**
   * Get anomaly detection statistics
   */
  async getAnomalyStatistics(spacecraftId = '25544') {
    return this.request(`/health/statistics?spacecraft_id=${spacecraftId}`);
  }

  /**
   * Create WebSocket connection for live telemetry
   */
  createHealthWebSocket(spacecraftId = '25544') {
    const wsUrl = `ws://localhost:8000/api/health/ws/stream?spacecraft_id=${spacecraftId}`;
    return new WebSocket(wsUrl);
  }

  // ==================== DISCOVERY MODULE ====================

  /**
   * Get transit candidates from TESS data
   */
  async getTransitCandidates(limit = 50) {
    return this.request(`/discovery/candidates?limit=${limit}`);
  }

  /**
   * Search TESS data for transits
   */
  async searchTransits(sector, camera, ccd) {
    return this.request(
      `/discovery/search?sector=${sector}&camera=${camera}&ccd=${ccd}`,
      { method: 'POST' }
    );
  }

  /**
   * Get candidate details
   */
  async getCandidateDetails(candidateId) {
    return this.request(`/discovery/candidate/${candidateId}`);
  }

  // ==================== GENERAL ====================

  /**
   * Health check
   */
  async healthCheck() {
    return this.request('/health', { baseUrl: 'http://localhost:8000' });
  }
}

// Export singleton instance
const api = new ApiClient();
export default api;