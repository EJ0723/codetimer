import wmi
import time
from datetime import datetime
from zoneinfo import ZoneInfo

ZED_APP = "Zed.exe"
VS_CODE_APP = "Code.exe"
APPS_TO_TRACK = [VS_CODE_APP]

def appMonitor(c, apps, interval=1):
  # Initialise counts
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
        total_count = sum(counts.values())

        # detect a change in process count for specific app
        if current_count != old_count:
          # detect first instance opened among both IDEs
          if current_count > 0 and total_count == 0:
            print(f"First IDE opened. ({"VS Code" if app == "Code.exe" else app})")
            start = datetime.now(ZoneInfo("Asia/Manila"))
            print(f"Start time: {start.strftime('%Y-%m-%d %H:%M:%S')}")
          # detect last instance closed among both IDEs
          elif current_count == 0 and total_count > 0:
            print(f"Last IDE closed. ({"VS Code" if app == "Code.exe" else app})")
            end = datetime.now(ZoneInfo("Asia/Manila"))
            print(f"End time: {end.strftime('%Y-%m-%d %H:%M:%S')}")

            # Get duration in minutes and seconds
            duration = (end - start) if (start and end) else None
            duration = divmod(duration.days * (24*60*60) + duration.seconds, 60) if duration else None

            duration_in_mins = duration[0] if duration else 0
            duration_in_secs = duration[1] if duration else 0
            print(f"Duration: {duration_in_mins} mins {duration_in_secs} secs")

          # Update counts for next iteration
          counts[app] = current_count
          total_count = sum(counts.values())

  except KeyboardInterrupt:
    print("\nExiting...")

if __name__ == "__main__":
  c = wmi.WMI()
  print("Monitoring coding session. Press Ctrl+C to stop.")
  appMonitor(c, APPS_TO_TRACK)
