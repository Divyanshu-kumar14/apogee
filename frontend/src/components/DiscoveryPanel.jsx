import { useState, useEffect } from 'react';
import api from '../services/api';

const DiscoveryPanel = () => {
  const [candidates, setCandidates] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [searchParams, setSearchParams] = useState({
    sector: 1,
    camera: 1,
    ccd: 1
  });

  // Fetch candidates on mount
  useEffect(() => {
    fetchCandidates();
    fetchStatistics();
  }, []);

  const fetchCandidates = async (minConfidence = 0.0) => {
    try {
      setLoading(true);
      const data = await api.getTransitCandidates(50, minConfidence);
      setCandidates(data.candidates || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch transit candidates');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const data = await api.getDiscoveryStatistics();
      setStatistics(data);
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  const handleSearch = async () => {
    try {
      setSearching(true);
      setError(null);
      await api.searchTransits(
        searchParams.sector,
        searchParams.camera,
        searchParams.ccd
      );
      alert(`Transit search started for Sector ${searchParams.sector}. This will take 2-5 minutes.`);
      
      // Refresh candidates after 30 seconds
      setTimeout(() => {
        fetchCandidates();
        fetchStatistics();
      }, 30000);
    } catch (err) {
      setError('Failed to start transit search: ' + err.message);
    } finally {
      setSearching(false);
    }
  };

  const handleCandidateClick = async (candidate) => {
    try {
      const data = await api.getCandidateDetails(candidate.id);
      setSelectedCandidate(data);
    } catch (err) {
      alert('Failed to fetch candidate details: ' + err.message);
    }
  };

  // Disposition badge component
  const DispositionBadge = ({ disposition }) => {
    const colors = {
      CONFIRMED: 'bg-green-100 text-green-800',
      CANDIDATE: 'bg-blue-100 text-blue-800',
      LIKELY: 'bg-cyan-100 text-cyan-800',
      FALSE_POSITIVE: 'bg-red-100 text-red-800',
      LIKELY_FP: 'bg-orange-100 text-orange-800',
      UNCERTAIN: 'bg-gray-100 text-gray-800'
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${colors[disposition] || colors.UNCERTAIN}`}>
        {disposition.replace('_', ' ')}
      </span>
    );
  };

  // Confidence bar component
  const ConfidenceBar = ({ confidence }) => {
    const percentage = (confidence * 100).toFixed(0);
    const color = confidence >= 0.8 ? 'bg-green-500' : confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';
    
    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`${color} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    );
  };

  if (loading && candidates.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading transit candidates...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Discovery Module</h2>
            <p className="text-sm text-gray-500 mt-1">
              TESS exoplanet transit detection with ML vetting
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">
              {statistics?.total_candidates || 0}
            </div>
            <div className="text-sm text-gray-500">Total Candidates</div>
          </div>
        </div>
      </div>

      {/* Search Controls */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-purple-900 mb-3">
          🔭 Search TESS Data
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Sector</label>
            <input
              type="number"
              min="1"
              max="100"
              value={searchParams.sector}
              onChange={(e) => setSearchParams({...searchParams, sector: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-purple-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Camera</label>
            <select
              value={searchParams.camera}
              onChange={(e) => setSearchParams({...searchParams, camera: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-purple-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {[1, 2, 3, 4].map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">CCD</label>
            <select
              value={searchParams.ccd}
              onChange={(e) => setSearchParams({...searchParams, ccd: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-purple-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {[1, 2, 3, 4].map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={searching}
              className={`w-full px-4 py-2 rounded font-medium ${
                searching 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-purple-600 hover:bg-purple-700'
              } text-white`}
            >
              {searching ? 'Searching...' : 'Search Transits'}
            </button>
          </div>
        </div>
        <p className="text-xs text-purple-700 mt-2">
          Runs BLS periodogram + Random Forest ML vetting. Takes 2-5 minutes.
        </p>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">High Confidence</div>
            <div className="text-2xl font-bold text-green-600">
              {statistics.by_confidence?.high || 0}
            </div>
            <div className="text-xs text-gray-400">≥ 80%</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Medium Confidence</div>
            <div className="text-2xl font-bold text-yellow-600">
              {statistics.by_confidence?.medium || 0}
            </div>
            <div className="text-xs text-gray-400">60-80%</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Confirmed</div>
            <div className="text-2xl font-bold text-blue-600">
              {statistics.by_disposition?.CONFIRMED || 0}
            </div>
            <div className="text-xs text-gray-400">ML Verified</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">False Positives</div>
            <div className="text-2xl font-bold text-red-600">
              {statistics.by_disposition?.FALSE_POSITIVE || 0}
            </div>
            <div className="text-xs text-gray-400">Rejected</div>
          </div>
        </div>
      )}

      {/* Candidates Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Transit Candidates
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => fetchCandidates(0.8)}
              className="px-3 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200"
            >
              High Confidence
            </button>
            <button
              onClick={() => fetchCandidates(0.0)}
              className="px-3 py-1 text-xs bg-gray-100 text-gray-800 rounded hover:bg-gray-200"
            >
              All
            </button>
          </div>
        </div>
        
        {error && (
          <div className="p-4 bg-red-50 border-b border-red-200">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <div className="overflow-x-auto">
          {candidates.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No transit candidates found. Run a search to discover exoplanets!
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">TIC ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sector</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period (days)</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Depth (%)</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SNR</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Disposition</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {candidates.map((candidate) => (
                  <tr key={candidate.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">
                      {candidate.tic_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {candidate.sector}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {candidate.period.toFixed(3)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {(candidate.depth * 100).toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {candidate.snr.toFixed(1)}
                    </td>
                    <td className="px-4 py-3">
                      <DispositionBadge disposition={candidate.disposition} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        <ConfidenceBar confidence={candidate.vetting_confidence} />
                        <div className="text-xs text-gray-500">
                          {(candidate.vetting_confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleCandidateClick(candidate)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Candidate Details Modal */}
      {selectedCandidate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-900">
                TIC {selectedCandidate.candidate.tic_id} - Sector {selectedCandidate.candidate.sector}
              </h3>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Candidate Info */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs text-gray-500">Period</div>
                  <div className="text-lg font-semibold">{selectedCandidate.candidate.period.toFixed(3)} days</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Depth</div>
                  <div className="text-lg font-semibold">{(selectedCandidate.candidate.depth * 100).toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Duration</div>
                  <div className="text-lg font-semibold">{(selectedCandidate.candidate.duration * 24).toFixed(1)} hrs</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">SNR</div>
                  <div className="text-lg font-semibold">{selectedCandidate.candidate.snr.toFixed(1)}</div>
                </div>
              </div>

              {/* Disposition and Confidence */}
              <div className="flex items-center gap-4">
                <DispositionBadge disposition={selectedCandidate.candidate.disposition} />
                <div className="flex-1">
                  <div className="text-xs text-gray-500 mb-1">ML Vetting Confidence</div>
                  <ConfidenceBar confidence={selectedCandidate.candidate.vetting_confidence} />
                </div>
              </div>

              {/* Light Curve Placeholder */}
              <div className="bg-gray-50 rounded p-4 text-center">
                <p className="text-sm text-gray-600">
                  📊 Light curve visualization would appear here
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {selectedCandidate.light_curve.time.length} data points available
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ML Info */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-indigo-900 mb-2">
          🤖 ML-Based Transit Vetting
        </h4>
        <p className="text-xs text-indigo-800">
          Using Random Forest classifier trained on transit features to distinguish real planets from 
          eclipsing binaries, instrumental artifacts, and stellar variability. Features include BLS power, 
          SNR, transit shape, secondary eclipse depth, and odd-even transit consistency.
        </p>
      </div>

      {/* Important Note */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-yellow-900 mb-2">
          ⚠️ Discovery Module - Separate Science Tool
        </h4>
        <p className="text-xs text-yellow-800">
          This module is intentionally NOT integrated with the alerts system. It serves as a separate 
          scientific discovery tool for exoplanet research, independent from operational spacecraft monitoring.
        </p>
      </div>
    </div>
  );
};

export default DiscoveryPanel;