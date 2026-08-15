import wmi
import time

ZED_APP = "Zed.exe"
VS_CODE_APP = "Code.exe"
APPS_TO_TRACK = [VS_CODE_APP]

def appMonitor(c, apps, interval=1):
    # Initialise counts
    counts = {} # TODO: There should only be a single count for both IDEs. \
                #       Count is currently separated per app. 
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

                if current_count != old_count:
                    if old_count == 0 and current_count > 0:
                        # First instance opened
                        pid = current_procs[0].ProcessId  # get one PID
                        print(f"{app} opened (first instance). PID: {pid}")
                    elif old_count > 0 and current_count == 0:
                        # Last instance closed
                        # We don't have the PID of the closed one, but we can track if needed
                        print(f"{app} closed (last instance).")
                    # (Optionally handle multiple instances opening/closing at once,
                    # but we only care about transitions to/from zero.)

                    counts[app] = current_count

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    c = wmi.WMI()
    print("Monitoring coding session. Press Ctrl+C to stop.")
    appMonitor(c, APPS_TO_TRACK)