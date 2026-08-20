from dataclasses import dataclass
import wmi

from config import APP_DISPLAY_NAMES, APPS_TO_TRACK

"""Information about a detected IDE process."""
@dataclass
class ProcessInfo:
  name: str
  display_name: str
  count: int
  process_ids: list[int]

  @property
  def is_running(self) -> bool:
    return self.count > 0

"""
Detects and tracks IDE processes using WMI.

This class encapsulates all WMI interaction logic, making it
easy to test and replace if needed.
"""
class IDEDetector:
  def __init__(self, apps_to_track: list[str] | None = None, wmi_connection = None):
    self._apps_to_track = apps_to_track or APPS_TO_TRACK
    self._wmi = wmi_connection or wmi.WMI()
    self._display_names = APP_DISPLAY_NAMES

  def getProcessCounts(self) -> dict[str, int]:
    counts = {}
    
    for app in self._apps_to_track:
      try:
        procs = self._wmi.Win32_Process(Name=app)
        counts[app] = len(procs)
      except Exception:
        counts[app] = 0
            
    return counts

  def getDetailedProcessInfo(self) -> dict[str, ProcessInfo]:
    info = {}

    for app in self._apps_to_track:
      try:
        procs = self._wmi.Win32_Process(Name=app)
        process_ids = [p.ProcessId for p in procs]
        
        info[app] = ProcessInfo(
          name=app,
          display_name=self._display_names.get(app, app),
          count=len(procs),
          process_ids=process_ids,
        )
      except Exception:
        info[app] = ProcessInfo(
          name=app,
          display_name=self._display_names.get(app, app),
          count=0,
          process_ids=[],
        )
        
    return info

  def getTotalCount(self) -> int:
    return sum(self.getProcessCounts().values())

  def getFirstRunningApp(self) -> str | None:
    for app in self._apps_to_track:
      try:
        procs = self._wmi.Win32_Process(Name=app)
        if len(procs) > 0:
          return app
      except Exception:
        continue
    return None

  def isAnyRunning(self) -> bool:
    return self.getTotalCount() > 0

  @property
  def appsToTrack(self) -> list[str]:
    return self._apps_to_track.copy()

  @property
  def displayNames(self) -> dict[str, str]:
    return self._display_names.copy()