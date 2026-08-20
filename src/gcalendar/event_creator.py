from datetime import datetime
from typing import Any

from googleapiclient.errors import HttpError

from gcalendar.auth import CalendarAuth
from config import CALENDAR_ID, DEFAULT_ATTENDEE_EMAIL, DEFAULT_EVENT_SUMMARY, TIME_ZONE
from monitor.session_tracker import CodingSession


class EventCreator:
  def __init__(
    self,
    auth: CalendarAuth | None = None,
    calendar_id: str = CALENDAR_ID,
    default_summary: str = DEFAULT_EVENT_SUMMARY,
    default_attendee_email: str = DEFAULT_ATTENDEE_EMAIL,
    timezone: str = TIME_ZONE,
  ):
    self._auth = auth or CalendarAuth()
    self._calendar_id = calendar_id
    self._default_summary = default_summary
    self._default_attendee_email = default_attendee_email
    self._timezone = timezone

  def createSessionEvent(self, session: CodingSession, summary: str | None = None) -> dict[str, Any] | None:
    event_body = self.buildEventBody(session, summary)

    try:
      service = self._auth.getService()
      event_result = service.events().insert(
        calendarId=self._calendar_id,
        body=event_body
      ).execute()

      return event_result

    except HttpError as error:
      print(f"Failed to create calendar event: {error}")
      return None

    except Exception as error:
      print(f"Unexpected error creating calendar event: {error}")
      return None

  def buildEventBody(self, session: CodingSession, summary: str | None = None) -> dict[str, Any]:
    event_summary = summary or self._default_summary

    return {
      "summary": event_summary,
      "description": self.buildDescription(session),
      "start": {
        "dateTime": session.start_time.isoformat(),
        "timeZone": self._timezone,
      },
      "end": {
        "dateTime": session.end_time.isoformat(),
        "timeZone": self._timezone,
      },
      "attendees": [
        {
          "email": self._default_attendee_email,
          "organizer": True,
          "self": True,
          "responseStatus": "accepted",
        }
      ],
      "reminders": {
        "useDefault": False,
        "overrides": [
        ],
      },
    }

  def buildDescription(self, session: CodingSession) -> str:
    return (
      f"Coding session tracked by CodeTimer\n\n"
      f"Duration: {session.duration_minutes} minutes {session.duration_seconds} seconds\n"
      f"First IDE: {session.first_app}\n"
      f"Last IDE: {session.last_app}\n"
      f"Started: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
      f"Ended: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

  def createCustomEvent(
    self,
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: str | None,
    attendee_email: str | None = None,
  ) -> dict[str, Any] | None:
    event_body = {
      "summary": summary,
      "start": {
        "dateTime": start_time.isoformat(),
        "timeZone": self._timezone,
      },
      "end": {
        "dateTime": end_time.isoformat(),
        "timeZone": self._timezone,
      },
      "attendees": [
        {
          "email": attendee_email,
          "organizer": True,
          "self": True,
          "responseStatus": "accepted",
        }
      ] if attendee_email else [],
    }

    if description:
      event_body["description"] = description

    try:
      service = self._auth.getService()

      return service.events().insert(
        calendarId=self._calendar_id,
        body=event_body,
      ).execute()

    except HttpError as error:
      print(f"Failed to create custom calendar event: {error}")
      return None
