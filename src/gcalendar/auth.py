from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import CREDENTIALS_FILE, SCOPES, TOKEN_FILE

class CalendarAuth:
  def __init__(
    self,
    credentials_file: Path | None = None,
    token_file: Path | None = None,
    scopes: list[str] | None = None,
  ):
    self._credentials_file: Path = credentials_file or CREDENTIALS_FILE
    self._token_file: Path = token_file or TOKEN_FILE
    self.scopes: list[str] = scopes or SCOPES
    self._credentials = None
    self._service = None

  def getCredentials(self):
    if self._credentials and self._credentials.valid:
      return self._credentials

    self._credentials = self.loadCredentials()

    if not self._credentials or not self._credentials.valid:
      self._credentials = self.authenticate()

    self.saveCredentials()

    return self._credentials

  def loadCredentials(self) -> Credentials | None:
    if self._token_file.exists():
      try:
        return Credentials.from_authorized_user_file(
          str(self._token_file),
          self.scopes
        )
      except Exception:
        pass
    return None

  def authenticate(self):
    if not self._credentials_file.exists():
      raise FileNotFoundError(
        f"Credentials file not found: {self._credentials_file}\n"
        f"Please download OAuth credentials from Google Cloud Console "
        f"and save as {self._credentials_file}"
      )

    if self._credentials and self._credentials.expired and self._credentials.refresh_token:
      try:
        self._credentials.refresh(Request())
        return self._credentials
      except Exception:
        pass

    flow = InstalledAppFlow.from_client_secrets_file(
        str(self._credentials_file), self.scopes
    )
    credentials = flow.run_local_server(port=0)
    return credentials

  def saveCredentials(self) -> None:
    self._token_file.parent.mkdir(parents=True, exist_ok=True)

    if not self._credentials:
      return

    with open(self._token_file, "w") as f:
      f.write(self._credentials.to_json())

  def getService(self):
    if self._service is None:
      creds = self.getCredentials()
      self._service = build("calendar", "v3", credentials=creds)

    return self._service

  def resetCredentials(self) -> None:
    self._credentials = None
    self._service = None

    if self._token_file.exists():
      self._token_file.unlink()

  @property
  def isAuthenticated(self) -> bool:
    if self._credentials and self._credentials.valid:
      return True

    try:
      creds = self.loadCredentials()
      return creds is not None and creds.valid
    except Exception:
      return False
