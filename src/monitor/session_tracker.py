from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable
from zoneinfo import ZoneInfo


from config import MIN_SESSION_DURATION_IN_MINUTES, TIME_ZONE


"""Represents a completed coding session."""
@dataclass
class CodingSession:
  start_time: datetime
  end_time: datetime
  duration: timedelta
  duration_minutes: int
  duration_seconds: int
  first_app: str
  last_app: str

  @property
  def meetsMinDuration(self) -> bool:
    return self.duration_minutes >= MIN_SESSION_DURATION_IN_MINUTES

  def __str__(self) -> str:
    return (
      f"CodingSession(start={self.start_time.strftime('%Y-%m-%d %H:%M:%S')}, "
      f"end={self.end_time.strftime('%Y-%m-%d %H:%M:%S')}, "
      f"duration={self.duration_minutes}m {self.duration_seconds}s, "
      f"first_app={self.first_app}, last_app={self.last_app})"
    )

"""Internal state of the session tracker."""
class SessionState:
  IDLE = "idle"
  ACTIVE = "active"

class SessionTracker:
  def __init__(
    self,
    timezone: ZoneInfo | None = None,
    min_duration_in_minutes: int = MIN_SESSION_DURATION_IN_MINUTES,
    onSessionStart: Callable[[str, datetime], None] | None= None,
    onSessionEnd: Callable[[CodingSession], None] | None= None,
  ):
    self._timezone = timezone or ZoneInfo(TIME_ZONE)
    self._min_duration_in_minutes = min_duration_in_minutes
    self.onSessionStart = onSessionStart
    self.onSessionEnd = onSessionEnd

    self._state = SessionState.IDLE
    self._start_time: datetime | None = None
    self._first_app: str | None = None
    self._last_app: str | None = None

  @property
  def state(self) -> str:
    return self._state

  @property
  def isActive(self) -> bool:
    return self._state == SessionState.ACTIVE

  @property
  def first_app(self) -> str | None:
    return self._first_app

  def update(self, total_count: int, current_app: str | None = None) -> CodingSession | None:
    if self._state == SessionState.IDLE:
      return self.handleIdleState(total_count, current_app)
    else:
      return self.handleActiveState(total_count, current_app)

  def handleIdleState(self, total_count: int, current_app: str | None = None) -> CodingSession | None:
    if total_count > 0:
      self._state = SessionState.ACTIVE
      self._start_time = datetime.now(self._timezone)
      self._first_app = current_app or "Unknown"
      self._last_app = self._first_app

      if self.onSessionStart:
        self.onSessionStart(self._first_app, self._start_time)

      return None

  def handleActiveState(self, total_count: int, current_app: str | None) -> CodingSession | None:
    if total_count == 0:
      end_time = datetime.now(self._timezone)
      self._last_app = current_app or "Unknown"

      session = self.createSession(end_time)
      self.reset()

      if self.onSessionEnd:
        self.onSessionEnd(session)

      return session

    if current_app:
      self._last_app = current_app

    return None

  def createSession(self, end_time: datetime) -> CodingSession:
    assert self._start_time is not None
    duration = end_time - self._start_time
    total_seconds = int(duration.total_seconds())
    duration_minutes = total_seconds // 60
    duration_seconds = total_seconds % 60

    return CodingSession(
      start_time=self._start_time,
      end_time=end_time,
      duration=duration,
      duration_minutes=duration_minutes,
      duration_seconds=duration_seconds,
      first_app=self._first_app or "Unknown",
      last_app=self._last_app or "Unknown",
    )

  def reset(self) -> None:
    self._state = SessionState.IDLE
    self._start_time = None
    self._first_app = None
    self._last_app = None

  def forceEndSession(self) -> CodingSession | None:
    if self._state == SessionState.ACTIVE and self._start_time:
      end_time = datetime.now(self._timezone)
      session = self.createSession(end_time)
      self.reset()

      if self.onSessionEnd:
        self.onSessionEnd(session)

      return session
    return None
