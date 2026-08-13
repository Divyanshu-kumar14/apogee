import { useState, useEffect, useCallback, useMemo, memo } from 'react';
import api from '../services/api';
import AlertExplanation from './shared/AlertExplanation';
import { useWebSocket, throttle } from '../hooks/useWebSocket';

// Memoized SeverityBadge component
const SeverityBadge = memo(({ severity }) => {
  const colors = {
    nominal: 'bg-green-100 text-green-800',
    watch: 'bg-yellow-100 text-yellow-800',
    critical: 'bg-red-100 text-red-800'
  };
  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold ${colors[severity] || colors.nominal}`}>
      {severity.toUpperCase()}
    </span>
  );
});
SeverityBadge.displayName = 'SeverityBadge';

// Memoized MetricCard component
const MetricCard = memo(({ metricName, data }) => {
  const displayName = metricName
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">{displayName}</h3>
        <SeverityBadge severity={data.severity} />
      </div>
      <div className="mt-2">
        <div className="text-3xl font-bold text-gray-900">
          {data.value.toFixed(2)}
        </div>
        <div className="text-sm text-gray-500">{data.unit}</div>
      </div>
      {data.normal_range && (
        <div className="mt-3 text-xs text-gray-500">
          Normal: {data.normal_range[0]} - {data.normal_range[1]} {data.unit}
        </div>
      )}
      {data.anomaly_score !== undefined && (
        <div className="mt-2 text-xs text-gray-600">
          Anomaly Score: {data.anomaly_score.toFixed(3)}
        </div>
      )}
    </div>
  );
});
MetricCard.displayName = 'MetricCard';

// Memoized AlertItem component
const AlertItem = memo(({ alert, onExplain }) => {
  return (
    <div className="p-4 hover:bg-gray-50">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <SeverityBadge severity={alert.severity} />
            <span className="text-xs text-gray-500">
              {alert.source === 'health' ? '🏥 Health' : '🛰️ Debris'}
            </span>
            <span className="text-xs text-gray-500">
              {alert.response_category}
            </span>
          </div>
          <p className="text-sm text-gray-900">{alert.message}</p>
          {alert.explained && alert.explanation && (
            <p className="text-xs text-gray-600 mt-1">
              💡 Explanation available
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 ml-4">
          <div className="text-xs text-gray-500">
            {new Date(alert.timestamp).toLocaleTimeString()}
          </div>
          <button
            onClick={() => onExplain(alert)}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
          >
            🤖 Explain
          </button>
        </div>
      </div>
    </div>
  );
});
AlertItem.displayName = 'AlertItem';

const HealthPanel = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [faultInjection, setFaultInjection] = useState({
    type: 'battery_drift',
    metric: 'battery_voltage',
    duration: 60
  });
  const [selectedAlert, setSelectedAlert] = useState(null);

  // Fetch initial health status
  const fetchHealthStatus = useCallback(async () => {
    try {
      const data = await api.getHealthStatus();
      setHealthStatus(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch health status');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch unified alerts
  const fetchAlerts = useCallback(async () => {
    try {
      const data = await api.getUnifiedAlerts();
      setAlerts(data.alerts || []);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    }
  }, []);

  // Throttled telemetry update handler (max 10 updates/sec)
  const handleTelemetryUpdate = useMemo(
    () => throttle((data) => {
      if (data.type === 'telemetry_update') {
        setHealthStatus(prev => {
          if (!prev) return prev;
          
          // Only update if value actually changed
          const currentValue = prev.metrics[data.metric_name]?.value;
          if (currentValue === data.value) return prev;
          
          const newMetrics = { ...prev.metrics };
          newMetrics[data.metric_name] = {
            value: data.value,
            unit: data.unit,
            timestamp: data.timestamp,
            severity: data.anomaly.severity,
            anomaly_score: data.anomaly.anomaly_score,
            normal_range: prev.metrics[data.metric_name]?.normal_range
          };

          // Update overall status
          const severities = Object.values(newMetrics).map(m => m.severity);
          let overall_status = 'nominal';
          if (severities.includes('critical')) overall_status = 'critical';
          else if (severities.includes('watch')) overall_status = 'watch';

          return {
            ...prev,
            metrics: newMetrics,
            overall_status,
            timestamp: data.timestamp
          };
        });

        // Refresh alerts if anomaly detected
        if (data.anomaly.is_anomaly) {
          fetchAlerts();
        }
      }
    }, 100),
    [fetchAlerts]
  );

  // WebSocket connection with automatic reconnection
  const { isConnected } = useWebSocket(
    'ws://localhost:8000/api/health/ws/stream?spacecraft_id=25544',
    {
      onMessage: handleTelemetryUpdate,
      onError: (error) => console.error('WebSocket error:', error),
      reconnectInterval: 1000,
      maxReconnectAttempts: 5
    }
  );

  // Initial data fetch
  useEffect(() => {
    fetchHealthStatus();
    fetchAlerts();
  }, [fetchHealthStatus, fetchAlerts]);

  // Inject fault for demo
  const handleInjectFault = useCallback(async () => {
    try {
      await api.injectFault(
        faultInjection.type,
        faultInjection.metric,
        faultInjection.duration
      );
      alert(`Fault injected: ${faultInjection.type} on ${faultInjection.metric}`);
    } catch (err) {
      alert('Failed to inject fault: ' + err.message);
    }
  }, [faultInjection]);

  // Memoize alert explanation handler
  const handleExplainAlert = useCallback((alert) => {
    setSelectedAlert(alert);
  }, []);

  // Memoize close modal handler
  const handleCloseModal = useCallback(() => {
    setSelectedAlert(null);
  }, []);

  // Memoize metrics array for rendering
  const metricsArray = useMemo(() => {
    if (!healthStatus?.metrics) return [];
    return Object.entries(healthStatus.metrics);
  }, [healthStatus?.metrics]);

  // Memoize alert statistics
  const alertStats = useMemo(() => {
    return alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
      return acc;
    }, { critical: 0, watch: 0, nominal: 0 });
  }, [alerts]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading health data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4">
        <p className="text-red-800">{error}</p>
        <button 
          onClick={fetchHealthStatus}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with overall status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Health Monitor</h2>
            <p className="text-sm text-gray-500 mt-1">
              ISS (NORAD 25544) • Real-time telemetry with ML anomaly detection
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
            <SeverityBadge severity={healthStatus?.overall_status || 'nominal'} />
          </div>
        </div>
      </div>

      {/* Telemetry Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricsArray.map(([metricName, data]) => (
          <MetricCard key={metricName} metricName={metricName} data={data} />
        ))}
      </div>

      {/* Fault Injection (Demo Controls) */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          🧪 Demo Controls - Fault Injection
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <select
            value={faultInjection.type}
            onChange={(e) => setFaultInjection({...faultInjection, type: e.target.value})}
            className="px-3 py-2 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="battery_drift">Battery Drift</option>
            <option value="temp_spike">Temperature Spike</option>
            <option value="attitude_oscillation">Attitude Oscillation</option>
            <option value="signal_degradation">Signal Degradation</option>
          </select>
          <select
            value={faultInjection.metric}
            onChange={(e) => setFaultInjection({...faultInjection, metric: e.target.value})}
            className="px-3 py-2 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="battery_voltage">Battery Voltage</option>
            <option value="internal_temp_c">Internal Temperature</option>
            <option value="attitude_deviation_deg">Attitude Deviation</option>
            <option value="signal_strength_db">Signal Strength</option>
          </select>
          <input
            type="number"
            value={faultInjection.duration}
            onChange={(e) => setFaultInjection({...faultInjection, duration: parseInt(e.target.value)})}
            placeholder="Duration (seconds)"
            className="px-3 py-2 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleInjectFault}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
          >
            Inject Fault
          </button>
        </div>
        <p className="text-xs text-blue-700 mt-2">
          Inject synthetic faults to demonstrate IsolationForest anomaly detection
        </p>
      </div>

      {/* Unified Alerts Feed */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                🚨 Unified Alerts Feed
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Combined health anomalies and debris conjunctions (Integration Proof)
              </p>
            </div>
            {alerts.length > 0 && (
              <div className="flex items-center gap-2 text-xs">
                {alertStats.critical > 0 && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded">
                    {alertStats.critical} Critical
                  </span>
                )}
                {alertStats.watch > 0 && (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                    {alertStats.watch} Watch
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          {alerts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No alerts - all systems nominal
            </div>
          ) : (
            alerts.map((alert) => (
              <AlertItem 
                key={alert.id} 
                alert={alert} 
                onExplain={handleExplainAlert}
              />
            ))
          )}
        </div>
      </div>

      {/* ML Detection Info */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-purple-900 mb-2">
          🤖 IsolationForest Anomaly Detection
        </h4>
        <p className="text-xs text-purple-800">
          Using scikit-learn IsolationForest for ML-based anomaly detection. 
          The model learns normal behavior patterns and identifies deviations without 
          assuming normal distribution. Anomaly scores closer to -1 indicate higher anomaly likelihood.
        </p>
      </div>

      {/* IBM Granite Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">
          🤖 IBM Granite LLM Explanations
        </h4>
        <p className="text-xs text-blue-800">
          Click "Explain" on any alert to generate a detailed, context-aware explanation using IBM Granite LLM. 
          The AI provides technical analysis, implications, and recommended actions for each alert.
        </p>
      </div>

      {/* Alert Explanation Modal */}
      {selectedAlert && (
        <AlertExplanation
          alert={selectedAlert}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default HealthPanel;
