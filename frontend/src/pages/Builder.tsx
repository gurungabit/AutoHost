import { useState } from 'react';
import { ConnectionForm } from '../components/ConnectionForm';
import { TerminalEmulator } from '../components/TerminalEmulator';
import { StepEditor } from '../components/StepEditor';
import { apiClient } from '../api/client';
import type { AutomationStep, AutomationScript, ConnectionRequest } from '../types/automation';

export function Builder() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionInfo, setConnectionInfo] = useState<ConnectionRequest | null>(null);

  const [script, setScript] = useState<AutomationScript>({
    id: crypto.randomUUID(),
    name: 'New Automation',
    host: '',
    port: 23,
    use_tls: true,
    steps: [],
  });

  const [recordMode, setRecordMode] = useState(false);
  const [editingStep, setEditingStep] = useState<AutomationStep | null>(null);
  const [showStepEditor, setShowStepEditor] = useState(false);

  const handleConnect = async (request: ConnectionRequest) => {
    setIsConnecting(true);
    try {
      const response = await apiClient.connect(request);
      setSessionId(response.session_id);
      setConnectionInfo(request);
      setScript((prev) => ({
        ...prev,
        host: request.host,
        port: request.port,
        use_tls: request.use_tls,
      }));
    } catch (error) {
      console.error('Connection failed:', error);
      alert('Failed to connect to host');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (sessionId) {
      try {
        await apiClient.disconnect(sessionId);
        setSessionId(null);
        setConnectionInfo(null);
      } catch (error) {
        console.error('Disconnect failed:', error);
      }
    }
  };

  const handleCellClick = (row: number, col: number) => {
    if (recordMode) {
      console.log(`Clicked cell: row=${row}, col=${col}`);
      const newStep: AutomationStep = {
        id: crypto.randomUUID(),
        action: 'send_text' as any,
        description: `Click at (${row}, ${col})`,
        row,
        col,
      };
      setEditingStep(newStep);
      setShowStepEditor(true);
    }
  };

  const handleSaveStep = (step: AutomationStep) => {
    setScript((prev) => {
      const existingIndex = prev.steps.findIndex((s) => s.id === step.id);
      if (existingIndex >= 0) {
        const newSteps = [...prev.steps];
        newSteps[existingIndex] = step;
        return { ...prev, steps: newSteps };
      } else {
        return { ...prev, steps: [...prev.steps, step] };
      }
    });
    setShowStepEditor(false);
    setEditingStep(null);
  };

  const handleDeleteStep = (stepId: string) => {
    setScript((prev) => ({
      ...prev,
      steps: prev.steps.filter((s) => s.id !== stepId),
    }));
  };

  const handleSaveScript = async () => {
    try {
      await apiClient.createScript(script);
      alert('Script saved successfully!');
    } catch (error) {
      console.error('Failed to save script:', error);
      alert('Failed to save script');
    }
  };

  const moveStep = (index: number, direction: 'up' | 'down') => {
    setScript((prev) => {
      const newSteps = [...prev.steps];
      const targetIndex = direction === 'up' ? index - 1 : index + 1;
      if (targetIndex < 0 || targetIndex >= newSteps.length) return prev;
      [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];
      return { ...prev, steps: newSteps };
    });
  };

  return (
    <div className="h-screen bg-gray-100 dark:bg-gray-900 p-6 flex flex-col">
      <div className="max-w-7xl mx-auto flex-1 flex flex-col">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          3270 Terminal Automation Builder
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
          {/* Left Panel: Connection & Terminal */}
          <div className="flex flex-col gap-6">
            {!sessionId ? (
              <ConnectionForm onConnect={handleConnect} isConnecting={isConnecting} />
            ) : (
              <>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                        Connected to {connectionInfo?.host}
                      </h2>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Session: {sessionId}
                      </p>
                    </div>
                    <button
                      onClick={handleDisconnect}
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>

                  <div className="flex items-center gap-4 mb-4">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={recordMode}
                        onChange={(e) => setRecordMode(e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                        Record Mode
                      </span>
                    </label>
                    {recordMode && (
                      <span className="text-xs text-red-600 dark:text-red-400 font-medium">
                        Click on terminal to capture coordinates
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex-1 min-h-0">
                  <TerminalEmulator
                    sessionId={sessionId}
                    onCellClick={handleCellClick}
                    recordMode={recordMode}
                  />
                </div>
              </>
            )}
          </div>

          {/* Right Panel: Automation Steps */}
          <div className="flex flex-col gap-6 overflow-y-auto">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <input
                    type="text"
                    value={script.name}
                    onChange={(e) => setScript({ ...script, name: e.target.value })}
                    className="text-xl font-bold bg-transparent border-b border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {script.steps.length} steps
                  </p>
                </div>
                <button
                  onClick={handleSaveScript}
                  disabled={!sessionId || script.steps.length === 0}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Save Script
                </button>
              </div>

              <button
                onClick={() => {
                  setEditingStep(null);
                  setShowStepEditor(true);
                }}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors mb-4"
              >
                + Add Step
              </button>

              {/* Steps List */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {script.steps.map((step, index) => (
                  <div
                    key={step.id}
                    className="bg-gray-50 dark:bg-gray-700 p-3 rounded border border-gray-200 dark:border-gray-600"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded">
                            {index + 1}
                          </span>
                          <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {step.action.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        </div>
                        {step.description && (
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{step.description}</p>
                        )}
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {step.row !== undefined && `Row: ${step.row} `}
                          {step.col !== undefined && `Col: ${step.col} `}
                          {step.text && `Text: "${step.text}" `}
                          {step.key && `Key: ${step.key} `}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => moveStep(index, 'up')}
                          disabled={index === 0}
                          className="p-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-30"
                          title="Move up"
                        >
                          ↑
                        </button>
                        <button
                          onClick={() => moveStep(index, 'down')}
                          disabled={index === script.steps.length - 1}
                          className="p-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-30"
                          title="Move down"
                        >
                          ↓
                        </button>
                        <button
                          onClick={() => {
                            setEditingStep(step);
                            setShowStepEditor(true);
                          }}
                          className="p-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                          title="Edit"
                        >
                          ✎
                        </button>
                        <button
                          onClick={() => handleDeleteStep(step.id)}
                          className="p-1 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                          title="Delete"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {showStepEditor && (
              <StepEditor
                step={editingStep || undefined}
                onSave={handleSaveStep}
                onCancel={() => {
                  setShowStepEditor(false);
                  setEditingStep(null);
                }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
