import React, { useState, lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { MeshGradientBackground } from './components/shared/AnimatedBackground'
import { fadeInVariants, tabVariants } from './utils/animations'

// Lazy load panel components for code splitting
const HealthPanel = lazy(() => import('./components/HealthPanel'))
const DebrisPanel = lazy(() => import('./components/DebrisPanel'))
const DiscoveryPanel = lazy(() => import('./components/DiscoveryPanel'))

function App() {
  const [spacecraftId] = useState("25544") // ISS - hardcoded for MVP
  const [activeTab, setActiveTab] = useState("health")
  const [direction, setDirection] = useState(0)

  const handleTabChange = (newTab) => {
    const tabs = ["health", "debris", "discovery"]
    const currentIndex = tabs.indexOf(activeTab)
    const newIndex = tabs.indexOf(newTab)
    setDirection(newIndex > currentIndex ? 1 : -1)
    setActiveTab(newTab)
  }

  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Animated Background */}
      <MeshGradientBackground />
      {/* Header with Glass Morphism */}
      <motion.header 
        className="glass-card border-b border-white/20 sticky top-0 z-50"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div 
              className="flex items-center space-x-4"
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h1 className="text-2xl font-bold text-apogee-blue">
                🛰️ APOGEE
              </h1>
              <div className="text-sm text-gray-600">
                <span className="font-semibold">ISS</span>
                <span className="mx-2">•</span>
                <span>NORAD {spacecraftId}</span>
              </div>
            </motion.div>
            
            <motion.div 
              className="flex items-center space-x-3"
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <span className="badge badge-watch">
                ⚠️ Simulated Telemetry
              </span>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Navigation Tabs with Glass Effect */}
      <nav className="glass-card border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <motion.button
              onClick={() => handleTabChange("health")}
              className={`py-4 px-2 border-b-2 font-medium text-sm relative ${
                activeTab === "health"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              📊 Health Monitor
              {activeTab === "health" && (
                <motion.div
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"
                  layoutId="activeTab"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
            </motion.button>
            <motion.button
              onClick={() => handleTabChange("debris")}
              className={`py-4 px-2 border-b-2 font-medium text-sm relative ${
                activeTab === "debris"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🛰️ Debris Risk
              {activeTab === "debris" && (
                <motion.div
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"
                  layoutId="activeTab"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
            </motion.button>
            <motion.button
              onClick={() => handleTabChange("discovery")}
              className={`py-4 px-2 border-b-2 font-medium text-sm relative ${
                activeTab === "discovery"
                  ? "border-purple-500 text-purple-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🔭 Discovery
              {activeTab === "discovery" && (
                <motion.div
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500"
                  layoutId="activeTab"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
            </motion.button>
          </div>
        </div>
      </nav>

      {/* Main Content with Animated Transitions */}
      <main className="max-w-7xl mx-auto px-4 py-6 relative">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={activeTab}
            custom={direction}
            variants={tabVariants}
            initial="enter"
            animate="center"
            exit="exit"
          >
            <Suspense fallback={
              <motion.div 
                className="flex items-center justify-center h-64"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="glass-card px-8 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">Loading...</span>
                  </div>
                </div>
              </motion.div>
            }>
              {activeTab === "health" && <HealthPanel spacecraftId={spacecraftId} />}
              {activeTab === "debris" && <DebrisPanel spacecraftId={spacecraftId} />}
              {activeTab === "discovery" && <DiscoveryPanel />}
            </Suspense>
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer with Glass Effect */}
      <motion.footer 
        className="glass-card border-t border-white/20 mt-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <p className="text-center text-sm text-gray-600">
            APOGEE v1.0.0 - Mission awareness at every altitude
          </p>
        </div>
      </motion.footer>
    </div>
  )
}

export default App
