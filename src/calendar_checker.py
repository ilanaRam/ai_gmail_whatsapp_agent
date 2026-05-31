import os
import inspect

# to work with google tools for exp: calendar (this tool holds personal data so it requires authentications and credentials)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from dotenv import load_dotenv

# to work with .env
load_dotenv()

# SCOPES are permissions (like a keys from your home) you give to your app, these permissions can be:
#--------Permission -------- Meaning------------------------
# calendar.readonly,        Read only — view events
# calendar.events,          Read + Create + Edit + Delete events
# calendar,                 Read + Create + Edit + Delete events + manage settings
#--------------------------------------------------------
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# what is credentials.json file:
# this file hold passwords - you should not tell or show or upload this file to git
# it contains permanent secretes from Google, we got them when I set up my app
# It contains secret codes (like a username and password) that prove your app is allowed to talk to Google.
# Google doesn’t trust apps by default. You need to prove your app is allowed to access your calendar
CREDENTIALS_FILE_NAME = 'google_calendar_credentials.json'

# what is token.json file:
# This file is created automatically the first time you run the app.
# It stores a temporary access token (like a temporary pass) so you don’t have to 'log in' every time. It is like "remember me"
# each time the code will run it will check if token.json exists - if yes it will not rewrite it else it will perform log in and token.json will be re created
TOKEN_FILE = 'token.json'

def connect_to_google_calendar():
    """
    If first run → opens browser for Google login → saves token.json
    Then every next run after → uses token.json automatically — no login needed
    :return: calendar_service_obj
    """

    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    my_app_creds = None

    # token.json stores the user's access token
    # it is created automatically on first login
    if os.path.exists(TOKEN_FILE):
        my_app_creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # if no valid credentials available, or they exist by not valid any longer (not up to dated) then ... ask user to login again
    if not my_app_creds or not my_app_creds.valid:
        if my_app_creds and my_app_creds.expired and my_app_creds.refresh_token:
            my_app_creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE_NAME, SCOPES)
            my_app_creds = flow.run_local_server(port=0)

        # save credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(my_app_creds.to_json())

    # build the calendar service object
    calendar_service_obj = build('calendar',
                                'v3',
                                credentials=my_app_creds)
    print(f"{func_name}: App is connected to Google Calendar successfully!")
    return calendar_service_obj


if __name__ == "__main__":
    connect_to_google_calendar()