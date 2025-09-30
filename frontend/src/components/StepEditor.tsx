import { useState } from 'react';
import { ActionType, type AutomationStep } from '../types/automation';

interface StepEditorProps {
  step?: AutomationStep;
  onSave: (step: AutomationStep) => void;
  onCancel: () => void;
}

export function StepEditor({ step, onSave, onCancel }: StepEditorProps) {
  const [action, setAction] = useState<ActionType>(step?.action || ActionType.SEND_TEXT);
  const [description, setDescription] = useState(step?.description || '');
  const [row, setRow] = useState(step?.row?.toString() || '');
  const [col, setCol] = useState(step?.col?.toString() || '');
  const [text, setText] = useState(step?.text || '');
  const [key, setKey] = useState(step?.key || '');
  const [timeout, setTimeout] = useState(step?.timeout?.toString() || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newStep: AutomationStep = {
      id: step?.id || crypto.randomUUID(),
      action,
      description: description || undefined,
      row: row ? parseInt(row) : undefined,
      col: col ? parseInt(col) : undefined,
      text: text || undefined,
      key: key || undefined,
      timeout: timeout ? parseFloat(timeout) : undefined,
    };

    onSave(newStep);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
        {step ? 'Edit Step' : 'Add Step'}
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Action Type
          </label>
          <select
            value={action}
            onChange={(e) => setAction(e.target.value as ActionType)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
          >
            {Object.values(ActionType).map((type) => (
              <option key={type} value={type}>
                {type.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
          />
        </div>

        {(action === ActionType.SEND_TEXT || action === ActionType.MOVE_CURSOR || action === ActionType.READ_POSITION) && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Row
              </label>
              <input
                type="number"
                value={row}
                onChange={(e) => setRow(e.target.value)}
                placeholder="0"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Column
              </label>
              <input
                type="number"
                value={col}
                onChange={(e) => setCol(e.target.value)}
                placeholder="0"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        )}

        {(action === ActionType.SEND_TEXT || action === ActionType.WAIT_FOR_TEXT || action === ActionType.ASSERT_TEXT) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Text
            </label>
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Text to send or expect"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
            />
          </div>
        )}

        {action === ActionType.SEND_KEY && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Key
            </label>
            <select
              value={key}
              onChange={(e) => setKey(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
            >
              <option value="enter">Enter</option>
              <option value="pf1">PF1</option>
              <option value="pf2">PF2</option>
              <option value="pf3">PF3</option>
              <option value="pf4">PF4</option>
              <option value="pf5">PF5</option>
              <option value="pf6">PF6</option>
              <option value="pf7">PF7</option>
              <option value="pf8">PF8</option>
              <option value="pf9">PF9</option>
              <option value="pf10">PF10</option>
              <option value="pf11">PF11</option>
              <option value="pf12">PF12</option>
              <option value="pa1">PA1</option>
              <option value="pa2">PA2</option>
              <option value="pa3">PA3</option>
              <option value="tab">Tab</option>
              <option value="clear">Clear</option>
            </select>
          </div>
        )}

        {(action === ActionType.WAIT || action === ActionType.WAIT_FOR_TEXT) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Timeout (seconds)
            </label>
            <input
              type="number"
              step="0.1"
              value={timeout}
              onChange={(e) => setTimeout(e.target.value)}
              placeholder="10"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
            />
          </div>
        )}

        <div className="flex gap-2 pt-4">
          <button
            type="submit"
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Save
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 bg-gray-300 hover:bg-gray-400 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-900 dark:text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
