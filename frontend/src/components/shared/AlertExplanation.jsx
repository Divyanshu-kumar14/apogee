import { useState } from 'react';
import api from '../../services/api';

const AlertExplanation = ({ alert, onClose }) => {
  const [explanation, setExplanation] = useState(alert.explanation || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExplain = async () => {
    if (explanation) return; // Already have explanation

    try {
      setLoading(true);
      setError(null);
      const data = await api.explainAlert(alert.id);
      setExplanation(data.explanation);
    } catch (err) {
      setError('Failed to generate explanation: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-explain if not already explained
  useState(() => {
    if (!alert.explained && !explanation) {
      handleExplain();
    }
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
          <div className="flex items-center gap-3">
            <div className="text-2xl">🤖</div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                IBM Granite LLM Explanation
              </h3>
              <p className="text-sm text-gray-500">
                AI-powered alert analysis and recommendations
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Alert Summary */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'watch' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {alert.source === 'health' ? '🏥 Health' : '🛰️ Debris'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {alert.response_category}
                  </span>
                </div>
                <p className="text-sm text-gray-900">{alert.message}</p>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              {new Date(alert.timestamp).toLocaleString()}
            </div>
          </div>

          {/* Explanation */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-600">Generating explanation with IBM Granite LLM...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
              <button
                onClick={handleExplain}
                className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Retry
              </button>
            </div>
          )}

          {explanation && !loading && (
            <div className="prose prose-sm max-w-none">
              <div 
                className="text-gray-800 leading-relaxed"
                dangerouslySetInnerHTML={{ 
                  __html: explanation
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n\n/g, '</p><p class="mt-4">')
                    .replace(/^(.+)$/gm, '<p>$1</p>')
                    .replace(/⚠️/g, '<span class="text-yellow-600">⚠️</span>')
                }}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="font-semibold">Powered by:</span>
              <span className="text-blue-600 font-mono">IBM Granite LLM</span>
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertExplanation;
