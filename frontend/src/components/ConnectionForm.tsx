import { useState } from 'react';
import type { ConnectionRequest } from '../types/automation';

interface ConnectionFormProps {
  onConnect: (request: ConnectionRequest) => Promise<void>;
  isConnecting: boolean;
}

export function ConnectionForm({ onConnect, isConnecting }: ConnectionFormProps) {
  const [host, setHost] = useState('');
  const [port, setPort] = useState('23');
  const [useTls, setUseTls] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onConnect({
      host,
      port: parseInt(port),
      use_tls: useTls,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Connect to 3270 Host</h2>

      <div className="space-y-4">
        <div>
          <label htmlFor="host" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Host Address
          </label>
          <input
            id="host"
            type="text"
            value={host}
            onChange={(e) => setHost(e.target.value)}
            placeholder="mainframe.example.com"
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div>
          <label htmlFor="port" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Port
          </label>
          <input
            id="port"
            type="number"
            value={port}
            onChange={(e) => setPort(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div className="flex items-center">
          <input
            id="useTls"
            type="checkbox"
            checked={useTls}
            onChange={(e) => setUseTls(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="useTls" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Use TLS/SSL
          </label>
        </div>

        <button
          type="submit"
          disabled={isConnecting}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
        >
          {isConnecting ? 'Connecting...' : 'Connect'}
        </button>
      </div>
    </form>
  );
}
