import wmi
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ZED_APP = "Zed.exe"
VS_CODE_APP = "Code.exe"
APPS_TO_TRACK = [ZED_APP, VS_CODE_APP]

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# def main():
#   creds = None

#   if os.path.exists(".env/token.json"):
#     creds = Credentials.from_authorized_user_file(".env/token.json", SCOPES)

#   if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#       creds.refresh(Request())
#     else:
#       flow = InstalledAppFlow.from_client_secrets_file(".env/credentials.json", SCOPES)
#       creds = flow.run_local_server(port=0)
#     with open(".env/token.json", "w") as token:
#       token.write(creds.to_json())

#   try:
#     service = build("calendar", "v3", credentials=creds)



#   except HttpError as error:
#     print(f"An error occurred: {error}")

def appMonitor(c, apps, interval=1):
  # Initialize credentials
  creds = None

  if os.path.exists(".env/token.json"):
    creds = Credentials.from_authorized_user_file(".env/token.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(".env/credentials.json", SCOPES)
      creds = flow.run_local_server(port=0)
    with open(".env/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Initialize service
    service = build("calendar", "v3", credentials=creds)

    # Initialize counts
    counts = {}
    start = None
    end = None

    for app in apps:
      procs = c.Win32_Process(Name=app)
      counts[app] = len(procs)
      if counts[app] > 0:
        print(f"{app} is already running ({counts[app]} instances).")

    try:
      while True:
        time.sleep(interval)
        for app in apps:
          current_procs = c.Win32_Process(Name=app)
          current_count = len(current_procs)
          old_count = counts[app]
          total_count = sum([len(c.Win32_Process(Name=app)) for app in apps])
          old_total_count = sum(counts.values())

          # detect a change in process count for specific app
          if current_count != old_count:
            # print(f"current_count ({app}): {current_count}\n old_count ({app}): {old_count}\n total_count: {total_count}\n old_total_count: {old_total_count}\n")
            # detect first instance opened among both IDEs
            if current_count > 0 and old_total_count == 0:
              print(f"First IDE opened. ({"VS Code" if app == "Code.exe" else app})")
              start = datetime.now(ZoneInfo("Asia/Manila"))
              print(f"Start time: {start.strftime('%Y-%m-%d %H:%M:%S')}")
            # detect last instance closed among both IDEs
            elif current_count == 0 and total_count == 0:
              print(f"Last IDE closed. ({"VS Code" if app == "Code.exe" else app})")
              end = datetime.now(ZoneInfo("Asia/Manila"))
              print(f"End time: {end.strftime('%Y-%m-%d %H:%M:%S')}")

              # Get duration in minutes and seconds
              duration = (end - start) if (start and end) else None
              duration = divmod(duration.days * (24*60*60) + duration.seconds, 60) if duration else None

              duration_in_mins = duration[0] if duration else 0
              duration_in_secs = duration[1] if duration else 0
              print(f"Duration: {duration_in_mins} mins {duration_in_secs} secs")

              # Create event if duration is 20 minutes or more
              if duration_in_mins >= 20:
                event = {
                  "summary": "Coding Session",
                  "start": {
                    "dateTime": start.isoformat() if start else None,
                    "timeZone": "Asia/Manila",
                  },
                  "end": {
                    "dateTime": end.isoformat() if end else None,
                    "timeZone": "Asia/Manila",
                  },
                  "attendees": [
                    {
                      "email": "joshwin.ona0723@gmail.com",
                      "organizer": True,
                      "self": True,
                      "responseStatus": "accepted",
                    }
                  ],
                }

                # Insert event into calendar
                event_result = service.events().insert(calendarId="primary", body=event).execute()
                print(f"Event created: {event_result.get('htmlLink')}")

            # Update counts for next iteration
            counts[app] = current_count
            # total_count = sum(counts.values())

    except KeyboardInterrupt:
      print("\nExiting...")

  except HttpError as error:
    print(f"An error occurred: {error}")

if __name__ == "__main__":
  c = wmi.WMI()
  print("Monitoring coding session. Press Ctrl+C to stop.")
  appMonitor(c, APPS_TO_TRACK)
