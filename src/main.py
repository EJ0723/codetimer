from datetime import datetime
import signal
import time
import logging
from logging.handlers import RotatingFileHandler

from gcalendar.auth import CalendarAuth
from gcalendar.event_creator import EventCreator
from config import (
  APP_DISPLAY_NAMES,
  MIN_SESSION_DURATION_IN_MINUTES,
  MONITOR_INTERVAL_IN_SECONDS,
  PRINT_DURATION,
  PRINT_EVENT_CREATED,
  PRINT_SESSION_END,
  PRINT_SESSION_START,
)
from monitor.ide_detector import IDEDetector
from monitor.session_tracker import CodingSession, SessionTracker
from utils.time_helper import formatDateTime, formatDuration, getTimezoneDisplayName


# Logging setup
LOG_FILE = "codetimer.log"
LOG_MAX_BYTES = 5 * 1024 * 1024   # 5 MiB per file
LOG_BACKUP_COUNT = 3              # keep 3 old files

logger = logging.getLogger("CodeTimer")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class CodeTimer:
  def __init__(
    self,
    apps_to_track = None,
    interval: int = MONITOR_INTERVAL_IN_SECONDS,
    min_duration_minutes: int = MIN_SESSION_DURATION_IN_MINUTES,
    ide_detector: IDEDetector | None = None,
    session_tracker: SessionTracker | None = None,
    calendar_auth: CalendarAuth | None = None,
    event_creator: EventCreator | None = None,
  ):
    self._interval = interval
    self._running = False

    self._ide_detector = ide_detector or IDEDetector(apps_to_track)
    self._calendar_auth = calendar_auth or CalendarAuth()
    self._event_creator = event_creator or EventCreator(self._calendar_auth)
    
    self._session_tracker = session_tracker or SessionTracker(
      min_duration_in_minutes=min_duration_minutes,
      onSessionStart=self.onSessionStart,
      onSessionEnd=self.onSessionEnd,
    )

    signal.signal(signal.SIGINT, self.signalHandler)
    signal.signal(signal.SIGTERM, self.signalHandler)

  def signalHandler(self, signum, frame):
    logger.info("Shutdown signal received. Finishing current session...")
    self.stop()

  def onSessionStart(self, app_name: str, start_time: datetime) -> None:
    display_name = APP_DISPLAY_NAMES.get(app_name, app_name)
    if PRINT_SESSION_START:
      logger.info(f"\n🚀 First IDE opened: {display_name}")
      logger.info(f"   Session started at: {formatDateTime(start_time)}")
      logger.info(f"   Timezone: {getTimezoneDisplayName()}")

  def onSessionEnd(self, session: CodingSession) -> None:
    if PRINT_SESSION_END:
      logger.info(f"\n🛑 Last IDE closed: {session.last_app}")
      logger.info(f"   Session ended at: {formatDateTime(session.end_time)}")

    if PRINT_DURATION:
      duration_str = formatDuration(session.duration)
      logger.info(f"   Duration: {duration_str} ({session.duration_minutes}m {session.duration_seconds}s)")

    # Create calendar event if session meets minimum duration
    if session.meetsMinDuration:
      logger.info(f"   ✅ Session meets minimum duration ({MIN_SESSION_DURATION_IN_MINUTES} min) - creating calendar event...")
      event = self._event_creator.createSessionEvent(session)
      if event and PRINT_EVENT_CREATED:
        logger.info(f"   📅 Event created: {event.get('htmlLink', 'Unknown URL')}")
    else:
      logger.info(f"   ⏭️  Session shorter than {MIN_SESSION_DURATION_IN_MINUTES} minutes - not creating calendar event")

  def run(self) -> None:
    self._running = True
    logger.info("=" * 60)
    logger.info("CodeTimer - Coding Session Tracker")
    logger.info("=" * 60)
    logger.info(f"Monitoring: {', '.join(APP_DISPLAY_NAMES.get(a, a) for a in self._ide_detector.appsToTrack)}")
    logger.info(f"Interval: {self._interval} second(s)")
    logger.info(f"Minimum session: {MIN_SESSION_DURATION_IN_MINUTES} minutes")
    logger.info(f"Timezone: {getTimezoneDisplayName()}")
    logger.info(f"Calendar: {self._calendar_auth._credentials_file.parent.name}/{self._calendar_auth._token_file.name}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    try:
      self._calendar_auth.getCredentials()
      logger.info("✅ Google Calendar authentication ready\n")
    except FileNotFoundError as e:
      logger.error(f"❌ Authentication setup required: {e}")
      logger.info("Please ensure credentials.json exists in the .env folder")
      return
    except Exception as e:
      logger.error(f"❌ Authentication failed: {e}")
      return

    initial_counts = self._ide_detector.getProcessCounts()
    total_initial = sum(initial_counts.values())
    if total_initial > 0:
      running_apps = [APP_DISPLAY_NAMES.get(a, a) for a, c in initial_counts.items() if c > 0]
      logger.info(f"⚠️  IDE(s) already running: {', '.join(running_apps)}")
      logger.info("   Session will start when all close and a new one opens.\n")

    try:
      while self._running:
        time.sleep(self._interval)

        counts = self._ide_detector.getProcessCounts()
        total_count = sum(counts.values())

        current_app = None
        for app, count in counts.items():
          if count > 0:
            current_app = app
            break

        self._session_tracker.update(total_count, current_app)
    except KeyboardInterrupt:
      logger.info("\n\nInterrupted by user.")
    finally:
      self._shutdown()

  def stop(self) -> None:
    self._running = False

  def _shutdown(self) -> None:
    session = self._session_tracker.forceEndSession()
    if session:
      logger.info(f"\n📝 Final session recorded: {session.duration_minutes}m {session.duration_seconds}s")
      
    logger.info("\n👋 CodeTimer stopped. Goodbye!")

def main():
  app = CodeTimer()
  app.run()

if __name__ == "__main__":
  main()