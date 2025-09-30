# AutoHost - 3270 Terminal Automation Builder

An interactive web-based automation builder for IBM 3270 mainframe terminals. Build, test, and execute automation scripts with a visual interface.

## Features

- **Live 3270 Terminal**: Real-time connection to mainframe hosts displayed in browser
- **Interactive Builder**: Visual automation designer with drag-and-drop step management
- **Click-to-Capture**: Click on terminal screen to capture coordinates for automation
- **Record Mode**: Capture user interactions as automation steps
- **Script Management**: Save, load, and execute automation scripts
- **WebSocket Streaming**: Real-time terminal updates
- **Modern Tech Stack**: Built with FastAPI, React, TypeScript, and IBM's tnz library

## Project Structure

```
AutoHost/
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration
│   │   ├── models/   # Data models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic (tnz integration)
│   ├── main.py       # Application entry point
│   └── pyproject.toml # Python dependencies
├── frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── api/      # API client
│   │   ├── components/ # React components
│   │   ├── pages/    # Page components
│   │   └── types/    # TypeScript types
│   └── package.json
├── scripts/          # Saved automation scripts (JSON)
└── logs/             # Execution logs and screenshots
```

## Prerequisites

- Python 3.12+
- Node.js 18+
- UV (Python package manager)
- Access to a 3270 mainframe host (for testing)

## Installation

### Backend Setup

```bash
cd backend

# Install dependencies with UV
uv sync

# Run the backend
uv run python main.py
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### 1. Connect to a Host

1. Navigate to the Builder page
2. Enter your 3270 host details:
   - Host address
   - Port (default: 23)
   - Enable/disable TLS
3. Click "Connect"

### 2. Build Automation

**Manual Mode:**
- Click "+ Add Step" to create automation steps
- Configure each step with:
  - Action type (send text, send key, wait, assert, etc.)
  - Coordinates (row/column)
  - Text or key to send
  - Timeout values

**Record Mode:**
- Enable "Record Mode" toggle
- Click on the terminal to capture coordinates
- A step editor will open with pre-filled coordinates
- Add text or key actions as needed

### 3. Manage Steps

- Drag steps up/down to reorder
- Edit steps by clicking the edit icon
- Delete unwanted steps
- Add descriptions for clarity

### 4. Save and Execute

- Give your automation a name
- Click "Save Script" to persist
- Navigate to Scripts page to view all saved scripts
- Click "Execute" to run an automation

## Automation Actions

- **CONNECT**: Connect to host
- **SEND_TEXT**: Type text at specific coordinates
- **SEND_KEY**: Send special keys (Enter, PF1-PF12, PA1-PA3, Tab, Clear)
- **MOVE_CURSOR**: Position cursor
- **WAIT**: Pause for specified duration
- **WAIT_FOR_TEXT**: Wait for text to appear on screen
- **READ_SCREEN**: Capture screen content
- **ASSERT_TEXT**: Verify text exists on screen
- **SCREENSHOT**: Capture screen image
- **DISCONNECT**: Close connection

## API Endpoints

### Connections
- `POST /api/v1/connections/connect` - Connect to host
- `POST /api/v1/connections/disconnect/{session_id}` - Disconnect
- `GET /api/v1/connections/sessions` - List active sessions
- `GET /api/v1/connections/screen/{session_id}` - Get screen data
- `POST /api/v1/connections/input` - Send input to terminal

### Automation
- `GET /api/v1/automation/scripts` - List all scripts
- `GET /api/v1/automation/scripts/{id}` - Get script by ID
- `POST /api/v1/automation/scripts` - Create new script
- `PUT /api/v1/automation/scripts/{id}` - Update script
- `DELETE /api/v1/automation/scripts/{id}` - Delete script
- `POST /api/v1/automation/execute/{id}` - Execute script

### WebSocket
- `WS /api/v1/ws/terminal/{session_id}` - Real-time terminal streaming

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **UV** - Fast Python package manager
- **tnz** - IBM 3270 terminal emulator library
- **Pydantic** - Data validation
- **WebSockets** - Real-time communication
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **xterm.js** - Terminal emulator
- **React Router** - Routing
- **TanStack Query** - API state management

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uv run python main.py

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint
uv run ruff check .
```

### Frontend Development

```bash
cd frontend

# Development server with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Project Archive

To create a clean zip archive (excluding dependencies and build artifacts):

```bash
./zip-project.sh
```

This will create a timestamped zip file like `AutoHost_20250930_143022.zip` that excludes:
- node_modules
- .venv, venv, ENV
- __pycache__, .pyc files
- .git
- dist, build folders
- Log files and scripts
- IDE configs

## Configuration

### Backend Configuration (`.env`)

```env
API_TITLE=3270 Terminal Automation Builder
API_VERSION=0.1.0
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]
SCRIPTS_DIR=../scripts
LOGS_DIR=../logs
```

## Security Notes

- Always use TLS when connecting to production mainframes
- Store credentials securely (not in automation scripts)
- Review automation scripts before execution
- Limit access to the builder interface
- Use appropriate firewall rules for the API

## Troubleshooting

### Connection Issues
- Verify host address and port
- Check firewall rules
- Ensure TLS settings match host requirements
- Review backend logs for connection errors

### WebSocket Issues
- Check browser console for errors
- Verify proxy configuration in `vite.config.ts`
- Ensure backend is running

### Terminal Display Issues
- Clear browser cache
- Check xterm.js version compatibility
- Verify screen dimensions in terminal settings

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open a GitHub issue.
