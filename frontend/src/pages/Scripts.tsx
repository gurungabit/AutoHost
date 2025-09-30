import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import type { AutomationScript } from '../types/automation';

export function Scripts() {
  const navigate = useNavigate();
  const [scripts, setScripts] = useState<Array<Partial<AutomationScript>>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [executing, setExecuting] = useState<string | null>(null);

  useEffect(() => {
    loadScripts();
  }, []);

  const loadScripts = async () => {
    try {
      const response = await apiClient.listScripts();
      setScripts(response.scripts);
    } catch (error) {
      console.error('Failed to load scripts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecute = async (scriptId: string) => {
    if (!confirm('Execute this automation script?')) return;

    setExecuting(scriptId);
    try {
      const result = await apiClient.executeScript(scriptId);
      alert(`Execution completed!\nSession: ${result.session_id}\nLogs: ${result.logs.length} entries`);
      console.log('Execution logs:', result.logs);
    } catch (error) {
      console.error('Execution failed:', error);
      alert('Script execution failed');
    } finally {
      setExecuting(null);
    }
  };

  const handleDelete = async (scriptId: string) => {
    if (!confirm('Are you sure you want to delete this script?')) return;

    try {
      await apiClient.deleteScript(scriptId);
      await loadScripts();
    } catch (error) {
      console.error('Failed to delete script:', error);
      alert('Failed to delete script');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-xl text-gray-600 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Automation Scripts
          </h1>
          <button
            onClick={() => navigate('/builder')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors font-medium"
          >
            + New Script
          </button>
        </div>

        {scripts.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">No automation scripts yet</p>
            <button
              onClick={() => navigate('/builder')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors"
            >
              Create Your First Script
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scripts.map((script) => (
              <div
                key={script.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  {script.name}
                </h3>
                {script.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {script.description}
                  </p>
                )}
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  <p>Host: {script.host}</p>
                  <p>Steps: {script.steps_count || 0}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExecute(script.id!)}
                    disabled={executing === script.id}
                    className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md transition-colors text-sm font-medium"
                  >
                    {executing === script.id ? 'Running...' : 'Execute'}
                  </button>
                  <button
                    onClick={() => handleDelete(script.id!)}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
