import React, { useState, lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'

// Lazy load panel components for code splitting
const HealthPanel = lazy(() => import('./components/HealthPanel'))
const DebrisPanel = lazy(() => import('./components/DebrisPanel'))
const DiscoveryPanel = lazy(() => import('./components/DiscoveryPanel'))

function App() {
  const [spacecraftId] = useState("25544") // ISS - hardcoded for MVP
  const [activeTab, setActiveTab] = useState("health")

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-apogee-blue">
                🛰️ APOGEE
              </h1>
              <div className="text-sm text-gray-600">
                <span className="font-semibold">ISS</span>
                <span className="mx-2">•</span>
                <span>NORAD {spacecraftId}</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className="badge badge-watch">
                ⚠️ Simulated Telemetry
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab("health")}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "health"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              📊 Health Monitor
            </button>
            <button
              onClick={() => setActiveTab("debris")}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "debris"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              🛰️ Debris Risk
            </button>
            <button
              onClick={() => setActiveTab("discovery")}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "discovery"
                  ? "border-purple-500 text-purple-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              🔭 Discovery
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Suspense fallback={
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading...</div>
          </div>
        }>
          {activeTab === "health" && <HealthPanel spacecraftId={spacecraftId} />}
          {activeTab === "debris" && <DebrisPanel spacecraftId={spacecraftId} />}
          {activeTab === "discovery" && <DiscoveryPanel />}
        </Suspense>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <p className="text-center text-sm text-gray-500">
            APOGEE v1.0.0 - Mission awareness at every altitude
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
