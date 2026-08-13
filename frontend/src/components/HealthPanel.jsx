import React from 'react'

export default function HealthPanel({ spacecraftId }) {
  return (
    <div className="panel">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Health Monitor
        </h2>
        <p className="text-sm text-gray-600">
          Real-time telemetry monitoring with ML-based anomaly detection
        </p>
      </div>

      {/* Placeholder content */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Phase 0: Placeholder
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>Health Monitor will be implemented in Phase 2 with:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Live telemetry streaming (4 metrics)</li>
                <li>IsolationForest anomaly detection</li>
                <li>Unified alerts feed (health + debris)</li>
                <li>Fault injection for demo</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Metric gauges placeholder */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        {['Battery Voltage', 'Internal Temperature', 'Attitude Deviation', 'Signal Strength'].map((metric) => (
          <div key={metric} className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
            <p className="text-sm text-gray-500">{metric}</p>
            <p className="text-2xl font-bold text-gray-400 mt-2">--</p>
          </div>
        ))}
      </div>
    </div>
  )
}
