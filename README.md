# codetimer

A Windows utility that tracks your coding sessions by monitoring when specific applications (e.g., VS Code, Zed) are opened or closed, and logs completed sessions to your Google Calendar.

**Author:** Edward Joshwin Oña

## Features

- **IDE detection** — Detects when VS Code (`Code.exe`) and Zed (`Zed.exe`) are opened or closed using WMI
- **Session tracking** — Tracks start/end time, duration, and first/last IDE per session
- **Google Calendar integration** — Automatically creates a calendar event when a session meets the minimum duration (default: 15 minutes)
- **Timezone-aware** — All timestamps use `Asia/Manila` (PHT) by default
- **Rotating logs** — Session activity is written to `codetimer.log` (5 MiB per file, 3 backups)

## Requirements

- Windows (the `wmi` package is Windows-only)
- Python 3.10+ (developed with 3.12.5)

## Project Structure

```
codetimer/
├── src/
│   ├── main.py                     # Entry point / orchestrator
│   ├── config.py                   # Centralized configuration
│   ├── monitor/
│   │   ├── ide_detector.py         # WMI process detection
│   │   └── session_tracker.py      # Session state machine
│   ├── gcalendar/
│   │   ├── auth.py                 # OAuth2 credential handling
│   │   └── event_creator.py        # Calendar event creation
│   └── utils/
│       └── time_helper.py          # Timezone and duration helpers
├── .env/                           # Local secrets (git-ignored)
│   ├── credentials.json            # Google OAuth client credentials
│   ├── token.json                  # Generated on first auth
│   └── email.txt                   # Attendee email for calendar events
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd codetimer
   ```

2. **Create and activate a virtual environment** (Windows PowerShell)
   ```powershell
   virtualenv -p 3.12.5 venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up Google Calendar access**
   - Create OAuth client credentials in the [Google Cloud Console](https://console.cloud.google.com/) and save them as `.env/credentials.json`
   - Put the email to add as attendee in `.env/email.txt` (optional — defaults to `[EMAIL]`)

5. **Run the script**
   ```powershell
   py .\src\main.py
   ```

## Usage

Start the script, then simply open or close VS Code / Zed:

- Opening an IDE starts a session
- Closing all tracked IDEs ends the session
- Sessions lasting at least 15 minutes (configurable) generate a Google Calendar event
- Press `Ctrl+C` to stop gracefully — the current session is finalized and logged

Activity is written to `codetimer.log` in the project root.

## Configuration

Adjust settings in `src/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `APPS_TO_TRACK` | `Zed.exe`, `Code.exe` | Applications to monitor |
| `MIN_SESSION_DURATION_IN_MINUTES` | `15` | Minimum session length to create a calendar event |
| `MONITOR_INTERVAL_IN_SECONDS` | `1` | Polling interval for process detection |
| `TIME_ZONE` | `Asia/Manila` | Timezone for all session timestamps |
| `CALENDAR_ID` | `primary` | Google Calendar to write events to |
| `DEFAULT_EVENT_SUMMARY` | `Coding Session` | Calendar event title |

## Development

**Update dependencies** — after installing a new package:
```powershell
pip freeze > requirements.txt
```

**Linting / Formatting (optional)** — if you add linting tools later:
```powershell
pip install -r requirements-dev.txt   # if you create a dev file
# e.g., flake8 . or black .
```

## Notes

- The script relies on the `wmi` package, which is Windows-only. Development and execution must be done on a Windows Python interpreter.
- Keep the virtual environment and secrets out of version control (`.gitignore` covers `venv/` and `.env/`).
- First run opens a browser for Google OAuth consent; subsequent runs reuse `.env/token.json` until it expires.

## License

MIT — feel free to use and modify.