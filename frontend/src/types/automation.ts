export enum ActionType {
  CONNECT = 'connect',
  SEND_TEXT = 'send_text',
  SEND_KEY = 'send_key',
  MOVE_CURSOR = 'move_cursor',
  WAIT = 'wait',
  WAIT_FOR_TEXT = 'wait_for_text',
  READ_SCREEN = 'read_screen',
  READ_POSITION = 'read_position',
  ASSERT_TEXT = 'assert_text',
  SCREENSHOT = 'screenshot',
  DISCONNECT = 'disconnect',
}

export interface AutomationStep {
  id: string;
  action: ActionType;
  params?: Record<string, any>;
  description?: string;
  row?: number;
  col?: number;
  text?: string;
  key?: string;
  timeout?: number;
}

export interface AutomationScript {
  id: string;
  name: string;
  description?: string;
  host: string;
  port: number;
  use_tls: boolean;
  steps: AutomationStep[];
  created_at?: string;
  updated_at?: string;
}

export interface ConnectionRequest {
  host: string;
  port: number;
  use_tls: boolean;
  session_id?: string;
}

export interface TerminalInput {
  session_id: string;
  text?: string;
  key?: string;
  row?: number;
  col?: number;
}

export interface ScreenData {
  session_id: string;
  rows: number;
  cols: number;
  cursor_row: number;
  cursor_col: number;
  text: string;
  fields?: Array<Record<string, any>>;
}

export interface ExecutionLog {
  step_id: string;
  status: 'success' | 'error' | 'running';
  message?: string;
  timestamp: string;
  screenshot?: string;
}

export interface Session {
  session_id: string;
  host: string;
  port: number;
  is_connected: boolean;
}
