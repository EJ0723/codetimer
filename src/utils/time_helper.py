from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def getTimezone(tz_name: str = "Asia/Manila") -> ZoneInfo:
  try:
    return ZoneInfo(tz_name)
  except ZoneInfoNotFoundError:
    return ZoneInfo("UTC")

def nowInTimezone(tz_name: str = "Asia/Manila") -> datetime:
  return datetime.now(getTimezone(tz_name))

def formatDateTime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
  return dt.strftime(format_str)

def formatDuration(duration: timedelta) -> str:
  total_seconds = int(duration.total_seconds())

  if total_seconds < 0:
    return "0s"

  hours = total_seconds // 3600
  minutes = (total_seconds % 3600) // 60
  seconds = total_seconds % 60

  parts: list[str] = []
  if hours > 0:
    parts.append(f"{hours}h")
  if minutes > 0 or hours > 0:
    parts.append(f"{minutes}m")
  parts.append(f"{seconds}s")

  return " ".join(parts)

def parseDurationMinutesSeconds(total_seconds: int):
  if total_seconds < 0:
    return (0, 0)
  return divmod(total_seconds, 60)

def calculateDuration(start: datetime, end: datetime) -> timedelta:
  if start.tzinfo is None or end.tzinfo is None:
    raise ValueError("Both datetimes must be timezone-aware")
  return end - start

def getDurationMinutesSeconds(duration: timedelta):
  total_seconds = int(duration.total_seconds())
  if total_seconds < 0:
    return (0, 0)
  return divmod(total_seconds, 60)

def isSessionLongEnough(duration: timedelta, minMinutes: int = 15) -> bool:
  return duration.total_seconds() >= minMinutes * 60

def getTimezoneDisplayName(tz_name: str = "Asia/Manila") -> str:
  tz = getTimezone(tz_name)
  now = datetime.now(tz)
  abbrev = now.tzname()
  return f"{tz_name} ({abbrev})" if abbrev else tz_name
