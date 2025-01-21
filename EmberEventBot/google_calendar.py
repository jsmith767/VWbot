from __future__ import print_function

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from EmberEventBot.settings import EmberEventBotSettings

SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar']
settings = EmberEventBotSettings()

GOOGLE_CALENDAR_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_CALENDAR_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
GOOGLE_CALENDAR_REDIRECT_URI = "http://localhost"


def get_creds():
    if settings.google_cal_client_secret == "":
        raise Exception("No client secret detected")
    refresh_token = settings.google_cal_refresh_token
    if refresh_token == "":
        # No refresh token detected in environment
        flow = InstalledAppFlow.from_client_config(
            {"installed": {"client_id": settings.google_cal_client_id,
                           "project_id": settings.google_cal_project_id,
                           "auth_uri": GOOGLE_CALENDAR_AUTH_URI,
                           "token_uri": GOOGLE_CALENDAR_TOKEN_URI,
                           "auth_provider_x509_cert_url": GOOGLE_CALENDAR_CERT_URL,
                           "client_secret": settings.google_cal_client_secret,
                           "redirect_uris": [GOOGLE_CALENDAR_REDIRECT_URI]}}
            , scopes=SCOPES)
        creds = flow.run_local_server(
            port=0,
            success_message="Success. Check the logs for the refresh token to add it to your environment or suffer "
                            "through having to run the authentication flow every time you create an event."
        )
        refresh_token = creds.refresh_token
        print(
            f"Your refresh token is: {refresh_token}. Add it to your environment as GOOGLE_CAL_REFRESH_TOKEN")
    creds = Credentials.from_authorized_user_info(info={
        "client_secret": settings.google_cal_client_secret,
        "refresh_token": refresh_token,
        "client_id": settings.google_cal_client_id,
    }, scopes=SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds.valid:
        if creds.expired:
            creds.refresh(Request())
    return creds


def get_service(credentials):
    return build("calendar", "v3", credentials=credentials)


if __name__ == "__main__":
    get_creds()
