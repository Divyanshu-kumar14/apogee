import React, { useState, useEffect } from 'react'
import { debrisAPI } from '../services/api'

export default function DebrisPanel({ spacecraftId }) {
  const [risks, setRisks] = useState([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [sortField, setSortField] = useState('risk_score')
  const [sortDirection, setSortDirection] = useState('desc')
  const [error, setError] = useState(null)

  useEffect(() => {
    loadRisks()
  }, [spacecraftId])

  const loadRisks = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await debrisAPI.getRisks(spacecraftId)
      setRisks(data.risks || [])
      setLastUpdate(new Date())
    } catch (err) {
      console.error('Failed to load risks:', err)
      setError('Failed to load risk data. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    setError(null)
    try {
      await debrisAPI.refresh(spacecraftId)
      // Wait a bit for background task to complete
      setTimeout(async () => {
        await loadRisks()
        setRefreshing(false)
      }, 5000)
    } catch (err) {
      console.error('Refresh failed:', err)
      setError('Failed to refresh data. Make sure the backend is running.')
      setRefreshing(false)
    }
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const sortedRisks = [...risks].sort((a, b) => {
    const multiplier = sortDirection === 'asc' ? 1 : -1
    return multiplier * (a[sortField] - b[sortField])
  })

  const getSeverityColor = (score) => {
    if (score >= 70) return 'text-red-600 bg-red-50'
    if (score >= 40) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  const getSeverityBadge = (score) => {
    if (score >= 70) return { text: 'CRITICAL', color: 'bg-red-100 text-red-800' }
    if (score >= 40) return { text: 'WATCH', color: 'bg-yellow-100 text-yellow-800' }
    return { text: 'NOMINAL', color: 'bg-green-100 text-green-800' }
  }

  return (
    <div className="panel">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Debris Risk Assessment
            </h2>
            <p className="text-sm text-gray-600">
              Orbital conjunction analysis using CelesTrak TLE data and SGP4 propagation
            </p>
          </div>
          <button 
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn-primary"
          >
            {refreshing ? '🔄 Refreshing...' : '🔄 Refresh Risk Data'}
          </button>
        </div>
      </div>

      {/* TLE Disclaimer */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-800">
              ⚠️ Risk scores are derived from public two-line element (TLE) data, 
              which carries inherent positional uncertainty. This is a relative 
              risk indicator, not a collision probability.
            </p>
          </div>
        </div>
      </div>

      {/* Last Update Info */}
      {lastUpdate && (
        <div className="mb-4 text-sm text-gray-600">
          Last updated: {lastUpdate.toLocaleString()}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading risk data...</p>
        </div>
      )}

      {/* Risk Table */}
      {!loading && risks.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b-2 border-gray-200">
                <th 
                  onClick={() => handleSort('object_norad_id')}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200"
                >
                  Object ID {sortField === 'object_norad_id' && (sortDirection === 'asc' ? '↑' : '↓')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Object Name
                </th>
                <th 
                  onClick={() => handleSort('closest_approach_km')}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200"
                >
                  Closest Approach (km) {sortField === 'closest_approach_km' && (sortDirection === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  onClick={() => handleSort('relative_velocity_kmps')}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200"
                >
                  Rel. Velocity (km/s) {sortField === 'relative_velocity_kmps' && (sortDirection === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  onClick={() => handleSort('risk_score')}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200"
                >
                  Risk Score {sortField === 'risk_score' && (sortDirection === 'asc' ? '↑' : '↓')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedRisks.map((risk) => {
                const badge = getSeverityBadge(risk.risk_score)
                return (
                  <tr key={risk.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {risk.object_norad_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {risk.object_name}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {risk.closest_approach_km.toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {risk.relative_velocity_kmps.toFixed(2)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1 rounded-full font-semibold text-sm ${getSeverityColor(risk.risk_score)}`}>
                          {risk.risk_score.toFixed(1)}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${badge.color}`}>
                          {badge.text}
                        </span>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!loading && risks.length === 0 && !error && (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p className="mt-2 text-gray-500">No risk data available</p>
          <p className="text-sm text-gray-400 mt-1">Click "Refresh Risk Data" to compute conjunction risks</p>
        </div>
      )}
    </div>
  )
}