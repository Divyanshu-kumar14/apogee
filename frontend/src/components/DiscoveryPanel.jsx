import React from 'react'

export default function DiscoveryPanel() {
  return (
    <div className="panel">
      {/* Header with clear separation */}
      <div className="border-l-4 border-purple-500 pl-4 mb-6">
        <h2 className="text-2xl font-bold text-purple-900 mb-2">
          🔭 Discovery Module
        </h2>
        <p className="text-sm text-gray-600 mb-1">
          Science Tool — Independent of spacecraft telemetry
        </p>
        <p className="text-xs text-gray-500">
          TESS exoplanet transit detection using BLS periodogram + ML vetting
        </p>
      </div>

      {/* Placeholder content */}
      <div className="bg-purple-50 border-l-4 border-purple-400 p-4 rounded mb-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-purple-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-purple-800">
              Phase 3: Science Module
            </h3>
            <div className="mt-2 text-sm text-purple-700">
              <p>Discovery Module will be implemented in Phase 3 with:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>TESS light curve caching (5-10 targets, no live MAST calls)</li>
                <li>BLS periodogram for transit detection</li>
                <li>ML vetting classifier (distinguishes planets from false positives)</li>
                <li>Folded light curve visualization</li>
                <li>Intentionally NOT integrated with operational alerts</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Layout placeholder */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 border-2 border-dashed border-gray-300 rounded-lg p-4">
          <p className="text-sm text-gray-500 text-center">Candidate List</p>
        </div>
        <div className="col-span-2 border-2 border-dashed border-gray-300 rounded-lg p-8">
          <p className="text-sm text-gray-500 text-center">Folded Light Curve Chart</p>
        </div>
      </div>
    </div>
  )
}
