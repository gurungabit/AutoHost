import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import '@xterm/xterm/css/xterm.css';
import type { ScreenData } from '../types/automation';

interface TerminalEmulatorProps {
  sessionId: string;
  onCellClick?: (row: number, col: number) => void;
  recordMode?: boolean;
}

export function TerminalEmulator({ sessionId, onCellClick, recordMode = false }: TerminalEmulatorProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize xterm
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Courier New, monospace',
      theme: {
        background: '#000000',
        foreground: '#00ff00',
      },
      rows: 24,
      cols: 80,
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();

    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);

    // Ensure container has dimensions before opening
    const container = terminalRef.current;
    if (container.offsetHeight === 0) {
      container.style.height = '600px';
    }

    terminal.open(container);

    // Don't use fit addon - keep the terminal at exactly 24x80 for 3270 compatibility
    // setTimeout(() => {
    //   fitAddon.fit();
    // }, 0);

    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;

    // Handle window resize
    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);

    // Handle clicks for coordinate capture
    if (onCellClick) {
      terminal.onData(() => {
        // Capture cursor position on input
        const buffer = terminal.buffer.active;
        const row = buffer.cursorY;
        const col = buffer.cursorX;
        if (recordMode) {
          onCellClick(row, col);
        }
      });
    }

    // WebSocket connection
    const connectWebSocket = () => {
      // Prevent duplicate connections
      if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
        return;
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/terminal/${sessionId}`);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'screen_update') {
          updateScreen(data.data as ScreenData);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket closed');
      };

      wsRef.current = ws;
    };

    // Handle keyboard input
    terminal.onData((data) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          command: 'input',
          text: data,
        }));
      }
    });

    // Small delay to avoid race condition in React StrictMode
    const timer = setTimeout(() => {
      connectWebSocket();
    }, 100);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', handleResize);
      wsRef.current?.close();
      terminal.dispose();
    };
  }, [sessionId, onCellClick, recordMode]);

  const updateScreen = (screenData: ScreenData) => {
    const terminal = xtermRef.current;
    if (!terminal) return;

    // Resize terminal if needed
    if (terminal.rows !== screenData.rows || terminal.cols !== screenData.cols) {
      terminal.resize(screenData.cols, screenData.rows);
    }

    // Clear terminal and reset cursor
    terminal.reset();

    // Write screen text line by line
    const lines = screenData.text.split('\n');
    lines.forEach((line, index) => {
      if (index > 0) {
        terminal.write('\r\n');
      }
      terminal.write(line);
    });

    // Move cursor to correct position
    terminal.write(`\x1b[${screenData.cursor_row + 1};${screenData.cursor_col + 1}H`);
  };

  const handleTerminalClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!onCellClick || !xtermRef.current) return;

    const terminal = xtermRef.current;
    const rect = terminalRef.current?.getBoundingClientRect();
    if (!rect) return;

    // Calculate cell position from mouse coordinates
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Approximate cell dimensions
    const cellWidth = rect.width / terminal.cols;
    const cellHeight = rect.height / terminal.rows;

    const col = Math.floor(x / cellWidth);
    const row = Math.floor(y / cellHeight);

    onCellClick(row, col);
  };

  return (
    <div className="relative h-full">
      <div className={`absolute top-2 right-2 px-2 py-1 rounded text-xs z-10 ${isConnected ? 'bg-green-600' : 'bg-red-600'} text-white`}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      <div
        ref={terminalRef}
        className="border border-gray-700 rounded h-full"
        onClick={handleTerminalClick}
        style={{
          cursor: recordMode ? 'crosshair' : 'text',
          minHeight: '600px',
        }}
      />
    </div>
  );
}
