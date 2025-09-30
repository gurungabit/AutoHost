import type {
  AutomationScript,
  ConnectionRequest,
  TerminalInput,
  ScreenData,
  Session,
  ExecutionLog,
} from '../types/automation';

const API_BASE = '/api/v1';

class ApiClient {
  // Connection endpoints
  async connect(request: ConnectionRequest): Promise<{ session_id: string; host: string; port: number; status: string }> {
    const response = await fetch(`${API_BASE}/connections/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error('Failed to connect');
    return response.json();
  }

  async disconnect(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/connections/disconnect/${sessionId}`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to disconnect');
  }

  async listSessions(): Promise<{ sessions: Session[] }> {
    const response = await fetch(`${API_BASE}/connections/sessions`);
    if (!response.ok) throw new Error('Failed to list sessions');
    return response.json();
  }

  async getScreen(sessionId: string): Promise<ScreenData> {
    const response = await fetch(`${API_BASE}/connections/screen/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get screen data');
    return response.json();
  }

  async sendInput(input: TerminalInput): Promise<void> {
    const response = await fetch(`${API_BASE}/connections/input`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    if (!response.ok) throw new Error('Failed to send input');
  }

  // Automation script endpoints
  async listScripts(): Promise<{ scripts: Array<Partial<AutomationScript>> }> {
    const response = await fetch(`${API_BASE}/automation/scripts`);
    if (!response.ok) throw new Error('Failed to list scripts');
    return response.json();
  }

  async getScript(scriptId: string): Promise<AutomationScript> {
    const response = await fetch(`${API_BASE}/automation/scripts/${scriptId}`);
    if (!response.ok) throw new Error('Failed to get script');
    return response.json();
  }

  async createScript(script: AutomationScript): Promise<{ status: string; script_id: string }> {
    const response = await fetch(`${API_BASE}/automation/scripts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(script),
    });
    if (!response.ok) throw new Error('Failed to create script');
    return response.json();
  }

  async updateScript(scriptId: string, script: AutomationScript): Promise<{ status: string; script_id: string }> {
    const response = await fetch(`${API_BASE}/automation/scripts/${scriptId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(script),
    });
    if (!response.ok) throw new Error('Failed to update script');
    return response.json();
  }

  async deleteScript(scriptId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/automation/scripts/${scriptId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete script');
  }

  async executeScript(scriptId: string): Promise<{ status: string; session_id: string; logs: ExecutionLog[] }> {
    const response = await fetch(`${API_BASE}/automation/execute/${scriptId}`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to execute script');
    return response.json();
  }

  // WebSocket connection
  connectWebSocket(sessionId: string): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/terminal/${sessionId}`);
    return ws;
  }
}

export const apiClient = new ApiClient();
