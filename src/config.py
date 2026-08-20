from pathlib import Path

"""
Configuration settings for CodeTimer.

Centralizes all configuration values to make them easily adjustable
and to separate configuration from business logic.
"""

# Application Settings
ZED_APP = "Zed.exe"
VS_CODE_APP = "Code.exe"
APPS_TO_TRACK = [ZED_APP, VS_CODE_APP]

# Display names
APP_DISPLAY_NAMES = {
  "Zed.exe": "Zed",
  "Code.exe": "VS Code",
}

# Google Calendar API settings
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "primary"

# OAuth file paths
CREDENTIALS_FILE = Path(__file__).parent.parent / ".env" / "credentials.json"
TOKEN_FILE = Path(__file__).parent.parent / ".env" / "token.json"

# Timezone Settings
TIME_ZONE = "Asia/Manila"
TIME_ZONE_DISPLAY = "Asia/Manila PHT"

# Session Tracking Settings
MIN_SESSION_DURATION_IN_MINUTES = 15
MONITOR_INTERVAL_IN_SECONDS = 1

# Calendar Event Settings
DEFAULT_EVENT_SUMMARY = "Coding Session"
ATTENDEE_EMAIL_FILE = Path(__file__).parent.parent / ".env" / "email.txt"
if ATTENDEE_EMAIL_FILE.exists():
    with open(ATTENDEE_EMAIL_FILE, 'r') as f:
        content = f.read().strip()
        DEFAULT_ATTENDEE_EMAIL = content if content else "[EMAIL]"

# Log Display Settings
PRINT_SESSION_START = True
PRINT_SESSION_END = True
PRINT_DURATION = True
PRINT_EVENT_CREATED = True
